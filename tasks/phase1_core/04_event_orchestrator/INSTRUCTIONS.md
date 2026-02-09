# Event Orchestrator

**Goal:** Implement an asynchronous event bus for communication between components and plugins.

## Steps

1.  **Implement `AsyncEventBus`**
    - Create `core/events.py`.
    - Implement an `AsyncEventBus` class.
    - Implement `subscribe(event_name, callback)`: Allows registering callbacks for specific events.
    - Implement `publish(event_name, data)`: Dispatches events to all subscribers.

2.  **Add Distributed Tracing**
    - Generate a unique `correlation_id` for each event published.
    - Ensure the `correlation_id` is passed to all subscribers.
    - If integrating with Taskiq, ensure the ID is propagated to background tasks.

3.  **Setup WebSocket Endpoint**
    - In `main.py` (or a dedicated router), create a WebSocket endpoint `/ws/events`.
    - Implement logic to broadcast relevant events to connected WebSocket clients (Frontend).

## Testing

-   **Unit Tests (`tests/core/test_events.py`):**
    -   **Pub/Sub:** Subscribe a mock callback to an event, publish the event, and verify the callback is invoked with the correct data.
    -   **Correlation ID:** Verify that a published event generates a `correlation_id` and that it is received by the subscriber.
    -   **WebSocket:** Use `TestClient` or a WebSocket client to connect to `/ws/events`, trigger an event, and verify the message is received over the socket.
