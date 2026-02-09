# System Plugin: Dashboard

**Goal:** Implement the main dashboard interface as a system plugin that hosts widgets from other plugins.

## Steps

1.  **Create Plugin Structure**
    - Create `plugins/system_dashboard/`.
    - Create `manifest.json`:
        - `id`: `system_dashboard`
        - `type`: `system`
        - `capabilities`: `["ui.dashboard"]`
    - Create `backend.py` (Minimal, mainly for serving UI assets).

2.  **Implement Dashboard Layout (Frontend)**
    - Create `plugins/system_dashboard/ui/MainView.svelte`.
    - Implement a Grid Layout (e.g., using `svelte-grid` or CSS Grid).
    - Allow users to move/resize widget containers (optional for MVP, fixed grid ok).

3.  **Implement Widget Host**
    - Use the core `SlotManager` or a specific `<WidgetSlot />` component.
    - Render components registered for the `dashboard_widget` slot.
    - Pass context (size, position) to the widgets.

4.  **Integration**
    - Ensure this plugin is loaded by default as the "Home" view in the main frontend application.

## Testing

-   **Unit Tests (Frontend):**
    -   **Rendering:** Verify that the dashboard renders and iterates over registered widgets.
    -   **Empty State:** Verify behavior when no widgets are present.
