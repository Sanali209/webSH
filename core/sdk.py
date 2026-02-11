from functools import wraps
from typing import Callable, Any, Optional, Type, Dict
from pydantic import BaseModel
from core.hooks import hookimpl
from core.utils import settings_to_json_schema

class BaseSettings(BaseModel):
    """
    Base class for plugin settings.
    Plugins should subclass this to define their settings schema.
    """
    pass

class BasePlugin:
    """
    Base class for all PC Center OS plugins.
    Provides automated registration of capabilities.
    """
    def __init__(self):
        self.name = self.__class__.__name__
        self.id: Optional[str] = None  # Will be set by loader

    def get_settings_model(self) -> Optional[Type[BaseModel]]:
        """
        Returns the Pydantic model for plugin settings.
        Override this to provide a settings schema.
        """
        return None

    def get_ui_manifest(self) -> Dict[str, Any]:
        """
        Returns the UI manifest dictionary.
        Override this to provide UI definitions programmatically.
        Keys: widgets, shortcuts, views.
        """
        return {}

    def get_settings_schema(self) -> Dict[str, Any]:
        """
        Exports the settings schema as a JSON schema dictionary.
        Uses the settings_to_json_schema helper for enhancement.
        """
        model = self.get_settings_model()
        return settings_to_json_schema(model)

    def export_settings_schema(self) -> Dict[str, Any]:
        """
        Exports the settings schema as a JSON schema dictionary.
        DEPRECATED: Use get_settings_schema instead.
        """
        return self.get_settings_schema()

    async def on_activate(self):
        """Called upon plugin activation."""
        pass

    async def on_deactivate(self):
        """Called upon plugin deactivation."""
        pass

    @hookimpl
    def sh_plugin_init(self, registry):
        # Automatically register methods decorated with @capability
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, "_is_capability"):
                registry.register(
                    domain=attr._capability_domain,
                    version=getattr(self, "VERSION", "1.0.0"),
                    handler=attr,
                    schema=getattr(attr, "_capability_schema", None)
                )
            
            if hasattr(attr, "_is_event_handler"):
                # Register event handler with Switchboard
                # TODO: Implement actual subscription to Switchboard
                pass

        # New: Register UI if provided
        ui_manifest = self.get_ui_manifest()
        if ui_manifest and self.id:
            registry.register_ui_extension(self.id, ui_manifest)

        # Trigger activation lifecycle
        # Note: Since sh_plugin_init is synchronous in Pluggy, we schedule this
        # on the event loop. In a robust system, we might await this in loader.
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.on_activate())
        except RuntimeError:
            # No running loop (e.g. tests), ignore or warn
            pass
            
    async def call(self, domain: str, params: Any = None, context: Any = None):
        """Helper to call another capability."""
        # This would typically use an internal API client or direct registry lookup
        # For now, we assume direct registry access if available globally
        # or fall back to HTTP if needed. 
        # Ideally, SDK injects a client. 
        # STARTUP HACK: We import 'registry' from core to resolve usage
        from core.registry import registry
        # This assumes registry has a method to invoke, which it might not directly expose nicely yet?
        # Let's check registry.py later. For now, pseudo-code or HTTP.
        # Actually, let's use httpx to loopback to API for consistency unless we have a direct dispatcher.
        pass # To be implemented if registry supports it, or use Taskiq for async dispatch

    async def emit(self, event: str, params: Any = None):
        """Helper to emit an event."""
        # Using Taskiq broker to publish if available
        try:
            from core.executor import broker
            # Taskiq doesn't have a direct 'emit' unless updated.
            # We used 'task.finished' which was a webhook.
            # Real event bus might be Redis PubSub directly or Taskiq.
            pass
        except ImportError:
            pass

    def get_state(self, key: str, default: Any = None) -> Any:
        """Helper to get persistent state."""
        # Placeholder for state management
        return default

def capability(domain: str, schema: Optional[Type[BaseModel]] = None):
    """
    Decorator to mark a method as a capability provider.
    """
    def decorator(func: Callable):
        func._is_capability = True
        func._capability_domain = domain
        func._capability_schema = schema
        @wraps(func)
        async def wrapper(self, params: Any, context: Any):
            return await func(self, params, context)
        return wrapper
    return decorator

def on_event(pattern: str):
    """
    Decorator to subscribe to events.
    """
    def decorator(func: Callable):
        func._is_event_handler = True
        func._event_pattern = pattern
        return func
    return decorator
