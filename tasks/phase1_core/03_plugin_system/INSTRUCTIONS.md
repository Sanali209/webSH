# Plugin System

**Goal:** Implement the logic to discover, load, and manage plugins.

## Steps

1.  **Implement `PluginLoader`**
    - Create `core/plugin_manager.py`.
    - Implement a `PluginLoader` class using `pluggy` (or similar mechanism).
    - Implement `scan_plugins(directory)`:
        - Scan the `plugins/` directory.
        - Look for `manifest.json` in each subdirectory.

2.  **Validate Manifest Schema**
    - Define the schema for `manifest.json` (e.g., id, version, permissions, dependencies).
    - Implement validation logic to ensure loaded manifests comply with the schema.
    - Reject plugins with invalid manifests.

3.  **Build `DependencyGraph`**
    - Implement logic to determine the load order based on plugin dependencies defined in `manifest.json`.
    - Detect circular dependencies and raise an error.

4.  **Load Python Modules**
    - Use `importlib` to dynamically load the Python module for each plugin.
    - Instantiate the plugin class.

## Testing

-   **Unit Tests (`tests/core/test_plugin_manager.py`):**
    -   **Valid Plugin:** Create a dummy plugin with a valid `manifest.json` and verify it loads.
    -   **Invalid Manifest:** Create a dummy plugin with a missing or invalid `manifest.json` and verify it is rejected.
    -   **Dependency Resolution:** Create multiple dummy plugins with dependencies and verify the load order is correct.
    -   **Circular Dependency:** Create plugins with circular dependencies and verify the loader raises an error.
