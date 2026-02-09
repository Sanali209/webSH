from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from core.events import event_bus

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("PC Center starting up...")
    yield
    # Shutdown
    print("PC Center shutting down...")

app = FastAPI(
    title="PC Center",
    description="A modular local 'Web OS' application.",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Welcome to PC Center"}

@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await event_bus.connect_websocket(websocket)
    try:
        while True:
            # Keep connection alive and listen for any incoming messages (though mostly one-way)
            await websocket.receive_text()
    except WebSocketDisconnect:
        event_bus.disconnect_websocket(websocket)
