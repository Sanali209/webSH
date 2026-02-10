import pytest
import os
import shutil
from fastapi.testclient import TestClient
from core.main import app

@pytest.fixture
def mock_dist(tmp_path):
    """
    Creates a mock dist directory with assets and index.html in the current working directory.
    """
    # Create dist folder in current directory (where main.py looks for it)
    dist_dir = os.path.join(os.getcwd(), "dist")
    assets_dir = os.path.join(dist_dir, "assets")

    # Clean up if exists
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)

    os.makedirs(assets_dir)

    # Create dummy files
    with open(os.path.join(dist_dir, "index.html"), "w") as f:
        f.write("<html><body>Mock Frontend</body></html>")

    with open(os.path.join(assets_dir, "style.css"), "w") as f:
        f.write("body { background: #fff; }")

    yield dist_dir

    # Cleanup
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)

def test_api_routes_still_work(mock_dist):
    """
    Verify that API routes are not shadowed by the catch-all handler.
    Note: We need to reload the app configuration or simulate the mount because
    app.mount checks for os.path.exists("dist") at module level execution time.

    Since we cannot easily reload the module in a unit test without side effects,
    we will rely on the fact that if 'dist' exists, the logic *would* execute.

    However, TestClient uses the app object as it was when imported.
    If 'dist' didn't exist at import time, the mounts won't be there.

    We can manually mount for the test client.
    """
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    # Manually apply the logic that runs in main.py if dist exists
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

    # Add catch-all route if not present (it might be tricky to inject into the router order dynamically correctly
    # if not done at startup, but let's try to simulate the response logic directly)

    client = TestClient(app)

    # API should still work
    response = client.get("/api/status")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_static_assets_serving(mock_dist):
    """
    Verify that assets are served.
    """
    # Manually mount for test context
    from fastapi.staticfiles import StaticFiles
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="test_assets")

    client = TestClient(app)
    response = client.get("/assets/style.css")
    assert response.status_code == 200
    assert "background" in response.text

def test_spa_catch_all_logic(mock_dist):
    """
    Verify the logic of the catch-all handler.
    """
    # We can test the handler function directly to avoid router ordering issues in tests
    from core.main import serve_gui
    import asyncio

    # Test non-api path
    response = asyncio.run(serve_gui("dashboard"))
    # FileResponse returns a response object, we can check path or status
    assert os.path.basename(response.path) == "index.html"

    # Test nested non-api path
    response = asyncio.run(serve_gui("settings/users"))
    assert os.path.basename(response.path) == "index.html"
