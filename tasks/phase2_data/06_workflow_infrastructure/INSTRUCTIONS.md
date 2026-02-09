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
