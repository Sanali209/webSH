# End-to-End Tests

**Goal:** Verify the system works as a whole from the user's perspective.

## Steps

1.  **Playwright Setup**
    - Configure `playwright.config.ts`.
    - Ensure backend and frontend servers are running (e.g., using `webServer` config).

2.  **Test Scenario**
    - **Open App:** Navigate to root URL.
    - **Check System FS:** Verify the "System FS" icon is present in the system tray/sidebar.
    - **Open Explorer:** Click the icon and verify the File Explorer view loads.
    - **File Operation:** Create a file in the watched directory (backend). Verify it appears in the Explorer UI (frontend) automatically (via WebSocket/Polling).

## Testing

-   **Run Tests:** Execute `npx playwright test` and ensure the scenario passes.
