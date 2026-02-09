# Core SDK Implementation

**Goal:** Create the base classes and context wrappers that plugins will use.

## Steps

1.  **Define `PluginBase` Abstract Class**
    - Create `core/sdk.py`.
    - Define an abstract base class `PluginBase`.
    - Define abstract methods:
        - `on_load(self, context)`: Called when the plugin is loaded.
        - `on_activate(self)`: Called when the plugin is activated.
        - `on_deactivate(self)`: Called when the plugin is deactivated.

2.  **Implement `PluginContext`**
    - In `core/sdk.py`, create a `PluginContext` class.
    - Implement a wrapper for database access:
        - `get_my_table(self)`: Returns a scoped database table for the plugin.
    - Implement a wrapper for Taskiq:
        - `background_task(self)`: A decorator or helper to schedule background tasks.

3.  **Define `PluginSettings`**
    - In `core/sdk.py`, define a `PluginSettings` class using Pydantic.
    - This will serve as a base for plugin-specific settings.

## Testing

-   **Unit Tests (`tests/core/test_sdk.py`):**
    -   Create a test class inheriting from `PluginBase` without implementing abstract methods and verify it raises `TypeError` on instantiation.
    -   Create a concrete implementation of `PluginBase` and verify it can be instantiated.
    -   Test `PluginContext` methods to ensure they return the expected objects (mocking DB and Taskiq).
    -   Test `PluginSettings` with valid and invalid data to ensure Pydantic validation works.
