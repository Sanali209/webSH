# Automated Data Tests

**Goal:** Verify data integrity, concurrency, and schema enforcement.

## Steps

1.  **Concurrency Tests**
    - Simulate multiple plugins writing to their own tables simultaneously.
    - Verify no data corruption or race conditions (e.g., using `asyncio.gather`).

2.  **Schema Migration Tests**
    - Create a test plugin with version 1.
    - Initialize the DB.
    - Update the plugin to version 2 (adding a column).
    - Run the migration.
    - Verify the table schema is updated and data is preserved.

3.  **Context Enforcement**
    - Verify that `PluginDatabaseContext` strictly enforces table naming conventions.
    - Attempt to access a table outside the plugin's scope without permission and verify it fails.

## Testing

-   **Run All Tests:** Execute `pytest tests/data` and ensure all tests pass.

## Walkthrough / Summary

### Execution Steps
1.  **Test Implementation:**
    -   Created `tests/data/test_integration_data.py`.
    -   **Concurrency:** Implemented `test_concurrent_writes` using `asyncio.gather` to spawn multiple coroutines writing to different tables via `PluginDatabaseContext`. Verified data integrity after writes.
    -   **Migration:** Implemented `test_schema_migration_integration` simulating a V1 -> V2 upgrade.
        -   Defined a `PluginV2` class with a `migrate` method that reads old data, modifies the dataframe (adds a column), and overwrites the table.
        -   Verified that the database version is updated and the new column exists with correct data.
    -   **Permissions:** Implemented `test_context_permission_enforcement`.
        -   Verified that accessing another plugin's table raises `PermissionError` by default.
        -   Verified that granting explicit permissions (e.g., `plugin:read:victim`) allows access.
2.  **Debugging & Refactoring:**
    -   Encountered issues with `table_names()` deprecation and `list_tables()` behavior in `core/database_manager.py`.
    -   Updated `core/database_manager.py` to robustly handle table listing (falling back to `table_names()` if `list_tables()` is unavailable or behaves unexpectedly), ensuring tests pass reliably.
3.  **Verification:**
    -   Ran `poetry run pytest tests/data/test_integration_data.py`. All tests passed.
