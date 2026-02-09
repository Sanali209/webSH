from fastapi import FastAPI
from contextlib import asynccontextmanager

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
