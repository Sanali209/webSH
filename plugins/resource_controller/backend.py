"""Resource Controller Plugin Backend - Monitor and manage system resources."""
import logging
import psutil
import time
from typing import Dict, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from core.sdk import PluginBase, PluginContext
from .config import ResourceSettings

logger = logging.getLogger(__name__)


class ResourceUsage(BaseModel):
    """Resource usage statistics for a plugin."""
    plugin_id: str
    cpu_percent: float
    memory_mb: float
    active_workers: int
    timestamp: float


class ResourceMonitor:
    """
    Service for monitoring system resources.
    
    Tracks CPU, memory, and worker usage per plugin.
    """
    
    def __init__(self, settings: ResourceSettings):
        self.settings = settings
        self._usage_data: Dict[str, ResourceUsage] = {}
        self._process = psutil.Process()
    
    def get_system_usage(self) -> Dict[str, float]:
        """
        Get overall system resource usage.
        
        Returns:
            Dictionary with cpu_percent, memory_mb, memory_percent
        """
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        return {
            "cpu_percent": cpu_percent,
            "memory_mb": memory.used / (1024 * 1024),
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / (1024 * 1024),
        }
    
    def get_process_usage(self) -> Dict[str, float]:
        """
        Get resource usage of the current process (PC Center backend).
        
        Returns:
            Dictionary with cpu_percent, memory_mb
        """
        try:
            cpu_percent = self._process.cpu_percent(interval=0.1)
            memory_info = self._process.memory_info()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_mb": memory_info.rss / (1024 * 1024),
                "num_threads": self._process.num_threads(),
            }
        except Exception as e:
            logger.error(f"Error getting process usage: {e}")
            return {
                "cpu_percent": 0.0,
                "memory_mb": 0.0,
                "num_threads": 0,
            }
    
    def update_plugin_usage(self, plugin_id: str, cpu: float = 0.0, 
                           memory: float = 0.0, workers: int = 0):
        """
        Update resource usage for a specific plugin.
        
        Args:
            plugin_id: Plugin identifier
            cpu: CPU usage percentage
            memory: Memory usage in MB
            workers: Number of active workers
        """
        self._usage_data[plugin_id] = ResourceUsage(
            plugin_id=plugin_id,
            cpu_percent=cpu,
            memory_mb=memory,
            active_workers=workers,
            timestamp=time.time()
        )
    
    def get_plugin_usage(self, plugin_id: str) -> Optional[ResourceUsage]:
        """Get resource usage for a specific plugin."""
        return self._usage_data.get(plugin_id)
    
    def get_all_usage(self) -> Dict[str, ResourceUsage]:
        """Get resource usage for all plugins."""
        return self._usage_data.copy()
    
    def check_quota(self, plugin_id: str) -> bool:
        """
        Check if plugin is within resource quotas.
        
        Returns:
            True if within limits, False if over quota
        """
        usage = self.get_plugin_usage(plugin_id)
        if not usage:
            return True
        
        # Check CPU quota
        if usage.cpu_percent > self.settings.max_cpu_percent:
            logger.warning(f"Plugin {plugin_id} exceeds CPU quota: "
                         f"{usage.cpu_percent}% > {self.settings.max_cpu_percent}%")
            return False
        
        # Check memory quota
        if usage.memory_mb > self.settings.max_memory_mb:
            logger.warning(f"Plugin {plugin_id} exceeds memory quota: "
                         f"{usage.memory_mb}MB > {self.settings.max_memory_mb}MB")
            return False
        
        # Check worker quota
        if usage.active_workers > self.settings.max_workers_per_plugin:
            logger.warning(f"Plugin {plugin_id} exceeds worker quota: "
                         f"{usage.active_workers} > {self.settings.max_workers_per_plugin}")
            return False
        
        return True


class ResourceControllerPlugin(PluginBase):
    """
    Resource Controller Plugin.
    
    Monitors and manages system resource usage by plugins.
    """
    
    def __init__(self):
        self.settings = ResourceSettings()
        self.monitor: Optional[ResourceMonitor] = None
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes for resource monitoring."""
        
        @self.router.get("/resources")
        async def get_resources():
            """
            Get system and per-plugin resource usage.
            
            Returns:
                Dictionary with system and plugin resource statistics
            """
            if not self.monitor:
                return {"error": "Resource monitor not initialized"}
            
            # Get system-wide usage
            system_usage = self.monitor.get_system_usage()
            process_usage = self.monitor.get_process_usage()
            
            # Get per-plugin usage
            plugin_usage = {
                plugin_id: usage.model_dump()
                for plugin_id, usage in self.monitor.get_all_usage().items()
            }
            
            return {
                "system": system_usage,
                "process": process_usage,
                "plugins": plugin_usage,
                "quotas": {
                    "max_workers_per_plugin": self.settings.max_workers_per_plugin,
                    "max_cpu_percent": self.settings.max_cpu_percent,
                    "max_memory_mb": self.settings.max_memory_mb,
                }
            }
        
        @self.router.get("/resources/{plugin_id}")
        async def get_plugin_resources(plugin_id: str):
            """Get resource usage for a specific plugin."""
            if not self.monitor:
                return {"error": "Resource monitor not initialized"}
            
            usage = self.monitor.get_plugin_usage(plugin_id)
            if not usage:
                return {
                    "plugin_id": plugin_id,
                    "message": "No usage data available",
                    "within_quota": True
                }
            
            within_quota = self.monitor.check_quota(plugin_id)
            
            return {
                **usage.model_dump(),
                "within_quota": within_quota,
                "quotas": {
                    "max_workers": self.settings.max_workers_per_plugin,
                    "max_cpu_percent": self.settings.max_cpu_percent,
                    "max_memory_mb": self.settings.max_memory_mb,
                }
            }
        
        @self.router.get("/info")
        async def get_info():
            """Get resource controller plugin information."""
            return {
                "name": "Resource Controller",
                "version": "0.1.0",
                "type": "system",
                "capabilities": ["resources.monitor", "resources.quota"],
                "status": "active" if self.monitor else "inactive",
                "settings": self.settings.model_dump()
            }
    
    def on_load(self, context: PluginContext) -> None:
        """
        Called when the plugin is loaded.
        Initializes the resource monitor.
        """
        logger.info("Loading Resource Controller Plugin...")
        
        # Initialize resource monitor
        self.monitor = ResourceMonitor(self.settings)
        
        # Register capabilities for other plugins
        def check_quota(plugin_id: str) -> bool:
            """Check if plugin is within resource quotas."""
            return self.monitor.check_quota(plugin_id) if self.monitor else True
        
        def get_usage(plugin_id: str) -> Optional[Dict]:
            """Get resource usage for a plugin."""
            if not self.monitor:
                return None
            usage = self.monitor.get_plugin_usage(plugin_id)
            return usage.model_dump() if usage else None
        
        context.capabilities.register("resources.check_quota", check_quota)
        context.capabilities.register("resources.get_usage", get_usage)
        
        logger.info("Resource Controller Plugin loaded successfully")
        logger.info(f"Resource quotas: {self.settings.max_workers_per_plugin} workers, "
                   f"{self.settings.max_cpu_percent}% CPU, {self.settings.max_memory_mb}MB memory")
    
    def on_activate(self) -> None:
        """Called when the plugin is activated."""
        logger.info("Resource Controller Plugin activated")
    
    def on_deactivate(self) -> None:
        """Called when the plugin is deactivated."""
        logger.info("Resource Controller Plugin deactivated")
