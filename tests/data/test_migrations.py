import pytest
import sqlite3
import os
from unittest.mock import MagicMock
from core.migrations import MigrationManager
from core.sdk import PluginBase
from core.plugin_manager import PluginLoader, PluginManifest

@pytest.fixture
def test_db_path(tmp_path):
    """
    Creates a temporary path for the SQLite database.
    """
    return str(tmp_path / "test_plugins.db")

@pytest.fixture
def migration_manager(test_db_path):
    """
    Returns a MigrationManager instance using the temporary DB.
    """
    return MigrationManager(db_path=test_db_path)

def test_init_db(test_db_path):
    """Verify that the database and table are created on initialization."""
    # Ensure file doesn't exist before
    assert not os.path.exists(test_db_path)

    # Initialize manager
    manager = MigrationManager(db_path=test_db_path)

    # Check file exists
    assert os.path.exists(test_db_path)

    # Check table schema
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='plugin_versions'")
    result = cursor.fetchone()
    conn.close()

    assert result is not None
    assert result[0] == 'plugin_versions'

def test_version_tracking(migration_manager):
    """Verify storing and retrieving plugin versions."""
    plugin_id = "test_plugin_v1"
    version = "1.0.0"

    # Initially None
    assert migration_manager.get_installed_version(plugin_id) is None

    # Set version
    migration_manager.update_version(plugin_id, version)
    assert migration_manager.get_installed_version(plugin_id) == version

    # Update version
    new_version = "1.1.0"
    migration_manager.update_version(plugin_id, new_version)
    assert migration_manager.get_installed_version(plugin_id) == new_version

def test_run_migrations_fresh_install(migration_manager):
    """
    Verify that a fresh install (no DB entry) updates the DB version
    but does NOT call migrate().
    """
    # Setup Mocks
    mock_loader = MagicMock(spec=PluginLoader)
    mock_plugin = MagicMock(spec=PluginBase)

    plugin_id = "fresh_plugin"
    version = "1.0.0"

    # Mock Manifest
    manifest = MagicMock(spec=PluginManifest)
    manifest.id = plugin_id
    manifest.version = version

    # Mock Loader State
    mock_loader.loaded_plugins = {plugin_id: mock_plugin}
    mock_loader.manifests = {plugin_id: manifest}

    # Run
    migration_manager.run_migrations(mock_loader)

    # Assert
    # DB should be updated
    assert migration_manager.get_installed_version(plugin_id) == version
    # migrate() hook should not be called
    mock_plugin.migrate.assert_not_called()

def test_run_migrations_update_triggers_hook(migration_manager):
    """
    Verify that if DB version differs from manifest version, migrate() is called.
    """
    plugin_id = "update_plugin"
    old_version = "1.0.0"
    new_version = "2.0.0"

    # 1. Pre-install old version
    migration_manager.update_version(plugin_id, old_version)

    # 2. Setup Mocks for new version
    mock_loader = MagicMock(spec=PluginLoader)
    mock_plugin = MagicMock(spec=PluginBase)

    manifest = MagicMock(spec=PluginManifest)
    manifest.id = plugin_id
    manifest.version = new_version

    mock_loader.loaded_plugins = {plugin_id: mock_plugin}
    mock_loader.manifests = {plugin_id: manifest}

    # 3. Run
    migration_manager.run_migrations(mock_loader)

    # 4. Assert
    mock_plugin.migrate.assert_called_once_with(old_version, new_version)
    assert migration_manager.get_installed_version(plugin_id) == new_version

def test_run_migrations_idempotency(migration_manager):
    """
    Verify that if versions match, migrate() is NOT called.
    """
    plugin_id = "idempotent_plugin"
    version = "1.0.0"

    # 1. Pre-install matching version
    migration_manager.update_version(plugin_id, version)

    # 2. Setup Mocks
    mock_loader = MagicMock(spec=PluginLoader)
    mock_plugin = MagicMock(spec=PluginBase)

    manifest = MagicMock(spec=PluginManifest)
    manifest.id = plugin_id
    manifest.version = version

    mock_loader.loaded_plugins = {plugin_id: mock_plugin}
    mock_loader.manifests = {plugin_id: manifest}

    # 3. Run
    migration_manager.run_migrations(mock_loader)

    # 4. Assert
    mock_plugin.migrate.assert_not_called()
    assert migration_manager.get_installed_version(plugin_id) == version
