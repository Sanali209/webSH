"""System LLM Plugin Backend - Provides embeddings and text generation."""
import logging
import hashlib
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.sdk import PluginBase, PluginContext
from .config import LLMSettings

logger = logging.getLogger(__name__)


# Request/Response models
class EmbedRequest(BaseModel):
    """Request model for embedding generation."""
    text: str
    
class EmbedResponse(BaseModel):
    """Response model for embedding generation."""
    embedding: List[float]
    dimension: int
    model: str


class EmbeddingsService:
    """
    Service for generating text embeddings.
    
    For MVP, uses a deterministic mock implementation.
    In production, this would use sentence-transformers or similar.
    """
    
    def __init__(self, settings: LLMSettings):
        self.settings = settings
        self.model_name = settings.embedding_model
        self.dimension = settings.embedding_dimension
        logger.info(f"Initialized EmbeddingsService with model: {self.model_name}, dimension: {self.dimension}")
        
        # In a real implementation, we would load the model here:
        # from sentence_transformers import SentenceTransformer
        # self.model = SentenceTransformer(self.model_name)
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embeddings for the given text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # For MVP: Generate deterministic mock embeddings based on text hash
        # This ensures consistent embeddings for the same text
        text_hash = hashlib.sha256(text.encode()).digest()
        
        # Convert hash bytes to normalized float values
        embedding = []
        for i in range(self.dimension):
            # Take bytes from hash cyclically
            byte_value = text_hash[i % len(text_hash)]
            # Normalize to [-1, 1] range
            normalized_value = (byte_value / 255.0) * 2 - 1
            embedding.append(normalized_value)
        
        logger.debug(f"Generated mock embedding for text: '{text[:50]}...' (dimension: {len(embedding)})")
        
        # TODO: Replace with real model when sentence-transformers is added:
        # embedding = self.model.encode(text).tolist()
        
        return embedding
    
    def embed_image(self, image_path: str) -> List[float]:
        """
        Generate embeddings for an image (optional, for future use).
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of floats representing the embedding vector
        """
        # For MVP, not implemented
        raise NotImplementedError("Image embeddings not yet implemented")


class SystemLLMPlugin(PluginBase):
    """
    System LLM Plugin that provides embedding and generation capabilities.
    """
    
    def __init__(self):
        self.settings = LLMSettings()
        self.embeddings_service: Optional[EmbeddingsService] = None
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes for the plugin."""
        
        @self.router.post("/embed", response_model=EmbedResponse)
        async def embed_text(request: EmbedRequest):
            """
            Generate embeddings for the given text.
            
            Example:
                POST /api/plugins/system_llm/embed
                {"text": "Hello, world!"}
            """
            if not self.embeddings_service:
                raise HTTPException(status_code=503, detail="Embeddings service not initialized")
            
            try:
                embedding = self.embeddings_service.embed_text(request.text)
                return EmbedResponse(
                    embedding=embedding,
                    dimension=len(embedding),
                    model=self.embeddings_service.model_name
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"Error generating embedding: {e}")
                raise HTTPException(status_code=500, detail="Failed to generate embedding")
        
        @self.router.get("/info")
        async def get_info():
            """Get information about the LLM plugin."""
            return {
                "model": self.settings.embedding_model,
                "dimension": self.settings.embedding_dimension,
                "capabilities": ["llm.embed", "llm.generate"],
                "status": "active" if self.embeddings_service else "inactive"
            }
    
    def on_load(self, context: PluginContext) -> None:
        """
        Called when the plugin is loaded.
        Initializes the embeddings service and registers capabilities.
        """
        logger.info("Loading System LLM Plugin...")
        
        # Initialize embeddings service
        self.embeddings_service = EmbeddingsService(self.settings)
        
        # Register capabilities for other plugins to use
        context.capabilities.register("llm.embed", self.embeddings_service.embed_text)
        
        # Register generation capability (mock for now)
        def generate_text(prompt: str, max_length: int = 100) -> str:
            """Mock text generation (to be implemented with real LLM)."""
            return f"[Mock Response to: {prompt[:50]}...]"
        
        context.capabilities.register("llm.generate", generate_text)
        
        logger.info("System LLM Plugin loaded successfully")
        logger.info(f"Registered capabilities: {context.capabilities.list_all()}")
    
    def on_activate(self) -> None:
        """Called when the plugin is activated."""
        logger.info("System LLM Plugin activated")
    
    def on_deactivate(self) -> None:
        """Called when the plugin is deactivated."""
        logger.info("System LLM Plugin deactivated")
