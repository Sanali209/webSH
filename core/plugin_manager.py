import json
import os
import importlib.util
import logging
from typing import List, Dict, Optional, Type
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError
from core.sdk import PluginBase, PluginContext
from core.database_manager import db_manager, PluginDatabaseContext

logger = logging.getLogger(__name__)

class PluginManifest(BaseModel):
    id: str
    name: str
    version: str
    description: str = ""
    author: str = ""
    dependencies: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    entry_point: str = "backend.py"  # Default entry point file

class PluginLoader:
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = plugin_dir
        self.manifests: Dict[str, PluginManifest] = {}
        self.loaded_plugins: Dict[str, PluginBase] = {}
        self.load_order: List[str] = []

    def scan_plugins(self) -> None:
        """
        Scans the plugin directory for subdirectories containing manifest.json.
        """
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"Plugin directory {self.plugin_dir} does not exist.")
            return

        for entry in os.scandir(self.plugin_dir):
            if entry.is_dir():
                manifest_path = os.path.join(entry.path, "manifest.json")
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, "r") as f:
                            data = json.load(f)
                        manifest = PluginManifest(**data)
                        self.manifests[manifest.id] = manifest
                        logger.info(f"Discovered plugin: {manifest.id}")
                    except (json.JSONDecodeError, ValidationError) as e:
                        logger.error(f"Failed to load manifest for {entry.name}: {e}")

    def resolve_dependencies(self) -> None:
        """
        Determines the load order based on dependencies using topological sort.
        """
        visited = set()
        temp_visited = set()
        order = []

        def visit(plugin_id: str):
            if plugin_id in temp_visited:
                raise ValueError(f"Circular dependency detected involving {plugin_id}")
            if plugin_id in visited:
                return

            if plugin_id not in self.manifests:
                raise ValueError(f"Missing dependency: {plugin_id}")

            temp_visited.add(plugin_id)

            for dep in self.manifests[plugin_id].dependencies:
                visit(dep)

            temp_visited.remove(plugin_id)
            visited.add(plugin_id)
            order.append(plugin_id)

        for plugin_id in self.manifests:
            if plugin_id not in visited:
                visit(plugin_id)

        self.load_order = order

    def load_plugin(self, plugin_id: str, app: Optional[FastAPI] = None) -> Optional[PluginBase]:
        """
        Dynamically loads the plugin module and instantiates the plugin class.
        Optionally mounts the plugin's UI directory if provided with an app instance.
        Also scans for and loads workflow.py if present to register nodes.
        """
        if plugin_id not in self.manifests:
            logger.error(f"Plugin {plugin_id} not found in manifests.")
            return None

        manifest = self.manifests[plugin_id]
        plugin_path = os.path.join(self.plugin_dir, plugin_id, manifest.entry_point)
        plugin_root = os.path.join(self.plugin_dir, plugin_id)

        if not os.path.exists(plugin_path):
            logger.error(f"Entry point {plugin_path} not found for plugin {plugin_id}")
            return None

        try:
            # Mount UI if app is provided and ui folder exists
            if app:
                ui_path = os.path.join(plugin_root, "ui")
                if os.path.exists(ui_path):
                    mount_path = f"/plugins/{plugin_id}/ui"
                    app.mount(mount_path, StaticFiles(directory=ui_path), name=f"ui_{plugin_id}")
                    logger.info(f"Mounted UI for plugin {plugin_id} at {mount_path}")

            # 1. Load Main Module (backend.py)
            module_name = f"plugins.{plugin_id}.backend"
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find the PluginBase subclass in the module
                plugin_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, PluginBase) and attr is not PluginBase:
                        plugin_class = attr
                        break

                if not plugin_class:
                    logger.error(f"No subclass of PluginBase found in {plugin_id}")
                    return None

                # Instantiate and initialize
                db_context = PluginDatabaseContext(
                    plugin_id=plugin_id,
                    db_manager=db_manager,
                    permissions=manifest.permissions
                )

                context = PluginContext(plugin_id=plugin_id, db_context=db_context)

                plugin_instance = plugin_class()
                plugin_instance.on_load(context)
                self.loaded_plugins[plugin_id] = plugin_instance
                logger.info(f"Successfully loaded plugin: {plugin_id}")

                # 2. Load Workflow Module (workflow.py) if exists
                workflow_path = os.path.join(plugin_root, "workflow.py")
                if os.path.exists(workflow_path):
                    wf_module_name = f"plugins.{plugin_id}.workflow"
                    wf_spec = importlib.util.spec_from_file_location(wf_module_name, workflow_path)
                    if wf_spec and wf_spec.loader:
                        wf_module = importlib.util.module_from_spec(wf_spec)
                        wf_spec.loader.exec_module(wf_module)
                        logger.info(f"Loaded workflow module for plugin: {plugin_id}")

                return plugin_instance

        except Exception as e:
            logger.error(f"Error loading plugin {plugin_id}: {e}")
            return None

    def load_all_plugins(self, app: Optional[FastAPI] = None) -> None:
        """
        Scans, resolves dependencies, and loads all plugins in order.
        """
        self.scan_plugins()
        try:
            self.resolve_dependencies()
        except ValueError as e:
            logger.error(f"Dependency resolution failed: {e}")
            return

        for plugin_id in self.load_order:
            self.load_plugin(plugin_id, app)
