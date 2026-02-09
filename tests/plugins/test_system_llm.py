"""Tests for System LLM Plugin."""
import pytest
from plugins.system_llm.backend import SystemLLMPlugin, EmbeddingsService
from plugins.system_llm.config import LLMSettings
from core.sdk import PluginContext


class TestEmbeddingsService:
    """Test the EmbeddingsService class."""
    
    def test_embed_text_returns_correct_dimension(self):
        """Test that embed_text returns a vector of the correct dimension."""
        settings = LLMSettings()
        service = EmbeddingsService(settings)
        
        text = "Hello, world!"
        embedding = service.embed_text(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == settings.embedding_dimension
        assert all(isinstance(x, float) for x in embedding)
    
    def test_embed_text_deterministic(self):
        """Test that the same text produces the same embedding."""
        settings = LLMSettings()
        service = EmbeddingsService(settings)
        
        text = "Test text for deterministic embeddings"
        embedding1 = service.embed_text(text)
        embedding2 = service.embed_text(text)
        
        assert embedding1 == embedding2
    
    def test_embed_text_different_for_different_texts(self):
        """Test that different texts produce different embeddings."""
        settings = LLMSettings()
        service = EmbeddingsService(settings)
        
        text1 = "First test text"
        text2 = "Second test text"
        
        embedding1 = service.embed_text(text1)
        embedding2 = service.embed_text(text2)
        
        assert embedding1 != embedding2
    
    def test_embed_text_empty_raises_error(self):
        """Test that empty text raises ValueError."""
        settings = LLMSettings()
        service = EmbeddingsService(settings)
        
        with pytest.raises(ValueError, match="Text cannot be empty"):
            service.embed_text("")
        
        with pytest.raises(ValueError, match="Text cannot be empty"):
            service.embed_text("   ")
    
    def test_embed_text_normalized_values(self):
        """Test that embedding values are in expected range."""
        settings = LLMSettings()
        service = EmbeddingsService(settings)
        
        text = "Test normalization"
        embedding = service.embed_text(text)
        
        # All values should be in [-1, 1] range for normalized embeddings
        assert all(-1.0 <= x <= 1.0 for x in embedding)
    
    def test_embed_image_not_implemented(self):
        """Test that image embedding raises NotImplementedError."""
        settings = LLMSettings()
        service = EmbeddingsService(settings)
        
        with pytest.raises(NotImplementedError):
            service.embed_image("/path/to/image.jpg")


class TestSystemLLMPlugin:
    """Test the SystemLLMPlugin class."""
    
    def test_plugin_initialization(self):
        """Test that the plugin initializes correctly."""
        plugin = SystemLLMPlugin()
        
        assert plugin.settings is not None
        assert isinstance(plugin.settings, LLMSettings)
        assert plugin.router is not None
    
    def test_plugin_on_load_initializes_service(self):
        """Test that on_load initializes the embeddings service."""
        plugin = SystemLLMPlugin()
        context = PluginContext("system_llm")
        
        assert plugin.embeddings_service is None
        
        plugin.on_load(context)
        
        assert plugin.embeddings_service is not None
        assert isinstance(plugin.embeddings_service, EmbeddingsService)
    
    def test_plugin_registers_capabilities(self):
        """Test that the plugin registers its capabilities."""
        plugin = SystemLLMPlugin()
        context = PluginContext("system_llm")
        
        plugin.on_load(context)
        
        # Check that capabilities are registered
        assert context.capabilities.has("llm.embed")
        assert context.capabilities.has("llm.generate")
        
        # Verify we can get the capabilities
        embed_capability = context.capabilities.get("llm.embed")
        assert embed_capability is not None
        assert callable(embed_capability)
    
    def test_capability_can_be_called(self):
        """Test that registered capability can be called."""
        plugin = SystemLLMPlugin()
        context = PluginContext("system_llm")
        
        plugin.on_load(context)
        
        # Get and call the embed capability
        embed_func = context.capabilities.get("llm.embed")
        result = embed_func("Test text for capability")
        
        assert isinstance(result, list)
        assert len(result) == plugin.settings.embedding_dimension
    
    def test_multiple_plugins_share_capabilities(self):
        """Test that capabilities are shared across plugin contexts."""
        plugin = SystemLLMPlugin()
        context1 = PluginContext("system_llm")
        context2 = PluginContext("other_plugin")
        
        # Load plugin with context1
        plugin.on_load(context1)
        
        # context2 should also be able to access the capability
        # because capabilities are shared at the class level
        assert context2.capabilities.has("llm.embed")
        
        embed_func = context2.capabilities.get("llm.embed")
        result = embed_func("Test from other plugin")
        
        assert isinstance(result, list)
        assert len(result) > 0


class TestCapabilityIntegration:
    """Test capability system integration."""
    
    def test_capability_registry_basic_operations(self):
        """Test basic capability registry operations."""
        from core.sdk import CapabilityRegistry
        
        registry = CapabilityRegistry()
        
        # Test registration
        def test_func(x):
            return x * 2
        
        registry.register("test.capability", test_func)
        
        # Test retrieval
        assert registry.has("test.capability")
        func = registry.get("test.capability")
        assert func is not None
        assert func(5) == 10
        
        # Test listing
        capabilities = registry.list_all()
        assert "test.capability" in capabilities
    
    def test_simulated_cross_plugin_usage(self):
        """Simulate one plugin using another plugin's capability."""
        # Plugin 1 (System LLM) registers capability
        llm_plugin = SystemLLMPlugin()
        llm_context = PluginContext("system_llm")
        llm_plugin.on_load(llm_context)
        
        # Plugin 2 (simulated) uses the capability
        consumer_context = PluginContext("consumer_plugin")
        
        # Consumer plugin can access LLM capabilities
        if consumer_context.capabilities.has("llm.embed"):
            embed_func = consumer_context.capabilities.get("llm.embed")
            
            # Use the embedding capability
            result = embed_func("Text from consumer plugin")
            
            assert isinstance(result, list)
            assert len(result) == 384  # Default dimension
        else:
            pytest.fail("Capability not found by consumer plugin")


@pytest.mark.asyncio
class TestLLMPluginAPI:
    """Test the API endpoints of the LLM plugin."""
    
    async def test_embed_endpoint_success(self):
        """Test successful embedding via API endpoint."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        plugin = SystemLLMPlugin()
        context = PluginContext("system_llm")
        plugin.on_load(context)
        
        # Create test app
        app = FastAPI()
        app.include_router(plugin.router, prefix="/api/plugins/system_llm")
        
        client = TestClient(app)
        
        # Test the embed endpoint
        response = client.post(
            "/api/plugins/system_llm/embed",
            json={"text": "Hello, world!"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "embedding" in data
        assert "dimension" in data
        assert "model" in data
        assert isinstance(data["embedding"], list)
        assert data["dimension"] == 384
    
    async def test_embed_endpoint_empty_text(self):
        """Test embed endpoint with empty text."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        plugin = SystemLLMPlugin()
        context = PluginContext("system_llm")
        plugin.on_load(context)
        
        app = FastAPI()
        app.include_router(plugin.router, prefix="/api/plugins/system_llm")
        
        client = TestClient(app)
        
        response = client.post(
            "/api/plugins/system_llm/embed",
            json={"text": ""}
        )
        
        assert response.status_code == 400
    
    async def test_info_endpoint(self):
        """Test the info endpoint."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        plugin = SystemLLMPlugin()
        context = PluginContext("system_llm")
        plugin.on_load(context)
        
        app = FastAPI()
        app.include_router(plugin.router, prefix="/api/plugins/system_llm")
        
        client = TestClient(app)
        
        response = client.get("/api/plugins/system_llm/info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "model" in data
        assert "dimension" in data
        assert "capabilities" in data
        assert "status" in data
        assert data["status"] == "active"
