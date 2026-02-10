# Code Review & Roadmap to Pro

This document provides a comprehensive analysis of the current codebase and outlines a roadmap to elevate the project to a professional standard.

## 1. Architecture Analysis

### Strengths
- **Modular Plugin System:** The `PluginLoader` and `PluginBase` provide a solid foundation for extensibility.
- **Event-Driven Design:** The `AsyncEventBus` facilitates decoupled communication between components.
- **Modern Stack:** Usage of FastAPI, Pydantic, and LanceDB aligns with modern Python standards.

### Weaknesses & Gaps
- **Singleton Reliance:** The system relies heavily on global singletons (`plugin_loader`, `event_bus`, `db_manager`). This makes unit testing difficult and hurts modularity.
  - *Recommendation:* Implement a proper Dependency Injection (DI) container (e.g., `dependency-injector` or FastAPI's `Depends`) to manage component lifecycles and dependencies.
- **Tight Coupling in Core:** `core/main.py` manually wires everything.
  - *Recommendation:* Use a bootstrap function or factory pattern to initialize the application, making it easier to spin up different configurations for testing or production.
- **Configuration Management:** Configuration is scattered across Pydantic models with default values.
  - *Recommendation:* Centralize configuration using `pydantic-settings` with `.env` file support.

## 2. Security Review

### Strengths
- **SSRF Protection:** `web_parser` implements `is_safe_url` to prevent server-side request forgery.
- **Basic Sandboxing:** `SandboxMiddleware` provides a safety net for plugin exceptions.

### Critical Issues
- **Unrestricted File Access:** `system_fs` exposes a `/scan` endpoint that can traverse the entire filesystem.
  - *Remediation:* Enforce a `root_path` configuration and validate that all requested paths are within this root.
- **Weak Permission Model:** `PluginDatabaseContext` uses simple string checks (`plugin:read:id`) without a centralized enforcement mechanism.
  - *Remediation:* Implement a robust RBAC (Role-Based Access Control) or ABAC (Attribute-Based Access Control) system. Plugins should declare permissions in `manifest.json`, and the core should enforce them via decorators or middleware.
- **No API Authentication:** The API is open.
  - *Remediation:* Even for a local tool, basic authentication (e.g., API Key or Local Token) prevents unauthorized access from other local processes or CSRF attacks.

## 3. Data & Persistence

### Strengths
- **LanceDB Integration:** Utilizing LanceDB for vector and relational data is excellent for this use case.

### Critical Issues
- **In-Memory State:** `web_parser` stores parsed pages in a Python dictionary (`self._pages`). This data is lost on restart.
  - *Remediation:* Persist parsed pages and embeddings in LanceDB.
- **Fragile Migrations:** `MigrationManager` lacks transaction support. A failed migration leaves the DB in an inconsistent state.
  - *Remediation:* Implement transactional migrations (commit/rollback) and a lock mechanism to prevent concurrent migrations.
- **Naive Search:** `web_parser` performs linear cosine similarity search in Python. This is O(N) and will block the event loop.
  - *Remediation:* Offload vector search to LanceDB's native ANN index.

## 4. Performance & Scalability

### Strengths
- **AsyncIO:** Extensive use of `async`/`await` for I/O-bound tasks.
- **Taskiq:** Background task processing is integrated.

### Bottlenecks
- **Blocking Operations:** `system_fs` calculates SHA256 hashes in the watchdog thread (bridged to async loop, but still heavy).
  - *Remediation:* Offload CPU-intensive tasks (hashing, embedding generation) to a process pool or a separate worker via Taskiq.
- **Aggressive Cache Invalidation:** `QueryCache` clears the *entire* cache on any file system event.
  - *Remediation:* Implement key-based invalidation or a TTL (Time-To-Live) strategy.
- **Event Bus Limitations:** `asyncio.gather` in `event_bus` creates a "fire-and-forget" pattern where one slow subscriber can't easily be timed out individually.
  - *Remediation:* Add timeouts and error isolation for event subscribers.

## 5. Best Practices & Quality

### Strengths
- **Type Hinting:** Codebase is well-typed.
- **Linting:** Code style is generally clean.

### Improvements Needed
- **Error Handling:** Inconsistent use of `try/except`. Some blocks swallow exceptions with just a log.
  - *Recommendation:* Define custom exception classes and use a global exception handler in FastAPI to standardize API error responses.
- **Logging:** Basic `logging` usage.
  - *Recommendation:* switch to `structlog` or `loguru` for structured JSON logging, which is easier to parse and monitor.
- **Testing:** Tests rely heavily on mocking.
  - *Recommendation:* Add integration tests that spin up a real database (in-memory or temp file) to verify actual behavior.

---

# Roadmap to Pro

## Phase 1: Foundation Hardening
1.  **Dependency Injection:** Refactor `core` to use a DI container.
2.  **Configuration:** Implement `pydantic-settings` for centralized config.
3.  **Logging:** Replace standard logging with `loguru` (or `structlog`).

## Phase 2: Data Persistence & Integrity
1.  **Refactor Web Parser:** Move storage from memory to LanceDB.
2.  **Optimize Search:** Replace Python loop with LanceDB vector search.
3.  **Robust Migrations:** Add transactions and rollback capabilities to `MigrationManager`.

## Phase 3: Security & Isolation
1.  **File System Sandboxing:** Restrict `system_fs` to a configured root directory.
2.  **Permission Enforcement:** Implement a decorator-based permission system for plugin routes.
3.  **API Auth:** Add a simple token-based authentication middleware.

## Phase 4: Performance & Observability
1.  **Worker Offloading:** Move file hashing and embedding generation to Taskiq workers.
2.  **Cache Strategy:** Optimize `QueryCache` invalidation logic.
3.  **Metrics:** Expose Prometheus metrics for system health (event rate, task queue depth).

## Phase 5: Developer Experience
1.  **SDK Improvements:** Enhance `PluginContext` with helper methods for common tasks (HTTP client with retry, scoped logger).
2.  **CLI:** Create a CLI tool for managing plugins (install, update, check).
