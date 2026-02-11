import asyncio
import httpx
from core.sdk import BasePlugin, capability
from core.executor import broker
from core.settings import settings
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from loguru import logger

class ExecuteParams(BaseModel):
    func_name: str = Field(..., description="Function to execute (whitelist: sleep)")
    params: Dict[str, Any] = Field(default_factory=dict, description="Function arguments")
    priority: int = 0

@broker.task
async def generic_executor_task(func_name: str, params: dict, correlation_id: str):
    logger.info(f"Worker: Starting task {func_name} [{correlation_id}]")
    status = "success"
    result = None
    
    try:
        # Whitelist
        if func_name == "sleep":
            seconds = params.get("seconds", 5)
            await asyncio.sleep(seconds)
            result = f"Slept for {seconds} seconds"
        else:
            raise ValueError(f"Function '{func_name}' is not whitelisted")
            
    except Exception as e:
        status = "error"
        result = str(e)
        logger.error(f"Worker: Task failed: {e}")

    # Emit task.finished via API (Callback to Kernel)
    # properly formatting as CapabilityEnvelope structure expected by /api/v1/call
    payload = {
        "domain": "task.finished",
        "params": {
            "correlation_id": correlation_id, 
            "status": status, 
            "result": result
        },
        "context": {
            "correlation_id": correlation_id,
            "trace_stack": ["worker"]
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Assume Kernel is on localhost:8000 (settings.PORT)
            url = f"http://127.0.0.1:{settings.PORT}/api/v1/call"
            await client.post(url, json=payload, timeout=5.0)
            logger.info(f"Worker: Sent task.finished to {url}")
    except Exception as e:
        logger.error(f"Worker: Failed to send callback: {e}")


class SystemExecutor(BasePlugin):
    @capability("core.execute", schema=ExecuteParams)
    async def execute(self, params: ExecuteParams, context):
        logger.info(f"Executor: Enqueueing {params.func_name}")
        # Dispatch to Taskiq
        task = await generic_executor_task.kiq(
            func_name=params.func_name, 
            params=params.params, 
            correlation_id=context.correlation_id or "unknown"
        )
        return {"task_id": task.task_id, "status": "queued"}

plugin = SystemExecutor()
