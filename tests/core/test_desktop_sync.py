import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import tempfile
import os
import lancedb
from core.schemas import DesktopConfig, WidgetConfig

@pytest.fixture
def test_db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test_desktop.lancedb")

@pytest.fixture
def client(test_db_path):
    # We define a side effect to redirect connection to test path
    original_connect = lancedb.connect

    def side_effect(uri, *args, **kwargs):
        # Always connect to the test path regardless of the URI requested
        return original_connect(test_db_path, *args, **kwargs)

    with patch("lancedb.connect", side_effect=side_effect):
        from main import app
        with TestClient(app) as c:
            yield c

def test_desktop_sync_flow(client):
    # 1. Start with clean state (lifespan initializes DB)

    # Sync empty list
    response = client.post("/api/v1/desktop/sync", json=[])
    assert response.status_code == 200, f"Error: {response.text}"
    assert response.json()["count"] == 0

    # Get empty list
    response = client.get("/api/v1/desktop/sync")
    assert response.status_code == 200
    assert response.json() == []

    # 2. Sync some data (2 empty desktops)
    desktops = [
        {"id": 0, "widgets": []},
        {"id": 1, "widgets": []}
    ]
    response = client.post("/api/v1/desktop/sync", json=desktops)
    assert response.status_code == 200, f"Error: {response.text}"
    assert response.json()["count"] == 2

    # 3. Get data back
    response = client.get("/api/v1/desktop/sync")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Verify order and content
    ids = sorted([d["id"] for d in data])
    assert ids == [0, 1]

    # 4. Sync data with widgets
    desktops = [
        {
            "id": 0,
            "widgets": [
                {"id": "w1", "x": 0, "y": 0, "w": 1, "h": 1, "type": "icon", "label": "Trash", "icon": "trash", "props": None}
            ]
        }
    ]
    response = client.post("/api/v1/desktop/sync", json=desktops)
    assert response.status_code == 200, f"Error: {response.text}"
    assert response.json()["count"] == 1

    # 5. Get data back
    response = client.get("/api/v1/desktop/sync")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["widgets"][0]["label"] == "Trash"
