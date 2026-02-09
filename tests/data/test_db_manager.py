import pytest
from unittest.mock import MagicMock
from core.database_manager import DatabaseManager, PluginDatabaseContext

def test_get_my_table_scoping():
    """
    Verify that get_my_table returns a table scoped to the plugin ID.
    """
    mock_db_manager = MagicMock(spec=DatabaseManager)
    context = PluginDatabaseContext(plugin_id="test_plugin", db_manager=mock_db_manager)

    context.get_my_table("data")

    # Check that get_table was called with the correct scoped name
    mock_db_manager.get_table.assert_called_with("plugin_test_plugin_data", schema=None)

def test_get_core_table():
    """
    Verify get_core_table calls the client's get_or_create_core_table.
    """
    mock_db_manager = MagicMock(spec=DatabaseManager)
    # Ensure db_manager.client is also a mock
    mock_db_manager.client = MagicMock()

    context = PluginDatabaseContext(plugin_id="test_plugin", db_manager=mock_db_manager)
    context.get_core_table()

    mock_db_manager.client.get_or_create_core_table.assert_called_once()

def test_get_other_table_permission_denied():
    """
    Verify that accessing another plugin's table without permission raises PermissionError.
    """
    mock_db_manager = MagicMock(spec=DatabaseManager)
    context = PluginDatabaseContext(
        plugin_id="plugin_a",
        db_manager=mock_db_manager,
        permissions=[]
    )

    with pytest.raises(PermissionError):
        context.get_other_table("plugin_b", "data")

def test_get_other_table_permission_granted_read():
    """
    Verify that accessing another plugin's table with read permission succeeds.
    """
    mock_db_manager = MagicMock(spec=DatabaseManager)
    context = PluginDatabaseContext(
        plugin_id="plugin_a",
        db_manager=mock_db_manager,
        permissions=["plugin:read:plugin_b"]
    )

    context.get_other_table("plugin_b", "data")
    mock_db_manager.get_table.assert_called_with("plugin_plugin_b_data")

def test_get_other_table_permission_granted_write():
    """
    Verify that accessing another plugin's table with write permission succeeds.
    """
    mock_db_manager = MagicMock(spec=DatabaseManager)
    context = PluginDatabaseContext(
        plugin_id="plugin_a",
        db_manager=mock_db_manager,
        permissions=["plugin:write:plugin_b"]
    )

    context.get_other_table("plugin_b", "data")
    mock_db_manager.get_table.assert_called_with("plugin_plugin_b_data")
