# Resource Controller

**Goal:** Monitor and manage system resources usage by plugins.

## Steps

1.  **Implement Resource Quotas**
    - Configure `Taskiq` to limit concurrent workers per plugin (e.g., using rate limiting or queues).
    - Track CPU/RAM usage per plugin (using `psutil` and process groups if possible).

2.  **Add Monitoring API**
    - Implement `/api/resources` endpoint.
    - Return current usage statistics for each plugin.

## Testing

-   **Unit Tests (`tests/core/test_resources.py`):**
    -   **Quota:** Simulate submitting more tasks than the limit and verify queuing/rejection.
    -   **Monitoring:** Verify the API returns valid JSON with usage stats.
