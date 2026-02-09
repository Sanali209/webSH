# Core Workflow Infrastructure

**Goal:** Establish the core types and decorators needed for the scripting engine integration.

## Steps

1.  **Define Workflow Models**
    - Create `core/workflow.py`.
    - Define `NodeInput` and `NodeOutput` using Pydantic.
    - Define `WorkflowNodeDefinition` to store metadata about a registered node.

2.  **Implement Decorator**
    - Implement `@workflow_node` decorator.
    - It should store the decorated function and its metadata in a registry (e.g., a simple global list or dictionary in `core/workflow.py` for now, which `system_script_engine` will read).

3.  **Update Plugin Loader**
    - Update `core/plugin_manager.py` to optionally load `workflow.py` if it exists in a plugin directory, ensuring nodes are registered during plugin load.

## Testing

-   **Unit Tests (`tests/core/test_workflow.py`):**
    -   **Decorator:** Decorate a function and verify it is added to the registry with correct metadata.
    -   **Loader:** Create a dummy plugin with `workflow.py`, load it, and verify its nodes are registered.

## Walkthrough / Summary

### Execution Steps
1.  **Workflow Models & Decorator:**
    -   Created `core/workflow.py` defining Pydantic models for `NodeInput`, `NodeOutput`, and `WorkflowNodeDefinition`.
    -   Implemented `@workflow_node` decorator which registers the function in a global `NODE_REGISTRY`.
2.  **Plugin Integration:**
    -   Updated `core/plugin_manager.py` in `load_plugin` to check for and load `workflow.py` using `importlib`. This ensures that any plugin defining workflow nodes gets them registered automatically upon system startup.
3.  **Testing:**
    -   Created `tests/core/test_workflow.py`.
    -   Verified that the decorator correctly populates the registry.
    -   Verified that the `PluginLoader` successfully imports `workflow.py` from a dummy plugin directory, triggering the registration mechanism.
    -   All tests passed.
