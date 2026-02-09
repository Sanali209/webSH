from typing import List, Dict, Callable, Any, Optional
from pydantic import BaseModel
import functools
import logging

logger = logging.getLogger(__name__)

class NodeInput(BaseModel):
    name: str
    type: str  # e.g., "string", "int", "list", "dict"
    description: str = ""

class NodeOutput(BaseModel):
    name: str
    type: str
    description: str = ""

class WorkflowNodeDefinition(BaseModel):
    id: str
    name: str
    description: str = ""
    inputs: List[NodeInput] = []
    outputs: List[NodeOutput] = []
    function: Callable[..., Any]

    class Config:
        arbitrary_types_allowed = True

# Global Registry
# Format: {node_id: WorkflowNodeDefinition}
NODE_REGISTRY: Dict[str, WorkflowNodeDefinition] = {}

def workflow_node(id: str, name: str, inputs: List[NodeInput] = None, outputs: List[NodeOutput] = None, description: str = ""):
    """
    Decorator to register a function as a workflow node.
    """
    def decorator(func: Callable[..., Any]):
        node_def = WorkflowNodeDefinition(
            id=id,
            name=name,
            description=description,
            inputs=inputs or [],
            outputs=outputs or [],
            function=func
        )

        if id in NODE_REGISTRY:
            logger.warning(f"Overwriting existing workflow node with id: {id}")

        NODE_REGISTRY[id] = node_def
        logger.debug(f"Registered workflow node: {id}")

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorator

def clear_registry():
    """Clear the node registry (useful for testing)."""
    global NODE_REGISTRY
    NODE_REGISTRY.clear()
