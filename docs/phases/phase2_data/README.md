# Phase 2: Data & Search Engine

**Goal:** Implement "Single Source of Truth" with LanceDB and secure data access.

## 1. LanceDB Integration (`core/database.py`)
- [ ] Connect to local LanceDB instance (`.lancedb` directory).
- [ ] Implement `CoreMetadataTable`:
  - `entity_id` (PK, string, SHA-256).
  - `path` (string).
  - `filename` (string).
  - `size` (int64).
  - `mime_type` (string).
  - `tags` (list[string]).
  - `last_indexed` (timestamp).
- [ ] Create PyArrow schema for Core Metadata.

## 2. Database Orchestrator (`core/database_manager.py`)
- [ ] Implement `DatabaseManager`:
  - `get_table(table_name, schema)`.
  - `list_tables()`.
- [ ] Implement Scoped Access (`PluginDatabaseContext`):
  - Injected into plugin `on_load`.
  - `.get_my_table(suffix)` -> returns `plugin_{id}_{suffix}`.
  - `.get_core_table()` -> returns Core Metadata (read-only).
  - `.get_other_table(plugin_id, suffix)` -> checks `manifest.permissions`.

## 3. Migration Engine (`core/migrations.py`)
- [ ] Define `schema_version` in `manifest.json`.
- [ ] Store current version in SQLite (`plugins.db`).
- [ ] On startup:
  - If `manifest.version > db.version`, call `plugin.migrate(old_version)`.
  - Update `db.version`.

## 4. Search Orchestrator (`core/search.py`)
- [ ] Implement Hybrid Search:
  - Text search (BM25 or similar) on `filename` and `tags` in Core Table.
  - Vector search on Plugin Tables (`plugin_parser_vectors`).
- [ ] Rank Fusion (RRF) with **Polars**:
  - `join(core_table, plugin_table, on="entity_id")`.
  - Calculate RRF score: `1 / (k + rank_text) + 1 / (k + rank_vector)`.
  - Return sorted results.

## 5. Automated Data Tests (`tests/data/`)
- [ ] Test multiple plugins writing to their own tables concurrently.
- [ ] Test schema migration (add column to plugin table).
- [ ] Verify `PluginDatabaseContext` enforces table prefixes.
