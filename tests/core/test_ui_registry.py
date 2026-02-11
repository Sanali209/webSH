import pytest
import json
import os
from fastapi.testclient import TestClient
from core.loader import PluginManifest, PluginLoader
from core.schemas import PluginUI, WidgetSchema
from core.registry import registry
from main import app
from pydantic import ValidationError

client = TestClient(app)

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

def test_plugin_ui_validation():
    # Valid UI
    ui_data = {
        "widgets": [{"id": "w1", "size": "1x1", "entry_point": "w1.svelte", "title": "My Button"}],
        "views": [{"id": "v1", "title": "My Page", "entry_point": "v1.svelte"}]
    }
    manifest = PluginManifest(id="test", ui=ui_data)
    assert manifest.ui.widgets[0].id == "w1"
    assert manifest.ui.views[0].entry_point == "v1.svelte"

    # Invalid UI (missing required field in WidgetSchema)
    # WidgetSchema: id, size, entry_point, title are required
    bad_ui = {
        "widgets": [{"id": "w1", "size": "1x1"}], # Missing title, entry_point
        "views": []
    }
    with pytest.raises(ValidationError):
        PluginManifest(id="test", ui=bad_ui)

def test_registry_storage(clean_registry):
    ui_data = {
        "widgets": [{"id": "w1", "size": "1x1", "entry_point": "w1.svelte", "title": "My Button"}],
        "views": []
    }
    registry.register_ui_extension("p1", ui_data)
    extensions = registry.get_ui_extensions()
    assert "p1" in extensions
    assert extensions["p1"]["widgets"][0]["title"] == "My Button"

def test_loader_ui_registration(temp_plugins_dir, clean_registry):
    # Use a fresh loader instance pointing to temp dir
    loader = PluginLoader(plugins_dir=str(temp_plugins_dir))

    ui_data = {
        "widgets": [{"id": "w1", "size": "1x1", "entry_point": "w1.svelte", "title": "My Button"}],
        "views": []
    }
    manifest = {
        "id": "ui_plugin",
        "version": "1.0.0",
        "ui": ui_data
    }

    create_plugin(temp_plugins_dir, "ui_plugin", manifest)

    loader.discover_and_load()

    assert "ui_plugin" in loader.loaded_plugins
    extensions = registry.get_ui_extensions()
    assert "ui_plugin" in extensions
    assert extensions["ui_plugin"]["widgets"][0]["id"] == "w1"

def test_loader_invalid_ui_manifest(temp_plugins_dir, clean_registry):
    loader = PluginLoader(plugins_dir=str(temp_plugins_dir))

    # Invalid UI in manifest (missing title for widget)
    manifest = {
        "id": "bad_ui_plugin",
        "version": "1.0.0",
        "ui": {
            "widgets": [{"id": "w1", "size": "1x1"}],
            "views": []
        }
    }

    create_plugin(temp_plugins_dir, "bad_ui_plugin", manifest)

    loader.discover_and_load()

    # Should fail to load because validation fails in _load_plugin
    assert "bad_ui_plugin" not in loader.loaded_plugins
    # And definitely not in registry
    assert "bad_ui_plugin" not in registry.get_ui_extensions()

def test_api_endpoint(clean_registry):
    # Manually register some data
    ui_data = {
        "widgets": [{"id": "w1", "size": "1x1", "entry_point": "w1.svelte", "title": "API Button"}],
        "views": []
    }
    registry.register_ui_extension("api_plugin", ui_data)

    response = client.get("/api/v1/registry/ui-extensions")
    assert response.status_code == 200
    data = response.json()
    assert "api_plugin" in data
    assert data["api_plugin"]["widgets"][0]["title"] == "API Button"
