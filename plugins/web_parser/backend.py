"""Web Parser Plugin Backend - Crawl, parse, and search web content."""
import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
import httpx
from bs4 import BeautifulSoup

from core.sdk import PluginBase, PluginContext
from .config import WebParserSettings

logger = logging.getLogger(__name__)


# Request/Response models
class ParseRequest(BaseModel):
    """Request model for parsing a URL."""
    url: HttpUrl
    force_refresh: bool = False


class ParseBatchRequest(BaseModel):
    """Request model for parsing multiple URLs."""
    urls: List[HttpUrl]
    force_refresh: bool = False


class ParseResponse(BaseModel):
    """Response model for parse operation."""
    url: str
    title: str
    status: str  # "parsed", "error", "cached"
    text_length: int
    embedding_dimension: Optional[int] = None
    parsed_at: str


class SearchRequest(BaseModel):
    """Request model for searching web content."""
    query: str
    limit: int = 10
    min_score: float = 0.5


class SearchResult(BaseModel):
    """Model for a search result."""
    url: str
    title: str
    snippet: str
    score: float
    parsed_at: str


class SearchResponse(BaseModel):
    """Response model for search operation."""
    query: str
    results: List[SearchResult]
    total_results: int


class PageInfo(BaseModel):
    """Model for page information."""
    url: str
    title: str
    text_length: int
    parsed_at: str
    status: str


class WebCrawler:
    """
    Service for crawling and parsing web pages.
    
    Fetches HTML content and extracts text, title, and metadata.
    """
    
    def __init__(self, settings: WebParserSettings):
        self.settings = settings
        self.client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self):
        """Initialize the HTTP client."""
        self.client = httpx.AsyncClient(
            timeout=self.settings.timeout,
            follow_redirects=True,
            headers={"User-Agent": self.settings.user_agent}
        )
    
    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
    
    async def fetch_url(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from a URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string, or None on error
        """
        if not self.client:
            await self.initialize()
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            # Check content length
            content_length = len(response.content)
            if content_length > self.settings.max_content_length:
                logger.warning(f"Content too large: {url} ({content_length} bytes)")
                return None
            
            return response.text
        except httpx.HTTPError as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None
    
    def parse_html(self, html: str, url: str) -> Dict[str, any]:
        """
        Parse HTML content and extract text and metadata.
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            Dictionary with title, text, and metadata
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.text.strip() if title_tag else urlparse(url).netloc
            
            # Remove unwanted tags
            for tag in self.settings.strip_html_tags:
                for element in soup.find_all(tag):
                    element.decompose()
            
            # Extract text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Limit text length
            if len(text) > self.settings.max_text_length:
                text = text[:self.settings.max_text_length]
            
            # Extract links if enabled
            links = []
            if self.settings.extract_links:
                for link in soup.find_all('a', href=True):
                    links.append(link['href'])
            
            return {
                "title": title,
                "text": text,
                "links": links,
                "text_length": len(text)
            }
        except Exception as e:
            logger.error(f"Error parsing HTML from {url}: {e}")
            return {
                "title": url,
                "text": "",
                "links": [],
                "text_length": 0
            }


class WebParserPlugin(PluginBase):
    """
    Web Parser Plugin.
    
    Crawls and parses web content, generates embeddings, and provides semantic search.
    """
    
    def __init__(self):
        self.settings = WebParserSettings()
        self.crawler: Optional[WebCrawler] = None
        self.router = APIRouter()
        
        # In-memory storage for parsed pages (in production, would use LanceDB)
        self._pages: Dict[str, Dict] = {}  # {url: {title, text, embedding, parsed_at}}
        self._embed_func = None
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes for the web parser."""
        
        @self.router.post("/parse", response_model=ParseResponse)
        async def parse_url(request: ParseRequest):
            """
            Parse a URL and store its content with embeddings.
            
            Example:
                POST /api/plugins/web_parser/parse
                {"url": "https://example.com"}
            """
            if not self.crawler:
                raise HTTPException(status_code=503, detail="Crawler not initialized")
            
            url = str(request.url)
            
            # Check if already cached
            if url in self._pages and not request.force_refresh:
                page = self._pages[url]
                return ParseResponse(
                    url=url,
                    title=page["title"],
                    status="cached",
                    text_length=page["text_length"],
                    embedding_dimension=len(page.get("embedding", [])),
                    parsed_at=page["parsed_at"]
                )
            
            # Fetch and parse
            html = await self.crawler.fetch_url(url)
            if not html:
                raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {url}")
            
            parsed = self.crawler.parse_html(html, url)
            if not parsed["text"]:
                raise HTTPException(status_code=400, detail=f"Failed to extract text from: {url}")
            
            # Generate embedding
            embedding = []
            embedding_dimension = 0
            if self._embed_func:
                try:
                    embedding = self._embed_func(parsed["text"])
                    embedding_dimension = len(embedding)
                except Exception as e:
                    logger.error(f"Error generating embedding for {url}: {e}")
            
            # Store page
            parsed_at = datetime.now().isoformat()
            self._pages[url] = {
                "title": parsed["title"],
                "text": parsed["text"],
                "text_length": parsed["text_length"],
                "embedding": embedding,
                "links": parsed["links"],
                "parsed_at": parsed_at,
                "status": "parsed"
            }
            
            return ParseResponse(
                url=url,
                title=parsed["title"],
                status="parsed",
                text_length=parsed["text_length"],
                embedding_dimension=embedding_dimension,
                parsed_at=parsed_at
            )
        
        @self.router.post("/parse_batch", response_model=List[ParseResponse])
        async def parse_batch(request: ParseBatchRequest):
            """
            Parse multiple URLs in batch.
            
            Example:
                POST /api/plugins/web_parser/parse_batch
                {"urls": ["https://example.com", "https://example.org"]}
            """
            async def parse_one(url):
                try:
                    return await parse_url(ParseRequest(url=url, force_refresh=request.force_refresh))
                except Exception as e:
                    logger.error(f"Error parsing {url}: {e}")
                    return ParseResponse(
                        url=str(url),
                        title=str(url),
                        status="error",
                        text_length=0,
                        parsed_at=datetime.now().isoformat()
                    )

            tasks = [parse_one(url) for url in request.urls]
            return await asyncio.gather(*tasks)
        
        @self.router.get("/search", response_model=SearchResponse)
        async def search(q: str, limit: int = 10, min_score: float = 0.5):
            """
            Search parsed web content using semantic search.
            
            Example:
                GET /api/plugins/web_parser/search?q=machine+learning&limit=10
            """
            if not self._embed_func:
                raise HTTPException(status_code=503, detail="Embedding function not available")
            
            if not self._pages:
                return SearchResponse(query=q, results=[], total_results=0)
            
            # Generate query embedding
            try:
                query_embedding = self._embed_func(q)
            except Exception as e:
                logger.error(f"Error generating query embedding: {e}")
                raise HTTPException(status_code=500, detail="Failed to generate query embedding")
            
            # Calculate similarity scores
            results = []
            for url, page in self._pages.items():
                if not page.get("embedding"):
                    continue
                
                # Calculate cosine similarity
                score = self._cosine_similarity(query_embedding, page["embedding"])
                
                if score >= min_score:
                    # Create snippet
                    text = page["text"]
                    snippet = text[:200] + "..." if len(text) > 200 else text
                    
                    results.append(SearchResult(
                        url=url,
                        title=page["title"],
                        snippet=snippet,
                        score=score,
                        parsed_at=page["parsed_at"]
                    ))
            
            # Sort by score descending
            results.sort(key=lambda x: x.score, reverse=True)
            results = results[:limit]
            
            return SearchResponse(
                query=q,
                results=results,
                total_results=len(results)
            )
        
        @self.router.get("/pages", response_model=List[PageInfo])
        async def list_pages():
            """
            List all parsed pages.
            
            Example:
                GET /api/plugins/web_parser/pages
            """
            pages = []
            for url, page in self._pages.items():
                pages.append(PageInfo(
                    url=url,
                    title=page["title"],
                    text_length=page["text_length"],
                    parsed_at=page["parsed_at"],
                    status=page["status"]
                ))
            
            return pages
        
        @self.router.delete("/pages/{url:path}")
        async def delete_page(url: str):
            """
            Delete a parsed page.
            
            Example:
                DELETE /api/plugins/web_parser/pages/https://example.com
            """
            if url not in self._pages:
                raise HTTPException(status_code=404, detail=f"Page not found: {url}")
            
            del self._pages[url]
            return {"status": "deleted", "url": url}
        
        @self.router.get("/info")
        async def get_info():
            """Get web parser plugin information."""
            return {
                "name": "Web Parser",
                "version": "0.1.0",
                "type": "utility",
                "capabilities": ["searcher.web", "parser.web"],
                "status": "active" if self.crawler else "inactive",
                "settings": self.settings.model_dump(),
                "stats": {
                    "pages_parsed": len(self._pages),
                    "embedding_available": self._embed_func is not None
                }
            }
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score (0.0-1.0)
        """
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        similarity = dot_product / (magnitude1 * magnitude2)
        
        # Normalize to 0-1 range (cosine similarity is -1 to 1)
        return (similarity + 1) / 2
    
    def on_load(self, context: PluginContext) -> None:
        """
        Called when the plugin is loaded.
        Initializes the crawler and registers capabilities.
        """
        logger.info("Loading Web Parser Plugin...")
        
        # Initialize crawler
        self.crawler = WebCrawler(self.settings)
        
        # Get embedding function from system_llm
        if context.capabilities.has("llm.embed"):
            self._embed_func = context.capabilities.get("llm.embed")
            logger.info("LLM embedding capability available")
        else:
            logger.warning("LLM embedding capability not available - search will be limited")
        
        # Register capabilities for other plugins
        def search_web(query: str, limit: int = 10) -> List[Dict]:
            """Search parsed web content."""
            if not self._embed_func:
                return []
            
            query_embedding = self._embed_func(query)
            results = []
            
            for url, page in self._pages.items():
                if not page.get("embedding"):
                    continue
                
                score = self._cosine_similarity(query_embedding, page["embedding"])
                if score >= self.settings.min_search_score:
                    results.append({
                        "url": url,
                        "title": page["title"],
                        "score": score
                    })
            
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]
        
        async def parse_web_page(url: str) -> Dict:
            """Parse a web page and return its content."""
            if not self.crawler:
                return {}
            
            html = await self.crawler.fetch_url(url)
            if not html:
                return {}
            
            return self.crawler.parse_html(html, url)
        
        context.capabilities.register("searcher.web", search_web)
        context.capabilities.register("parser.web", parse_web_page)
        
        logger.info("Web Parser Plugin loaded successfully")
    
    def on_activate(self) -> None:
        """Called when the plugin is activated."""
        logger.info("Web Parser Plugin activated")
    
    def on_deactivate(self) -> None:
        """Called when the plugin is deactivated."""
        logger.info("Web Parser Plugin deactivated")
        # Close crawler if needed
        # Note: In async context, would call await self.crawler.close()
