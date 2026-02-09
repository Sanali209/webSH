# Phase 1: Core Micro-OS Foundation

**Goal:** Establish a stable, isolated platform capable of loading and managing plugins.

## 1. Project Setup
- [ ] Initialize repository structure:
  - `core/`: Kernel logic (PluginManager, EventBus).
  - `plugins/`: Directory for user/system plugins.
  - `web/`: Svelte frontend.
  - `tests/`: Pytest suite.
- [ ] Configure `pyproject.toml` (Poetry) with dependencies: `fastapi`, `uvicorn`, `pluggy`, `taskiq`, `loguru`.
- [ ] Create `docker-compose.yml` for local development (Redis/ZeroMQ if needed).

## 2. Core SDK Implementation (`core/sdk.py`)
- [ ] Define `PluginBase` abstract class:
  - `on_load(context)`
  - `on_activate()`
  - `on_deactivate()`
- [ ] Implement `PluginContext`:
  - Wrapper for database access (`get_my_table`).
  - Wrapper for Taskiq (`background_task` decorator).
- [ ] Define standard Pydantic models for settings (`PluginSettings`).

## 3. Plugin System (`core/plugin_manager.py`)
- [ ] Implement `PluginLoader` using `pluggy`:
  - Scan `plugins/` directory for `manifest.json`.
  - Validate manifest schema (permissions, dependencies).
  - Build `DependencyGraph` to determine load order.
  - Load Python modules via `importlib`.

## 4. Event Orchestrator (`core/events.py`)
- [ ] Implement `AsyncEventBus`:
  - `subscribe(event_name, callback)`
  - `publish(event_name, data)`
- [ ] Add Distributed Tracing:
  - Generate `correlation_id` for each event.
  - Propagate ID to all subscribers and Taskiq tasks.
- [ ] Setup WebSocket endpoint (`/ws/events`) to broadcast events to Frontend.

## 5. API Gateway (`main.py`)
- [ ] Create FastAPI app.
- [ ] Implement `SandboxMiddleware`:
  - Catch all exceptions from `/api/plugins/*` routes.
  - Return standardized error JSON.
- [ ] Dynamic Router Mounting:
  - Iterate loaded plugins and call `app.include_router(plugin.router)`.

## 6. Testing (`tests/core/`)
- [ ] Unit tests for `PluginLoader` (loading valid/invalid manifests).
- [ ] Unit tests for `AsyncEventBus` (pub/sub logic).
- [ ] Integration test: Load a dummy plugin and verify its router is mounted.
