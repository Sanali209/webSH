# API Gateway

**Goal:** Create the main FastAPI application and set up routing and middleware.

## Steps

1.  **Create FastAPI App**
    - In `main.py`, initialize the `FastAPI` application.

2.  **Implement `SandboxMiddleware`**
    - Create a middleware that intercepts requests to `/api/plugins/*`.
    - Implement error handling to catch exceptions raised by plugins.
    - Return a standardized JSON error response (e.g., `{"error": "Plugin Error", "details": ...}`).

3.  **Dynamic Router Mounting**
    - In `main.py` (during startup), iterate through the loaded plugins.
    - Check if the plugin exposes a FastAPI router.
    - Use `app.include_router()` to mount the plugin's router under `/api/plugins/{plugin_id}`.

## Testing

-   **Integration Tests (`tests/core/test_api.py`):**
    -   **Endpoint Reachability:** Verify that base endpoints are reachable.
    -   **Middleware:** create a dummy route that raises an exception and verify the middleware catches it and returns the expected JSON structure.
    -   **Plugin Routing:** Load a dummy plugin with a router, and verify its endpoints are accessible via `/api/plugins/{dummy_id}/...`.
