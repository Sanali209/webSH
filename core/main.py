import logging
from typing import Callable, Any
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from core.events import event_bus
from core.plugin_manager import PluginLoader
from core.middleware import SandboxMiddleware

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize plugin loader globally
plugin_loader = PluginLoader()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("PC Center starting up...")

    # Load Plugins
    plugin_loader.load_all_plugins()

    # Dynamic Router Mounting
    for plugin_id, plugin_instance in plugin_loader.loaded_plugins.items():
        if hasattr(plugin_instance, "router"):
            app.include_router(
                plugin_instance.router,
                prefix=f"/api/plugins/{plugin_id}",
                tags=[plugin_id]
            )
            logger.info(f"Mounted router for plugin: {plugin_id}")

    yield
    # Shutdown
    logger.info("PC Center shutting down...")
    # Trigger on_deactivate for all plugins (optional cleanup)
    for plugin in plugin_loader.loaded_plugins.values():
        plugin.on_deactivate()

app = FastAPI(
    title="PC Center",
    description="A modular local 'Web OS' application.",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(SandboxMiddleware)

@app.get("/")
async def root():
    return {"message": "Welcome to PC Center"}

@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await event_bus.connect_websocket(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        event_bus.disconnect_websocket(websocket)

# Expose internal list of plugins for frontend
@app.get("/api/plugins")
async def list_plugins():
    manifests = []
    if hasattr(plugin_loader, "manifests"):
        for m in plugin_loader.manifests.values():
            manifests.append({
                "id": m.id,
                "name": m.name,
                "version": m.version,
                "description": m.description,
                "status": "active" if m.id in plugin_loader.loaded_plugins else "inactive"
            })
    return manifests
