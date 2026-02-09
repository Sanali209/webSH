# Phase 4: Advanced Modules

**Goal:** Implement complex plugins for data processing and search.

## 1. Web Parser Plugin (`plugins/web_parser`)
- [ ] Implement `WebParser`:
  - `Taskiq` worker to crawl URLs (`requests/httpx`).
  - Extract text/content using `BeautifulSoup`.
  - Generate embedding using `system_llm` capability.
  - Save to `plugin_parser_vectors` (LanceDB).
- [ ] Add Search Integration:
  - Register `searcher:web` capability.
  - Implement `search(query) -> list[results]`.

## 2. Deduplicator Plugin (`plugins/deduplicator`)
- [ ] Implement `Deduplicator`:
  - Calculate perceptual hash (`imagehash`).
  - Calculate content hash (`md5`).
  - Save to `plugin_dedup_hashes` (LanceDB).
- [ ] Implement `CrossTableQuery`:
  - Find duplicates across `CoreMetadataTable` (same size/mtime) and `plugin_dedup_hashes`.
- [ ] Add Context Menu Action:
  - "Find Duplicates" on file right-click.

## 3. Resource Controller (`core/resources.py`)
- [ ] Implement Resource Quotas:
  - Limit `Taskiq` workers per plugin (e.g., max 2 concurrent tasks).
  - Track CPU/RAM usage per plugin (psutil).
  - Add API endpoint `/api/resources` to monitor usage.

## 4. Performance Testing (`tests/perf/`)
- [ ] Benchmark LanceDB:
  - Create 100 plugin tables.
  - Insert 10k records each.
  - Measure search latency.
- [ ] Benchmark Polars:
  - Join 1M Core records with 10k Plugin records.
  - Measure RRF calculation time.
- [ ] Frontend performance:
  - Load 1000 items in File Explorer grid (Virtual Scrolling).
