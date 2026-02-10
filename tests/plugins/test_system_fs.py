import os
import shutil
import time
import pytest
from unittest.mock import MagicMock, patch
from plugins.system_fs.backend import SystemFSPlugin, FSHandler
from core.sdk import PluginContext
from plugins.system_fs.config import FSSettings

# Helper to create a dummy file structure
@pytest.fixture
def fs_setup(tmp_path):
    root = tmp_path / "fs_root"
    root.mkdir()
    (root / "file1.txt").write_text("content1")
    (root / "dir1").mkdir()
    (root / "dir1" / "file2.txt").write_text("content2")
    return root

@pytest.fixture
def mock_context():
    context = MagicMock(spec=PluginContext)
    # Mock DB context
    context.db = MagicMock()
    context.db.get_core_table.return_value = MagicMock()
    return context

def test_fs_scan(fs_setup):
    plugin = SystemFSPlugin()
    # Direct call to scan logic (we can't call async router handler easily without client,
    # but we can test the logic if we extract it or call it via a test client)
    # Actually, we can just call os.scandir to verify our assumptions,
    # but better to test the router function if possible.
    # We'll use TestClient in integration tests. Here we test the plugin class methods if any.
    # The plugin exposes scan via router.
    # Let's test FSHandler logic.
    pass

def test_fs_handler_sync(fs_setup, mock_context):
    settings = FSSettings(root_path=str(fs_setup))
    loop = MagicMock()
    handler = FSHandler(mock_context, settings, loop)

    # Test on_created
    new_file = fs_setup / "new.txt"
    new_file.write_text("new content")

    event = MagicMock()
    event.is_directory = False
    event.src_path = str(new_file)

    handler.on_created(event)

    # Verify DB add was called
    mock_context.db.get_core_table().add.assert_called_once()
    args = mock_context.db.get_core_table().add.call_args[0][0]
    assert args[0]["path"] == str(new_file)
    assert args[0]["filename"] == "new.txt"
    assert args[0]["size"] == len("new content")

def test_fs_handler_delete(fs_setup, mock_context):
    settings = FSSettings(root_path=str(fs_setup))
    loop = MagicMock()
    handler = FSHandler(mock_context, settings, loop)

    file_to_del = fs_setup / "file1.txt"

    event = MagicMock()
    event.is_directory = False
    event.src_path = str(file_to_del)

    handler.on_deleted(event)

    # Verify DB delete was called
    mock_context.db.get_core_table().delete.assert_called_once_with(f"path = '{str(file_to_del)}'")

@pytest.mark.asyncio
async def test_api_scan(fs_setup):
    # To test the router, we can mount it in a dummy app or just inspect the route handler.
    # But simpler: use FastAPI TestClient
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    plugin = SystemFSPlugin()
    app = FastAPI()
    app.include_router(plugin.router)

    client = TestClient(app)

    response = client.get(f"/scan?path={fs_setup}")
    assert response.status_code == 200
    data = response.json()

    filenames = [entry["name"] for entry in data]
    assert "file1.txt" in filenames
    assert "dir1" in filenames
