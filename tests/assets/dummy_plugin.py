from fastapi import APIRouter
from core.sdk import PluginBase, PluginContext

class DummyPlugin(PluginBase):
    def __init__(self):
        self.router = APIRouter()
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
