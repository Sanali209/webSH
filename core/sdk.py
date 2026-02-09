import abc
from typing import Any, Callable, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class PluginSettings(BaseModel):
    """Base class for plugin settings."""
    enabled: bool = True

class PluginContext:
    """
    Context object provided to plugins, giving access to core capabilities.
    """
    def __init__(self, plugin_id: str, db_context: Any = None):
        self.plugin_id = plugin_id
        # This will be replaced by the actual PluginDatabaseContext instance
        self.db = db_context

    def get_my_table(self) -> str:
        """
        Deprecated: Use self.db.get_my_table().
        """
        return f"plugin_{self.plugin_id}_data"

    def background_task(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator/Helper to mark a function as a background task.
        For now, this is a placeholder. In Phase 1 Task 4/5, this will integrate with Taskiq.
        """
        # In a real implementation, this might register the task with Taskiq
        # or return a wrapped taskiq task.
        return func

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
