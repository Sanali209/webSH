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

## Walkthrough / Summary

### Execution Steps
1.  **Middleware Implementation:**
    -   Created `core/middleware.py` containing `SandboxMiddleware`.
    -   This middleware intercepts exceptions specifically for paths starting with `/api/plugins/` and returns a 500 JSON response with error details.
2.  **Main Application Update:**
    -   Updated `core/main.py` to initialize `PluginLoader` globally.
    -   In the `lifespan` startup event, added logic to:
        -   Call `plugin_loader.load_all_plugins()`.
        -   Iterate through loaded plugins and checks for a `.router` attribute.
        -   Dynamically mount these routers using `app.include_router(..., prefix="/api/plugins/{id}")`.
    -   Added `app.add_middleware(SandboxMiddleware)` to the FastAPI app.
    -   Added an endpoint `/api/plugins` to list loaded plugins (useful for frontend).
3.  **Testing:**
    -   Created `tests/core/test_api.py` and a helper `tests/assets/dummy_plugin.py`.
    -   **Reachability:** Verified the root endpoint `/` returns 200.
    -   **Router Mounting:** Manually mounted a `DummyPlugin` router and verified its endpoints are accessible.
    -   **Error Handling:** Triggered an intentional error in the dummy plugin and verified that `SandboxMiddleware` caught it and returned the standardized JSON error format.
