import pytest
import asyncio
import os
import shutil
from core.schemas import CapabilityEnvelope, Context
from plugins.system_storage.backend import SystemStoragePlugin, SetParams, GetParams, SearchParams

@pytest.fixture
def storage():
    # Setup a clean test DB
    test_db_dir = os.path.join("data", "test_storage.lancedb")
    if os.path.exists(test_db_dir):
        shutil.rmtree(test_db_dir)
    os.makedirs(test_db_dir, exist_ok=True)
    
    plugin = SystemStoragePlugin()
    # Override db_path for testing
    plugin.db_path = test_db_dir
    plugin._init_db()
    
    yield plugin
    
    # Cleanup
    if os.path.exists(test_db_dir):
        # We need to close the connection first (if possible) or just let it be
        # LanceDB connections are handles.
        pass

@pytest.mark.asyncio
async def test_storage_set_get(storage):
    # 1. Set data
    params = SetParams(
        table="test_table",
        data=[
            {"id": 1, "name": "item1", "value": 10.5},
            {"id": 2, "name": "item2", "value": 20.0}
        ]
    )
    result = await storage.set_data(params, Context(caller_id="test"))
    assert result["status"] == "success"
    assert result["count"] == 2
    
    # 2. Get data
    get_params = GetParams(table="test_table")
    items = await storage.get_data(get_params, Context(caller_id="test"))
    assert len(items) == 2
    assert any(i["name"] == "item1" for i in items)

@pytest.mark.asyncio
async def test_storage_search(storage):
    # 1. Create table with vectors
    # LanceDB infers schema from the first insertion
    data = [
        {"id": 1, "vector": [0.1, 0.2, 0.3], "text": "apple"},
        {"id": 2, "vector": [0.9, 0.8, 0.7], "text": "banana"}
    ]
    await storage.set_data(SetParams(table="vectors", data=data), Context(caller_id="test"))
    
    # 2. Search
    search_params = SearchParams(
        table="vectors",
        vector=[0.11, 0.21, 0.31],
        limit=1
    )
    results = await storage.search_data(search_params, Context(caller_id="test"))
    assert len(results) == 1
    assert results[0]["text"] == "apple"

@pytest.mark.asyncio
async def test_persistence():
    test_db_dir = os.path.join("data", "persist_test.lancedb")
    if os.path.exists(test_db_dir):
        shutil.rmtree(test_db_dir)
    
    # 1. Create and write
    p1 = SystemStoragePlugin()
    p1.db_path = test_db_dir
    p1._init_db()
    await p1.set_data(SetParams(table="p", data=[{"k": "v"}]), Context(caller_id="t"))
    # Note: LanceDB might need explicit close or flush if it was more complex, but usually it writes on add.
    
    # 2. Re-open
    p2 = SystemStoragePlugin()
    p2.db_path = test_db_dir
    p2._init_db()
    items = await p2.get_data(GetParams(table="p"), Context(caller_id="t"))
    assert len(items) == 1
    assert items[0]["k"] == "v"
