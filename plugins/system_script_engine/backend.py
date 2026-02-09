"""
Script Engine Plugin Backend.

Implements workflow execution engine with node discovery and graph execution.
"""

import asyncio
import importlib
import logging
import time
import uuid
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core.sdk import PluginBase, PluginContext
from core.workflow import NODE_REGISTRY, WorkflowNodeDefinition
from .config import ScriptEngineSettings

logger = logging.getLogger(__name__)


# Pydantic models for API
class WorkflowNodeSchema(BaseModel):
    """Schema for a node in the workflow graph."""
    id: str = Field(..., description="Unique node instance ID")
    type: str = Field(..., description="Node type (references registered node)")
    config: Dict[str, Any] = Field(default_factory=dict, description="Node configuration")
    position: Optional[Dict[str, float]] = Field(None, description="Position in visual editor")


class WorkflowEdge(BaseModel):
    """Schema for an edge connecting two nodes."""
    from_node: str = Field(..., alias="from", description="Source node ID")
    to_node: str = Field(..., alias="to", description="Target node ID")
    from_port: str = Field(..., description="Source output port")
    to_port: str = Field(..., description="Target input port")


class WorkflowGraph(BaseModel):
    """Schema for a complete workflow graph."""
    name: Optional[str] = Field(None, description="Workflow name")
    nodes: List[WorkflowNodeSchema] = Field(..., description="List of nodes")
    edges: List[WorkflowEdge] = Field(..., description="List of edges")


class ExecutionResult(BaseModel):
    """Result of workflow execution."""
    execution_id: str
    status: str  # "success", "error", "running"
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    node_results: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class NodeScanner:
    """Scans plugins for workflow nodes and builds catalog."""
    
    def __init__(self, plugins_dir: Path):
        self.plugins_dir = plugins_dir
        self.scanned_modules: Set[str] = set()
    
    def scan_all_plugins(self) -> Dict[str, WorkflowNodeDefinition]:
        """Scan all plugins for workflow.py modules and import them."""
        logger.info(f"Scanning for workflow nodes in {self.plugins_dir}")
        
        for plugin_dir in self.plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue
            
            workflow_file = plugin_dir / "workflow.py"
            if workflow_file.exists():
                self._import_workflow_module(plugin_dir.name)
        
        logger.info(f"Found {len(NODE_REGISTRY)} workflow nodes")
        return NODE_REGISTRY
    
    def _import_workflow_module(self, plugin_name: str):
        """Import a plugin's workflow module to trigger decorator registration."""
        module_name = f"plugins.{plugin_name}.workflow"
        
        if module_name in self.scanned_modules:
            return
        
        try:
            logger.debug(f"Importing workflow module: {module_name}")
            importlib.import_module(module_name)
            self.scanned_modules.add(module_name)
            logger.info(f"Loaded workflow nodes from {plugin_name}")
        except ImportError as e:
            logger.warning(f"Could not import {module_name}: {e}")
        except Exception as e:
            logger.error(f"Error loading workflow nodes from {plugin_name}: {e}")


class WorkflowExecutor:
    """Executes workflow graphs with topological sorting and data flow."""
    
    def __init__(self, settings: ScriptEngineSettings):
        self.settings = settings
        self.executions: Dict[str, ExecutionResult] = {}
    
    async def execute_workflow(self, graph: WorkflowGraph) -> ExecutionResult:
        """Execute a workflow graph."""
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        result = ExecutionResult(
            execution_id=execution_id,
            status="running",
            start_time=start_time
        )
        self.executions[execution_id] = result
        
        try:
            # Validate workflow
            self._validate_graph(graph)
            
            # Build execution order using topological sort
            execution_order = self._topological_sort(graph)
            
            # Execute nodes in order
            node_results = {}
            for node_id in execution_order:
                node_result = await self._execute_node(node_id, graph, node_results)
                node_results[node_id] = node_result
            
            # Success
            result.status = "success"
            result.node_results = node_results
            result.end_time = time.time()
            result.duration = result.end_time - start_time
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            result.status = "error"
            result.error = str(e)
            result.end_time = time.time()
            result.duration = result.end_time - start_time
        
        return result
    
    def _validate_graph(self, graph: WorkflowGraph):
        """Validate workflow graph."""
        if len(graph.nodes) == 0:
            raise ValueError("Workflow must have at least one node")
        
        if len(graph.nodes) > self.settings.max_workflow_nodes:
            raise ValueError(f"Workflow exceeds maximum nodes ({self.settings.max_workflow_nodes})")
        
        # Check all node types exist
        node_map = {node.id: node for node in graph.nodes}
        for node in graph.nodes:
            if node.type not in NODE_REGISTRY:
                raise ValueError(f"Unknown node type: {node.type}")
        
        # Check all edges reference valid nodes
        for edge in graph.edges:
            if edge.from_node not in node_map:
                raise ValueError(f"Edge references non-existent node: {edge.from_node}")
            if edge.to_node not in node_map:
                raise ValueError(f"Edge references non-existent node: {edge.to_node}")
    
    def _topological_sort(self, graph: WorkflowGraph) -> List[str]:
        """
        Perform topological sort to determine execution order.
        Uses Kahn's algorithm.
        """
        # Build adjacency list and in-degree map
        adjacency: Dict[str, List[str]] = defaultdict(list)
        in_degree: Dict[str, int] = defaultdict(int)
        
        # Initialize all nodes with 0 in-degree
        for node in graph.nodes:
            in_degree[node.id] = 0
        
        # Build graph
        for edge in graph.edges:
            adjacency[edge.from_node].append(edge.to_node)
            in_degree[edge.to_node] += 1
        
        # Find nodes with no incoming edges
        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        execution_order = []
        
        while queue:
            node_id = queue.popleft()
            execution_order.append(node_id)
            
            # Reduce in-degree for neighbors
            for neighbor in adjacency[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles
        if len(execution_order) != len(graph.nodes):
            raise ValueError("Workflow contains cycles - cannot execute")
        
        return execution_order
    
    async def _execute_node(
        self,
        node_id: str,
        graph: WorkflowGraph,
        previous_results: Dict[str, Any]
    ) -> Any:
        """Execute a single node."""
        # Find node definition
        node_instance = next(n for n in graph.nodes if n.id == node_id)
        node_def = NODE_REGISTRY.get(node_instance.type)
        
        if not node_def:
            raise ValueError(f"Node type not found: {node_instance.type}")
        
        # Gather inputs from previous nodes
        inputs = self._gather_inputs(node_id, graph, previous_results, node_instance)
        
        # Execute node function
        logger.debug(f"Executing node {node_id} (type: {node_instance.type})")
        func = node_def.function
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(**inputs)
            else:
                result = func(**inputs)
            
            return result
        except Exception as e:
            logger.error(f"Node {node_id} execution failed: {e}")
            raise RuntimeError(f"Node {node_id} failed: {e}")
    
    def _gather_inputs(
        self,
        node_id: str,
        graph: WorkflowGraph,
        previous_results: Dict[str, Any],
        node_instance: WorkflowNodeSchema
    ) -> Dict[str, Any]:
        """Gather inputs for a node from previous nodes and config."""
        inputs = {}
        
        # Start with config values
        inputs.update(node_instance.config)
        
        # Add values from incoming edges
        for edge in graph.edges:
            if edge.to_node == node_id:
                source_result = previous_results.get(edge.from_node)
                if source_result is not None:
                    # If result is a dict, use the specific port value
                    if isinstance(source_result, dict) and edge.from_port in source_result:
                        inputs[edge.to_port] = source_result[edge.from_port]
                    else:
                        # Otherwise use the entire result
                        inputs[edge.to_port] = source_result
        
        return inputs
    
    def get_execution(self, execution_id: str) -> Optional[ExecutionResult]:
        """Get execution result by ID."""
        return self.executions.get(execution_id)


class SystemScriptEnginePlugin(PluginBase):
    """System Script Engine plugin for workflow automation."""
    
    def __init__(self):
        super().__init__()
        self.settings = ScriptEngineSettings()
        self.scanner: Optional[NodeScanner] = None
        self.executor: Optional[WorkflowExecutor] = None
        self.router = APIRouter()
        self._setup_routes()
    
    def on_load(self, context: PluginContext):
        """Called when plugin is loaded."""
        logger.info("Loading System Script Engine plugin")
        
        # Initialize scanner and scan for workflow nodes
        plugins_dir = Path(__file__).parent.parent
        self.scanner = NodeScanner(plugins_dir)
        self.scanner.scan_all_plugins()
        
        # Initialize executor
        self.executor = WorkflowExecutor(self.settings)
        
        # Register capabilities
        context.capabilities.register("script.run", self.run_workflow)
        context.capabilities.register("workflow.engine", self.get_executor)
        
        logger.info(f"Script Engine loaded with {len(NODE_REGISTRY)} nodes")
    
    def on_activate(self):
        """Called when plugin is activated."""
        logger.info("Script Engine plugin activated")
    
    def on_deactivate(self):
        """Called when plugin is deactivated."""
        logger.info("Script Engine plugin deactivated")
    
    async def run_workflow(self, graph: Dict[str, Any]) -> ExecutionResult:
        """Run a workflow graph (capability function)."""
        workflow = WorkflowGraph(**graph)
        return await self.executor.execute_workflow(workflow)
    
    def get_executor(self) -> WorkflowExecutor:
        """Get the workflow executor (capability function)."""
        return self.executor
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.router.get("/nodes")
        async def list_nodes():
            """Get all available workflow nodes."""
            nodes = []
            for node_id, node_def in NODE_REGISTRY.items():
                nodes.append({
                    "id": node_def.id,
                    "name": node_def.name,
                    "description": node_def.description,
                    "inputs": [inp.dict() for inp in node_def.inputs],
                    "outputs": [out.dict() for out in node_def.outputs]
                })
            return {"nodes": nodes, "total": len(nodes)}
        
        @self.router.post("/run")
        async def run_workflow(graph: WorkflowGraph):
            """Execute a workflow graph."""
            if not self.executor:
                raise HTTPException(status_code=500, detail="Executor not initialized")
            
            result = await self.executor.execute_workflow(graph)
            return result.dict()
        
        @self.router.get("/status/{execution_id}")
        async def get_execution_status(execution_id: str):
            """Get execution status."""
            if not self.executor:
                raise HTTPException(status_code=500, detail="Executor not initialized")
            
            result = self.executor.get_execution(execution_id)
            if not result:
                raise HTTPException(status_code=404, detail="Execution not found")
            
            return result.dict()
        
        @self.router.get("/info")
        async def get_info():
            """Get plugin information."""
            return {
                "name": "Script Engine",
                "version": "1.0.0",
                "nodes_available": len(NODE_REGISTRY),
                "settings": self.settings.dict()
            }
