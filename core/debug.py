import asyncio
import json
from typing import List, Set
from fastapi import WebSocket

class TraceBroadcaster:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        if not self.active_connections:
            return
            
        payload = json.dumps(message)
        # Iterate over a copy to avoid modification during iteration if disconnect happens concurrently
        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload)
            except Exception:
                # Assuming disconnect or error, remove connection
                self.disconnect(connection)

# Global broadcaster instance
broadcaster = TraceBroadcaster()
