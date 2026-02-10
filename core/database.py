import os
import lancedb
import pyarrow as pa
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Core Metadata Schema Definition
CORE_METADATA_SCHEMA = pa.schema([
    pa.field("entity_id", pa.string(), nullable=False),  # PK
    pa.field("path", pa.string(), nullable=False),
    pa.field("filename", pa.string(), nullable=False),
    pa.field("size", pa.int64(), nullable=False),
    pa.field("mime_type", pa.string(), nullable=True),
    pa.field("tags", pa.list_(pa.string()), nullable=True),
    pa.field("last_indexed", pa.timestamp("ms"), nullable=False),
])

class DatabaseClient:
    def __init__(self, db_path: str = ".lancedb"):
        self.db_path = db_path
        self.connection: Optional[lancedb.DBConnection] = None

    def connect(self) -> lancedb.DBConnection:
        """
        Connects to the LanceDB instance. Creates the directory if it doesn't exist.
        """
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path, exist_ok=True)
            logger.info(f"Created LanceDB directory at {self.db_path}")

        self.connection = lancedb.connect(self.db_path)
        logger.info(f"Connected to LanceDB at {self.db_path}")
        return self.connection

    def get_or_create_core_table(self) -> lancedb.table.Table:
        """
        Retrieves the Core Metadata Table, creating it if it doesn't exist.
        """
        if self.connection is None:
            self.connect()

        table_name = "core_metadata"

        existing_tables = self.connection.list_tables()

        if table_name in existing_tables:
             return self.connection.open_table(table_name)
        else:
            logger.info(f"Creating table '{table_name}'")
            return self.connection.create_table(table_name, schema=CORE_METADATA_SCHEMA)

# Global instance (can be overridden for tests)
db_client = DatabaseClient()
