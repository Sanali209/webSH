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

## Walkthrough / Summary

### Execution Steps
1.  **PluginManifest Definition:**
    -   Created `PluginManifest` Pydantic model in `core/plugin_manager.py` to validate `manifest.json`.
    -   Fields: `id`, `name`, `version`, `description`, `author`, `dependencies`, `permissions`, `entry_point`.
2.  **PluginLoader Implementation:**
    -   Implemented `scan_plugins` to iterate through directories and parse manifests.
    -   Implemented `resolve_dependencies` using a topological sort algorithm (DFS based) to determine load order.
    -   Implemented `load_plugin` using `importlib.util.spec_from_file_location` to dynamically load Python modules from the plugin directory.
    -   Implemented logic to find and instantiate the `PluginBase` subclass within the loaded module.
3.  **Testing:**
    -   Created `tests/core/test_plugin_manager.py`.
    -   Implemented helper `create_plugin` to generate dummy plugins on the fly.
    -   Verified manifest parsing and validation.
    -   Verified dependency resolution (correct order and circular dependency detection).
    -   Verified dynamic loading and instantiation of plugin classes.
    -   All tests passed.
