"""Tests for Web Parser Plugin."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from plugins.web_parser.backend import (
    WebParserPlugin,
    WebCrawler,
    SearchResult
)
from plugins.web_parser.config import WebParserSettings
from core.sdk import PluginContext


# Sample HTML for testing
SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <script>console.log('test');</script>
</head>
<body>
    <h1>Welcome to Test Page</h1>
    <p>This is a test paragraph with some content.</p>
    <a href="https://example.com/page1">Link 1</a>
    <a href="https://example.com/page2">Link 2</a>
    <style>body { color: black; }</style>
</body>
</html>
"""


class TestWebCrawler:
    """Test the WebCrawler class."""
    
    def test_parse_html_extracts_title(self):
        """Test that HTML parsing extracts the title correctly."""
        settings = WebParserSettings()
        crawler = WebCrawler(settings)
        
        parsed = crawler.parse_html(SAMPLE_HTML, "https://example.com")
        
        assert parsed["title"] == "Test Page"
    
    def test_parse_html_extracts_text(self):
        """Test that HTML parsing extracts text content."""
        settings = WebParserSettings()
        crawler = WebCrawler(settings)
        
        parsed = crawler.parse_html(SAMPLE_HTML, "https://example.com")
        
        assert "Welcome to Test Page" in parsed["text"]
        assert "test paragraph" in parsed["text"]
        # Script content should not be in text
        assert "console.log" not in parsed["text"]
        # Style content should not be in text
        assert "color: black" not in parsed["text"]
    
    def test_parse_html_extracts_links(self):
        """Test that HTML parsing extracts links."""
        settings = WebParserSettings(extract_links=True)
        crawler = WebCrawler(settings)
        
        parsed = crawler.parse_html(SAMPLE_HTML, "https://example.com")
        
        assert "https://example.com/page1" in parsed["links"]
        assert "https://example.com/page2" in parsed["links"]
        assert len(parsed["links"]) == 2
    
    def test_parse_html_no_links_when_disabled(self):
        """Test that links are not extracted when disabled."""
        settings = WebParserSettings(extract_links=False)
        crawler = WebCrawler(settings)
        
        parsed = crawler.parse_html(SAMPLE_HTML, "https://example.com")
        
        assert parsed["links"] == []
    
    def test_parse_html_limits_text_length(self):
        """Test that text is limited to max_text_length."""
        long_text = "a" * 100000
        html = f"<html><body><p>{long_text}</p></body></html>"
        
        settings = WebParserSettings(max_text_length=1000)
        crawler = WebCrawler(settings)
        
        parsed = crawler.parse_html(html, "https://example.com")
        
        assert len(parsed["text"]) <= 1000
    
    def test_parse_html_strips_unwanted_tags(self):
        """Test that unwanted tags are removed."""
        settings = WebParserSettings()
        crawler = WebCrawler(settings)
        
        parsed = crawler.parse_html(SAMPLE_HTML, "https://example.com")
        
        # Script and style content should be removed
        assert "console.log" not in parsed["text"]
        assert "color: black" not in parsed["text"]
    
    def test_parse_html_handles_no_title(self):
        """Test parsing HTML without a title tag."""
        html = "<html><body><p>Content without title</p></body></html>"
        settings = WebParserSettings()
        crawler = WebCrawler(settings)
        
        parsed = crawler.parse_html(html, "https://example.com")
        
        # Should use domain as fallback
        assert "example.com" in parsed["title"]
    
    @pytest.mark.asyncio
    async def test_fetch_url_success(self):
        """Test successful URL fetching."""
        settings = WebParserSettings()
        crawler = WebCrawler(settings)
        
        # Mock httpx client
        mock_response = Mock()
        mock_response.text = SAMPLE_HTML
        mock_response.content = SAMPLE_HTML.encode()
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        
        crawler.client = mock_client
        
        html = await crawler.fetch_url("https://example.com")
        
        assert html == SAMPLE_HTML
        mock_client.get.assert_called_once_with("https://example.com")
    
    @pytest.mark.asyncio
    async def test_fetch_url_too_large(self):
        """Test that oversized content is rejected."""
        settings = WebParserSettings(max_content_length=100)
        crawler = WebCrawler(settings)
        
        # Mock httpx client with large response
        large_content = "a" * 1000
        mock_response = Mock()
        mock_response.text = large_content
        mock_response.content = large_content.encode()
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        
        crawler.client = mock_client
        
        html = await crawler.fetch_url("https://example.com")
        
        # Should return None for oversized content
        assert html is None


class TestWebParserPlugin:
    """Test the WebParserPlugin class."""
    
    def test_plugin_initialization(self):
        """Test that the plugin initializes correctly."""
        plugin = WebParserPlugin()
        
        assert plugin.settings is not None
        assert isinstance(plugin.settings, WebParserSettings)
        assert plugin.router is not None
        assert plugin.crawler is None  # Not initialized until on_load
    
    def test_plugin_on_load_initializes_crawler(self):
        """Test that on_load initializes the crawler."""
        plugin = WebParserPlugin()
        context = PluginContext("web_parser")
        
        assert plugin.crawler is None
        
        plugin.on_load(context)
        
        assert plugin.crawler is not None
        assert isinstance(plugin.crawler, WebCrawler)
    
    def test_plugin_registers_capabilities(self):
        """Test that the plugin registers its capabilities."""
        plugin = WebParserPlugin()
        context = PluginContext("web_parser")
        
        # Mock embedding function
        context.capabilities.register("llm.embed", lambda x: [0.1] * 384)
        
        plugin.on_load(context)
        
        # Check that capabilities are registered
        assert context.capabilities.has("searcher.web")
        assert context.capabilities.has("parser.web")
        
        # Verify capabilities are callable
        search_web = context.capabilities.get("searcher.web")
        parse_web = context.capabilities.get("parser.web")
        
        assert callable(search_web)
        assert callable(parse_web)
    
    def test_plugin_uses_llm_embedding(self):
        """Test that plugin uses LLM embedding capability."""
        plugin = WebParserPlugin()
        context = PluginContext("web_parser")
        
        # Mock embedding function
        embed_calls = []
        def mock_embed(text):
            embed_calls.append(text)
            return [0.1] * 384
        
        context.capabilities.register("llm.embed", mock_embed)
        
        plugin.on_load(context)
        
        assert plugin._embed_func is not None
    
    def test_cosine_similarity_identical_vectors(self):
        """Test cosine similarity with identical vectors."""
        plugin = WebParserPlugin()
        
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [1.0, 2.0, 3.0]
        
        similarity = plugin._cosine_similarity(vec1, vec2)
        
        # Identical vectors should have similarity close to 1.0
        assert similarity > 0.99
    
    def test_cosine_similarity_orthogonal_vectors(self):
        """Test cosine similarity with orthogonal vectors."""
        plugin = WebParserPlugin()
        
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        
        similarity = plugin._cosine_similarity(vec1, vec2)
        
        # Orthogonal vectors should have similarity close to 0.5
        assert 0.4 < similarity < 0.6
    
    def test_cosine_similarity_opposite_vectors(self):
        """Test cosine similarity with opposite vectors."""
        plugin = WebParserPlugin()
        
        vec1 = [1.0, 1.0, 1.0]
        vec2 = [-1.0, -1.0, -1.0]
        
        similarity = plugin._cosine_similarity(vec1, vec2)
        
        # Opposite vectors should have similarity close to 0.0
        assert similarity < 0.1
    
    def test_cosine_similarity_different_lengths(self):
        """Test cosine similarity with different length vectors."""
        plugin = WebParserPlugin()
        
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [1.0, 2.0]
        
        similarity = plugin._cosine_similarity(vec1, vec2)
        
        # Different lengths should return 0
        assert similarity == 0.0
    
    def test_search_with_embeddings(self):
        """Test search functionality with embeddings."""
        plugin = WebParserPlugin()
        context = PluginContext("web_parser")
        
        # Mock embedding function
        def mock_embed(text):
            # Return different embeddings based on text
            if "machine learning" in text.lower():
                return [1.0, 0.0, 0.0]
            elif "data science" in text.lower():
                return [0.9, 0.1, 0.0]
            else:
                return [0.0, 0.0, 1.0]
        
        context.capabilities.register("llm.embed", mock_embed)
        plugin.on_load(context)
        
        # Add some pages
        plugin._pages["https://example.com/ml"] = {
            "title": "Machine Learning Guide",
            "text": "This is a guide about machine learning",
            "text_length": 42,
            "embedding": [1.0, 0.0, 0.0],
            "links": [],
            "parsed_at": "2024-01-01T00:00:00",
            "status": "parsed"
        }
        
        plugin._pages["https://example.com/ds"] = {
            "title": "Data Science Tutorial",
            "text": "This is a tutorial about data science",
            "text_length": 37,
            "embedding": [0.9, 0.1, 0.0],
            "links": [],
            "parsed_at": "2024-01-01T00:00:00",
            "status": "parsed"
        }
        
        # Test search via capability
        search_func = context.capabilities.get("searcher.web")
        results = search_func("machine learning", limit=10)
        
        assert len(results) > 0
        # ML page should be first due to higher similarity
        assert results[0]["url"] == "https://example.com/ml"


@pytest.mark.asyncio
class TestWebParserAPI:
    """Test the API endpoints of the Web Parser plugin."""
    
    async def test_info_endpoint(self):
        """Test the /info endpoint."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        plugin = WebParserPlugin()
        context = PluginContext("web_parser")
        plugin.on_load(context)
        
        app = FastAPI()
        app.include_router(plugin.router, prefix="/api/plugins/web_parser")
        
        client = TestClient(app)
        
        response = client.get("/api/plugins/web_parser/info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Web Parser"
        assert data["version"] == "0.1.0"
        assert data["type"] == "utility"
        assert data["status"] == "active"
        assert "capabilities" in data
        assert "settings" in data
        assert "stats" in data
    
    async def test_list_pages_endpoint_empty(self):
        """Test the /pages endpoint with no pages."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        plugin = WebParserPlugin()
        context = PluginContext("web_parser")
        plugin.on_load(context)
        
        app = FastAPI()
        app.include_router(plugin.router, prefix="/api/plugins/web_parser")
        
        client = TestClient(app)
        
        response = client.get("/api/plugins/web_parser/pages")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 0
    
    async def test_list_pages_endpoint_with_pages(self):
        """Test the /pages endpoint with parsed pages."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        plugin = WebParserPlugin()
        context = PluginContext("web_parser")
        plugin.on_load(context)
        
        # Add a page manually
        plugin._pages["https://example.com"] = {
            "title": "Example Page",
            "text": "Test content",
            "text_length": 12,
            "embedding": [],
            "links": [],
            "parsed_at": "2024-01-01T00:00:00",
            "status": "parsed"
        }
        
        app = FastAPI()
        app.include_router(plugin.router, prefix="/api/plugins/web_parser")
        
        client = TestClient(app)
        
        response = client.get("/api/plugins/web_parser/pages")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 1
        assert data[0]["url"] == "https://example.com"
        assert data[0]["title"] == "Example Page"
    
    async def test_search_endpoint_no_embedding(self):
        """Test search endpoint without embedding function."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        plugin = WebParserPlugin()
        context = PluginContext("web_parser")
        plugin.on_load(context)
        
        # Ensure no embedding function
        plugin._embed_func = None
        
        app = FastAPI()
        app.include_router(plugin.router, prefix="/api/plugins/web_parser")
        
        client = TestClient(app)
        
        response = client.get("/api/plugins/web_parser/search?q=test")
        
        assert response.status_code == 503
    
    async def test_search_endpoint_with_results(self):
        """Test search endpoint with results."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        plugin = WebParserPlugin()
        context = PluginContext("web_parser")
        
        # Mock embedding function
        def mock_embed(text):
            return [1.0, 0.0, 0.0]
        
        context.capabilities.register("llm.embed", mock_embed)
        plugin.on_load(context)
        
        # Add a page
        plugin._pages["https://example.com"] = {
            "title": "Test Page",
            "text": "This is test content about machine learning",
            "text_length": 44,
            "embedding": [1.0, 0.0, 0.0],
            "links": [],
            "parsed_at": "2024-01-01T00:00:00",
            "status": "parsed"
        }
        
        app = FastAPI()
        app.include_router(plugin.router, prefix="/api/plugins/web_parser")
        
        client = TestClient(app)
        
        response = client.get("/api/plugins/web_parser/search?q=machine+learning")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["query"] == "machine learning"
        assert data["total_results"] > 0
        assert len(data["results"]) > 0
        assert data["results"][0]["url"] == "https://example.com"
