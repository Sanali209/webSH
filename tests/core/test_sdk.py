import pytest
from core.sdk import PluginBase, PluginContext, PluginSettings

class MockPlugin(PluginBase):
    def on_load(self, context: PluginContext) -> None:
        self.context = context

    def on_activate(self) -> None:
        pass

    def on_deactivate(self) -> None:
        pass

def test_plugin_base_abstract():
    """Verify that PluginBase cannot be instantiated directly."""
    with pytest.raises(TypeError):
        PluginBase()

def test_plugin_base_implementation():
    """Verify that a concrete implementation of PluginBase can be instantiated."""
    plugin = MockPlugin()
    assert isinstance(plugin, PluginBase)

def test_plugin_context_get_my_table():
    """Verify that PluginContext returns a scoped table name."""
    context = PluginContext(plugin_id="test_plugin")
    table_name = context.get_my_table()
    assert table_name == "plugin_test_plugin_data"

def test_plugin_context_background_task():
    """Verify that background_task decorator returns the function."""
    context = PluginContext(plugin_id="test_plugin")

    @context.background_task
    def my_task():
        return "done"

    assert my_task() == "done"

def test_plugin_settings_defaults():
    """Verify PluginSettings defaults."""
    settings = PluginSettings()
    assert settings.enabled is True

def test_plugin_settings_validation():
    """Verify PluginSettings validation (Pydantic)."""
    with pytest.raises(ValueError):
        PluginSettings(enabled="not-a-bool")
