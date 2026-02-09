# Health Checks

**Goal:** Maintain system stability by monitoring component health.

## Steps

1.  **Implement `HealthCheckService`**
    - Create `core/health.py`.
    - Periodically ping all active plugins (e.g., call `plugin.health_check()`).
    - Check Taskiq queue depth (using Redis or broker metrics).
    - Check LanceDB connection status.

2.  **Add API Endpoint**
    - Implement `/api/health`.
    - Return a JSON object with the status of each component:
        - `{"status": "ok", "plugins": {"plugin_id": "ok"}, "db": "ok"}`

3.  **Fail-safe Logic**
    - If a plugin fails the health check (e.g., times out or returns error):
        - Log the error.
        - Deactivate the plugin (`plugin.deactivate()`).
        - Notify the user via `NotificationManager`.

## Testing

-   **Unit Tests (`tests/core/test_health.py`):**
    -   **Pass:** Verify that all checks pass when everything is running.
    -   **Fail:** Simulate a plugin failure (mock) and verify it is reported as "failed" and deactivated.
