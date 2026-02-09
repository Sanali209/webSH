# Deduplicator Plugin

**Goal:** Identify duplicate files across the system using hashing.

## Steps

1.  **Implement `Deduplicator`**
    - Create `plugins/deduplicator/`.
    - Implement hash calculation:
        - `md5` for exact content match.
        - `imagehash` for perceptual image match.
    - Store hashes in `plugin_dedup_hashes`.

2.  **Implement `CrossTableQuery`**
    - Implement logic to find duplicates:
        - Query `CoreMetadataTable` for files with same size/mtime.
        - Query `plugin_dedup_hashes` for same hash.
    - Return groups of duplicate files.

3.  **Add Context Menu Action**
    - "Find Duplicates" on file right-click.

## Testing

-   **Unit Tests (`tests/plugins/test_deduplicator.py`):**
    -   **Hashing:** Verify hash functions return consistent results.
    -   **Detection:** Create two identical files (same content), run deduplication, and verify they are identified as duplicates.
