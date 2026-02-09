import sqlite3
import logging
import os
from typing import Optional
from core.sdk import PluginBase
from core.plugin_manager import PluginLoader

logger = logging.getLogger(__name__)

class MigrationManager:
    """
    Manages plugin schema migrations using a SQLite database to track versions.
    """
    def __init__(self, db_path: str = "plugins.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """
        Initializes the SQLite database and creates the version tracking table.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plugin_versions (
                plugin_id TEXT PRIMARY KEY,
                version TEXT
            )
        """)
        conn.commit()
        conn.close()

    def get_installed_version(self, plugin_id: str) -> Optional[str]:
        """
        Retrieves the currently installed version of a plugin from the DB.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM plugin_versions WHERE plugin_id = ?", (plugin_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def update_version(self, plugin_id: str, new_version: str):
        """
        Updates the stored version for a plugin.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO plugin_versions (plugin_id, version)
            VALUES (?, ?)
            ON CONFLICT(plugin_id) DO UPDATE SET version = excluded.version
        """, (plugin_id, new_version))
        conn.commit()
        conn.close()
        logger.info(f"Updated version for plugin {plugin_id} to {new_version}")

    def run_migrations(self, loader: PluginLoader):
        """
        Iterates through loaded plugins and triggers migration if necessary.
        """
        for plugin_id, plugin_instance in loader.loaded_plugins.items():
            manifest = loader.manifests.get(plugin_id)
            if not manifest:
                continue

            current_version = manifest.version
            installed_version = self.get_installed_version(plugin_id)

            if installed_version is None:
                # First install: just update the DB, no migration logic needed usually,
                # or perhaps call a "install" hook. For now, assume fresh install.
                logger.info(f"First install detected for {plugin_id} (v{current_version})")
                self.update_version(plugin_id, current_version)
            elif installed_version != current_version:
                logger.info(f"Migrating {plugin_id} from {installed_version} to {current_version}")
                try:
                    plugin_instance.migrate(installed_version, current_version)
                    self.update_version(plugin_id, current_version)
                    logger.info(f"Migration successful for {plugin_id}")
                except Exception as e:
                    logger.error(f"Migration failed for {plugin_id}: {e}")
            else:
                logger.debug(f"Plugin {plugin_id} is up to date (v{current_version})")

# Global instance
migration_manager = MigrationManager()
