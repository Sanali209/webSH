import os
import hashlib
import mimetypes
import logging
import time
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from core.sdk import PluginBase, PluginContext
from core.events import event_bus
from .config import FSSettings

logger = logging.getLogger(__name__)

class FSHandler(FileSystemEventHandler):
    def __init__(self, context: PluginContext, settings: FSSettings, loop: asyncio.AbstractEventLoop):
        self.context = context
        self.settings = settings
        self.core_table = context.db.get_core_table()
        self.loop = loop

    def _emit_change(self, event_type: str, path: str):
        try:
            future = asyncio.run_coroutine_threadsafe(
                event_bus.publish(f"fs:{event_type}", {"path": path, "event": event_type}),
                self.loop
            )
            # We don't wait for result to avoid blocking watchdog thread
        except Exception as e:
            logger.error(f"Failed to emit fs change event: {e}")

    def _should_ignore(self, path: str) -> bool:
        """Check if path should be ignored based on settings."""
        parts = path.split(os.sep)
        for part in parts:
            if part in self.settings.excluded_dirs:
                return True
            if part.startswith("."): # Ignore hidden files/dirs by default for now
                return True
        return False

    def _calculate_hash(self, filepath: str) -> str:
        """Calculate SHA256 hash of file content."""
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                # Read in chunks to avoid memory issues
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except (PermissionError, FileNotFoundError):
            return ""

    def _update_db(self, filepath: str):
        if self._should_ignore(filepath):
            return

        if not os.path.isfile(filepath):
            return

        try:
            stat = os.stat(filepath)
            size = stat.st_size
            mime_type, _ = mimetypes.guess_type(filepath)
            entity_id = self._calculate_hash(filepath)

            if not entity_id:
                return

            data = [{
                "entity_id": entity_id,
                "path": filepath,
                "filename": os.path.basename(filepath),
                "size": size,
                "mime_type": mime_type,
                "tags": [],
                "last_indexed": datetime.now()
            }]

            # Upsert logic: LanceDB merge_insert is available in newer versions,
            # but standard 'add' appends. We might need to delete existing first?
            # Or use 'merge_insert' if available.
            # Assuming 'add' for now, duplicates handled by query or cleanup?
            # Actually, standard practice with LanceDB is append-only + cleanup or merge.
            # Let's try to delete existing by path first if possible, or just append.
            # Since 'entity_id' is PK in schema? No, LanceDB doesn't enforce PK constraint on 'add'.
            # But we want to avoid duplicates.
            # Let's try to delete by path first.
            try:
                self.core_table.delete(f"path = '{filepath}'")
            except Exception as e:
                logger.warning(f"Failed to delete existing entry for {filepath}: {e}")

            self.core_table.add(data)
            logger.info(f"Indexed file: {filepath}")

        except Exception as e:
            logger.error(f"Error processing file {filepath}: {e}")

    def _delete_from_db(self, filepath: str):
        try:
            self.core_table.delete(f"path = '{filepath}'")
            logger.info(f"Removed file from index: {filepath}")
        except Exception as e:
            logger.error(f"Error removing file {filepath}: {e}")

    def on_created(self, event):
        if not event.is_directory:
            self._update_db(event.src_path)
            self._emit_change("created", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._update_db(event.src_path)
            self._emit_change("modified", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self._delete_from_db(event.src_path)
            self._emit_change("deleted", event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._delete_from_db(event.src_path)
            self._update_db(event.dest_path)
            self._emit_change("moved", event.dest_path)


class SystemFSPlugin(PluginBase):
    def __init__(self):
        self.settings = FSSettings()
        self.observer = None
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("/scan")
        async def scan_directory(path: str = "."):
            """List files in a directory."""
            abs_path = os.path.abspath(path)
            # Security check: prevent accessing outside root?
            # For System Plugin, maybe allowed? But let's restrict to root_path or subdirs if possible.
            # For now, allow any path but warn.

            if not os.path.exists(abs_path):
                 raise HTTPException(status_code=404, detail="Path not found")

            if not os.path.isdir(abs_path):
                 raise HTTPException(status_code=400, detail="Not a directory")

            entries = []
            try:
                with os.scandir(abs_path) as it:
                    for entry in it:
                        entries.append({
                            "name": entry.name,
                            "path": entry.path,
                            "is_dir": entry.is_dir(),
                            "size": entry.stat().st_size if not entry.is_dir() else 0,
                            "mtime": entry.stat().st_mtime
                        })
            except PermissionError:
                raise HTTPException(status_code=403, detail="Permission denied")

            return entries

    def on_load(self, context: PluginContext) -> None:
        self.observer = Observer()
        # Get the running loop from main thread context (on_load is called synchronously but we can get loop)
        try:
            loop = asyncio.get_running_loop()
            logger.info("SystemFSPlugin captured running event loop.")
        except RuntimeError:
            # Fallback if no loop running (should not happen in main app, but maybe tests)
            logger.warning("SystemFSPlugin: No running loop found! Creating new detached loop. Events may fail.")
            loop = asyncio.new_event_loop()

        handler = FSHandler(context, self.settings, loop)
        path_to_watch = os.path.abspath(self.settings.root_path)

        if os.path.exists(path_to_watch):
            self.observer.schedule(handler, path_to_watch, recursive=True)
            self.observer.start()
            logger.info(f"SystemFSPlugin watching: {path_to_watch}")
        else:
            logger.warning(f"Watch path does not exist: {path_to_watch}")

    def on_activate(self) -> None:
        pass

    def on_deactivate(self) -> None:
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("SystemFSPlugin watcher stopped.")
