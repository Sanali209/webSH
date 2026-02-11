from functools import wraps
from typing import Callable, Any, Optional, Type
from pydantic import BaseModel
from core.hooks import hookimpl

class BasePlugin:
    """
    Base class for all PC Center OS plugins.
    Provides automated registration of capabilities.
    """
    def __init__(self):
        self.name = self.__class__.__name__

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
