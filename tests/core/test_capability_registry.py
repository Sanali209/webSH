import pytest
import logging
from unittest.mock import Mock
from core.sdk import CapabilityRegistry, PluginContext

class TestCapabilityRegistry:
    """Tests for the CapabilityRegistry class."""

    @pytest.fixture
    def registry(self):
        """Fixture that provides a fresh CapabilityRegistry instance."""
        return CapabilityRegistry()

    def test_initialization(self, registry):
        """Verify the registry starts empty."""
        assert registry._capabilities == {}
        assert registry.list_all() == []

    def test_register_and_get(self, registry):
        """Verify registering and retrieving a capability."""
        handler = Mock()
        registry.register("test.capability", handler)

        assert registry.has("test.capability")
        assert registry.get("test.capability") == handler
        assert registry.list_all() == ["test.capability"]

    def test_get_non_existent(self, registry):
        """Verify getting a non-existent capability returns None."""
        assert registry.get("non.existent") is None
        assert not registry.has("non.existent")

    def test_register_overwrite(self, registry, caplog):
        """Verify overwriting a capability works and logs a warning."""
        handler1 = Mock()
        handler2 = Mock()

        registry.register("test.capability", handler1)

        with caplog.at_level(logging.WARNING):
            registry.register("test.capability", handler2)

        assert "Capability 'test.capability' is being overwritten" in caplog.text
        assert registry.get("test.capability") == handler2

    def test_list_all(self, registry):
        """Verify list_all returns all capability names."""
        registry.register("cap1", Mock())
        registry.register("cap2", Mock())

        capabilities = registry.list_all()
        assert len(capabilities) == 2
        assert "cap1" in capabilities
        assert "cap2" in capabilities

    def test_plugin_context_access(self):
        """Verify PluginContext has access to the global registry."""
        context = PluginContext(plugin_id="test_plugin")
        # Since _global_capabilities is shared, we should check if it's the correct type
        assert isinstance(context.capabilities, CapabilityRegistry)
        # Verify it's the shared instance
        context2 = PluginContext(plugin_id="another_plugin")
        assert context.capabilities is context2.capabilities
