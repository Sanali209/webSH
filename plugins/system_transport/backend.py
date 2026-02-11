import os
import asyncio
from multiprocessing import shared_memory
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from core.sdk import BasePlugin, capability
from loguru import logger

class AllocParams(BaseModel):
    size: int = Field(..., description="Size in bytes to allocate")

class FreeParams(BaseModel):
    name: str = Field(..., description="Name of the shared memory segment to free")

class SystemTransportPlugin(BasePlugin):
    VERSION = "1.0.0"

    def __init__(self):
        super().__init__()
        self.segments: Dict[str, shared_memory.SharedMemory] = {}

    @capability("transport.alloc", schema=AllocParams)
    async def alloc(self, params: AllocParams, context):
        """
        Allocates a shared memory segment.
        """
        try:
            shm = shared_memory.SharedMemory(create=True, size=params.size)
            self.segments[shm.name] = shm
            logger.info(f"Allocated shared memory segment: {shm.name} (Size: {params.size})")
            return {"name": shm.name, "size": params.size, "uri": f"shm://{shm.name}"}
        except Exception as e:
            logger.error(f"Failed to allocate shared memory: {e}")
            return {"status": "error", "message": str(e)}

    @capability("transport.free", schema=FreeParams)
    async def free(self, params: FreeParams, context):
        """
        Frees a shared memory segment.
        """
        if params.name in self.segments:
            shm = self.segments.pop(params.name)
            try:
                shm.close()
                shm.unlink()
                logger.info(f"Freed shared memory segment: {params.name}")
                return {"status": "success"}
            except Exception as e:
                logger.error(f"Error freeing shared memory {params.name}: {e}")
                return {"status": "error", "message": str(e)}
        else:
            # Maybe it was created elsewhere, try to attach and unlink as a fallback
            try:
                shm = shared_memory.SharedMemory(name=params.name)
                shm.close()
                shm.unlink()
                return {"status": "success", "note": "segment was not tracked but unlinked"}
            except Exception:
                return {"status": "error", "message": "segment not found"}

    def sh_plugin_init(self, registry):
        # Additional initialization if needed
        super().sh_plugin_init(registry)

    def on_shutdown(self):
        # Cleanup all segments on shutdown
        for name, shm in list(self.segments.items()):
            try:
                shm.close()
                shm.unlink()
                logger.debug(f"Cleanup: unlinked {name}")
            except:
                pass
        self.segments.clear()

plugin = SystemTransportPlugin()
