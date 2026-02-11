import pytest
from core.sdk import BasePlugin, BaseSettings
from pydantic import BaseModel, Field
from typing import Dict, Any

class MySettings(BaseSettings):
    key: str = Field(default="value", description="A test setting")
    enabled: bool = True

class MyPlugin(BasePlugin):
    def get_settings_model(self):
        return MySettings

    def get_ui_manifest(self) -> Dict[str, Any]:
        return {
            "widgets": [{"id": "w1", "type": "button", "name": "My Button"}],
            "shortcuts": [{"id": "s1", "key": "ctrl+k", "action": "open_search"}],
            "views": []
        }

def test_base_plugin_defaults():
    plugin = BasePlugin()
    assert plugin.get_settings_model() is None
    assert plugin.get_ui_manifest() == {}
    assert plugin.export_settings_schema() == {}

def test_custom_plugin_settings():
    plugin = MyPlugin()
    schema = plugin.export_settings_schema()
    # Title is removed by core.utils.settings_to_json_schema
    assert "title" not in schema
    assert "key" in schema["properties"]
    assert "enabled" in schema["properties"]

def test_custom_plugin_ui():
    plugin = MyPlugin()
    manifest = plugin.get_ui_manifest()
    assert "widgets" in manifest
    assert manifest["widgets"][0]["name"] == "My Button"
    assert "shortcuts" in manifest
    assert manifest["shortcuts"][0]["key"] == "ctrl+k"

def test_sh_plugin_init_registers_ui():
    # Mock registry
    class MockRegistry:
        def __init__(self):
            self.ui_extensions = {}
            self.capabilities = []

        def register(self, *args, **kwargs):
            self.capabilities.append(kwargs)

        def register_ui_extension(self, plugin_id, ui_data):
            self.ui_extensions[plugin_id] = ui_data

    registry = MockRegistry()
    plugin = MyPlugin()
    plugin.id = "my-plugin" # Simulate loader setting ID

    plugin.sh_plugin_init(registry)

    assert "my-plugin" in registry.ui_extensions
    ui = registry.ui_extensions["my-plugin"]
    assert ui["widgets"][0]["id"] == "w1"

def test_sh_plugin_init_no_ui():
    class NoUIPlugin(BasePlugin):
        pass

    class MockRegistry:
        def __init__(self):
            self.ui_extensions = {}
        def register(self, *args, **kwargs): pass
        def register_ui_extension(self, plugin_id, ui_data):
            self.ui_extensions[plugin_id] = ui_data

    registry = MockRegistry()
    plugin = NoUIPlugin()
    plugin.id = "no-ui"

    plugin.sh_plugin_init(registry)

    assert "no-ui" not in registry.ui_extensions
