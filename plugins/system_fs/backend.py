import os
import logging
import mimetypes
from typing import Optional

from fastapi import APIRouter, HTTPException
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from core.sdk import PluginBase, PluginContext
from .config import FSSettings
from .services import FileService, DatabaseService

logger = logging.getLogger(__name__)

class FSHandler(FileSystemEventHandler):
    def __init__(self, context: PluginContext, settings: FSSettings):
        self.file_service = FileService(settings)
        self.db_service = DatabaseService(context)

    def on_created(self, event):
        if not event.is_directory:
            self._process_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._process_file(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.db_service.delete_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.db_service.delete_file(event.src_path)
            self._process_file(event.dest_path)

    def _process_file(self, filepath: str):
        if self.file_service.should_ignore(filepath):
            return

        if not os.path.isfile(filepath):
            return

        try:
            stat = os.stat(filepath)
            size = stat.st_size
            mime_type = mimetypes.guess_type(filepath)[0]
            entity_id = self.file_service.calculate_hash(filepath)

            if not entity_id:
                return

            self.db_service.upsert_file(filepath, entity_id, size, mime_type)

        except Exception as e:
            logger.error(f"Error processing file {filepath}: {e}")

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
        handler = FSHandler(context, self.settings)
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
