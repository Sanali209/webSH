# System Plugin: LLM Provider

**Goal:** Provide LLM capabilities (embeddings, generation) to other plugins.

## Steps

1.  **Create Plugin Structure**
    - Create `plugins/system_llm/`.
    - Create `manifest.json`:
        - `id`: `system_llm`
        - `capabilities`: `["llm.embed", "llm.generate"]`
    - Create `backend.py`:
        - Initialize connection to local LLM (e.g., Ollama or HuggingFace).

2.  **Implement `EmbeddingsService`**
    - Implement `embed_text(text: str) -> list[float]`.
    - Implement `embed_image(path: str) -> list[float]` (optional, using CLIP or similar).

3.  **Expose Capability via Core SDK**
    - Ensure other plugins can access this service via `context.capabilities.get("llm.embed")`.

## Testing

-   **Unit Tests (`tests/plugins/test_system_llm.py`):**
    -   **Embedding:** Mock the LLM provider. specific test `embed_text` returns a list of floats of expected dimension.
    -   **Integration:** Verify another dummy plugin can request the embedding capability.
