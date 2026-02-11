import pytest
import os
import shutil
import json
from core.loader import PluginLoader
from core.registry import registry

@pytest.fixture
def temp_plugins_dir(tmp_path):
    d = tmp_path / "plugins"
    d.mkdir()
    return d

def create_plugin(directory, plugin_id, manifest_data, code_content="plugin = None"):
    p = directory / plugin_id
    p.mkdir()
    with open(p / "manifest.json", "w") as f:
        json.dump(manifest_data, f)
    with open(p / "backend.py", "w") as f:
        f.write(code_content)
    return p

def test_loader_discovery(temp_plugins_dir):
    loader = PluginLoader(plugins_dir=str(temp_plugins_dir))
    
    # Create a valid plugin
    manifest = {"id": "test_plugin", "version": "1.0.1", "author": "Tester"}
    create_plugin(temp_plugins_dir, "test_plugin", manifest, "class P: pass\nplugin = P()")
    
    loader.discover_and_load()
    
    assert "test_plugin" in loader.loaded_plugins
    p_meta = registry.get_plugin("test_plugin")
    assert p_meta is not None
    assert p_meta["version"] == "1.0.1"

def test_loader_broken_manifest(temp_plugins_dir):
    loader = PluginLoader(plugins_dir=str(temp_plugins_dir))
    
    # Plugin with missing ID in manifest
    p = temp_plugins_dir / "broken_plugin"
    p.mkdir()
    with open(p / "manifest.json", "w") as f:
        f.write('{"version": "1.0.0"}') # Missing 'id'
    
    # Should not crash
    loader.discover_and_load()
    assert "broken_plugin" not in loader.loaded_plugins

def test_loader_import_error(temp_plugins_dir):
    loader = PluginLoader(plugins_dir=str(temp_plugins_dir))
    
    # Plugin with syntax error in backend.py
    manifest = {"id": "syntax_error_plugin"}
    create_plugin(temp_plugins_dir, "syntax_error_plugin", manifest, "This is not valid python")
    
    # Should not crash
    loader.discover_and_load()
    assert "syntax_error_plugin" not in loader.loaded_plugins

def test_registry_list_plugins():
    # Registry is global, check if we can see the plugin from test_loader_discovery
    # (Assuming tests run in order or we register one here)
    registry.register_plugin({"id": "api_test", "version": "2.0.0"})
    plugins = registry.list_plugins()
    assert any(p["id"] == "api_test" for p in plugins)
