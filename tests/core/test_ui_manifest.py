import pytest
import json
import os
from core.loader import PluginLoader
from core.registry import registry
from core.sdk import VERSION
from pydantic import ValidationError

@pytest.fixture
def clean_registry():
    # Save original state
    original_ui = registry._ui_extensions.copy()
    original_plugins = registry._plugins.copy()

    registry._ui_extensions = {}
    registry._plugins = {}
    yield
    # Restore original state
    registry._ui_extensions = original_ui
    registry._plugins = original_plugins

@pytest.fixture
def temp_plugins_dir(tmp_path):
    d = tmp_path / "plugins"
    d.mkdir()
    return d

def create_plugin(directory, plugin_id, manifest_data, code_content="class P: pass\nplugin = P()"):
    p = directory / plugin_id
    p.mkdir()
    with open(p / "manifest.json", "w") as f:
        json.dump(manifest_data, f)
    with open(p / "backend.py", "w") as f:
        f.write(code_content)
    return p

def test_version_compatibility_success(temp_plugins_dir, clean_registry):
    loader = PluginLoader(plugins_dir=str(temp_plugins_dir))
    manifest = {
        "id": "compat_plugin",
        "version": "1.0.0",
        "compatibility_version": f">={VERSION}",
        "ui": {
            "widgets": [],
            "views": []
        }
    }
    create_plugin(temp_plugins_dir, "compat_plugin", manifest)
    loader.discover_and_load()
    assert "compat_plugin" in loader.loaded_plugins

def test_version_compatibility_failure(temp_plugins_dir, clean_registry):
    loader = PluginLoader(plugins_dir=str(temp_plugins_dir))
    manifest = {
        "id": "incompat_plugin",
        "version": "1.0.0",
        "compatibility_version": ">=99.0.0", # Assumes VERSION is < 99.0.0
        "ui": {
            "widgets": [],
            "views": []
        }
    }
    create_plugin(temp_plugins_dir, "incompat_plugin", manifest)
    loader.discover_and_load()
    assert "incompat_plugin" not in loader.loaded_plugins

def test_version_compatibility_invalid_specifier(temp_plugins_dir, clean_registry):
    loader = PluginLoader(plugins_dir=str(temp_plugins_dir))
    manifest = {
        "id": "bad_ver_plugin",
        "version": "1.0.0",
        "compatibility_version": "invalid-version-spec",
        "ui": {
            "widgets": [],
            "views": []
        }
    }
    create_plugin(temp_plugins_dir, "bad_ver_plugin", manifest)
    loader.discover_and_load()
    assert "bad_ver_plugin" not in loader.loaded_plugins

def test_ui_schema_validation_success(temp_plugins_dir, clean_registry):
    loader = PluginLoader(plugins_dir=str(temp_plugins_dir))
    manifest = {
        "id": "ui_plugin",
        "version": "1.0.0",
        "ui": {
            "widgets": [{"id": "w1", "size": "1x1", "entry_point": "w1.js", "title": "W1"}],
            "views": [{"id": "v1", "title": "V1", "entry_point": "v1.js"}],
            "shortcuts": [{"icon": "ico", "title": "S1", "action": "act"}]
        }
    }
    create_plugin(temp_plugins_dir, "ui_plugin", manifest)
    loader.discover_and_load()
    assert "ui_plugin" in loader.loaded_plugins

    ext = registry.get_ui_extensions()["ui_plugin"]
    assert ext["widgets"][0]["size"] == "1x1"
    assert ext["shortcuts"][0]["title"] == "S1"

def test_ui_schema_validation_invalid_size(temp_plugins_dir, clean_registry):
    loader = PluginLoader(plugins_dir=str(temp_plugins_dir))
    manifest = {
        "id": "bad_size_plugin",
        "version": "1.0.0",
        "ui": {
            "widgets": [{"id": "w1", "size": "10x10", "entry_point": "w1.js", "title": "W1"}],
            "views": []
        }
    }
    create_plugin(temp_plugins_dir, "bad_size_plugin", manifest)
    loader.discover_and_load()
    assert "bad_size_plugin" not in loader.loaded_plugins

def test_ui_schema_validation_extra_fields(temp_plugins_dir, clean_registry):
    loader = PluginLoader(plugins_dir=str(temp_plugins_dir))
    manifest = {
        "id": "extra_field_plugin",
        "version": "1.0.0",
        "ui": {
            "widgets": [{"id": "w1", "size": "1x1", "entry_point": "w1.js", "title": "W1", "extra": "forbidden"}],
            "views": []
        }
    }
    create_plugin(temp_plugins_dir, "extra_field_plugin", manifest)
    loader.discover_and_load()
    assert "extra_field_plugin" not in loader.loaded_plugins

def test_mixed_plugins_loading(temp_plugins_dir, clean_registry):
    loader = PluginLoader(plugins_dir=str(temp_plugins_dir))

    # Valid plugin
    manifest_valid = {
        "id": "valid_plugin",
        "version": "1.0.0",
        "compatibility_version": f">={VERSION}",
        "ui": {
            "widgets": [],
            "views": []
        }
    }
    create_plugin(temp_plugins_dir, "valid_plugin", manifest_valid)

    # Invalid plugin (version incompatibility)
    manifest_invalid = {
        "id": "invalid_plugin",
        "version": "1.0.0",
        "compatibility_version": ">=99.0.0",
        "ui": {
            "widgets": [],
            "views": []
        }
    }
    create_plugin(temp_plugins_dir, "invalid_plugin", manifest_invalid)

    loader.discover_and_load()

    assert "valid_plugin" in loader.loaded_plugins
    assert "invalid_plugin" not in loader.loaded_plugins
