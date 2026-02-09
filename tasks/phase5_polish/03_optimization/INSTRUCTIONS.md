# Optimization

**Goal:** Improve system responsiveness and efficiency.

## Steps

1.  **Implement `QueryCache`**
    - Create `core/optimization.py`.
    - Implement an LRU cache for search queries.
    - Store results for frequent queries.
    - **Invalidation:** Clear the cache when file system changes are detected (`fs_provider`).

2.  **Optimize Polars**
    - Refactor search logic to use `scan_parquet` (lazy execution) instead of `read_parquet`.
    - Apply filters *before* joining tables to reduce memory usage.

## Testing

-   **Unit Tests (`tests/core/test_optimization.py`):**
    -   **Cache Hit:** Perform a search, perform it again, and verify the second call returns cached results (faster).
    -   **Invalidation:** Modify a file (mock) and verify the cache is cleared.
