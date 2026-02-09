# Phase 4 Implementation Progress

## Overview
Phase 4: Advanced Modules focuses on building sophisticated plugins that demonstrate real-world use cases and the power of the plugin architecture.

**Status:** 20% Complete (1/5 tasks)

---

## Completed Tasks ✅

### ✅ Task 3: Resource Controller (COMPLETE)
**Files Created:**
- `plugins/resource_controller/backend.py` (270 lines)
- `plugins/resource_controller/config.py`
- `plugins/resource_controller/manifest.json`
- `tests/plugins/test_resource_controller.py` (350 lines, 19 tests)

**Features:**
- System-wide resource monitoring (CPU, memory)
- Per-plugin resource tracking
- Quota management (workers, CPU, memory)
- Capabilities: `resources.check_quota`, `resources.get_usage`
- API endpoints for monitoring

**Test Results:** 19/19 passing ✅

---

## Remaining Tasks

### Task 1: Web Parser Plugin
**Goal:** Crawl and embed web content for search

**Requirements:**
- [ ] Create `plugins/web_parser/` structure
- [ ] Implement web crawling (httpx, BeautifulSoup)
- [ ] Use system_llm capability for embeddings
- [ ] Store in `plugin_parser_vectors` LanceDB table
- [ ] Implement vector search
- [ ] Add tests for crawling, embedding, search

**Dependencies Needed:**
```toml
beautifulsoup4 = "^4.12.0"
lxml = "^5.1.0"
```

**Estimated:** 4-6 hours

---

### Task 2: Deduplicator Plugin
**Goal:** Identify duplicate files using hashing

**Requirements:**
- [ ] Create `plugins/deduplicator/` structure
- [ ] Implement MD5 hashing for exact match
- [ ] Implement imagehash for perceptual match
- [ ] Store in `plugin_dedup_hashes` table
- [ ] Cross-table duplicate detection
- [ ] Context menu "Find Duplicates" action
- [ ] Add tests for hashing and detection

**Dependencies Needed:**
```toml
imagehash = "^4.3.0"
pillow = "^10.2.0"
```

**Estimated:** 3-5 hours

---

### Task 4: Performance Testing
**Goal:** Ensure system scales efficiently

**Requirements:**
- [ ] Benchmark LanceDB (100 tables, 10k records)
- [ ] Benchmark Polars (1M core + 10k plugin records)
- [ ] Frontend performance (1000 items, FPS)
- [ ] Script engine performance (50 nodes)
- [ ] Record results, verify thresholds

**Estimated:** 2-3 hours

---

### Task 5: Script Engine Plugin
**Goal:** Automation workflows (n8n-style)

**Requirements:**
- [ ] Create `plugins/system_script_engine/` structure
- [ ] Implement workflow decorators in `core/workflow.py`
- [ ] Node scanner to discover workflow nodes
- [ ] Execution engine with topological sort
- [ ] Visual node editor (Svelte Flow)
- [ ] API: GET /nodes, POST /run
- [ ] Tests for registry, execution, control

**Estimated:** 8-12 hours (Most complex)

---

## Recommended Implementation Order

### Option 1: Complexity-Based (Easiest First)
1. ✅ Resource Controller (DONE)
2. Deduplicator Plugin (3-5h)
3. Web Parser Plugin (4-6h)
4. Performance Testing (2-3h)
5. Script Engine (8-12h)

### Option 2: Value-Based (Most Useful First)
1. ✅ Resource Controller (DONE)
2. Web Parser Plugin (4-6h) - AI features
3. Deduplicator Plugin (3-5h) - Useful feature
4. Script Engine (8-12h) - Most powerful
5. Performance Testing (2-3h) - Validation

---

## Total Remaining Time

**Minimum:** 17 hours  
**Maximum:** 26 hours  
**Realistic:** 20-22 hours

---

## Dependencies Summary

### Already Installed
- ✅ psutil (for Resource Controller)
- ✅ httpx (available)
- ✅ lancedb, pandas, polars

### To Be Added
- beautifulsoup4, lxml (Web Parser)
- imagehash, pillow (Deduplicator)

---

## Architecture Integration

### Capability Usage
- **Web Parser** will consume `llm.embed` from system_llm
- **Deduplicator** will use `fs.scan` from system_fs
- **All plugins** can use `resources.check_quota` from resource_controller
- **Script Engine** will provide `script.run` and `workflow.engine`

### LanceDB Tables
- `plugin_parser_vectors` - Web content embeddings
- `plugin_dedup_hashes` - File hashes

---

## Next Recommended Action

**Implement Deduplicator Plugin:**
- Moderate complexity
- Uses existing system_fs data
- Good demonstration of cross-plugin queries
- Useful feature for end users

---

**Status:** Phase 4 is 20% complete. 4 tasks remaining.
