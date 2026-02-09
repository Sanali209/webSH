# Search Orchestrator

**Goal:** Implement a unified search engine combining text and vector search.

## Steps

1.  **Implement Hybrid Search**
    - Create `core/search.py`.
    - Implement a search function that accepts a query string.
    - **Text Search:** Perform a BM25 (or similar full-text) search on the `filename` and `tags` columns of the Core Metadata Table.
    - **Vector Search:** If plugins have vector tables (`plugin_parser_vectors`), perform a vector search (using embeddings generated from the query).

2.  **Rank Fusion (RRF)**
    - Use **Polars** to merge results.
    - Join results from the Core Table and Plugin Tables on `entity_id`.
    - Calculate the Reciprocal Rank Fusion (RRF) score:
        - `score = 1 / (k + rank_text) + 1 / (k + rank_vector)`
        - `k` is a constant (e.g., 60).
    - Sort the final results by the RRF score.

## Testing

-   **Unit Tests (`tests/data/test_search.py`):**
    -   **Text Search:** specific test for BM25 functionality (mocking the DB).
    -   **Vector Search:** specific test for vector search logic.
    -   **RRF Calculation:** Create two dataframes (text results, vector results) with known ranks, calculate RRF, and verify the sorting order.
