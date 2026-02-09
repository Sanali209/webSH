# Frontend Core Integration

**Goal:** enable dynamic loading of plugin UI components.

## Steps

1.  **Implement `ModuleLoader`**
    - In `web/src/lib/core/module_loader.ts` (or similar).
    - Fetch list of active plugins from `/api/plugins`.
    - Use dynamic imports (`import()`) to load the plugin's main entry point from the served static path: `/plugins/{plugin_id}/ui/index.js`.

2.  **Implement `SlotManager`**
    - Create `web/src/lib/core/SlotManager.svelte`.
    - Implement logic to render components into specific slots:
        - `system_tray`: Render icons/buttons from plugins.
        - `context_menu`: Render actions based on context (e.g., selected file).

## Testing

-   **Unit Tests (Frontend):**
    -   **Loader:** specific test that `ModuleLoader` correctly fetches the plugin list and attempts to import from the correct URL structure.
    -   **Slot:** Render `SlotManager` with mock plugin data and verify components are rendered.
