# API Gateway

**Goal:** Create the main FastAPI application and set up routing, middleware, and static file serving for the frontend.

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

4.  **Serve Frontend (SPA)**
    - Check if the `dist/` directory exists (build output from Svelte).
    - If it exists:
        - Mount `dist/assets` to `/assets`.
        - Implement a "Catch-all" route (`/{full_path:path}`) that serves `dist/index.html` for any path *not* starting with `/api`.
    - This allows Svelte's client-side routing to handle navigation while FastAPI serves the app shell.

## Testing

-   **Integration Tests (`tests/core/test_api.py`):**
    -   **Endpoint Reachability:** Verify that base endpoints are reachable.
    -   **Middleware:** create a dummy route that raises an exception and verify the middleware catches it and returns the expected JSON structure.
    -   **Plugin Routing:** Load a dummy plugin with a router, and verify its endpoints are accessible via `/api/plugins/{dummy_id}/...`.
    -   **Static Serving:** Mock the existence of `dist/index.html` and verify that a GET request to `/some-random-page` returns the HTML content (SPA support).

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
3.  **Frontend Serving Configuration:**
    -   Added conditional mounting of `StaticFiles` for `dist/` if the directory exists.
    -   Added a catch-all route to serve `index.html` for SPA routing, ensuring API routes take precedence.
4.  **Testing:**
    -   Created `tests/core/test_api.py` and a helper `tests/assets/dummy_plugin.py`.
    -   **Reachability:** Verified the root endpoint `/` returns 200.
    -   **Router Mounting:** Manually mounted a `DummyPlugin` router and verified its endpoints are accessible.
    -   **Error Handling:** Triggered an intentional error in the dummy plugin and verified that `SandboxMiddleware` caught it and returned the standardized JSON error format.
