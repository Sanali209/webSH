# Web Parser Plugin

**Goal:** Crawl, parse, and embed web content for search.

## Steps

1.  **Implement `WebParser`**
    - Create `plugins/web_parser/`.
    - Implement a `Taskiq` worker function:
        - Accepts a URL.
        - Fetches content using `httpx` or `requests`.
        - Extracts text using `BeautifulSoup`.
    - Call `system_llm` capability to generate embeddings for the text.
    - Store the result (URL, title, text, embedding) in `plugin_parser_vectors` (LanceDB).

2.  **Add Search Integration**
    - Register `searcher:web` capability.
    - Implement `search(query) -> list[results]`:
        - Vector search on `plugin_parser_vectors`.
        - Return matching URLs.

## Testing

-   **Unit Tests (`tests/plugins/test_web_parser.py`):**
    -   **Crawling:** Mock `httpx` and verify text extraction.
    -   **Embedding:** Mock `system_llm` and verify embedding call.
    -   **Search:** Insert sample data and verify search returns relevant results.
