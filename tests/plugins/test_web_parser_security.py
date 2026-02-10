import sys
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Mock dependencies before importing plugin modules
class MockBaseModel:
    def __init__(self, **data):
        # Set some default values that are expected by the code
        self.timeout = 30
        self.user_agent = "PC-Center-WebParser/0.1.0"
        self.max_content_length = 5 * 1024 * 1024
        self.max_text_length = 50000
        self.extract_links = True
        self.strip_html_tags = ["script", "style"]
        self.min_search_score = 0.5
        for k, v in data.items():
            setattr(self, k, v)
    def model_dump(self):
        return {}

pydantic_mock = MagicMock()
pydantic_mock.BaseModel = MockBaseModel
sys.modules['pydantic'] = pydantic_mock

fastapi_mock = MagicMock()
sys.modules['fastapi'] = fastapi_mock

httpx_mock = MagicMock()
class MockHTTPError(Exception):
    pass
httpx_mock.HTTPError = MockHTTPError
sys.modules['httpx'] = httpx_mock

bs4_mock = MagicMock()
sys.modules['bs4'] = bs4_mock

sys.modules['lxml'] = MagicMock()

import unittest
import asyncio
import socket
import logging

from plugins.web_parser.utils import is_safe_url
from plugins.web_parser.backend import WebCrawler
from plugins.web_parser.config import WebParserSettings

# Configure logging to see output during tests
logging.basicConfig(level=logging.INFO)

class TestWebParserSecurity(unittest.IsolatedAsyncioTestCase):
    """Security tests for Web Parser plugin."""

    async def test_is_safe_url_valid_external(self):
        """Test that a valid external URL is considered safe."""
        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.getaddrinfo = AsyncMock(return_value=[
                (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 0))
            ])
            self.assertTrue(await is_safe_url("https://example.com"))

    async def test_is_safe_url_localhost(self):
        """Test that localhost is considered unsafe."""
        self.assertFalse(await is_safe_url("http://localhost"))
        self.assertFalse(await is_safe_url("http://127.0.0.1"))
        self.assertFalse(await is_safe_url("http://[::1]"))

    async def test_is_safe_url_private_ip(self):
        """Test that private IP ranges are considered unsafe."""
        self.assertFalse(await is_safe_url("http://10.0.0.1"))
        self.assertFalse(await is_safe_url("http://172.16.0.1"))
        self.assertFalse(await is_safe_url("http://192.168.1.1"))

    async def test_is_safe_url_link_local(self):
        """Test that link-local IPs are considered unsafe."""
        self.assertFalse(await is_safe_url("http://169.254.169.254"))

    async def test_is_safe_url_invalid_scheme(self):
        """Test that non-http/https schemes are blocked."""
        self.assertFalse(await is_safe_url("file:///etc/passwd"))
        self.assertFalse(await is_safe_url("ftp://example.com"))

    async def test_web_crawler_blocks_ssrf(self):
        """Test that WebCrawler blocks requests to unsafe URLs."""
        settings = WebParserSettings()
        crawler = WebCrawler(settings)

        # Mock httpx client
        mock_client = AsyncMock()
        crawler.client = mock_client

        # Target a local address
        with self.assertLogs('plugins.web_parser.backend', level='WARNING') as cm:
            html = await crawler.fetch_url("http://127.0.0.1/admin")
            self.assertIn("SSRF Protection: Blocked request to http://127.0.0.1/admin", cm.output[0])

        self.assertIsNone(html)
        self.assertEqual(mock_client.get.call_count, 0)

    async def test_web_crawler_blocks_redirect_ssrf(self):
        """Test that WebCrawler blocks redirects to unsafe URLs."""
        settings = WebParserSettings()
        crawler = WebCrawler(settings)

        # Mock httpx client to return a redirect to localhost
        mock_response = MagicMock()
        mock_response.is_redirect = True
        mock_response.status_code = 302
        mock_response.headers = {"Location": "http://127.0.0.1/admin"}

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        crawler.client = mock_client

        # Initial URL is safe, but redirect is unsafe
        with patch("plugins.web_parser.backend.is_safe_url", side_effect=[True, False]):
            with self.assertLogs('plugins.web_parser.backend', level='WARNING') as cm:
                html = await crawler.fetch_url("https://example.com/redirect")
                self.assertIn("SSRF Protection: Blocked request to http://127.0.0.1/admin", cm.output[0])

        self.assertIsNone(html)
        self.assertEqual(mock_client.get.call_count, 1)
        mock_client.get.assert_called_with("https://example.com/redirect")

    async def test_web_crawler_follows_safe_redirect(self):
        """Test that WebCrawler follows safe redirects."""
        settings = WebParserSettings()
        crawler = WebCrawler(settings)

        # Mock first response as a safe redirect
        redirect_response = MagicMock()
        redirect_response.is_redirect = True
        redirect_response.status_code = 302
        redirect_response.headers = {"Location": "https://example.com/page"}
        redirect_response.url = MagicMock()
        # Mocking joining of URLs
        redirect_response.url.join = lambda x: x

        # Mock second response as success
        success_response = MagicMock()
        success_response.is_redirect = False
        success_response.status_code = 200
        success_response.text = "Success content"
        success_response.content = b"Success content"
        success_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=[redirect_response, success_response])

        crawler.client = mock_client

        with patch("plugins.web_parser.backend.is_safe_url", return_value=True):
            html = await crawler.fetch_url("https://example.com/start")

        self.assertEqual(html, "Success content")
        self.assertEqual(mock_client.get.call_count, 2)

if __name__ == "__main__":
    unittest.main()
