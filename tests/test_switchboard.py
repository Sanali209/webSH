import pytest
import asyncio
from core.schemas import CapabilityEnvelope, Context
from core.switchboard import Switchboard
from core.registry import Registry
from core.sdk import BasePlugin, capability
from pydantic import BaseModel, Field
from typing import Optional

# 1. Setup Mock Plugin
class MockParams(BaseModel):
    message: str
    count: Optional[int] = 1

class MockPlugin(BasePlugin):
    VERSION = "1.2.3"
    
    @capability("mock.test", schema=MockParams)
    async def test_cap(self, params: MockParams, context):
        return {"echo": params.message, "count": params.count}

    @capability("mock.no_schema")
    async def no_schema_cap(self, params, context):
        return {"raw_params": params}

# 2. Tests
@pytest.mark.asyncio
async def test_switchboard_routing():
    reg = Registry()
    plugin = MockPlugin()
    plugin.sh_plugin_init(reg)
    
    # Inject our registry into a new switchboard
    sb = Switchboard()
    # Mocking the registry used by switchboard for this test
    import core.switchboard
    core.switchboard.registry = reg
    
    envelope = CapabilityEnvelope(
        domain="mock.test",
        params={"message": "hello", "count": 5},
        context=Context(caller_id="test_user")
    )
    
    result = await sb.dispatch(envelope)
    
    assert result["status"] == "success"
    assert result["data"]["echo"] == "hello"
    assert result["data"]["count"] == 5
    assert "kernel.switchboard" in envelope.context.trace_stack

@pytest.mark.asyncio
async def test_schema_validation_failure():
    reg = Registry()
    plugin = MockPlugin()
    plugin.sh_plugin_init(reg)
    
    sb = Switchboard()
    import core.switchboard
    core.switchboard.registry = reg
    
    # Missing required 'message' field
    envelope = CapabilityEnvelope(
        domain="mock.test",
        params={"count": 5},
        context=Context(caller_id="test_user")
    )
    
    result = await sb.dispatch(envelope)
    
    assert result["status"] == "error"
    assert result["type"] == "schema_validation_error"
    assert len(result["details"]) > 0

@pytest.mark.asyncio
async def test_circular_dependency():
    sb = Switchboard(max_trace_depth=2)
    
    envelope = CapabilityEnvelope(
        domain="any.domain",
        params={},
        context=Context(caller_id="test_user", trace_stack=["node1", "node2"])
    )
    
    with pytest.raises(RuntimeError) as excinfo:
        await sb.dispatch(envelope)
    
    assert "Max trace depth exceeded" in str(excinfo.value)

@pytest.mark.asyncio
async def test_no_schema_capability():
    reg = Registry()
    plugin = MockPlugin()
    plugin.sh_plugin_init(reg)
    
    sb = Switchboard()
    import core.switchboard
    core.switchboard.registry = reg
    
    envelope = CapabilityEnvelope(
        domain="mock.no_schema",
        params={"foo": "bar"},
        context=Context(caller_id="test_user")
    )
    
    result = await sb.dispatch(envelope)
    
    assert result["status"] == "success"
    assert result["data"]["raw_params"]["foo"] == "bar"
