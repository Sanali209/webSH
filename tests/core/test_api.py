import pytest
from fastapi.testclient import TestClient
from fastapi import APIRouter
from core.main import app
from core.sdk import PluginBase, PluginContext

class DummyPlugin(PluginBase):
    def __init__(self):
        self.router = APIRouter()
        # Define routes as standalone functions or closures
        self.router.add_api_route("/hello", self.hello, methods=["GET"])
        self.router.add_api_route("/error", self.error, methods=["GET"])

    def on_load(self, context: PluginContext) -> None:
        self.context = context

    def on_activate(self) -> None:
        pass

    def on_deactivate(self) -> None:
        pass

    async def hello(self):
        return {"message": "Hello from Dummy Plugin"}

    async def error(self):
        raise ValueError("Intentional plugin error")

# Create a fresh client
client = TestClient(app)

# Manually mount the router for the tests
dummy_plugin = DummyPlugin()
app.include_router(dummy_plugin.router, prefix="/api/plugins/dummy", tags=["dummy"])

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to PC Center"}

def test_plugin_router_reachability():
    """
    Verify that the manually mounted dummy plugin is reachable.
    """
    response = client.get("/api/plugins/dummy/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from Dummy Plugin"}

def test_sandbox_middleware_error_handling():
    """
    Verify that exceptions in plugin routes are caught by the middleware.
    """
    # The middleware should intercept the ValueError raised by /error
    response = client.get("/api/plugins/dummy/error")

    assert response.status_code == 500
    data = response.json()
    assert data["error"] == "Plugin Execution Error"
    assert "Intentional plugin error" in data["detail"]
    assert data["path"] == "/api/plugins/dummy/error"
