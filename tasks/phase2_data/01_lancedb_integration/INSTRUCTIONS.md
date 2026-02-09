# LanceDB Integration

**Goal:** Set up the primary data storage using LanceDB and define the core metadata schema.

## Steps

1.  **Connect to LanceDB**
    - Create `core/database.py`.
    - Implement a connection to a local LanceDB instance (e.g., in a `.lancedb` directory).
    - Ensure the directory is created if it doesn't exist.

2.  **Implement `CoreMetadataTable`**
    - Define the schema for the Core Metadata Table:
        - `entity_id` (PK, string, SHA-256 hash of the file path or content).
        - `path` (string): Full path to the file.
        - `filename` (string): Name of the file.
        - `size` (int64): File size in bytes.
        - `mime_type` (string): MIME type of the file.
        - `tags` (list[string]): User-defined tags.
        - `last_indexed` (timestamp): When the file was last indexed.

3.  **Create PyArrow Schema**
    - Use PyArrow to define the schema structure formally.
    - Create the table in LanceDB using this schema if it doesn't exist.

## Testing

-   **Unit Tests (`tests/data/test_lancedb.py`):**
    -   **Connection:** Verify that a connection to the LanceDB instance can be established.
    -   **Table Creation:** verify that the table is created with the correct schema.
    -   **CRUD Operations:** Insert a sample record, retrieve it by `entity_id`, update a field, and delete it.

## Walkthrough / Summary

### Execution Steps
1.  **Dependency Management:**
    -   Added `lancedb`, `pyarrow`, and `pandas` to `pyproject.toml`.
2.  **Database Client Implementation:**
    -   Created `core/database.py`.
    -   Implemented `DatabaseClient` to manage the LanceDB connection.
    -   Defined `CORE_METADATA_SCHEMA` using `pyarrow`.
    -   Implemented `get_or_create_core_table` to ensure the table exists with the correct schema on startup.
3.  **Testing:**
    -   Created `tests/data/test_lancedb.py`.
    -   Verified that the `.lancedb` directory is automatically created.
    -   Verified that the `core_metadata` table is created with the expected PyArrow schema.
    -   Verified that data can be inserted (`table.add()`) and retrieved (`table.search()...to_pandas()`).
    -   Resolved a `ModuleNotFoundError` for `pandas` by adding it as a dependency.
