import os
import json
import importlib.util
import traceback
from typing import List, Optional
from pydantic import BaseModel, Field
import pluggy
from loguru import logger
from packaging.specifiers import SpecifierSet
from core.hooks import PluginSpec
from core.registry import registry
from core.schemas import PluginUI
from core.dashboard import dashboard, console
from core.sdk import VERSION as SDK_VERSION
from rich.panel import Panel

class PluginManifest(BaseModel):
    id: str
    version: str = "1.0.0"
    compatibility_version: str = ">=1.0.0"
    author: str = "Unknown"
    description: str = ""
    capabilities: List[str] = Field(default_factory=list)
    ui: Optional[PluginUI] = None

class PluginLoader:
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = plugins_dir
        self.pm = pluggy.PluginManager("sh")
        self.pm.add_hookspecs(PluginSpec)
        self.loaded_plugins = []
        self.plugin_paths = {}

    def discover_and_load(self):
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)
            logger.info(f"Created {self.plugins_dir} directory")

        # Ensure data directories exist
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"Created {data_dir} directory for persistence")

        for entry in os.scandir(self.plugins_dir):
            if entry.is_dir():
                self._load_plugin(entry.path)

        # Trigger initialization hooks
        self.pm.hook.sh_plugin_init(registry=registry)
        logger.info(f"Plugin initialization complete. Total: {len(self.loaded_plugins)}")

    def _load_plugin(self, plugin_path: str):
        manifest_path = os.path.join(plugin_path, "manifest.json")
        if not os.path.exists(manifest_path):
            return

        try:
            # 1. Validate Manifest
            with open(manifest_path, "r") as f:
                manifest_data = json.load(f)
            manifest = PluginManifest(**manifest_data)

            # 1.5 Version Compatibility Check
            try:
                spec = SpecifierSet(manifest.compatibility_version)
                if SDK_VERSION not in spec:
                    logger.error(f"Plugin {manifest.id} requires SDK version {manifest.compatibility_version}, but current version is {SDK_VERSION}. Skipping.")
                    return
            except Exception as e:
                logger.error(f"Invalid compatibility_version '{manifest.compatibility_version}' in plugin {manifest.id}: {e}")
                return

            # 2. Dynamic Import
            module_file = os.path.join(plugin_path, "backend.py")
            if not os.path.exists(module_file):
                module_file = os.path.join(plugin_path, "__init__.py")
            
            if not os.path.exists(module_file):
                logger.warning(f"No entry point found for plugin: {manifest.id}")
                return

            spec = importlib.util.spec_from_file_location(manifest.id, module_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 3. Register with Pluggy
            plugin_instance = getattr(module, "plugin", None)
            if not plugin_instance:
                logger.warning(f"No 'plugin' instance found in {manifest.id}")
                return

            # Inject ID into plugin instance
            plugin_instance.id = manifest.id

            self.pm.register(plugin_instance)
            self.loaded_plugins.append(manifest.id)
            self.plugin_paths[manifest.id] = plugin_path
            
            # 4. Register with Registry
            plugin_data = manifest.model_dump()
            if hasattr(plugin_instance, "get_settings_schema"):
                plugin_data["settings_schema"] = plugin_instance.get_settings_schema()

            registry.register_plugin(plugin_data)

            # 5. Register UI Extensions
            if manifest.ui:
                registry.register_ui_extension(manifest.id, manifest.ui.model_dump())
            
            logger.info(f"Successfully loaded plugin: {manifest.id} (v{manifest.version})")

        except Exception as e:
            traceback.print_exc()
            # Beautiful error reporting via Rich
            console.print(Panel(
                f"[bold red]Failed to load plugin at {plugin_path}[/bold red]\n"
                f"Error: [yellow]{str(e)}[/yellow]\n"
                f"Plugin ID: [cyan]{plugin_path.split(os.sep)[-1]}[/cyan]",
                title="[bold red]Plugin Loading Error[/bold red]",
                border_style="red"
            ))
            logger.error(f"Failed to load plugin at {plugin_path}: {e}")

loader = PluginLoader()
