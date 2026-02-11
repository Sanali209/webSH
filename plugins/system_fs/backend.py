import os
import asyncio
import time
import base64
import imohash
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from loguru import logger
from core.sdk import BasePlugin, capability
from concurrent.futures import ThreadPoolExecutor

class PathParams(BaseModel):
    path: str = Field(..., description="Path relative to workspace root")

class WriteParams(PathParams):
    content: str
    encoding: str = "utf-8"  # "utf-8" or "base64"

class ListParams(PathParams):
    recursive: bool = False

class SystemFSPlugin(BasePlugin, FileSystemEventHandler):
    VERSION = "1.0.0"

    def __init__(self):
        super().__init__()
        self.root_dir = os.getcwd()
        self.observer = Observer()
        self.event_queue = asyncio.Queue()
        self.debouncer_task = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Debouncing settings
        self.debounce_seconds = 0.5
        self.pending_changes = {} # path -> last_time

    def start_monitoring(self):
        self.observer.schedule(self, self.root_dir, recursive=True)
        self.observer.start()
        logger.info(f"FS Monitor started on {self.root_dir}")
        # Start the async debouncer
        try:
            loop = asyncio.get_running_loop()
            self.debouncer_task = loop.create_task(self._debounce_worker())
        except RuntimeError:
            # Not in an event loop (during init)
            pass

    def stop_monitoring(self):
        try:
            if self.observer.is_alive():
                self.observer.stop()
                self.observer.join()
        except RuntimeError:
            pass
            
        if self.debouncer_task:
            self.debouncer_task.cancel()

    # --- Watchdog overrides ---
    def on_modified(self, event):
        if not event.is_directory:
            asyncio.run_coroutine_threadsafe(
                self.event_queue.put(("modified", event.src_path)), 
                asyncio.get_event_loop()
            )

    def on_created(self, event):
        asyncio.run_coroutine_threadsafe(
            self.event_queue.put(("created", event.src_path)), 
            asyncio.get_event_loop()
        )

    # --- Async Debouncer ---
    async def _debounce_worker(self):
        while True:
            event_type, full_path = await self.event_queue.get()
            rel_path = os.path.relpath(full_path, self.root_dir)
            
            # Simple debounce logic
            self.pending_changes[rel_path] = (event_type, time.time())
            
            await asyncio.sleep(0.1) # Check interval
            
            now = time.time()
            to_emit = []
            for path, (etype, timestamp) in list(self.pending_changes.items()):
                if now - timestamp >= self.debounce_seconds:
                    to_emit.append((path, etype))
                    del self.pending_changes[path]
            
            for path, etype in to_emit:
                # In a real broker, this would be bus.emit("fs.changed", ...)
                logger.info(f"FS Event Detected: {etype} on {path}")
                # Placeholder for actual event emission

    # --- Safe Path Helper ---
    def _safe_path(self, rel_path: str) -> str:
        full_path = os.path.abspath(os.path.join(self.root_dir, rel_path))
        if not full_path.startswith(self.root_dir):
            raise PermissionError(f"Access denied: {rel_path} is outside sandbox")
        return full_path

    # --- Capabilities ---
    @capability("fs.list", schema=ListParams)
    async def list_dir(self, params: ListParams, context):
        path = self._safe_path(params.path)
        if not os.path.isdir(path):
            return {"error": "Not a directory"}
        
        items = []
        for entry in os.scandir(path):
            stat = entry.stat()
            items.append({
                "name": entry.name,
                "is_dir": entry.is_dir(),
                "size": stat.st_size,
                "mtime": stat.st_mtime
            })
        return items

    @capability("fs.read", schema=PathParams)
    async def read_file(self, params: PathParams, context):
        path = self._safe_path(params.path)
        if not os.path.isfile(path):
            return {"error": "File not found"}
        
        # Read in executor to avoid blocking
        def _read():
            with open(path, "rb") as f:
                return f.read()
        
        data = await asyncio.get_event_loop().run_in_executor(self.executor, _read)
        try:
            return {"content": data.decode("utf-8"), "encoding": "utf-8"}
        except UnicodeDecodeError:
            return {"content": base64.b64encode(data).decode("ascii"), "encoding": "base64"}

    @capability("fs.write", schema=WriteParams)
    async def write_file(self, params: WriteParams, context):
        path = self._safe_path(params.path)
        
        def _write():
            content = params.content
            if params.encoding == "base64":
                content = base64.b64decode(content)
            else:
                content = content.encode("utf-8")
            
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(content)
            return True

        await asyncio.get_event_loop().run_in_executor(self.executor, _write)
        return {"status": "success"}

    @capability("fs.hash", schema=PathParams)
    async def hash_file(self, params: PathParams, context):
        path = self._safe_path(params.path)
        if not os.path.isfile(path):
            return {"error": "File not found"}
            
        def _hash():
            return imohash.hashfile(path, hexdigest=True)
            
        h = await asyncio.get_event_loop().run_in_executor(self.executor, _hash)
        return {"hash": h}

plugin = SystemFSPlugin()
# Auto-start monitoring when loaded if possible, 
# or wait for a specific hook. For now, we'll let it be manual or via hook.
