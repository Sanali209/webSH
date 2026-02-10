import os
import hashlib
import logging
from datetime import datetime
from typing import Optional

from core.sdk import PluginContext
from .config import FSSettings

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, settings: FSSettings):
        self.settings = settings

    def should_ignore(self, path: str) -> bool:
        """Check if path should be ignored based on settings."""
        parts = path.split(os.sep)
        for part in parts:
            if part in self.settings.excluded_dirs:
                return True
            if part.startswith("."): # Ignore hidden files/dirs by default for now
                return True
        return False

    def calculate_hash(self, filepath: str) -> Optional[str]:
        """Calculate SHA256 hash of file content."""
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                # Read in chunks to avoid memory issues
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except (PermissionError, FileNotFoundError):
            return None

class DatabaseService:
    def __init__(self, context: PluginContext):
        self.core_table = context.db.get_core_table()

    def upsert_file(self, filepath: str, entity_id: str, size: int, mime_type: Optional[str]):
        """Upsert file information into the database."""
        data = [{
            "entity_id": entity_id,
            "path": filepath,
            "filename": os.path.basename(filepath),
            "size": size,
            "mime_type": mime_type,
            "tags": [],
            "last_indexed": datetime.now()
        }]

        # Try to delete existing entry first to avoid duplicates (if using append-only store)
        self.delete_file(filepath, log_success=False)

        try:
            self.core_table.add(data)
            logger.info(f"Indexed file: {filepath}")
        except Exception as e:
            logger.error(f"Error indexing file {filepath}: {e}")

    def delete_file(self, filepath: str, log_success: bool = True):
        """Delete file information from the database."""
        try:
            self.core_table.delete(f"path = '{filepath}'")
            if log_success:
                logger.info(f"Removed file from index: {filepath}")
        except Exception as e:
            logger.error(f"Error removing file {filepath}: {e}")
