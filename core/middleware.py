import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class SandboxMiddleware(BaseHTTPMiddleware):
    """
    Middleware to catch exceptions from plugins and enforce sandboxing (basic).
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Check if the path is a plugin path.
            # Note: Middleware catches exceptions raised during request handling.
            # Starlette/FastAPI's BaseHTTPMiddleware can sometimes swallow exceptions or
            # handle them before dispatch finishes, but for unhandled exceptions in routes:
            path = request.url.path
            if "/api/plugins/" in path:
                logger.error(f"Plugin error at {path}: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Plugin Execution Error",
                        "detail": str(e),
                        "path": path
                    }
                )
            # Re-raise other errors to be handled by default FastAPI exception handlers
            raise e
