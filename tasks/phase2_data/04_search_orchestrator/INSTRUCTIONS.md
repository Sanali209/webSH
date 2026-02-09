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

## Walkthrough / Summary

### Execution Steps
1.  **HybridSearcher Implementation:**
    -   Implemented `HybridSearcher` in `core/search.py`.
    -   Used **Polars** for efficient dataframe manipulation.
    -   **Text Search:** Implemented a fallback mechanism: tries FTS first, falls back to substring filtering if no index exists.
    -   **Vector Search:** Iterates through plugin IDs, searches their vector tables, and concatenates results using Polars.
2.  **RRF Logic:**
    -   Implemented Reciprocal Rank Fusion algorithm using Polars expressions.
    -   Used `how="full"` (full outer join) and `coalesce=True` to merge text and vector results on `entity_id`, preserving items that appear in only one source.
    -   Handled missing ranks by filling with a large constant to minimize their impact on the score.
3.  **Testing:**
    -   Created `tests/data/test_search.py`.
    -   Verified RRF calculation logic with mixed results, text-only, and vector-only scenarios.
    -   Verified that the join logic correctly handles non-overlapping entity IDs.
    -   Mocked database interactions to test search orchestration without a real LanceDB instance.
