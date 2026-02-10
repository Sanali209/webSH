import os
from typing import Callable, Any
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from loguru import logger

from core.events import event_bus
from core.plugin_manager import PluginLoader
from core.middleware import SandboxMiddleware
from core.migrations import migration_manager
from core.broker import broker
from core.health import HealthCheckService
from core.config import settings
from core.logging_config import setup_logging

# Initialize Logging
setup_logging()

# Initialize plugin loader globally (Singleton pattern for now, but configured via settings)
plugin_loader = PluginLoader(plugin_dir=settings.PLUGIN_DIR)

# Initialize Health Check Service
health_service = HealthCheckService(plugin_loader)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting up...")

    # Start Taskiq Broker
    if not broker.is_worker_process:
        await broker.startup()

    # Load Plugins (passing app for UI mounting)
    plugin_loader.load_all_plugins(app)

    # Run Migrations
    logger.info("Checking for plugin migrations...")
    migration_manager.run_migrations(plugin_loader)

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
    logger.info(f"{settings.APP_NAME} shutting down...")

    # Shutdown Taskiq Broker
    if not broker.is_worker_process:
        await broker.shutdown()

    # Trigger on_deactivate for all plugins (optional cleanup)
    for plugin in plugin_loader.loaded_plugins.values():
        plugin.on_deactivate()

app = FastAPI(
    title=settings.APP_NAME,
    description="A modular local 'Web OS' application.",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.add_middleware(SandboxMiddleware)

@app.get("/api/status")
async def status():
    return {"status": "ok", "version": settings.APP_VERSION}

@app.get("/api/health")
async def health_check():
    """
    Returns the health status of all system components.
    """
    status = await health_service.check_all()
    if status["status"] == "error":
        return JSONResponse(status_code=503, content=status)
    return status

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

# Define handler globally for testing access
async def serve_gui(full_path: str):
    if full_path.startswith("api"):
        return JSONResponse(status_code=404, content={"error": "Not Found"})

    # Fallback to index.html for SPA routing
    index_path = os.path.join(settings.STATIC_DIR, "index.html")
    if os.path.exists(index_path):
         return FileResponse(index_path)
    return JSONResponse(status_code=404, content={"error": "Frontend not found"})

# Note: Generic /plugins mount removed for security (prevent backend code exposure).
# Specific plugin UI directories are mounted by PluginLoader.

# Mount Frontend Static Files
if os.path.exists(settings.STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=f"{settings.STATIC_DIR}/assets"), name="assets")

    # Catch-all for SPA routing
    app.add_api_route("/{full_path:path}", serve_gui, methods=["GET"])
else:
    @app.get("/")
    async def welcome():
        return {"message": "Frontend not found. Run 'npm run build' in your svelte project."}
