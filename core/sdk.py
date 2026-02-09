import abc
from typing import Any, Callable, TypeVar, Dict, Optional
from pydantic import BaseModel
import logging

T = TypeVar("T")
logger = logging.getLogger(__name__)

class PluginSettings(BaseModel):
    """Base class for plugin settings."""
    enabled: bool = True

class CapabilityRegistry:
    """
    Registry for plugin capabilities that can be shared across plugins.
    """
    def __init__(self):
        self._capabilities: Dict[str, Callable] = {}
    
    def register(self, name: str, handler: Callable) -> None:
        """
        Register a capability handler.
        
        Args:
            name: Capability name (e.g., "llm.embed", "llm.generate")
            handler: Callable that implements the capability
        """
        if name in self._capabilities:
            logger.warning(f"Capability '{name}' is being overwritten")
        self._capabilities[name] = handler
        logger.info(f"Registered capability: {name}")
    
    def get(self, name: str) -> Optional[Callable]:
        """
        Get a capability handler by name.
        
        Args:
            name: Capability name
            
        Returns:
            The capability handler or None if not found
        """
        return self._capabilities.get(name)
    
    def has(self, name: str) -> bool:
        """Check if a capability is registered."""
        return name in self._capabilities
    
    def list_all(self) -> list[str]:
        """List all registered capability names."""
        return list(self._capabilities.keys())

class PluginContext:
    """
    Context object provided to plugins, giving access to core capabilities.
    """
    # Class-level capability registry shared across all plugins
    _global_capabilities = CapabilityRegistry()
    
    def __init__(self, plugin_id: str, db_context: Any = None):
        self.plugin_id = plugin_id
        # This will be replaced by the actual PluginDatabaseContext instance
        self.db = db_context
        # Access to global capability registry
        self.capabilities = self._global_capabilities

    def get_my_table(self) -> str:
        """
        Deprecated: Use self.db.get_my_table().
        """
        return f"plugin_{self.plugin_id}_data"

    def background_task(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator/Helper to mark a function as a background task.
        Wraps the function with the Taskiq broker task decorator.
        """
        from core.broker import broker
        return broker.task(func)

class PluginBase(abc.ABC):
    """
    Abstract base class that all plugins must inherit from.
    """

    @abc.abstractmethod
    def on_load(self, context: PluginContext) -> None:
        """
        Called when the plugin is loaded (e.g., application startup).
        Use this to register hooks, initialize database tables, etc.
        """
        pass

    @abc.abstractmethod
    def on_activate(self) -> None:
        """
        Called when the plugin is activated by the user.
        """
        pass

    @abc.abstractmethod
    def on_deactivate(self) -> None:
        """
        Called when the plugin is deactivated by the user.
        """
        pass

    def migrate(self, old_version: str, new_version: str) -> None:
        """
        Called when the plugin version has changed.
        Implement schema migration logic here.
        Default implementation does nothing.
        """
        pass
