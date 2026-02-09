import pytest
import asyncio
import os
import shutil
import lancedb
import pyarrow as pa
from core.database import DatabaseClient
from core.database_manager import DatabaseManager, PluginDatabaseContext
from core.migrations import MigrationManager
from core.plugin_manager import PluginLoader, PluginManifest
from core.sdk import PluginBase, PluginContext

@pytest.fixture
def integration_db_path(tmp_path):
    path = str(tmp_path / "integration_lancedb")
    yield path
    if os.path.exists(path):
        shutil.rmtree(path)

@pytest.fixture
def db_client_instance(integration_db_path):
    return DatabaseClient(db_path=integration_db_path)

@pytest.fixture
def db_manager_instance(db_client_instance):
    return DatabaseManager(client=db_client_instance)

@pytest.fixture
def migration_db_path(tmp_path):
    return str(tmp_path / "integration_plugins.db")

@pytest.mark.asyncio
async def test_concurrent_writes(db_manager_instance):
    """
    Simulate multiple plugins writing to their own tables concurrently.
    """
    # Setup contexts for two plugins
    ctx_a = PluginDatabaseContext("plugin_a", db_manager_instance)
    ctx_b = PluginDatabaseContext("plugin_b", db_manager_instance)

    schema = pa.schema([pa.field("id", pa.int32()), pa.field("val", pa.string())])

    # Create tables
    table_a = ctx_a.get_my_table("data", schema=schema)
    table_b = ctx_b.get_my_table("data", schema=schema)

    async def write_to_a():
        for i in range(10):
            table_a.add([{"id": i, "val": f"a_{i}"}])
            await asyncio.sleep(0.01) # Simulate IO delay

    async def write_to_b():
        for i in range(10):
            table_b.add([{"id": i, "val": f"b_{i}"}])
            await asyncio.sleep(0.01)

    # Run concurrently
    await asyncio.gather(write_to_a(), write_to_b())

    # Verify data
    assert len(table_a.to_pandas()) == 10
    assert len(table_b.to_pandas()) == 10

    # Verify isolation
    df_a = table_a.to_pandas()
    assert all(val.startswith("a_") for val in df_a["val"])

    df_b = table_b.to_pandas()
    assert all(val.startswith("b_") for val in df_b["val"])

def test_schema_migration_integration(db_manager_instance, migration_db_path):
    """
    Simulate a plugin migration scenario: v1 -> v2 (add column).
    """
    migrator = MigrationManager(db_path=migration_db_path)
    plugin_id = "migrating_plugin"

    # --- Phase 1: Install v1 ---
    # Setup v1 schema
    schema_v1 = pa.schema([pa.field("id", pa.int32())])

    # Create plugin v1 instance (mock logic)
    class PluginV1(PluginBase):
        def on_load(self, context): pass
        def on_activate(self): pass
        def on_deactivate(self): pass

    # Initialize DB with v1 data
    ctx_v1 = PluginDatabaseContext(plugin_id, db_manager_instance)
    table = ctx_v1.get_my_table("main", schema=schema_v1)
    table.add([{"id": 1}, {"id": 2}])

    # Register v1 installation
    migrator.update_version(plugin_id, "1.0.0")

    # --- Phase 2: Upgrade to v2 ---
    # Setup v2 schema (add 'name' column)
    schema_v2 = pa.schema([pa.field("id", pa.int32()), pa.field("name", pa.string())])

    class PluginV2(PluginBase):
        def on_load(self, context): pass
        def on_activate(self): pass
        def on_deactivate(self): pass

        def migrate(self, old_ver, new_ver):
            if old_ver == "1.0.0" and new_ver == "2.0.0":
                # Migration logic: Read old data, transform, write new table
                # Note: LanceDB allows schema evolution (adding columns) or we can overwrite.
                # For this test, we'll demonstrate adding a column via merge or overwrite.
                # LanceDB's merge/update support is evolving. Simple approach: replace table.

                ctx = PluginDatabaseContext(plugin_id, db_manager_instance)
                tbl = ctx.get_my_table("main")
                df = tbl.to_pandas()

                # Add new column
                df["name"] = df["id"].apply(lambda x: f"item_{x}")

                # Overwrite table with new schema
                # db_manager.client.connection.create_table(tbl.name, data=df, mode="overwrite")
                # But we should use the context/manager.
                # Direct overwrite via connection for migration is acceptable if Manager doesn't expose it.
                # Let's assume we use the underlying connection for migration heavy lifting.

                db_manager_instance.client.connection.create_table(tbl.name, data=df, mode="overwrite")

    plugin_instance = PluginV2()

    # Mock Loader for Migration Run
    from unittest.mock import MagicMock
    loader = MagicMock()
    loader.loaded_plugins = {plugin_id: plugin_instance}
    loader.manifests = {plugin_id: PluginManifest(id=plugin_id, name="Test", version="2.0.0")}

    # Run Migration
    migrator.run_migrations(loader)

    # Verify DB version updated
    assert migrator.get_installed_version(plugin_id) == "2.0.0"

    # Verify Data Migrated
    table_v2 = ctx_v1.get_my_table("main")
    df_v2 = table_v2.to_pandas()

    assert "name" in df_v2.columns
    assert df_v2.iloc[0]["name"] == "item_1"
    assert len(df_v2) == 2

def test_context_permission_enforcement(db_manager_instance):
    """
    Verify that PluginDatabaseContext strictly prohibits unauthorized access.
    """
    ctx_attacker = PluginDatabaseContext("attacker", db_manager_instance, permissions=[])
    ctx_victim = PluginDatabaseContext("victim", db_manager_instance)

    # Victim creates a table
    schema = pa.schema([pa.field("secret", pa.string())])
    ctx_victim.get_my_table("secrets", schema=schema)

    # Attacker tries to access it
    with pytest.raises(PermissionError):
        ctx_attacker.get_other_table("victim", "secrets")

    # Attacker tries to guess the name via get_table directly on manager?
    # Ideally, plugins shouldn't have access to the raw db_manager instance,
    # but strictly through their context.
    # This test verifies the context method enforces it.

    # Verify Authorized Access
    ctx_authorized = PluginDatabaseContext(
        "authorized_friend",
        db_manager_instance,
        permissions=["plugin:read:victim"]
    )

    # Should succeed
    table = ctx_authorized.get_other_table("victim", "secrets")
    assert table.name == "plugin_victim_secrets"
