"""
Workflow nodes for LLM plugin.
"""

from typing import List

from core.workflow import workflow_node, NodeInput, NodeOutput


@workflow_node(
    id="llm_embed_text",
    name="Embed Text",
    description="Generate embeddings for text using LLM",
    inputs=[
        NodeInput(name="text", type="string", description="Text to embed")
    ],
    outputs=[
        NodeOutput(name="embedding", type="array", description="Text embedding vector")
    ]
)
def embed_text_node(text: str) -> List[float]:
    """Generate text embeddings."""
    # Import here to avoid circular dependency
    from plugins.system_llm.backend import EmbeddingsService
    
    service = EmbeddingsService()
    return service.embed_text(text)


@workflow_node(
    id="llm_text_length",
    name="Text Length",
    description="Count characters in text",
    inputs=[
        NodeInput(name="text", type="string", description="Input text")
    ],
    outputs=[
        NodeOutput(name="length", type="number", description="Character count")
    ]
)
def text_length(text: str) -> int:
    """Count text length."""
    return len(text)


@workflow_node(
    id="llm_concat_text",
    name="Concatenate Text",
    description="Combine two text strings",
    inputs=[
        NodeInput(name="text1", type="string", description="First text"),
        NodeInput(name="text2", type="string", description="Second text")
    ],
    outputs=[
        NodeOutput(name="result", type="string", description="Combined text")
    ]
)
def concat_text(text1: str, text2: str) -> str:
    """Concatenate two texts."""
    return text1 + text2
