import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from core.events import AsyncEventBus

@pytest.mark.asyncio
async def test_subscribe_and_publish():
    """Verify that subscribers receive published events."""
    bus = AsyncEventBus()
    received_data = []

    async def callback(data, correlation_id):
        received_data.append((data, correlation_id))

    bus.subscribe("test_event", callback)
    await bus.publish("test_event", {"msg": "hello"}, correlation_id="123")

    assert len(received_data) == 1
    assert received_data[0][0] == {"msg": "hello"}
    assert received_data[0][1] == "123"

@pytest.mark.asyncio
async def test_multiple_subscribers():
    """Verify that all subscribers are notified."""
    bus = AsyncEventBus()
    count = 0

    async def callback1(data, correlation_id):
        nonlocal count
        count += 1

    async def callback2(data, correlation_id):
        nonlocal count
        count += 1

    bus.subscribe("test_event", callback1)
    bus.subscribe("test_event", callback2)
    await bus.publish("test_event", {})

    assert count == 2

@pytest.mark.asyncio
async def test_correlation_id_generation():
    """Verify that a correlation ID is generated if not provided."""
    bus = AsyncEventBus()
    captured_id = None

    async def callback(data, correlation_id):
        nonlocal captured_id
        captured_id = correlation_id

    bus.subscribe("test_event", callback)
    await bus.publish("test_event", {})

    assert captured_id is not None
    assert isinstance(captured_id, str)
    assert len(captured_id) > 0

@pytest.mark.asyncio
async def test_websocket_broadcast():
    """Verify that events are broadcast to connected websockets."""
    bus = AsyncEventBus()
    mock_ws = AsyncMock()

    # Simulate a connected websocket
    bus.websockets.append(mock_ws)

    test_data = {"msg": "broadcast"}
    await bus.publish("test_event", test_data, correlation_id="abc")

    # Check that send_json was called
    mock_ws.send_json.assert_called_once()
    call_args = mock_ws.send_json.call_args[0][0]

    assert call_args["event"] == "test_event"
    assert call_args["data"] == test_data
    assert call_args["correlation_id"] == "abc"
