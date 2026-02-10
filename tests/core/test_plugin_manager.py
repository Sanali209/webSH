import json
import os
import sys
import pytest
from core.plugin_manager import PluginLoader
from core.sdk import PluginBase, PluginContext

def create_plugin(plugin_dir, plugin_id, dependencies=None, entry_point="backend.py"):
    """
    Helper to create a dummy plugin on disk.
    """
    if dependencies is None:
        dependencies = []

    plugin_path = os.path.join(plugin_dir, plugin_id)
    os.makedirs(plugin_path, exist_ok=True)

    manifest = {
        "id": plugin_id,
        "name": f"Plugin {plugin_id}",
        "version": "1.0.0",
        "description": "Test plugin",
        "author": "Tester",
        "dependencies": dependencies,
        "permissions": [],
        "entry_point": entry_point
    }

    with open(os.path.join(plugin_path, "manifest.json"), "w") as f:
        json.dump(manifest, f)

    # Create dummy backend.py
    backend_content = f"""
from core.sdk import PluginBase, PluginContext

class {plugin_id.capitalize()}Plugin(PluginBase):
    def on_load(self, context: PluginContext) -> None:
        self.context = context
        print("Loaded {plugin_id}")

    def on_activate(self) -> None:
        pass

    def on_deactivate(self) -> None:
        pass
"""
    with open(os.path.join(plugin_path, entry_point), "w") as f:
        f.write(backend_content)

def test_scan_plugins(tmp_path):
    """Verify that plugins are discovered."""
    plugin_dir = tmp_path / "plugins"
    create_plugin(plugin_dir, "plugin_a")
    create_plugin(plugin_dir, "plugin_b")

    loader = PluginLoader(plugin_dir=str(plugin_dir))
    loader.scan_plugins()

    assert "plugin_a" in loader.manifests
    assert "plugin_b" in loader.manifests
    assert loader.manifests["plugin_a"].id == "plugin_a"

def test_resolve_dependencies(tmp_path):
    """Verify dependency resolution order."""
    plugin_dir = tmp_path / "plugins"
    create_plugin(plugin_dir, "plugin_a", dependencies=["plugin_b"])
    create_plugin(plugin_dir, "plugin_b", dependencies=[])
    create_plugin(plugin_dir, "plugin_c", dependencies=["plugin_a"])

    loader = PluginLoader(plugin_dir=str(plugin_dir))
    loader.scan_plugins()
    loader.resolve_dependencies()

    # Order should be B -> A -> C
    assert loader.load_order == ["plugin_b", "plugin_a", "plugin_c"]

def test_circular_dependency(tmp_path):
    """Verify circular dependency detection."""
    plugin_dir = tmp_path / "plugins"
    create_plugin(plugin_dir, "plugin_a", dependencies=["plugin_b"])
    create_plugin(plugin_dir, "plugin_b", dependencies=["plugin_a"])

    loader = PluginLoader(plugin_dir=str(plugin_dir))
    loader.scan_plugins()

    with pytest.raises(ValueError, match="Circular dependency"):
        loader.resolve_dependencies()

def test_missing_dependency(tmp_path):
    """Verify missing dependency detection."""
    plugin_dir = tmp_path / "plugins"
    create_plugin(plugin_dir, "plugin_a", dependencies=["non_existent_plugin"])

    loader = PluginLoader(plugin_dir=str(plugin_dir))
    loader.scan_plugins()

    with pytest.raises(ValueError, match="Missing dependency: non_existent_plugin"):
        loader.resolve_dependencies()

def test_load_plugin(tmp_path):
    """Verify plugin loading and instantiation."""
    plugin_dir = tmp_path / "plugins"
    create_plugin(plugin_dir, "plugin_a")

    loader = PluginLoader(plugin_dir=str(plugin_dir))
    loader.scan_plugins()
    plugin = loader.load_plugin("plugin_a")

    assert plugin is not None
    assert isinstance(plugin, PluginBase)
    # Check if context was set (on_load called)
    assert hasattr(plugin, "context")
    assert isinstance(plugin.context, PluginContext)
    assert plugin.context.plugin_id == "plugin_a"

def test_invalid_manifest(tmp_path):
    """Verify handling of invalid manifest."""
    plugin_dir = tmp_path / "plugins"
    plugin_path = plugin_dir / "invalid_plugin"
    plugin_path.mkdir(parents=True)

    with open(plugin_path / "manifest.json", "w") as f:
        f.write("{invalid_json")

    loader = PluginLoader(plugin_dir=str(plugin_dir))
    loader.scan_plugins()

    assert "invalid_plugin" not in loader.manifests
