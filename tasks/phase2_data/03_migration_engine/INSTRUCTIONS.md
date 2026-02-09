# Migration Engine

**Goal:** Handle database schema changes for plugins over time.

## Steps

1.  **Define Schema Version**
    - Add `schema_version` to the `manifest.json` schema.

2.  **Store Version in SQLite**
    - Create a simple SQLite database (`plugins.db`) to store plugin metadata.
    - Create a table to track installed plugins and their current schema version.

3.  **Implement Migration Logic**
    - In `core/migrations.py` (or `PluginLoader`):
    - On startup, for each loaded plugin:
        - Read `manifest.version`.
        - Read the stored version from `plugins.db`.
        - If `manifest.version > db.version`:
            - Call the plugin's `migrate(old_version)` method (which should be part of `PluginBase`).
            - Update `db.version` to `manifest.version`.

## Testing

-   **Unit Tests (`tests/data/test_migrations.py`):**
    -   **Migration Trigger:** Simulate a scenario where the manifest version is higher than the DB version. Verify `migrate` is called.
    -   **Idempotency:** Verify that if versions match, `migrate` is not called.
    -   **Version Update:** Verify that the DB version is updated after a successful migration.

## Walkthrough / Summary

### Execution Steps
1.  **PluginBase Update:**
    -   Added `migrate(self, old_version: str, new_version: str)` method to `PluginBase` in `core/sdk.py`.
2.  **MigrationManager Implementation:**
    -   Created `core/migrations.py`.
    -   Implemented SQLite-based version tracking (`plugins.db`).
    -   Implemented `run_migrations(loader)`:
        -   Iterates through loaded plugins.
        -   Compares manifest version with stored DB version.
        -   Updates DB for fresh installs.
        -   Calls `plugin.migrate()` and updates DB for version upgrades.
3.  **Testing:**
    -   Created `tests/data/test_migrations.py`.
    -   Verified DB initialization.
    -   Verified version storage/retrieval.
    -   Verified fresh install logic (no migration hook, just DB update).
    -   Verified update logic (migration hook called, DB updated).
    -   Verified idempotency (no hook called if versions match).
