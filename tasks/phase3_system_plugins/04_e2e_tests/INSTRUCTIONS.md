# End-to-End Tests

**Goal:** Verify the system works as a whole from the user's perspective using Playwright.

## Steps

1.  **Playwright Setup**
    - Configure `playwright.config.ts`.
    - Ensure backend and frontend servers are running (e.g., using `webServer` config).

2.  **Test Scenarios**
    - **System FS:**
        - **Open App:** Navigate to root URL.
        - **Check System FS:** Verify the "System FS" icon is present in the system tray/sidebar.
        - **Open Explorer:** Click the icon and verify the File Explorer view loads.
        - **File Operation:** Create a file in the watched directory (backend). Verify it appears in the Explorer UI (frontend) automatically (via WebSocket/Polling).
    - **Dashboard:**
        - Verify widgets from plugins appear on the dashboard grid.
    - **Script Engine:**
        - Open the Visual Editor.
        - Create a basic workflow (e.g., File Scan -> Log).
        - Run the workflow and verify success notification/output.
    - **Settings & Theme:**
        - Toggle Dark/Light mode and verify visual changes.
        - Change a plugin setting and verify it persists.

## Testing

-   **Run Tests:** Execute `npx playwright test` and ensure the scenarios pass.
