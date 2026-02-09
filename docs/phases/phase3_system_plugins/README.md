# Phase 3: System Plugins Implementation

**Goal:** Implement essential capabilities (File System, LLM) as standard plugins.

## 1. System Plugin: File System (`plugins/system_fs`)
- [ ] Create plugin structure:
  - `manifest.json`: id `system_fs`, capabilities `fs.scan`, `fs.watch`, `opener:directory`.
  - `backend.py`: Logic for `os.walk` and `watchdog`.
- [ ] Implement `CoreTableSync`:
  - On file created/modified -> Update `CoreMetadataTable` (size, mime_type, mtime).
  - On file deleted -> Remove from `CoreMetadataTable` (using `entity_id`).
- [ ] Implement `FileExplorer.svelte` (`web/src/lib/components/system_fs/`):
  - Grid/List view toggle.
  - Breadcrumbs navigation.
  - Integration with `Core SDK` search.
  - Context Menu slots (`<slot name="context_menu" />`).

## 2. System Plugin: LLM Provider (`plugins/system_llm`)
- [ ] Create plugin structure:
  - `manifest.json`: id `system_llm`, capabilities `llm.embed`, `llm.generate`.
  - `backend.py`: Wrapper for local LLM (Ollama API or HuggingFace Transformers).
- [ ] Implement `EmbeddingsService`:
  - `embed_text(text: str) -> list[float]`.
  - `embed_image(path: str) -> list[float]`.
- [ ] Expose capability via `Core SDK` (`sdk.capabilities.get("llm.embed")`).

## 3. Frontend Core Integration (`web/src/lib/core/`)
- [ ] Implement `ModuleLoader`:
  - Fetch plugin list from `/api/plugins`.
  - Dynamically import Svelte components via `import()`.
- [ ] Implement `SlotManager`:
  - `<Slot name="system_tray" />`: Render icons from all active plugins.
  - `<Slot name="context_menu" />`: Render actions based on selected file type.

## 4. End-to-End Tests (`tests/e2e/`)
- [ ] Playwright setup (`playwright.config.ts`).
- [ ] Test scenario:
  - Open app -> Navigate to `/`.
  - Verify "System FS" icon is present.
  - Click icon -> Verify File Explorer loads.
  - Create file on disk -> Verify it appears in Explorer (Watchdog test).
