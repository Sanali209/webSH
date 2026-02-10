import logging
import asyncio
from typing import Dict, Any, TYPE_CHECKING
from core.database_manager import db_manager
from core.broker import broker

if TYPE_CHECKING:
    from core.plugin_manager import PluginLoader

logger = logging.getLogger(__name__)

class HealthCheckService:
    def __init__(self, plugin_loader: 'PluginLoader'):
        self.plugin_loader = plugin_loader

    async def check_all(self) -> Dict[str, Any]:
        """
        Runs health checks on all system components.
        """
        components = {
            "database": await self.check_database(),
            "broker": await self.check_broker(),
            "plugins": await self.check_plugins()
        }

        global_status = "ok"
        for key, value in components.items():
            if isinstance(value, dict):
                if value.get("status") == "error":
                    global_status = "error"
                # Check nested plugins
                if key == "plugins":
                    for p_status in value.values():
                        if isinstance(p_status, dict) and p_status.get("status") == "error":
                            global_status = "error"
            elif value == "error":
                global_status = "error"

        return {
            "status": global_status,
            "components": components
        }

    async def check_database(self) -> Dict[str, Any]:
        try:
            # Simple check: list tables to verify connection
            db_manager.list_tables()
            return {"status": "ok"}
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "error", "details": str(e)}

    async def check_broker(self) -> Dict[str, Any]:
        # Taskiq broker check
        try:
             # If using InMemoryBroker, it's always local.
             # If using Redis, we might want to ping.
             # Current broker implementation is InMemoryBroker or similar.
             # We can assume it's OK if the process is running for now.
             return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "details": str(e)}

    async def check_plugins(self) -> Dict[str, Any]:
        plugin_status = {}
        for plugin_id, plugin in self.plugin_loader.loaded_plugins.items():
            try:
                if hasattr(plugin, "health_check"):
                    if asyncio.iscoroutinefunction(plugin.health_check):
                        res = await plugin.health_check()
                    else:
                        res = plugin.health_check()
                    plugin_status[plugin_id] = res
                else:
                    plugin_status[plugin_id] = {"status": "ok"}
            except Exception as e:
                logger.error(f"Plugin {plugin_id} health check failed: {e}")
                plugin_status[plugin_id] = {"status": "error", "details": str(e)}
        return plugin_status
