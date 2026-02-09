"""System Dashboard Plugin Backend - Minimal backend for UI hosting."""
import logging
from fastapi import APIRouter

from core.sdk import PluginBase, PluginContext
from .config import DashboardSettings

logger = logging.getLogger(__name__)


class SystemDashboardPlugin(PluginBase):
    """
    System Dashboard Plugin that provides the main dashboard interface.
    
    This plugin is primarily frontend-focused and serves as the host
    for widgets from other plugins.
    """
    
    def __init__(self):
        self.settings = DashboardSettings()
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup minimal API routes for the dashboard."""
        
        @self.router.get("/config")
        async def get_dashboard_config():
            """
            Get dashboard configuration.
            
            Returns layout settings for the frontend.
            """
            return {
                "grid_columns": self.settings.grid_columns,
                "row_height": self.settings.row_height,
                "gap": self.settings.gap,
                "default_view": self.settings.default_view
            }
        
        @self.router.get("/info")
        async def get_info():
            """Get dashboard plugin information."""
            return {
                "name": "System Dashboard",
                "version": "0.1.0",
                "type": "system",
                "capabilities": ["ui.dashboard"],
                "status": "active"
            }
    
    def on_load(self, context: PluginContext) -> None:
        """
        Called when the plugin is loaded.
        
        Dashboard is primarily a UI plugin, so minimal backend initialization.
        """
        logger.info("Loading System Dashboard Plugin...")
        logger.info(f"Dashboard configuration: {self.settings.grid_columns} columns, "
                   f"{self.settings.row_height}px row height")
        logger.info("System Dashboard Plugin loaded successfully")
    
    def on_activate(self) -> None:
        """Called when the plugin is activated."""
        logger.info("System Dashboard Plugin activated")
    
    def on_deactivate(self) -> None:
        """Called when the plugin is deactivated."""
        logger.info("System Dashboard Plugin deactivated")
