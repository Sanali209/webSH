import lancedb
import logging
from typing import List, Optional, Any
from core.database import db_client, DatabaseClient

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Central manager for database operations, wrapping the DatabaseClient.
    """
    def __init__(self, client: DatabaseClient = db_client):
        self.client = client

    def get_table(self, table_name: str, schema: Optional[Any] = None) -> lancedb.table.Table:
        """
        Retrieves or creates a table.
        """
        if self.client.connection is None:
            self.client.connect()

        # Check if table exists using list_tables
        existing_tables = self.list_tables()
        if table_name in existing_tables:
            return self.client.connection.open_table(table_name)

        # If not exists, create if schema provided
        if schema:
            logger.info(f"Creating table '{table_name}'")
            return self.client.connection.create_table(table_name, schema=schema)
        else:
            raise ValueError(f"Table '{table_name}' does not exist and no schema provided.")

    def list_tables(self) -> List[str]:
        """
        Returns a list of all table names.
        """
        if self.client.connection is None:
            self.client.connect()

        try:
            # table_names() is the most reliable way to get a list of strings currently,
            # even if deprecated. list_tables() in some versions returns iterators of objects.
            # We'll rely on table_names for now to ensure tests pass, ignoring the warning.
            return self.client.connection.table_names()
        except AttributeError:
             # Fallback if strictly removed (unlikely in minor version updates)
             if hasattr(self.client.connection, "list_tables"):
                 # Assuming list_tables returns objects with 'name' attribute or similar if not strings
                 tables = self.client.connection.list_tables()
                 # Try to parse if they are not strings
                 return [t if isinstance(t, str) else getattr(t, 'name', str(t)) for t in tables]
             return []

class PluginDatabaseContext:
    """
    Scoped database access for a specific plugin.
    """
    def __init__(self, plugin_id: str, db_manager: DatabaseManager, permissions: List[str] = None):
        self.plugin_id = plugin_id
        self.db_manager = db_manager
        self.permissions = permissions or []

    def get_my_table(self, suffix: str, schema: Optional[Any] = None) -> lancedb.table.Table:
        """
        Returns a table scoped to this plugin: `plugin_{id}_{suffix}`.
        """
        table_name = f"plugin_{self.plugin_id}_{suffix}"
        return self.db_manager.get_table(table_name, schema=schema)

    def get_core_table(self) -> lancedb.table.Table:
        """
        Returns the Core Metadata Table.
        """
        return self.db_manager.client.get_or_create_core_table()

    def get_other_table(self, target_plugin_id: str, suffix: str) -> lancedb.table.Table:
        """
        Returns a table belonging to another plugin, if permission is granted.
        Permission format: `plugin:read:{target_plugin_id}` or `plugin:write:{target_plugin_id}`.
        """
        # Basic permission check
        required_read_perm = f"plugin:read:{target_plugin_id}"
        required_write_perm = f"plugin:write:{target_plugin_id}"

        if required_read_perm not in self.permissions and required_write_perm not in self.permissions:
             raise PermissionError(f"Plugin '{self.plugin_id}' does not have permission to access tables of '{target_plugin_id}'.")

        table_name = f"plugin_{target_plugin_id}_{suffix}"
        # We don't allow creating other plugin's tables via this method, only accessing existing ones
        return self.db_manager.get_table(table_name)

# Global instance
db_manager = DatabaseManager()
