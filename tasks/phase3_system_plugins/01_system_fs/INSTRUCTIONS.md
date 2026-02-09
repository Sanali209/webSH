# System Plugin: File System

**Goal:** Implement the file system browser and synchronization logic as a system plugin.

## Steps

1.  **Create Plugin Structure**
    - Create `plugins/system_fs/`.
    - Create `manifest.json`:
        - `id`: `system_fs`
        - `capabilities`: `["fs.scan", "fs.watch", "opener:directory"]`
    - Create `backend.py`:
        - Implement `on_load`: Start file watcher.
        - Implement `fs.scan`: Recursive directory listing (`os.walk`).
        - Implement `fs.watch`: Use `watchdog` to monitor file changes.

2.  **Implement `CoreTableSync`**
    - In `backend.py`, subscribe to file watcher events.
    - **On Create/Modify:**
        - Calculate metadata (size, mime_type, hash).
        - Update `CoreMetadataTable`.
    - **On Delete:**
        - Remove entry from `CoreMetadataTable`.

3.  **Implement `FileExplorer.svelte`**
    - Create `web/src/lib/components/system_fs/FileExplorer.svelte`.
    - Features:
        - Toggle between Grid and List view.
        - Breadcrumbs for navigation.
        - Context Menu slot (`<slot name="context_menu" />`).

## Testing

-   **Unit Tests (`tests/plugins/test_system_fs.py`):**
    -   **Scanning:** Create a temp directory structure, scan it, and verify the output.
    -   **Watching:** Create a file, wait for the watcher event, and verify the callback is triggered.
    -   **Sync:** Verify that file creation updates the mock Core Table.
