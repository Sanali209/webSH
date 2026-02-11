from core.sdk import BasePlugin, capability
from pydantic import BaseModel, Field
from loguru import logger

class PingParams(BaseModel):
    name: str = "World"

class HelloWorld(BasePlugin):
    async def on_activate(self):
        logger.info(f"{self.name}: Activated! Hello World initialized.")
        
    async def on_deactivate(self):
        logger.info(f"{self.name}: Deactivated!")

    @capability("hello.ping", schema=PingParams)
    async def ping(self, params: PingParams, context):
        logger.info(f"{self.name}: Received ping from {params.name}")
        return {"message": f"Hello, {params.name}!"}

plugin = HelloWorld()
