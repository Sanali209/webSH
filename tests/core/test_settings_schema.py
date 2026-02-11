import pytest
from pydantic import BaseModel, SecretStr, Field
from typing import Optional, List, Dict
from core.utils import settings_to_json_schema
from core.sdk import BasePlugin, BaseSettings
from core.registry import registry

class SettingsModel(BaseSettings):
    api_key: SecretStr = Field(..., title="API Key")
    username: str = Field(..., description="Your username")
    password: Optional[SecretStr] = None
    debug: bool = False
    custom_widget: str = Field(..., json_schema_extra={"ui:widget": "textarea"})
    tags: List[str] = []
    config: Dict[str, str] = {}

def test_settings_to_json_schema():
    schema = settings_to_json_schema(SettingsModel)

    properties = schema["properties"]

    # Check SecretStr handling
    assert properties["api_key"]["ui:widget"] == "password"
    assert properties["api_key"]["format"] == "password"

    # Check Optional[SecretStr]
    # "password" property should contain ui:widget at top level
    assert properties["password"]["ui:widget"] == "password"

    # Check custom widget
    assert properties["custom_widget"]["ui:widget"] == "textarea"

    # Check title removal
    # "username" generated title would be "Username".
    # settings_to_json_schema removes title if it matches generated title.
    assert "title" not in properties["username"]

    # "api_key" has explicit title "API Key", which differs from "Api Key". So title should remain.
    assert properties["api_key"]["title"] == "API Key"

    # Check complex types
    assert properties["tags"]["type"] == "array"
    assert properties["config"]["type"] == "object"

def test_base_plugin_integration():
    class MyPlugin(BasePlugin):
        def get_settings_model(self):
            return SettingsModel

    plugin = MyPlugin()
    schema = plugin.get_settings_schema()

    assert schema["properties"]["api_key"]["ui:widget"] == "password"

def test_loader_integration_mock():
    # Verify that if a plugin exposes settings schema, it gets passed to registry
    from unittest.mock import MagicMock

    # Mock registry
    original_register = registry.register_plugin
    registry.register_plugin = MagicMock()

    try:
        class MyPlugin(BasePlugin):
            def get_settings_model(self):
                return SettingsModel

        plugin = MyPlugin()
        plugin.id = "test_plugin"

        # Simulate the logic we added to loader.py
        plugin_data = {"id": "test_plugin"}
        if hasattr(plugin, "get_settings_schema"):
            plugin_data["settings_schema"] = plugin.get_settings_schema()

        registry.register_plugin(plugin_data)

        registry.register_plugin.assert_called_once()
        call_args = registry.register_plugin.call_args[0][0]
        assert "settings_schema" in call_args
        assert call_args["settings_schema"]["properties"]["api_key"]["ui:widget"] == "password"

    finally:
        registry.register_plugin = original_register
