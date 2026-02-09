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
