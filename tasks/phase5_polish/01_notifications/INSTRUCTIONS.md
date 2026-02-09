# Notifications

**Goal:** Provide feedback and alerts to the user.

## Steps

1.  **Implement `NotificationManager`**
    - Create `plugins/system_notifications/`.
    - Implement `send(message: str, severity: str = "info")`.
    - Use `desktop-notifier` for OS-level alerts (e.g., Windows toast, macOS notification).

2.  **Implement UI Components**
    - Create `web/src/lib/components/notifications/Toast.svelte`.
    - Implement a `NotificationStore` to manage active notifications.
    - Create a sidebar component for Notification History.

## Testing

-   **Unit Tests (`tests/plugins/test_notifications.py`):**
    -   **Send:** Verify that calling `send` adds the notification to the queue/history.
    -   **UI:** Verify that adding a notification to the store triggers the Toast component to appear.
