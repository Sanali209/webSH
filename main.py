import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger
import redis.asyncio as redis
from whitenoise import WhiteNoise
from secure import Secure, ContentSecurityPolicy, PermissionsPolicy, StrictTransportSecurity, XContentTypeOptions, ReferrerPolicy, XFrameOptions
from a2wsgi import WSGIMiddleware
from core.settings import settings
from core.dashboard import dashboard, console
from rich.live import Live
from fastapi.responses import ORJSONResponse
from core.schemas import CapabilityEnvelope, Context, DesktopConfig
from core.switchboard import switchboard
from core.registry import registry
from typing import List
import lancedb
from lancedb.pydantic import pydantic_to_schema

# Subsystem instances
redis_client = None
desktop_db = None
from core.loader import loader

async def check_infrastructure():
    global redis_client
    
    # Check Redis
    try:
        dashboard.update_status("Redis", "Connecting...")
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        dashboard.update_status("Redis", "Connected")
        logger.info("Successfully connected to Redis")
    except Exception as e:
        dashboard.update_status("Redis", f"Error: {str(e)}")
        logger.error(f"Failed to connect to Redis: {e}")

    # Check Tracing (OTEL)
    # Placeholder for actual OTEL check, since it's usually UDP/gRPC and less blocking
    dashboard.update_status("Tracing", "Ready")
    logger.info("Tracing initialized")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    dashboard.update_status("Kernel", "Ready")
    
    # Initialize Tracing
    from core.tracing import setup_tracing
    setup_tracing()
    
    # Discovery and Load Plugins
    dashboard.update_status("Plugins", "Loading...")
    loader.discover_and_load()
    dashboard.update_status("Plugins", f"Loaded: {len(loader.loaded_plugins)}")
    
    # Mount Plugin UI Static Files
    for plugin_id in loader.loaded_plugins:
        plugin_path = loader.plugin_paths.get(plugin_id)
        if plugin_path:
            ui_path = os.path.join(plugin_path, "ui")
            if os.path.exists(ui_path):
                app.mount(f"/plugins/{plugin_id}/ui", StaticFiles(directory=ui_path), name=f"{plugin_id}_ui")
                logger.info(f"Mounted UI for plugin {plugin_id} at /plugins/{plugin_id}/ui")

    await check_infrastructure()

    # Start Executor Broker
    from core.executor import broker
    await broker.startup()
    dashboard.update_status("Executor", "Started")

    # Initialize Desktop DB
    global desktop_db
    try:
        os.makedirs("data", exist_ok=True)
        desktop_db = lancedb.connect("data/desktop.lancedb")

        tables = desktop_db.list_tables()
        # Handle recent lancedb versions returning object with tables attribute
        table_names = tables.tables if hasattr(tables, "tables") else tables

        if "desktop_state" not in table_names:
            # Create empty table
            desktop_db.create_table("desktop_state", schema=pydantic_to_schema(DesktopConfig))

        dashboard.update_status("DesktopDB", "Ready")
    except Exception as e:
        logger.error(f"Failed to init desktop db: {e}")
        dashboard.update_status("DesktopDB", "Error")
    
    yield
    
    # Shutdown
    if redis_client:
        await redis_client.close()
    
    await broker.shutdown()
    logger.info("Kernel shutdown complete")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    default_response_class=ORJSONResponse
)

# CSP and Security Headers
csp = (
    ContentSecurityPolicy()
    .default_src("'self'")
    .script_src("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net")
    .style_src("'self'", "'unsafe-inline'")
    .frame_src("'self'")
)
secure_headers = Secure(csp=csp)

@app.middleware("http")
async def set_secure_headers(request, call_next):
    response = await call_next(request)
    secure_headers.set_headers(response)
    return response

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, allow all. In prod, strict list.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WhiteNoise Configuration for Static Assets
# Create a dummy WSGI app to wrap with WhiteNoise
def dummy_wsgi_app(environ, start_response):
    status = '404 Not Found'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [b'Not Found']

desktop_app = WhiteNoise(dummy_wsgi_app, root='dist')
# Mount the WSGI app as an ASGI app
app.mount("/desktop", WSGIMiddleware(desktop_app))

@app.post("/api/v1/call")
async def capability_call(envelope: CapabilityEnvelope):
    """
    Main entry point for all capability calls (Signal Routing).
    """
    return await switchboard.dispatch(envelope)

@app.get("/api/v1/plugins")
async def list_plugins():
    """
    Returns a list of all loaded plugins and their metadata.
    """
    return registry.list_plugins()

@app.get("/api/v1/registry/ui-extensions")
async def list_ui_extensions():
    """
    Returns a list of all registered UI extensions, grouped by plugin ID.
    """
    return registry.get_ui_extensions()

from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Echo for now, or send to switchboard
            await websocket.send_text(f"Message text was: {data}")
    except Exception:
        pass

from fastapi import WebSocketDisconnect
from core.debug import broadcaster

@app.websocket("/api/v1/debug/stream")
async def debug_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time system tracing.
    """
    await broadcaster.connect(websocket)
    try:
        while True:
            # Keep connection open, maybe listen for client commands (filter, pause)
            data = await websocket.receive_text()
            # For now, we just ignore client messages or log them
            pass
    except WebSocketDisconnect:
        broadcaster.disconnect(websocket)
    except Exception:
        broadcaster.disconnect(websocket)

@app.get("/health")
async def health_check():
    redis_alive = False
    if redis_client:
        try:
            await redis_client.ping()
            redis_alive = True
        except:
            pass
            
    return {
        "status": "online",
        "version": settings.APP_VERSION,
        "subsystems": {
            "redis": "connected" if redis_alive else "disconnected",
            "tracing": "ready"
        }
    }

@app.get("/health/ui/{plugin_id}")
async def health_ui_check(plugin_id: str):
    """
    Checks if the UI for a specific plugin is available.
    """
    if plugin_id not in loader.loaded_plugins:
        return ORJSONResponse(status_code=404, content={"status": "plugin_not_found"})

    plugin_path = loader.plugin_paths.get(plugin_id)
    if not plugin_path:
        return ORJSONResponse(status_code=500, content={"status": "path_error"})

    ui_path = os.path.join(plugin_path, "ui")
    if not os.path.exists(ui_path):
        return ORJSONResponse(status_code=404, content={"status": "ui_not_found"})

    # Check for index.js or manifest.json
    index_exists = os.path.exists(os.path.join(ui_path, "index.js"))
    manifest_exists = os.path.exists(os.path.join(ui_path, "manifest.json"))

    if index_exists or manifest_exists:
        return {"status": "available", "files": {"index.js": index_exists, "manifest.json": manifest_exists}}
    else:
        return ORJSONResponse(status_code=404, content={"status": "assets_missing"})

@app.post("/api/v1/desktop/sync")
async def sync_desktop(desktops: List[DesktopConfig]):
    try:
        # Overwrite all.
        if desktops:
            # When providing data (list of pydantic models), lancedb can infer schema or take schema
            # pydantic_to_schema returns pyarrow schema which create_table accepts
            # We convert models to dicts to ensure compatibility
            data = [d.model_dump() for d in desktops]
            # Try letting lancedb infer schema from data to avoid pyarrow compatibility issues
            desktop_db.create_table("desktop_state", data=data, mode="overwrite")
        else:
            desktop_db.create_table("desktop_state", schema=pydantic_to_schema(DesktopConfig), mode="overwrite")

        return {"status": "synced", "count": len(desktops)}
    except Exception as e:
        logger.error(f"Sync error: {e}")
        return ORJSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/v1/desktop/sync", response_model=List[DesktopConfig])
async def get_desktop_state():
    try:
        if not desktop_db:
            return []

        tables = desktop_db.list_tables()
        table_names = tables.tables if hasattr(tables, "tables") else tables

        if "desktop_state" not in table_names:
            return []

        tbl = desktop_db.open_table("desktop_state")
        # to_pylist() should return list of dicts which pydantic response_model will validate
        return tbl.to_arrow().to_pylist()
    except Exception as e:
        logger.error(f"Get state error: {e}")
        return []

if __name__ == "__main__":
    import uvicorn
    
    # Start uvicorn directly to see errors
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, log_level="info")
