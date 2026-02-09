"""Configuration for System LLM Plugin."""
from pydantic import BaseModel, Field
from core.sdk import PluginSettings


class LLMSettings(PluginSettings):
    """Settings for the LLM plugin."""
    
    # Embedding model configuration
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Name of the sentence-transformers model to use for embeddings"
    )
    
    embedding_dimension: int = Field(
        default=384,
        description="Dimension of the embedding vectors (384 for all-MiniLM-L6-v2)"
    )
    
    # Generation model configuration (for future use)
    generation_model: str = Field(
        default="mock",
        description="Model to use for text generation (mock, ollama, etc.)"
    )
    
    # Performance settings
    use_gpu: bool = Field(
        default=False,
        description="Use GPU acceleration if available"
    )
    
    max_batch_size: int = Field(
        default=32,
        description="Maximum batch size for embedding generation"
    )
