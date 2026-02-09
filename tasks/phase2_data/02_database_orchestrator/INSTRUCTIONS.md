# Database Orchestrator

**Goal:** Manage database access and enforce isolation between plugins.

## Steps

1.  **Implement `DatabaseManager`**
    - Create `core/database_manager.py`.
    - Implement methods:
        - `get_table(table_name, schema)`: Returns a LanceDB table object.
        - `list_tables()`: Returns a list of all tables.

2.  **Implement `PluginDatabaseContext`**
    - Create a context class that will be injected into plugins (part of `PluginContext`).
    - Implement `get_my_table(suffix)`:
        - Returns a table name formatted as `plugin_{plugin_id}_{suffix}`.
        - Ensures plugins can only access their own tables by default.
    - Implement `get_core_table()`:
        - Returns the Core Metadata Table (read-only access ideally, or controlled write).
    - Implement `get_other_table(plugin_id, suffix)`:
        - Checks `manifest.permissions` to see if the calling plugin has access to the target plugin's data.

## Testing

-   **Unit Tests (`tests/data/test_db_manager.py`):**
    -   **Scoped Access:** Mock a plugin context and verify `get_my_table("test")` returns `plugin_mock_id_test`.
    -   **Core Table Access:** Verify `get_core_table()` returns the correct table.
    -   **Permission Check:** Mock permissions and verify `get_other_table` raises an error if permission is denied, and succeeds if granted.
