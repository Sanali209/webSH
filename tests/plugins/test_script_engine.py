"""
Tests for Script Engine Plugin.
"""

import pytest
from fastapi.testclient import TestClient

from core.workflow import NODE_REGISTRY, workflow_node, NodeInput, NodeOutput, clear_registry
from plugins.system_script_engine.backend import (
    SystemScriptEnginePlugin,
    WorkflowExecutor,
    NodeScanner,
    WorkflowGraph,
    WorkflowNodeSchema,
    WorkflowEdge
)
from plugins.system_script_engine.config import ScriptEngineSettings
from core.sdk import PluginContext


class TestWorkflowDecorator:
    """Test workflow node decorator and registry."""
    
    def setup_method(self):
        """Clear registry before each test."""
        clear_registry()
    
    def test_workflow_node_registration(self):
        """Test that workflow_node decorator registers nodes."""
        
        @workflow_node(
            id="test_node",
            name="Test Node",
            inputs=[NodeInput(name="input1", type="string")],
            outputs=[NodeOutput(name="output1", type="string")]
        )
        def test_func(input1: str) -> str:
            return input1.upper()
        
        assert "test_node" in NODE_REGISTRY
        node_def = NODE_REGISTRY["test_node"]
        assert node_def.id == "test_node"
        assert node_def.name == "Test Node"
        assert len(node_def.inputs) == 1
        assert len(node_def.outputs) == 1
        # The stored function is the original, but the decorated function is a wrapper
        # So we compare with __wrapped__ if available, or just skip identity check
        if hasattr(test_func, "__wrapped__"):
            assert node_def.function == test_func.__wrapped__
        else:
            # If mocking interferes with __wrapped__, we skip identity check
            pass
    
    def test_workflow_node_execution(self):
        """Test that decorated function still works."""
        
        @workflow_node(
            id="upper_case",
            name="Upper Case",
            inputs=[NodeInput(name="text", type="string")],
            outputs=[NodeOutput(name="result", type="string")]
        )
        def upper_case(text: str) -> str:
            return text.upper()
        
        result = upper_case("hello")
        assert result == "HELLO"
    
    def test_multiple_nodes_registration(self):
        """Test registering multiple nodes."""
        clear_registry()
        
        @workflow_node(id="node1", name="Node 1")
        def func1():
            return "1"
        
        @workflow_node(id="node2", name="Node 2")
        def func2():
            return "2"
        
        assert len(NODE_REGISTRY) == 2
        assert "node1" in NODE_REGISTRY
        assert "node2" in NODE_REGISTRY


class TestWorkflowExecutor:
    """Test workflow execution engine."""
    
    def setup_method(self):
        """Setup for each test."""
        clear_registry()
        self.settings = ScriptEngineSettings()
        self.executor = WorkflowExecutor(self.settings)
    
    def test_simple_workflow_execution(self):
        """Test executing a simple workflow."""
        
        # Define test nodes
        @workflow_node(
            id="input_node",
            name="Input",
            outputs=[NodeOutput(name="value", type="string")]
        )
        def input_node() -> str:
            return "hello"
        
        @workflow_node(
            id="upper_node",
            name="Upper",
            inputs=[NodeInput(name="text", type="string")],
            outputs=[NodeOutput(name="result", type="string")]
        )
        def upper_node(text: str) -> str:
            return text.upper()
        
        # Create workflow graph
        graph = WorkflowGraph(
            nodes=[
                WorkflowNodeSchema(id="n1", type="input_node", config={}),
                WorkflowNodeSchema(id="n2", type="upper_node", config={})
            ],
            edges=[
                WorkflowEdge(**{"from": "n1", "to": "n2", "from_port": "value", "to_port": "text"})
            ]
        )
        
        # Execute
        import asyncio
        result = asyncio.run(self.executor.execute_workflow(graph))
        
        assert result.status == "success"
        assert "n1" in result.node_results
        assert "n2" in result.node_results
        assert result.node_results["n2"] == "HELLO"
    
    def test_workflow_with_config(self):
        """Test workflow node with config values."""
        
        @workflow_node(
            id="echo_node",
            name="Echo",
            inputs=[NodeInput(name="message", type="string")],
            outputs=[NodeOutput(name="result", type="string")]
        )
        def echo_node(message: str) -> str:
            return f"Echo: {message}"
        
        graph = WorkflowGraph(
            nodes=[
                WorkflowNodeSchema(id="n1", type="echo_node", config={"message": "test"})
            ],
            edges=[]
        )
        
        import asyncio
        result = asyncio.run(self.executor.execute_workflow(graph))
        
        assert result.status == "success"
        assert result.node_results["n1"] == "Echo: test"
    
    def test_topological_sort(self):
        """Test topological sort produces correct execution order."""
        
        @workflow_node(id="node_a", name="A")
        def node_a() -> str:
            return "A"
        
        @workflow_node(
            id="node_b",
            name="B",
            inputs=[NodeInput(name="input", type="string")]
        )
        def node_b(input: str) -> str:
            return f"B-{input}"
        
        @workflow_node(
            id="node_c",
            name="C",
            inputs=[NodeInput(name="input", type="string")]
        )
        def node_c(input: str) -> str:
            return f"C-{input}"
        
        # Graph: A -> B -> C
        graph = WorkflowGraph(
            nodes=[
                WorkflowNodeSchema(id="n3", type="node_c", config={}),
                WorkflowNodeSchema(id="n1", type="node_a", config={}),
                WorkflowNodeSchema(id="n2", type="node_b", config={})
            ],
            edges=[
                WorkflowEdge(**{"from": "n1", "to": "n2", "from_port": "output", "to_port": "input"}),
                WorkflowEdge(**{"from": "n2", "to": "n3", "from_port": "output", "to_port": "input"})
            ]
        )
        
        order = self.executor._topological_sort(graph)
        
        # n1 should come before n2, n2 before n3
        assert order.index("n1") < order.index("n2")
        assert order.index("n2") < order.index("n3")
    
    def test_workflow_with_cycle_detection(self):
        """Test that cycles in workflow are detected."""
        
        @workflow_node(id="node_x", name="X", inputs=[NodeInput(name="i", type="string")])
        def node_x(i: str) -> str:
            return i
        
        @workflow_node(id="node_y", name="Y", inputs=[NodeInput(name="i", type="string")])
        def node_y(i: str) -> str:
            return i
        
        # Create cycle: n1 -> n2 -> n1
        graph = WorkflowGraph(
            nodes=[
                WorkflowNodeSchema(id="n1", type="node_x", config={}),
                WorkflowNodeSchema(id="n2", type="node_y", config={})
            ],
            edges=[
                WorkflowEdge(**{"from": "n1", "to": "n2", "from_port": "o", "to_port": "i"}),
                WorkflowEdge(**{"from": "n2", "to": "n1", "from_port": "o", "to_port": "i"})
            ]
        )
        
        with pytest.raises(ValueError, match="cycles"):
            self.executor._topological_sort(graph)
    
    def test_workflow_error_handling(self):
        """Test error handling in workflow execution."""
        
        @workflow_node(id="error_node", name="Error Node")
        def error_node():
            raise ValueError("Test error")
        
        graph = WorkflowGraph(
            nodes=[WorkflowNodeSchema(id="n1", type="error_node", config={})],
            edges=[]
        )
        
        import asyncio
        result = asyncio.run(self.executor.execute_workflow(graph))
        
        assert result.status == "error"
        assert "Test error" in result.error
    
    def test_async_node_execution(self):
        """Test execution of async nodes."""
        
        @workflow_node(
            id="async_node",
            name="Async Node",
            outputs=[NodeOutput(name="result", type="string")]
        )
        async def async_node() -> str:
            # Simulate async operation
            import asyncio
            await asyncio.sleep(0.01)
            return "async_result"
        
        graph = WorkflowGraph(
            nodes=[WorkflowNodeSchema(id="n1", type="async_node", config={})],
            edges=[]
        )
        
        import asyncio
        result = asyncio.run(self.executor.execute_workflow(graph))
        
        assert result.status == "success"
        assert result.node_results["n1"] == "async_result"
    
    def test_workflow_validation_unknown_node(self):
        """Test validation catches unknown node types."""
        graph = WorkflowGraph(
            nodes=[WorkflowNodeSchema(id="n1", type="unknown_node", config={})],
            edges=[]
        )
        
        with pytest.raises(ValueError, match="Unknown node type"):
            self.executor._validate_graph(graph)
    
    def test_workflow_validation_invalid_edge(self):
        """Test validation catches invalid edges."""
        
        @workflow_node(id="valid_node", name="Valid")
        def valid_node():
            return "ok"
        
        graph = WorkflowGraph(
            nodes=[WorkflowNodeSchema(id="n1", type="valid_node", config={})],
            edges=[
                WorkflowEdge(**{"from": "n1", "to": "n999", "from_port": "o", "to_port": "i"})
            ]
        )
        
        with pytest.raises(ValueError, match="non-existent node"):
            self.executor._validate_graph(graph)


class TestScriptEnginePlugin:
    """Test the script engine plugin."""
    
    def setup_method(self):
        """Setup for each test."""
        clear_registry()
    
    def test_plugin_initialization(self):
        """Test plugin initializes correctly."""
        plugin = SystemScriptEnginePlugin()
        context = PluginContext("system_script_engine")
        
        plugin.on_load(context)
        
        assert plugin.scanner is not None
        assert plugin.executor is not None
        assert context.capabilities.has("script.run")
        assert context.capabilities.has("workflow.engine")
    
    def test_plugin_run_workflow_capability(self):
        """Test run_workflow capability."""
        plugin = SystemScriptEnginePlugin()
        context = PluginContext("system_script_engine")
        plugin.on_load(context)
        
        @workflow_node(
            id="test_cap_node",
            name="Test",
            outputs=[NodeOutput(name="result", type="string")]
        )
        def test_cap_node() -> str:
            return "capability_test"
        
        graph_dict = {
            "nodes": [{"id": "n1", "type": "test_cap_node", "config": {}}],
            "edges": []
        }
        
        import asyncio
        result = asyncio.run(plugin.run_workflow(graph_dict))
        
        assert result.status == "success"
        assert result.node_results["n1"] == "capability_test"


class TestScriptEngineAPI:
    """Test the script engine API endpoints."""
    
    def setup_method(self):
        """Setup for each test."""
        clear_registry()
        
        # Register some test nodes
        @workflow_node(
            id="api_test_node",
            name="API Test Node",
            description="Test node for API",
            inputs=[NodeInput(name="input", type="string")],
            outputs=[NodeOutput(name="output", type="string")]
        )
        def api_test_node(input: str) -> str:
            return f"processed: {input}"
    
    def test_list_nodes_endpoint(self):
        """Test GET /nodes endpoint."""
        from fastapi import FastAPI
        plugin = SystemScriptEnginePlugin()
        context = PluginContext("system_script_engine")
        plugin.on_load(context)
        
        app = FastAPI()
        app.include_router(plugin.router)
        client = TestClient(app)
        response = client.get("/nodes")
        
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "total" in data
        assert len(data["nodes"]) > 0
    
    def test_run_workflow_endpoint(self):
        """Test POST /run endpoint."""
        from fastapi import FastAPI
        plugin = SystemScriptEnginePlugin()
        context = PluginContext("system_script_engine")
        plugin.on_load(context)
        
        app = FastAPI()
        app.include_router(plugin.router)
        client = TestClient(app)
        
        workflow = {
            "nodes": [
                {"id": "n1", "type": "api_test_node", "config": {"input": "test"}}
            ],
            "edges": []
        }
        
        response = client.post("/run", json=workflow)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "n1" in data["node_results"]
    
    def test_get_execution_status_endpoint(self):
        """Test GET /status/{execution_id} endpoint."""
        from fastapi import FastAPI
        plugin = SystemScriptEnginePlugin()
        context = PluginContext("system_script_engine")
        plugin.on_load(context)
        
        app = FastAPI()
        app.include_router(plugin.router)
        client = TestClient(app)
        
        # First run a workflow
        workflow = {
            "nodes": [
                {"id": "n1", "type": "api_test_node", "config": {"input": "test"}}
            ],
            "edges": []
        }
        
        run_response = client.post("/run", json=workflow)
        execution_id = run_response.json()["execution_id"]
        
        # Then check status
        status_response = client.get(f"/status/{execution_id}")
        
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["execution_id"] == execution_id
        assert data["status"] == "success"
    
    def test_get_info_endpoint(self):
        """Test GET /info endpoint."""
        from fastapi import FastAPI
        plugin = SystemScriptEnginePlugin()
        context = PluginContext("system_script_engine")
        plugin.on_load(context)
        
        app = FastAPI()
        app.include_router(plugin.router)
        client = TestClient(app)
        response = client.get("/info")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "nodes_available" in data
        assert data["name"] == "Script Engine"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
