# Performance Testing

**Goal:** ensure the system scales efficiently.

## Steps

1.  **Benchmark LanceDB**
    - Create a script to generate 100 plugin tables.
    - Insert 10k records into each table.
    - Measure search latency across all tables.

2.  **Benchmark Polars**
    - Create a dataframe representing 1M Core records.
    - Create a dataframe representing 10k Plugin records.
    - Measure the time to perform the RRF join and sort.

3.  **Frontend Performance**
    - Create a test page with a File Explorer grid.
    - Load 1000 items.
    - Verify scrolling smoothness (FPS) and DOM node count (Virtual Scrolling).

## Testing

-   **Run Benchmarks:** Execute the performance scripts and record the results. Ensure they meet defined thresholds (e.g., search < 200ms).
