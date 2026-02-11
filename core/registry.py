from typing import Dict, Any, Callable, Optional, Type, List
from pydantic import BaseModel
from loguru import logger

class Registry:
    def __init__(self):
        # Maps "domain@version" to a callable handler
        self._capabilities: Dict[str, Callable] = {}
        # Maps "domain@version" to a validation schema (Pydantic model)
        self._schemas: Dict[str, Type[BaseModel]] = {}
        # Maps "domain" to the latest registered version
        self._latest_versions: Dict[str, str] = {}
        # Stores plugin metadata
        self._plugins: Dict[str, Any] = {}
        # Stores UI extensions
        self._ui_extensions: Dict[str, Any] = {}

    def register(self, domain: str, version: str, handler: Callable, schema: Optional[Type[BaseModel]] = None):
        key = f"{domain}@{version}"
        self._capabilities[key] = handler
        if schema:
            self._schemas[key] = schema
        
        # Simple latest version tracking (could be improved with semver logic)
        if domain not in self._latest_versions or version > self._latest_versions[domain]:
            self._latest_versions[domain] = version
        
        logger.info(f"Registered capability: {key} (Schema: {'Yes' if schema else 'No'})")

    def resolve(self, domain_query: str) -> Optional[Callable]:
        """
        Resolves a domain query to a handler.
        Supports "domain@version" or just "domain" (resolves to latest).
        """
        if "@" in domain_query:
            return self._capabilities.get(domain_query)
        
        latest_version = self._latest_versions.get(domain_query)
        if latest_version:
            return self._capabilities.get(f"{domain_query}@{latest_version}")
        
        return None

    def get_schema(self, domain_query: str) -> Optional[Type[BaseModel]]:
        """
        Retrieves the schema for a domain query.
        """
        if "@" in domain_query:
            return self._schemas.get(domain_query)
        
        latest_version = self._latest_versions.get(domain_query)
        if latest_version:
            return self._schemas.get(f"{domain_query}@{latest_version}")
        
        return None

    def register_plugin(self, manifest_data: Dict[str, Any]):
        """
        Registers a plugin's metadata.
        """
        plugin_id = manifest_data.get("id")
        if plugin_id:
            self._plugins[plugin_id] = manifest_data
            logger.debug(f"Registered plugin metadata: {plugin_id}")

    def get_plugin(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        return self._plugins.get(plugin_id)

    def list_plugins(self) -> List[Dict[str, Any]]:
        return list(self._plugins.values())

    def register_ui_extension(self, plugin_id: str, ui_data: Dict[str, Any]):
        """
        Registers UI extensions for a plugin.
        """
        self._ui_extensions[plugin_id] = ui_data
        logger.info(f"Registered UI extensions for plugin: {plugin_id}")

    def get_ui_extensions(self) -> Dict[str, Any]:
        """
        Returns all registered UI extensions.
        """
        return self._ui_extensions

registry = Registry()
