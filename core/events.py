import asyncio
import uuid
import logging
from typing import Dict, List, Callable, Awaitable, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

EventHandler = Callable[[Dict[str, Any], str], Awaitable[None]]

class AsyncEventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[EventHandler]] = {}
        self.websockets: List[WebSocket] = []

    def subscribe(self, event_name: str, callback: EventHandler) -> None:
        """
        Registers an asynchronous callback for a specific event.
        The callback should accept (data, correlation_id).
        """
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        self.subscribers[event_name].append(callback)
        logger.info(f"Subscribed to event: {event_name}")

    async def publish(self, event_name: str, data: Any, correlation_id: Optional[str] = None) -> None:
        """
        Publishes an event to all local subscribers and connected WebSockets.
        """
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        logger.debug(f"Publishing event {event_name} [ID: {correlation_id}]")

        # 1. Notify local subscribers
        if event_name in self.subscribers:
            tasks = []
            for callback in self.subscribers[event_name]:
                # Directly execute the callback if it's awaitable
                try:
                    tasks.append(callback(data, correlation_id))
                except Exception as e:
                    logger.error(f"Error executing callback for event {event_name}: {e}")
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

        # 2. Broadcast to WebSockets (Frontend)
        # We only broadcast if there are connected clients to avoid overhead
        if self.websockets:
            message = {
                "event": event_name,
                "data": data,
                "correlation_id": correlation_id
            }
            await self.broadcast_websocket(message)

    async def connect_websocket(self, websocket: WebSocket):
        """
        Accepts a new WebSocket connection and adds it to the list.
        """
        await websocket.accept()
        self.websockets.append(websocket)
        logger.info("WebSocket client connected")

    def disconnect_websocket(self, websocket: WebSocket):
        """
        Removes a WebSocket connection.
        """
        if websocket in self.websockets:
            self.websockets.remove(websocket)
            logger.info("WebSocket client disconnected")

    async def broadcast_websocket(self, message: Dict[str, Any]):
        """
        Sends a JSON message to all connected WebSocket clients.
        """
        disconnected = []
        for ws in self.websockets:
            try:
                await ws.send_json(message)
            except (WebSocketDisconnect, RuntimeError):
                disconnected.append(ws)

        for ws in disconnected:
            self.disconnect_websocket(ws)

# Global instance
event_bus = AsyncEventBus()
