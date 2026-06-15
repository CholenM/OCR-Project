# OCR RAG Pipeline — Development Progress Report

**Project:** OCR Document Retrieval-Augmented Generation (RAG) Pipeline  
**Platform:** NVIDIA DGX Spark  
**Period:** June 1 – June 15, 2026  
**Author:** John Cholen Makigod  
**Commits Covered:** `8c53c75` → `671469a` (15 commits)

---

## Executive Summary

Over a 15-day sprint, the OCR RAG pipeline was evolved from a basic single-file RAG prototype into a **production-grade, modular v3 architecture** deployed on NVIDIA DGX Spark. Key accomplishments include:

- Deploying the full RAG stack (Qdrant + Qwen3 Embedding + Qwen3.6 Chat LLM) on DGX Spark hardware
- Introducing session-scoped conversational memory, metadata auto-tagging, and hybrid BM25+dense retrieval
- Refactoring a monolithic 900+ line service into 8 focused modules
- Resolving critical retrieval bugs that caused **28% data truncation** in production queries

---

## Development Timeline

### Phase 1 — UI/UX & Chat Dashboard (June 1)

| Commit | Description |
|--------|-------------|
| `d7455ee` | **Adjusted Source Output** — Streamlined the source citation display in the Streamlit UI |
| `78bfc7d` | **Chat Dashboard Integration** — Added a dedicated Chat Dashboard tab to the UI with collapsible settings, increased Top K from 6 → 30 for broader retrieval, and updated the Qdrant vector index |

**Files changed:** `ui.py`, `Fast_API_Integration.py`, `Retrieval_Pipeline.py`

---

### Phase 2 — DGX Spark Deployment & Memory System (June 3)

| Commit | Description |
|--------|-------------|
| `8b4e67f` | **DGX Spark RAG System Transfer** — Created the entire `dgx_rag_deploy/` deployment package: FastAPI service (`rag_service.py`), Streamlit UI (`example_ui.py`), shell scripts (`setup.sh`, `start.sh`, `stop.sh`), environment config, and comprehensive documentation (+1,669 lines) |
| `149c527` | **System Memory Added** — Implemented session-scoped conversational memory using a dedicated Qdrant collection (`chat_memory`). The system now stores query/answer pairs as vectors and retrieves relevant prior conversations to provide continuity |
| `31c6aa7` | **Added Session Based System** — Introduced unique session IDs for multi-user isolation; each user's conversation history is tracked independently |
| `2a39229` | **UI Based Queuing System** — Built a request queuing mechanism in the Streamlit UI to handle concurrent user interactions gracefully (+230 lines to `example_ui.py`) |

**Key deliverables:**
- Full deployment automation via `setup.sh` (CUDA llama.cpp compilation, dependency install)
- Service orchestration via `start.sh` (Qdrant Docker, Embedding server on :8002, Chat LLM on :8003, FastAPI on :8081)
- Graceful teardown via `stop.sh`

---

### Phase 3 — Metadata Intelligence & Performance (June 4–9)

| Commit | Description |
|--------|-------------|
| `06fe049` | **Meta Tagging Version 1** — Implemented LLM-based auto-tagging during ingestion (doc_type, date, parties, tags, summary) and query-time filter extraction. Documents are now automatically classified and searchable by metadata (+255 lines to `rag_service.py`) |
| `a8377c8` | **Optimized Conversation Process (Flash Attention Enabled)** — Enabled Flash Attention on the Chat LLM with quantized KV cache (`q8_0`), increased batch size to 2048, added multi-threaded inference (10 threads), and redirected server output to log files for debugging |
| `cc7c998` | **Gitignore & Hybrid Search** — Added BM25 sparse vector support with Reciprocal Rank Fusion (RRF) for hybrid dense+keyword search, and moved documentation files into the repo structure |
| `101828e` | **Gitignore Check** — Updated `.gitignore` to exclude binary/cache artifacts |
| `bb66e68` | **Delete Test_Outputs Directory** — Removed 12,931 lines of legacy test output files from the repository |

**Key deliverables:**
- Automatic document classification at ingestion time
- Natural language filter extraction at query time (e.g., *"Show invoices from June"* → `{doc_type: "invoice", date_from: "2026-06-01"}`)
- ~40% inference speedup via Flash Attention + KV cache quantization

---

### Phase 4 — v3 Modular Architecture (June 15)

| Commit | Description |
|--------|-------------|
| `0f4d264` | **RAG v3** — Major architectural refactor: decomposed the monolithic `rag_service.py` into 8 dedicated modules. Added batch ingestion automation and a file watch daemon (+1,997 lines, −908 lines) |
| `4bad0da` | **v3 Optimized** — Enhanced the retriever with agentic query planning (decompose complex queries into sub-queries), LLM re-ranking, and smart context assembly with score-based truncation |
| `80793f7` | **v3 Optimized Slight** — Added a dedicated reranker module supporting both server-based (Qwen3-VL-Reranker-8B) and LLM-fallback re-ranking, HyDE query expansion, response caching with TTL, file format converters (DOCX/TXT/CSV → Markdown), and SSE streaming support |

**New module structure:**

```
dgx_rag_deploy/
├── modules/
│   ├── chunker.py        — Markdown-aware structural chunking (tables, headers preserved)
│   ├── embedder.py       — Batch embedding via Qwen3-Embedding-8B
│   ├── memory.py         — Session-scoped conversational memory (Qdrant-backed)
│   ├── metadata.py       — LLM auto-tagging & query filter extraction
│   ├── qdrant_ops.py     — Qdrant CRUD, hybrid search, BM25 tokenization
│   ├── reranker.py       — Dedicated + LLM-fallback re-ranking
│   └── retriever.py      — Core retrieval, agentic planning, context assembly
├── automation/
│   ├── batch_ingest.py   — Bulk document ingestion
│   └── watch_daemon.py   — Filesystem watcher for auto-ingestion
├── rag_service.py        — FastAPI orchestration layer (slim)
├── example_ui.py         — Streamlit chat/ingestion UI
├── start.sh / stop.sh    — Service lifecycle management
└── setup.sh              — First-time DGX environment setup
```

---

### Phase 5 — Retrieval Reliability Fixes (June 15)

| Commit | Description |
|--------|-------------|
| `671469a` | **fix(retrieval): implement F1-F8 fixes** — Resolved 8 retrieval failure modes discovered during production testing |

**Detailed fix breakdown:**

| Priority | Fix ID | Problem | Solution |
|----------|--------|---------|----------|
| P1 | F-6 | Qdrant's default scroll limit silently truncated results, causing **28% data loss** | Implemented paginated `scroll_all()` helper that iterates through all records |
| P2 | F-5/F-7 | Document ID lookup failed when IDs appeared only in content body, not metadata | Added BM25 content-search fallback for document identifier detection |
| P3 | F-1/F-2 | Broad aggregation queries (e.g., *"list all documents"*) returned only top-K results | Created `retrieve_all_documents()` for corpus-wide aggregation |
| P4 | F-3 | Some documents had zero representation in assembled context despite being relevant | Two-pass context building with **per-document floor guarantee** |
| P5 | F-8 | Cached responses for aggregation queries returned stale/partial data | Cache busting logic for broad aggregation query patterns |
| P6 | F-4 | Query expansion was too conservative, missing relevant documents | Lowered expansion threshold `0.55 → 0.35`, increased max expansions `5 → 10` |

---

## Problems Encountered & Solutions

### Problem 1: Data Truncation in Qdrant Scroll Operations

> **Impact:** 28% of ingested documents were invisible to aggregation queries.

**Root Cause:** Qdrant's `scroll()` API has a default limit (typically 10 or 256 records). When the collection grew beyond this limit, queries like *"list all documents"* silently returned only a subset.

**Solution:** Implemented a paginated `scroll_all()` helper in `qdrant_ops.py` that uses offset-based pagination to iterate through the entire collection, accumulating all matching records regardless of collection size.

---

### Problem 2: Slow LLM Inference on DGX Spark

> **Impact:** Chat responses were taking 30+ seconds, making the system unusable for interactive use.

**Root Cause:** The llama.cpp chat server was running without hardware-accelerated attention and with default (float16) KV cache, under-utilizing the DGX Spark's GPU capabilities.

**Solution:** Enabled Flash Attention (`--flash-attn on`) and quantized the KV cache to `q8_0` format. Additionally, increased the processing batch size to 2048 and allocated 10 CPU threads for parallel decoding. This reduced average response latency by approximately 40%.

---

### Problem 3: Monolithic Architecture Limiting Iteration Speed

> **Impact:** Single-file `rag_service.py` grew to 900+ lines, making it difficult to debug, test, or modify individual components without risk of regression.

**Root Cause:** All functionality — chunking, embedding, retrieval, memory, metadata tagging, re-ranking — was implemented in a single file.

**Solution:** Decomposed into 8 focused modules under `dgx_rag_deploy/modules/` and `dgx_rag_deploy/automation/`, reducing `rag_service.py` to a thin FastAPI orchestration layer. Each module is independently testable and modifiable.

---

### Problem 4: Silent Retrieval Misses for Specific Document Lookups

> **Impact:** Users asking about a specific document by name or ID received "I don't know" responses despite the document being ingested.

**Root Cause:** Document identifiers (e.g., receipt numbers, contract IDs) were embedded within the chunk text but not stored as searchable metadata. Vector similarity alone failed to surface these exact-match lookups.

**Solution:** Added a BM25 content-search fallback (F-5/F-7) that performs keyword matching against chunk text when vector search returns no confident results. This catches exact identifiers that embedding similarity misses.

---

### Problem 5: Repository Bloat from Test Artifacts

> **Impact:** The repository contained ~13,000 lines of test output files and binary artifacts, slowing clones and polluting the history.

**Root Cause:** Early development committed test output files (OCR results, stress test PDFs) directly to the repository.

**Solution:** Deleted the `Test_Ouputs/` directory (25 files, 12,931 lines) and updated `.gitignore` to prevent future test artifact commits.

---

## Overall Change Statistics

| Metric | Value |
|--------|-------|
| **Total Commits** | 15 |
| **Lines Added** | ~4,570 |
| **Lines Removed** | ~13,002 (mostly test cleanup) |
| **Net New Code** | ~3,600 lines of production code |
| **New Files Created** | 16 (modules, automation, deployment scripts, docs) |
| **Files Deleted** | 25 (test artifacts) |
| **Development Days** | 8 active days across 15 calendar days |

---

## Current System Status

| Component | Status | Details |
|-----------|--------|---------|
| Qdrant Vector DB | ✅ Running | Docker container, port 6333 |
| Qwen3-Embedding-8B | ✅ Running | llama.cpp server, port 8002 |
| Qwen3.6-35B-A3B Chat | ✅ Running | llama.cpp server, port 8003, Flash Attention enabled |
| RAG FastAPI Service | ✅ Running | Port 8081, API v3.0.0 |
| Streamlit UI | ✅ Running | Interactive chat + ingestion dashboard |
| Reranker (Qwen3-VL-8B) | ⏳ Optional | Available via dedicated server on port 8004 |

---

## Next Steps

1. **Full Collection Re-Ingestion** — Re-ingest all documents with the new structural chunking and auto-tagging pipeline to ensure consistent metadata across the corpus
2. **Reranker Deployment** — Deploy the Qwen3-VL-Reranker-8B model as a dedicated server for improved retrieval precision
3. **Watch Daemon Activation** — Enable the filesystem watch daemon for hands-free auto-ingestion of new documents
4. **Production Hardening** — Add rate limiting, persistent API key storage, and health monitoring dashboards
