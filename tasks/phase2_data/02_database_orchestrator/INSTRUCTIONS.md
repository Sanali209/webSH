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

## Walkthrough / Summary

### Execution Steps
1.  **DatabaseManager Implementation:**
    -   Implemented `DatabaseManager` in `core/database_manager.py` to wrap `DatabaseClient` and provide table retrieval logic.
    -   Implemented `get_table` which creates tables if they don't exist and a schema is provided.
    -   Implemented `list_tables`.
2.  **PluginDatabaseContext Implementation:**
    -   Implemented `PluginDatabaseContext` to provide scoped access.
    -   `get_my_table` enforces the `plugin_{id}_{suffix}` naming convention.
    -   `get_other_table` checks for `plugin:read:{id}` or `plugin:write:{id}` permissions in the manifest before granting access.
3.  **Core Integration:**
    -   Updated `core/sdk.py` to accept a `db_context` in `PluginContext`.
    -   Updated `core/plugin_manager.py` to instantiate `PluginDatabaseContext` with permissions from the manifest and inject it into the plugin context.
4.  **Testing:**
    -   Created `tests/data/test_db_manager.py`.
    -   Verified that plugins can only access their own tables by default.
    -   Verified that `get_core_table` delegates to the correct client method.
    -   Verified that accessing another plugin's table raises `PermissionError` unless explicit permissions are granted.
