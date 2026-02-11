from core.sdk import BasePlugin, capability
from pydantic import BaseModel, Field
from loguru import logger
from typing import Optional

class PingParams(BaseModel):
    message: str = Field(..., description="Message to echo back")
    repeat: Optional[int] = Field(1, description="Number of times to repeat (not used)")

class TestPlugin(BasePlugin):
    VERSION = "1.0.0"

    @capability("test.ping", schema=PingParams)
    async def ping(self, params: PingParams, context):
        logger.info(f"Test Plugin pinged with params: {params}")
        # Note: Switchboard will pass the validated PingParams object
        return {"status": "pong", "echo": params.message}

plugin = TestPlugin()
