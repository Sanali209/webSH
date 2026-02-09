import pytest
import os
import json
from core.workflow import workflow_node, NODE_REGISTRY, NodeInput, NodeOutput
from core.plugin_manager import PluginLoader

def test_workflow_decorator_registration():
    """Verify that @workflow_node registers function in global registry."""
    # Clear registry for test isolation
    NODE_REGISTRY.clear()

    @workflow_node(
        id="test_node",
        name="Test Node",
        inputs=[NodeInput(name="in", type="string")],
        outputs=[NodeOutput(name="out", type="string")]
    )
    def my_func(ctx, inputs):
        return "result"

    assert "test_node" in NODE_REGISTRY
    node_def = NODE_REGISTRY["test_node"]
    assert node_def.name == "Test Node"
    assert len(node_def.inputs) == 1
    assert node_def.inputs[0].name == "in"

    # Verify function is callable
    assert my_func(None, {}) == "result"

def test_workflow_module_loading(tmp_path):
    """Verify that PluginLoader loads workflow.py and registers nodes."""
    NODE_REGISTRY.clear()

    plugin_dir = tmp_path / "plugins"
    plugin_id = "workflow_plugin"
    plugin_path = plugin_dir / plugin_id
    os.makedirs(plugin_path)

    # Create manifest
    with open(plugin_path / "manifest.json", "w") as f:
        json.dump({"id": plugin_id, "name": "WF Plugin", "version": "1.0"}, f)

    # Create dummy backend.py
    with open(plugin_path / "backend.py", "w") as f:
        f.write("""
from core.sdk import PluginBase, PluginContext
class WFPlugin(PluginBase):
    def on_load(self, ctx): pass
    def on_activate(self): pass
    def on_deactivate(self): pass
""")

    # Create workflow.py
    with open(plugin_path / "workflow.py", "w") as f:
        f.write("""
from core.workflow import workflow_node

@workflow_node(id="loaded_node", name="Loaded Node")
def run_node(ctx, inputs):
    pass
""")

    loader = PluginLoader(plugin_dir=str(plugin_dir))
    loader.scan_plugins()
    loader.load_plugin(plugin_id)

    assert "loaded_node" in NODE_REGISTRY
    assert NODE_REGISTRY["loaded_node"].name == "Loaded Node"
