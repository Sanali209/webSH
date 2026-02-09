"""Configuration for Web Parser Plugin."""
from pydantic import BaseModel, Field
from core.sdk import PluginSettings
from typing import List


class WebParserSettings(PluginSettings):
    """Settings for the Web Parser plugin."""
    
    # HTTP settings
    timeout: int = Field(
        default=30,
        description="HTTP request timeout in seconds"
    )
    
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed requests"
    )
    
    user_agent: str = Field(
        default="PC-Center-WebParser/0.1.0",
        description="User agent string for HTTP requests"
    )
    
    # Crawling settings
    max_content_length: int = Field(
        default=5 * 1024 * 1024,  # 5 MB
        description="Maximum content length to fetch in bytes"
    )
    
    respect_robots_txt: bool = Field(
        default=True,
        description="Whether to respect robots.txt"
    )
    
    # Parsing settings
    extract_links: bool = Field(
        default=True,
        description="Whether to extract links from pages"
    )
    
    max_text_length: int = Field(
        default=50000,
        description="Maximum text length to store (characters)"
    )
    
    strip_html_tags: List[str] = Field(
        default=["script", "style", "noscript", "iframe"],
        description="HTML tags to remove during text extraction"
    )
    
    # Embedding settings
    chunk_size: int = Field(
        default=1000,
        description="Size of text chunks for embedding (characters)"
    )
    
    chunk_overlap: int = Field(
        default=200,
        description="Overlap between text chunks (characters)"
    )
    
    # Search settings
    default_search_limit: int = Field(
        default=10,
        description="Default number of search results to return"
    )
    
    min_search_score: float = Field(
        default=0.5,
        description="Minimum similarity score for search results (0.0-1.0)"
    )
