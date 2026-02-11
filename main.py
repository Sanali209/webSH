import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
import redis.asyncio as redis
from core.settings import settings
from core.dashboard import dashboard, console
from rich.live import Live
from fastapi.responses import ORJSONResponse
from core.schemas import CapabilityEnvelope, Context
from core.switchboard import switchboard
from core.registry import registry

# Subsystem instances
redis_client = None
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
    
    await check_infrastructure()

    # Start Executor Broker
    from core.executor import broker
    await broker.startup()
    dashboard.update_status("Executor", "Started")
    
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

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, allow all. In prod, strict list.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

if __name__ == "__main__":
    import uvicorn
    
    # Start uvicorn directly to see errors
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, log_level="info")
