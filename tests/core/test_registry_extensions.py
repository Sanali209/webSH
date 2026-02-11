import pytest
from core.registry import Registry
from core.registry import registry as global_registry
import asyncio

def test_list_extensions():
    registry = Registry()

    # Register widgets
    registry.register_ui_extension("p1", {
        "widgets": [
            {"id": "w1", "type": "widget", "title": "Widget 1", "size": "1x1", "entry_point": "w1.js"}
        ]
    })

    # Register views (applications)
    registry.register_ui_extension("p2", {
        "views": [
            {"id": "v1", "title": "App 1", "entry_point": "v1.js"}
        ]
    })

    # Register shortcuts
    registry.register_ui_extension("p3", {
        "shortcuts": [
            {"title": "Shortcut 1", "action": "do_something", "icon": "icon"}
        ]
    })

    # Register top bar
    registry.register_ui_extension("p4", {
        "top_bar": [
            {"id": "tb1", "type": "top_bar.item", "entry_point": "tb1.js"}
        ]
    })

    extensions = registry.list_extensions()

    assert len(extensions["widgets"]) == 1
    assert extensions["widgets"][0]["id"] == "w1"
    assert extensions["widgets"][0]["plugin_id"] == "p1"

    assert len(extensions["applications"]) == 1
    assert extensions["applications"][0]["id"] == "v1"
    assert extensions["applications"][0]["type"] == "application"
    assert extensions["applications"][0]["plugin_id"] == "p2"

    assert len(extensions["shortcuts"]) == 1
    assert extensions["shortcuts"][0]["title"] == "Shortcut 1"
    assert extensions["shortcuts"][0]["type"] == "shortcut"

    assert len(extensions["top_bar"]) == 1
    assert extensions["top_bar"][0]["id"] == "tb1"

def test_api_list_ui_extensions():
    async def run_test():
        from main import app
        from httpx import AsyncClient, ASGITransport

        # Populate global registry
        global_registry.register_ui_extension("test_plugin", {
            "widgets": [
                {"id": "test_w", "type": "widget", "title": "Test Widget", "size": "1x1", "entry_point": "test.js"}
            ]
        })

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/registry/ui-extensions")

        assert response.status_code == 200
        data = response.json()

        assert "widgets" in data
        assert len(data["widgets"]) >= 1
        found = False
        for w in data["widgets"]:
            if w["id"] == "test_w":
                found = True
                break
        assert found

    asyncio.run(run_test())
