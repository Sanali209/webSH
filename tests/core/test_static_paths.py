import pytest
from fastapi.testclient import TestClient
import os
import sys
from unittest.mock import MagicMock

# Mock redis to avoid connection errors
sys.modules["redis.asyncio"] = MagicMock()

# Import app after mocking
from main import app, loader

client = TestClient(app)

def test_csp_headers():
    response = client.get("/health")
    assert response.status_code == 200
    headers = response.headers
    assert "content-security-policy" in headers
    csp = headers["content-security-policy"]
    # Check for expected directives
    assert "default-src 'self'" in csp
    assert "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net" in csp
    assert "style-src 'self' 'unsafe-inline'" in csp
    assert "frame-src 'self'" in csp

def test_desktop_static_serving():
    # Ensure dist exists
    if not os.path.exists("dist"):
        os.makedirs("dist")

    # Create a test file
    test_file = "dist/test_static.txt"
    with open(test_file, "w") as f:
        f.write("Static Content")

    # Refresh WhiteNoise index since it scans on startup
    from main import desktop_app
    desktop_app.add_files("dist")

    try:
        response = client.get("/desktop/test_static.txt")
        assert response.status_code == 200
        assert response.text == "Static Content"
        # WhiteNoise adds cache headers usually
        # But allow flexibility if configuration differs
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

def test_ui_health_check_missing_plugin():
    response = client.get("/health/ui/nonexistent_plugin")
    assert response.status_code == 404
    assert response.json() == {"status": "plugin_not_found"}

def test_ui_health_check_valid_plugin(tmp_path):
    plugin_id = "test_plugin_health"
    # Create fake plugin structure
    plugin_dir = tmp_path / plugin_id
    ui_dir = plugin_dir / "ui"
    ui_dir.mkdir(parents=True)
    (ui_dir / "index.js").write_text("console.log('hi')")

    # Inject into loader
    loader.loaded_plugins.append(plugin_id)
    loader.plugin_paths[plugin_id] = str(plugin_dir)

    try:
        response = client.get(f"/health/ui/{plugin_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "available"
        assert data["files"]["index.js"] is True
        assert data["files"]["manifest.json"] is False
    finally:
        # Clean up loader
        if plugin_id in loader.loaded_plugins:
            loader.loaded_plugins.remove(plugin_id)
        if plugin_id in loader.plugin_paths:
            del loader.plugin_paths[plugin_id]
