import pytest
import os
import shutil
import lancedb
import pyarrow as pa
from core.database import DatabaseClient, CORE_METADATA_SCHEMA

@pytest.fixture
def test_db_path(tmp_path):
    """
    Creates a temporary directory for the LanceDB instance.
    """
    db_path = tmp_path / "test_lancedb"
    yield str(db_path)
    # Cleanup (handled by tmp_path fixture, but explicit is good)
    if os.path.exists(db_path):
        shutil.rmtree(db_path)

def test_connect_creates_directory(test_db_path):
    """
    Test that the connect method creates the database directory.
    """
    client = DatabaseClient(db_path=test_db_path)
    assert not os.path.exists(test_db_path)

    client.connect()
    assert os.path.exists(test_db_path)
    assert client.connection is not None

def test_create_core_table(test_db_path):
    """
    Test that the core_metadata table is created with the correct schema.
    """
    client = DatabaseClient(db_path=test_db_path)
    client.connect()

    table = client.get_or_create_core_table()
    assert table.name == "core_metadata"

    # Verify schema
    # LanceDB might add some internal metadata, so we check for our fields
    table_schema = table.schema
    expected_fields = set(f.name for f in CORE_METADATA_SCHEMA)
    actual_fields = set(f.name for f in table_schema)

    assert expected_fields.issubset(actual_fields)

def test_insert_and_retrieve(test_db_path):
    """
    Test basic CRUD operations on the core table.
    """
    client = DatabaseClient(db_path=test_db_path)
    client.connect()
    table = client.get_or_create_core_table()

    # Insert data
    data = [{
        "entity_id": "12345",
        "path": "/tmp/test.txt",
        "filename": "test.txt",
        "size": 1024,
        "mime_type": "text/plain",
        "tags": ["test", "document"],
        "last_indexed": 1700000000000
    }]

    table.add(data)

    # Retrieve data
    result = table.search().where("entity_id = '12345'").to_pandas()

    assert len(result) == 1
    assert result.iloc[0]["filename"] == "test.txt"
    assert result.iloc[0]["size"] == 1024
