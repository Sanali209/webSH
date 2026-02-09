"""Tests for Resource Controller Plugin."""
import pytest
from plugins.resource_controller.backend import (
    ResourceControllerPlugin,
    ResourceMonitor,
    ResourceUsage
)
from plugins.resource_controller.config import ResourceSettings
from core.sdk import PluginContext


class TestResourceMonitor:
    """Test the ResourceMonitor class."""
    
    def test_get_system_usage(self):
        """Test getting system-wide resource usage."""
        settings = ResourceSettings()
        monitor = ResourceMonitor(settings)
        
        usage = monitor.get_system_usage()
        
        assert "cpu_percent" in usage
        assert "memory_mb" in usage
        assert "memory_percent" in usage
        assert "memory_available_mb" in usage
        
        # CPU should be between 0 and 100
        assert 0 <= usage["cpu_percent"] <= 100
        # Memory should be positive
        assert usage["memory_mb"] > 0
    
    def test_get_process_usage(self):
        """Test getting current process resource usage."""
        settings = ResourceSettings()
        monitor = ResourceMonitor(settings)
        
        usage = monitor.get_process_usage()
        
        assert "cpu_percent" in usage
        assert "memory_mb" in usage
        assert "num_threads" in usage
        
        # CPU should be >= 0
        assert usage["cpu_percent"] >= 0
        # Memory should be positive
        assert usage["memory_mb"] > 0
        # Threads should be positive
        assert usage["num_threads"] > 0
    
    def test_update_plugin_usage(self):
        """Test updating plugin resource usage."""
        settings = ResourceSettings()
        monitor = ResourceMonitor(settings)
        
        # Update usage for a plugin
        monitor.update_plugin_usage("test_plugin", cpu=50.0, memory=100.0, workers=3)
        
        # Retrieve usage
        usage = monitor.get_plugin_usage("test_plugin")
        
        assert usage is not None
        assert usage.plugin_id == "test_plugin"
        assert usage.cpu_percent == 50.0
        assert usage.memory_mb == 100.0
        assert usage.active_workers == 3
        assert usage.timestamp > 0
    
    def test_get_nonexistent_plugin_usage(self):
        """Test getting usage for a plugin that hasn't been tracked."""
        settings = ResourceSettings()
        monitor = ResourceMonitor(settings)
        
        usage = monitor.get_plugin_usage("nonexistent_plugin")
        
        assert usage is None
    
    def test_get_all_usage(self):
        """Test getting all plugin usage data."""
        settings = ResourceSettings()
        monitor = ResourceMonitor(settings)
        
        # Add usage for multiple plugins
        monitor.update_plugin_usage("plugin1", cpu=10.0, memory=50.0, workers=1)
        monitor.update_plugin_usage("plugin2", cpu=20.0, memory=100.0, workers=2)
        
        all_usage = monitor.get_all_usage()
        
        assert len(all_usage) == 2
        assert "plugin1" in all_usage
        assert "plugin2" in all_usage
        assert all_usage["plugin1"].cpu_percent == 10.0
        assert all_usage["plugin2"].memory_mb == 100.0
    
    def test_check_quota_within_limits(self):
        """Test quota checking for plugin within limits."""
        settings = ResourceSettings(
            max_cpu_percent=80.0,
            max_memory_mb=512,
            max_workers_per_plugin=5
        )
        monitor = ResourceMonitor(settings)
        
        # Plugin within limits
        monitor.update_plugin_usage("good_plugin", cpu=50.0, memory=256.0, workers=3)
        
        within_quota = monitor.check_quota("good_plugin")
        
        assert within_quota is True
    
    def test_check_quota_cpu_exceeded(self):
        """Test quota checking when CPU limit is exceeded."""
        settings = ResourceSettings(
            max_cpu_percent=80.0,
            max_memory_mb=512,
            max_workers_per_plugin=5
        )
        monitor = ResourceMonitor(settings)
        
        # Plugin exceeds CPU limit
        monitor.update_plugin_usage("bad_plugin", cpu=90.0, memory=256.0, workers=3)
        
        within_quota = monitor.check_quota("bad_plugin")
        
        assert within_quota is False
    
    def test_check_quota_memory_exceeded(self):
        """Test quota checking when memory limit is exceeded."""
        settings = ResourceSettings(
            max_cpu_percent=80.0,
            max_memory_mb=512,
            max_workers_per_plugin=5
        )
        monitor = ResourceMonitor(settings)
        
        # Plugin exceeds memory limit
        monitor.update_plugin_usage("bad_plugin", cpu=50.0, memory=600.0, workers=3)
        
        within_quota = monitor.check_quota("bad_plugin")
        
        assert within_quota is False
    
    def test_check_quota_workers_exceeded(self):
        """Test quota checking when worker limit is exceeded."""
        settings = ResourceSettings(
            max_cpu_percent=80.0,
            max_memory_mb=512,
            max_workers_per_plugin=5
        )
        monitor = ResourceMonitor(settings)
        
        # Plugin exceeds worker limit
        monitor.update_plugin_usage("bad_plugin", cpu=50.0, memory=256.0, workers=10)
        
        within_quota = monitor.check_quota("bad_plugin")
        
        assert within_quota is False
    
    def test_check_quota_nonexistent_plugin(self):
        """Test quota checking for plugin with no usage data."""
        settings = ResourceSettings()
        monitor = ResourceMonitor(settings)
        
        # Plugin with no usage data should be considered within quota
        within_quota = monitor.check_quota("new_plugin")
        
        assert within_quota is True


class TestResourceControllerPlugin:
    """Test the ResourceControllerPlugin class."""
    
    def test_plugin_initialization(self):
        """Test that the plugin initializes correctly."""
        plugin = ResourceControllerPlugin()
        
        assert plugin.settings is not None
        assert isinstance(plugin.settings, ResourceSettings)
        assert plugin.router is not None
        assert plugin.monitor is None  # Not initialized until on_load
    
    def test_plugin_on_load_initializes_monitor(self):
        """Test that on_load initializes the resource monitor."""
        plugin = ResourceControllerPlugin()
        context = PluginContext("resource_controller")
        
        assert plugin.monitor is None
        
        plugin.on_load(context)
        
        assert plugin.monitor is not None
        assert isinstance(plugin.monitor, ResourceMonitor)
    
    def test_plugin_registers_capabilities(self):
        """Test that the plugin registers its capabilities."""
        plugin = ResourceControllerPlugin()
        context = PluginContext("resource_controller")
        
        plugin.on_load(context)
        
        # Check that capabilities are registered
        assert context.capabilities.has("resources.check_quota")
        assert context.capabilities.has("resources.get_usage")
        
        # Verify capabilities are callable
        check_quota = context.capabilities.get("resources.check_quota")
        get_usage = context.capabilities.get("resources.get_usage")
        
        assert callable(check_quota)
        assert callable(get_usage)
    
    def test_capability_check_quota(self):
        """Test the check_quota capability."""
        plugin = ResourceControllerPlugin()
        context = PluginContext("resource_controller")
        plugin.on_load(context)
        
        # Update plugin usage
        plugin.monitor.update_plugin_usage("test_plugin", cpu=50.0, memory=256.0, workers=3)
        
        # Get and call the capability
        check_quota = context.capabilities.get("resources.check_quota")
        result = check_quota("test_plugin")
        
        assert result is True
    
    def test_capability_get_usage(self):
        """Test the get_usage capability."""
        plugin = ResourceControllerPlugin()
        context = PluginContext("resource_controller")
        plugin.on_load(context)
        
        # Update plugin usage
        plugin.monitor.update_plugin_usage("test_plugin", cpu=50.0, memory=256.0, workers=3)
        
        # Get and call the capability
        get_usage = context.capabilities.get("resources.get_usage")
        result = get_usage("test_plugin")
        
        assert result is not None
        assert result["plugin_id"] == "test_plugin"
        assert result["cpu_percent"] == 50.0
        assert result["memory_mb"] == 256.0
        assert result["active_workers"] == 3


@pytest.mark.asyncio
class TestResourceControllerAPI:
    """Test the API endpoints of the Resource Controller plugin."""
    
    async def test_resources_endpoint(self):
        """Test the /resources endpoint."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        plugin = ResourceControllerPlugin()
        context = PluginContext("resource_controller")
        plugin.on_load(context)
        
        # Create test app
        app = FastAPI()
        app.include_router(plugin.router, prefix="/api/plugins/resource_controller")
        
        client = TestClient(app)
        
        # Test the resources endpoint
        response = client.get("/api/plugins/resource_controller/resources")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "system" in data
        assert "process" in data
        assert "plugins" in data
        assert "quotas" in data
        
        # Check system data
        assert "cpu_percent" in data["system"]
        assert "memory_mb" in data["system"]
        
        # Check quotas
        assert data["quotas"]["max_workers_per_plugin"] == 5
    
    async def test_plugin_resources_endpoint(self):
        """Test the /resources/{plugin_id} endpoint."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        plugin = ResourceControllerPlugin()
        context = PluginContext("resource_controller")
        plugin.on_load(context)
        
        # Add some usage data
        plugin.monitor.update_plugin_usage("test_plugin", cpu=30.0, memory=150.0, workers=2)
        
        app = FastAPI()
        app.include_router(plugin.router, prefix="/api/plugins/resource_controller")
        
        client = TestClient(app)
        
        # Test the plugin-specific endpoint
        response = client.get("/api/plugins/resource_controller/resources/test_plugin")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["plugin_id"] == "test_plugin"
        assert data["cpu_percent"] == 30.0
        assert data["memory_mb"] == 150.0
        assert data["active_workers"] == 2
        assert data["within_quota"] is True
        assert "quotas" in data
    
    async def test_plugin_resources_endpoint_nonexistent(self):
        """Test the endpoint for a plugin with no usage data."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        plugin = ResourceControllerPlugin()
        context = PluginContext("resource_controller")
        plugin.on_load(context)
        
        app = FastAPI()
        app.include_router(plugin.router, prefix="/api/plugins/resource_controller")
        
        client = TestClient(app)
        
        response = client.get("/api/plugins/resource_controller/resources/nonexistent")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["plugin_id"] == "nonexistent"
        assert "message" in data
        assert data["within_quota"] is True
    
    async def test_info_endpoint(self):
        """Test the /info endpoint."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        plugin = ResourceControllerPlugin()
        context = PluginContext("resource_controller")
        plugin.on_load(context)
        
        app = FastAPI()
        app.include_router(plugin.router, prefix="/api/plugins/resource_controller")
        
        client = TestClient(app)
        
        response = client.get("/api/plugins/resource_controller/info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Resource Controller"
        assert data["version"] == "0.1.0"
        assert data["type"] == "system"
        assert data["status"] == "active"
        assert "capabilities" in data
        assert "settings" in data
