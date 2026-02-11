import os
import lancedb
import pandas as pd
import pyarrow as pa
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from core.sdk import BasePlugin, capability
from loguru import logger
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Schemas for validation
class SetParams(BaseModel):
    table: str = Field(..., description="Table name (plugin_state, capabilities, etc.)")
    data: List[Dict[str, Any]] = Field(..., description="List of records to insert")

class GetParams(BaseModel):
    table: str
    filter: Optional[str] = None
    limit: Optional[int] = 10

class SearchParams(BaseModel):
    table: str
    vector: List[float]
    limit: Optional[int] = 5

class SystemStoragePlugin(BasePlugin):
    VERSION = "1.0.0"

    def __init__(self):
        super().__init__()
        self.db_path = os.path.join("data", "system_storage.lancedb")
        self.db = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._init_db()

    def _init_db(self):
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path, exist_ok=True)
        self.db = lancedb.connect(self.db_path)
        logger.info(f"LanceDB connected at {self.db_path}")

    async def _run_in_executor(self, func, *args):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)

    def _get_or_create_table(self, name: str, schema: pa.Schema):
        if name in self.db.list_tables():
            return self.db.open_table(name)
        return self.db.create_table(name, schema=schema)

    @capability("storage.set", schema=SetParams)
    async def set_data(self, params: SetParams, context):
        """
        Inserts or appends data to a table.
        """
        def _sync_set():
            table = self.db.open_table(params.table) if params.table in self.db.list_tables() else None
            if table:
                table.add(params.data)
            else:
                # Create table from the first batch of data if it doesn't exist
                self.db.create_table(params.table, data=params.data)
            return {"status": "success", "count": len(params.data)}

        try:
            return await self._run_in_executor(_sync_set)
        except Exception as e:
            logger.error(f"Error in storage.set: {e}")
            raise

    @capability("storage.get", schema=GetParams)
    async def get_data(self, params: GetParams, context):
        """
        Retrieves data from a table with an optional filter.
        """
        def _sync_get():
            if params.table not in self.db.list_tables():
                return []
            table = self.db.open_table(params.table)
            query = table.search()
            if params.filter:
                query = query.where(params.filter)
            return query.limit(params.limit).to_list()

        try:
            results = await self._run_in_executor(_sync_get)
            return results
        except Exception as e:
            logger.error(f"Error in storage.get: {e}")
            raise

    @capability("storage.search", schema=SearchParams)
    async def search_data(self, params: SearchParams, context):
        """
        Performs vector search.
        """
        def _sync_search():
            if params.table not in self.db.list_tables():
                return []
            table = self.db.open_table(params.table)
            return table.search(params.vector).limit(params.limit).to_list()

        try:
            return await self._run_in_executor(_sync_search)
        except Exception as e:
            logger.error(f"Error in storage.search: {e}")
            raise

    @capability("storage.batch_insert")
    async def batch_insert(self, params: Dict[str, Any], context):
        """
        High-throughput batch insertion.
        Expects params: {"table": str, "data": List[Dict]}
        """
        # Reuse set_data logic but maybe with optimized arrow handling in future
        set_params = SetParams(table=params["table"], data=params["data"])
        return await self.set_data(set_params, context)

plugin = SystemStoragePlugin()
