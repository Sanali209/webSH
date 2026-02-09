# System Plugin: Script Engine

**Goal:** Implement a scripting engine to support automation workflows (n8n-style) and custom user scripts.

## Steps

1.  **Create Plugin Structure**
    - Create `plugins/system_script_engine/`.
    - Create `manifest.json`:
        - `id`: `system_script_engine`
        - `type`: `system`
        - `capabilities`: `["script.run", "workflow.engine"]`
    - Create `backend.py`.

2.  **Implement Workflow Decorators (Core)**
    - *Note: Ideally, the decorators should be in `core` so plugins can import them without depending on another plugin directly, or `system_script_engine` exposes them via SDK.*
    - Create `core/workflow.py`:
        - Define `NodeInput`, `NodeOutput` Pydantic models.
        - Implement `@workflow_node` decorator that registers the function in a global or context-aware registry.

3.  **Implement Node Scanner**
    - In `plugins/system_script_engine/backend.py`:
        - Implement logic to scan all loaded plugins for `workflow.py` modules.
        - Import these modules to trigger the `@workflow_node` decorators.
        - Collect the registered nodes into a catalog.

4.  **Implement Execution Engine**
    - Implement `execute_workflow(graph: dict)`:
        - Parses a JSON graph of nodes and edges.
        - topological sort of the graph.
        - Executes nodes sequentially (or parallel where possible) using `Taskiq`.
        - Passes outputs of one node to inputs of the next.

5.  **API Endpoints**
    - `GET /nodes`: Returns list of available workflow nodes (from all plugins).
    - `POST /run`: Accepts a workflow graph and executes it.

## Testing

-   **Unit Tests (`tests/plugins/test_script_engine.py`):**
    -   **Registry:** Define a dummy node with decorator, verify it appears in the scanner results.
    -   **Execution:** Create a simple graph (Node A -> Node B), execute it, and verify data flow.
