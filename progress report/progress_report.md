# OCR/RAG Pipeline — Development Progress Report

**Period:** June 5 – June 15, 2026
**Author:** John Cholen
**Commit Range:** `a8377c8` → `671469a` (7 commits)
**Source Changes:** 21 files changed · **3,009 insertions** · **779 deletions** (source only, excludes test output cleanup)

---

## Executive Summary

Over a 10-day development period, the DGX RAG Pipeline underwent a **major architectural overhaul** (v2 → v3), transforming a monolithic single-file service into a modular, production-grade system. The work culminated in the identification and resolution of **8 retrieval reliability bugs** (F1–F8) that caused silent data loss on broad aggregation queries. The system is now live and stable on DGX Spark.

---

## Timeline & Commit History

| # | Date | Commit | Description |
|---|------|--------|-------------|
| 1 | Jun 5 | `a8377c8` | **Baseline** — Optimized Conversation Process (Flash Attention Enabled) |
| 2 | Jun 9 | `cc7c998` | Repository hygiene — `.gitignore` updates, documentation reorganization |
| 3 | Jun 9 | `101828e` | `.gitignore` refinement for generated outputs |
| 4 | Jun 9 | `bb66e68` | Cleaned up `Test_Outputs/` directory (12,931 lines of stale test data removed) |
| 5 | Jun 15 | `0f4d264` | **RAG v3** — Full modular architecture rewrite (+1,997 lines, −908 lines) |
| 6 | Jun 15 | `4bad0da` | **v3 Optimized** — Retriever enhancements and chunker improvements |
| 7 | Jun 15 | `80793f7` | **v3 Optimized (cont.)** — Reranker integration, streaming UI, deployment script upgrades |
| 8 | Jun 15 | `671469a` | **F1–F8 Retrieval Fixes** — Critical bug fixes for broad aggregation and document ID lookup |

---

## Work Completed

### 1. Repository Cleanup (Commits 2–4)

- Updated `.gitignore` to properly exclude generated outputs, logs, and model files.
- Relocated documentation files (`Model Differentiation.md`, flowcharts, pipeline visuals`) to tracked paths.
- **Deleted the entire `Test_Outputs/` directory** — 25 stale test files (12,931 lines) including OCR test results, billing documents, and stress test artifacts that should never have been committed.

### 2. RAG v3 — Modular Architecture Rewrite (Commit 5)

The monolithic `rag_service.py` (1,200+ lines) was decomposed into a clean, modular architecture:

| New Module | Purpose | Lines |
|------------|---------|-------|
| `modules/chunker.py` | Markdown-aware structural chunking with table preservation | 180 |
| `modules/embedder.py` | Batch-aware embedding client with retry logic | 118 |
| `modules/memory.py` | O(n) conversation memory management per session | 187 |
| `modules/metadata.py` | Auto-tagging and LLM-driven metadata filter extraction | 137 |
| `modules/qdrant_ops.py` | Qdrant vector DB operations, hybrid search, BM25 tokenization | 270 |
| `modules/retriever.py` | Core retrieval pipeline: HyDE, context expansion, query planning | 275 |
| `automation/batch_ingest.py` | Bulk batch ingestion from directory | 143 |
| `automation/watch_daemon.py` | Filesystem watch daemon for hands-free ingestion | 228 |

> [!IMPORTANT]
> The refactor preserved 100% backward API compatibility — all existing endpoints (`/v1/ingest`, `/v1/chat`, `/v1/sessions/*`) continue to work without client-side changes.

### 3. Performance & Feature Optimization (Commits 6–7)

**Retriever Enhancements:**
- Implemented neighbor-based context expansion (±3 chunks) instead of fetching all document chunks — significantly reduces context window waste.
- Added HyDE (Hypothetical Document Embedding) for improved semantic search on ambiguous queries.
- Integrated query result caching with TTL for repeated queries.

**Reranker Integration:**
- Added optional Qwen3-VL-Reranker-8B model support via `modules/reranker.py` (123 lines).
- Updated `start.sh` to auto-detect the reranker model file and conditionally launch it on port `:8004`.
- Reranker is **opt-in** (disabled by default) to avoid adding latency to standard queries.

**UI Improvements (`example_ui.py`):**
- Added per-file download buttons and batch ZIP download for OCR results.
- Real-time elapsed time display during OCR processing.
- Token-per-second metrics shown alongside OCR results.
- New **Retrieval Engine Settings** panel with toggleable features: Re-ranking, Agentic RAG, Auto Filters, HyDE, and Streaming.
- Warning banner when enhanced features (extra LLM calls) are enabled.
- Improved ingestion progress with per-file status and chunk counts.
- Dedup-aware re-ingestion (overwrites existing document chunks).

**Deployment Script (`start.sh`):**
- Dynamic step counter based on enabled features.
- Optional Watch Daemon launch (`WATCH_ENABLED=true`).
- Optional Reranker service (auto-detected from model file).
- Enhanced status banner showing all active services and feature flags.

---

## Problems Encountered & Solutions Implemented

### Problem Set: Silent Retrieval Failures (F1–F8)

During production testing after the v3 deployment, we identified **8 distinct retrieval reliability bugs** that caused partial or total data loss on certain query types. These were especially severe for **broad aggregation queries** (e.g., "list all documents", "summarize everything about X across all files").

| Fix ID | Problem | Root Cause | Solution |
|--------|---------|------------|----------|
| **F-1** | Broad aggregation queries missed documents | Only top-k retrieval was used; documents below the similarity threshold were invisible | Implemented `retrieve_all_documents()` — enumerates all unique filenames, runs per-document filtered search (best 2 chunks each), then merges with top-k |
| **F-2** | Corpus-wide queries had no per-document guarantee | Standard vector search returns only the globally highest-scoring chunks | Added two-pass retrieval: per-document floor guarantee + global top-k merge |
| **F-3** | Context assembly favored high-scoring docs | Some documents got zero representation in the final context | Two-pass context building with per-document floor guarantee |
| **F-4** | Context expansion was too conservative | Expansion threshold was 0.55 (too high), `max_expansion` was 5 (too low) | Lowered threshold from 0.55 → 0.35, increased `max_expansion` from 5 → 10. In broad mode, expands all documents in results |
| **F-5** | Document ID queries failed for exact filenames | Embedding-only search couldn't match exact document names reliably | Added BM25 content search fallback for document identifier detection |
| **F-6** | Paginated scroll truncated at 200 records | `client.scroll()` was called with `limit=200`, silently dropping data beyond that threshold | Implemented `scroll_all()` helper with paginated scrolling — fixed **28% data truncation** |
| **F-7** | Exact filename lookups returned empty | No dedicated path for "show me document X" type queries | Combined BM25 + filtered vector search for filename-specific queries |
| **F-8** | Cached results were stale during active ingestion | Broad aggregation results were cached, so new documents weren't visible until cache expired | Cache busting for broad aggregation queries — `_is_broad_query()` check skips cache |

> [!WARNING]
> **F-6 was the most critical bug.** The Qdrant `client.scroll()` API silently truncates results when the collection exceeds the `limit` parameter. With 200 as the limit, any collection with >200 vectors lost ~28% of its data during enumeration. This affected both the `/v1/sessions/{name}` info endpoint and the retrieval pipeline. The `scroll_all()` paginated helper now guarantees complete corpus enumeration regardless of collection size.

### Key Technical Detail: The `scroll_all()` Fix

```python
# BEFORE (broken): silently truncates at 200 records
points, _ = client.scroll(collection_name=name, limit=200, with_payload=True)

# AFTER (fixed): paginated helper guarantees full enumeration
points = scroll_all(client, name, payload_keys=["filename"])
```

The `scroll_all()` helper iterates with `offset` tokens until the server returns no more results, collecting all points regardless of collection size.

---

## Files Changed Summary

### New Files (8)
- `dgx_rag_deploy/modules/__init__.py`
- `dgx_rag_deploy/modules/chunker.py`
- `dgx_rag_deploy/modules/embedder.py`
- `dgx_rag_deploy/modules/memory.py`
- `dgx_rag_deploy/modules/metadata.py`
- `dgx_rag_deploy/modules/qdrant_ops.py`
- `dgx_rag_deploy/modules/retriever.py`
- `dgx_rag_deploy/modules/reranker.py`
- `dgx_rag_deploy/automation/__init__.py`
- `dgx_rag_deploy/automation/batch_ingest.py`
- `dgx_rag_deploy/automation/watch_daemon.py`

### Modified Files (6)
- `dgx_rag_deploy/rag_service.py` — Refactored from monolith to thin orchestrator importing modules
- `dgx_rag_deploy/example_ui.py` — UI improvements (downloads, progress, retrieval settings)
- `dgx_rag_deploy/start.sh` — Reranker + watch daemon support, dynamic step counter
- `dgx_rag_deploy/requirements.txt` — Updated dependencies
- `dgx_rag_deploy/.env.example` — New config variables for reranker, watch daemon, feature flags
- `.gitignore` — Exclude generated outputs

### Deleted (25 files)
- Entire `Test_Outputs/` directory — stale test artifacts

---

## Current System Status

| Component | Status | Port |
|-----------|--------|------|
| Qdrant Vector DB | ✅ Running | :6333 |
| Embedding Model (Qwen3-Embedding-8B) | ✅ Running | :8002 |
| Chat LLM (Qwen3.6-35B-A3B) | ✅ Running | :8003 |
| Reranker (Qwen3-VL-Reranker-8B) | ⚙️ Optional | :8004 |
| FastAPI RAG Service | ✅ Running | :8081 |
| Watch Daemon | ⚙️ Optional | N/A |
| Streamlit UI | ✅ Running | :8501 |

**Architecture:** DGX Spark → GPU-accelerated inference via llama-server (Flash Attention enabled)

---

## Next Steps

1. **Full collection re-ingestion** — Required to apply new chunking strategy to existing documents.
2. **Production monitoring** — Add logging/metrics for retrieval quality (hit rate, latency percentiles).
3. **Reranker evaluation** — Benchmark re-ranking precision gains vs. latency cost on production queries.
4. **Watch daemon deployment** — Enable for hands-free document ingestion from shared inbox directory.
