# Experimental OCR API Pipeline

> An API-driven Optical Character Recognition system that converts complex documents (PDFs, images) into structured Markdown via vision-language models, with a built-in RAG pipeline for semantic search over extracted content.

**Status:** Highly Experimental · Optimized for Apple Silicon (Metal) and NVIDIA DGX (CUDA)

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [How It Works](#how-it-works)
- [Components](#components)
  - [FastAPI Backend](#1-fastapi-backend--fast_api_integrationpy)
  - [Ingestion Pipeline](#2-ingestion-pipeline--ingestion_pipelinepy)
  - [Retrieval Pipeline](#3-retrieval-pipeline--retrieval_pipelinepy)
  - [Streamlit UI](#4-streamlit-ui--uipy)
- [System Flow](#system-flow)
- [API Reference](#api-reference)
- [RAG Pipeline](#rag-pipeline)
- [Configuration Reference](#configuration-reference)
- [Models Evaluated](#models-evaluated)
- [Benchmarks](#benchmarks)
- [Getting Started](#getting-started)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Streamlit UI (ui.py)                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │   OCR Dashboard  │  │  Chat Dashboard  │  │  RAG Ingestion   │  │
│  │  • Upload docs   │  │  • Query vector  │  │  • Chunk + embed │  │
│  │  • View results  │  │    store via LLM │  │  • Store in      │  │
│  │  • API metrics   │  │  • Source citing  │  │    Qdrant        │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │
└───────────┼─────────────────────┼─────────────────────┼────────────┘
            │ HTTP                │ Direct call         │ Direct call
            ▼                    ▼                      ▼
┌────────────────────┐  ┌─────────────────┐  ┌──────────────────────┐
│  FastAPI Backend   │  │   Retrieval     │  │  Ingestion Pipeline  │
│  (Fast_API_        │  │   Pipeline      │  │  (Ingestion_         │
│   Integration.py)  │  │  (Retrieval_    │  │   Pipeline.py)       │
│                    │  │   Pipeline.py)  │  │                      │
│  • /v1/ocr         │  │  • Embed query  │  │  • Chunk markdown    │
│  • /v1/metrics     │  │  • Search       │  │  • Embed via Ollama  │
│  • Auth + billing  │  │    Qdrant       │  │  • Upsert to Qdrant  │
└────────┬───────────┘  │  • LLM answer   │  └──────────┬───────────┘
         │              └────────┬────────┘             │
         │ HTTP                  │                      │
         ▼                      ▼                      ▼
┌────────────────────┐  ┌─────────────────┐  ┌──────────────────────┐
│  llama.cpp Server  │  │     Ollama      │  │       Qdrant         │
│  (LM Studio or    │  │  • Embeddings   │  │   Vector Database    │
│   raw llama.cpp)   │  │  • Chat LLM    │  │   (localhost:6333)   │
│  Vision-Language   │  │ (localhost:     │  │                      │
│  Model (OCR)       │  │      11434)    │  │                      │
└────────────────────┘  └─────────────────┘  └──────────────────────┘
```

---

## How It Works

The system operates as a **three-stage pipeline**:

### Stage 1 — OCR Extraction
A document (PDF, JPG, or PNG) is uploaded through the Streamlit UI or directly via the FastAPI endpoint. The backend converts each page into a base64-encoded JPEG and sends it to a **vision-language model** running on a local llama.cpp server. The model extracts all visible text, tables, and structure into Markdown. A post-processing step normalizes Markdown tables to ensure consistent column counts.

### Stage 2 — RAG Ingestion (Optional)
The extracted Markdown can be ingested into a local vector store. The text is split into overlapping chunks (paragraph-aware), each chunk is embedded using an Ollama embedding model, and the resulting vectors are stored in Qdrant with source metadata.

### Stage 3 — Retrieval & Chat (Optional)
Users can query the ingested documents through a chat interface. The query is embedded, the most relevant chunks are retrieved from Qdrant via cosine similarity, and a local LLM synthesizes an answer grounded in the retrieved context.

---

## Components

### 1. FastAPI Backend · `Fast_API_Integration.py`

The core API service that handles document intake, authentication, inference orchestration, and telemetry.

| Responsibility | Detail |
|---|---|
| **Authentication** | API key validation via `X-API-KEY` header with per-key spend caps and active/inactive state |
| **Document Processing** | PDF page extraction via PyMuPDF, image base64 encoding |
| **Inference** | Forwards images to llama.cpp server (`/v1/chat/completions`) with a legal-document-optimized system prompt |
| **Processing Modes** | Serial (page-by-page) or Concurrent (async with configurable semaphore, default 3) |
| **Table Normalization** | Post-processes Markdown tables to enforce consistent column counts across rows |
| **Telemetry** | Tracks tokens, latency, cost, and throughput per request; appends to per-key audit logs |

### 2. Ingestion Pipeline · `Ingestion_Pipeline.py`

Handles chunking and embedding of OCR output for vector storage.

| Responsibility | Detail |
|---|---|
| **Chunking** | Paragraph-aware splitting with configurable `chunk_size` (default 1200 chars) and `chunk_overlap` (default 150 chars) |
| **Embedding** | Batch embedding via Ollama `/api/embed` with single-doc fallback via `/api/embeddings` |
| **Storage** | Creates/ensures Qdrant collection with cosine distance; upserts points with source metadata (filename, chunk index, timestamp) |

### 3. Retrieval Pipeline · `Retrieval_Pipeline.py`

Provides semantic search and RAG-based question answering.

| Responsibility | Detail |
|---|---|
| **Query Embedding** | Embeds user query using the same Ollama model used for ingestion |
| **Vector Search** | Searches Qdrant with configurable `top_k` (default 30) and optional score threshold |
| **Answer Generation** | Builds context from retrieved chunks, sends to Ollama chat model with RAG system prompt |
| **Source Citation** | Returns source filenames, chunk indices, and similarity scores alongside the generated answer |

### 4. Streamlit UI · `ui.py`

A two-tab control center providing the user-facing interface.

**OCR Dashboard Tab:**
- API key authentication with live metrics display (spend tracking, document counts, token usage)
- Document upload with PDF-specific controls (DPI slider 120–350, serial/concurrent mode, concurrency level)
- Side-by-side raw and rendered Markdown preview
- Download button for extracted Markdown
- RAG ingestion controls (collection name, chunk size, overlap, embedding model)
- n8n webhook integration for external workflow automation

**Chat Dashboard Tab:**
- Conversational RAG interface with chat history
- Configurable retrieval parameters (collection, top-k, embedding model, chat model, system prompt)
- Source attribution displayed in expandable sections per response

---

## System Flow

```
   Document Upload          OCR Extraction            Post-Processing
  ┌──────────────┐     ┌─────────────────────┐     ┌──────────────────┐
  │ PDF/JPG/PNG  │────▶│ PyMuPDF page render  │────▶│ Table column     │
  │ via UI or    │     │ Base64 encode        │     │ normalization    │
  │ API call     │     │ Send to llama.cpp    │     │ Markdown cleanup │
  └──────────────┘     └─────────────────────┘     └────────┬─────────┘
                                                            │
                       ┌────────────────────────────────────┤
                       ▼                                    ▼
              ┌─────────────────┐                 ┌─────────────────┐
              │ Download .md    │                 │  RAG Ingestion  │
              │ file directly   │                 │  (optional)     │
              └─────────────────┘                 └────────┬────────┘
                                                           │
                                                           ▼
                                                  ┌─────────────────┐
                                                  │ Chunk → Embed → │
                                                  │ Store in Qdrant │
                                                  └────────┬────────┘
                                                           │
                                                           ▼
                                                  ┌─────────────────┐
                                                  │ Chat / Query    │
                                                  │ Retrieve + LLM  │
                                                  │ answer          │
                                                  └─────────────────┘
```

---

## API Reference

### `POST /v1/ocr`

Process a document and return structured Markdown.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `file` | UploadFile | *required* | PDF, JPG, or PNG document |
| `dpi` | int | `200` | Render resolution for PDFs (72–400) |
| `mode` | string | `concurrent` | `serial` or `concurrent` processing |
| `max_concurrency` | int | `3` | Max parallel pages (1–3, concurrent mode only) |

**Headers:**
- `X-API-KEY` (required) — Authentication key

**Response:** `text/markdown` body with telemetry headers:
- `X-Process-Time` — Total processing time in seconds
- `X-Total-Tokens` — Combined input + output tokens
- `X-Tokens-Per-Sec` — Throughput metric

### `GET /v1/metrics`

Returns the authenticated key's usage metrics, spend tracking, and full audit log.

**Headers:**
- `X-API-KEY` (required) — Authentication key

---

## RAG Pipeline

### Prerequisites

| Service | Requirement |
|---|---|
| **Ollama** | Running locally with embedding model pulled: `ollama pull qwen3-embedding:8b` |
| **Qdrant** | Running locally at `http://localhost:6333` |
| **Python Packages** | `pip install qdrant-client requests` |

### Ingestion Flow
1. OCR Markdown output is split into paragraph-aware chunks (default 1200 chars, 150 overlap)
2. Each chunk is embedded via Ollama (`qwen3-embedding:8b`)
3. Vectors are upserted into Qdrant with metadata (`source`, `filename`, `chunk_index`, `created_at`)

### Retrieval Flow
1. User query is embedded using the same embedding model
2. Top-k similar chunks are retrieved from Qdrant (default k=30, cosine similarity)
3. Retrieved chunks are assembled into a context block with source headers
4. Context + query are sent to an Ollama chat model (`nemotron-3-nano:30b-cloud`) for grounded answer generation

---

## Configuration Reference

All settings are configurable via environment variables:

| Variable | Default | Used By |
|---|---|---|
| `OLLAMA_URL` | `http://localhost:11434` | Ingestion, Retrieval |
| `OLLAMA_EMBED_MODEL` | `qwen3-embedding:8b` | Ingestion, Retrieval |
| `OLLAMA_CHAT_MODEL` | `nemotron-3-nano:30b-cloud` | Retrieval |
| `QDRANT_URL` | `http://localhost:6333` | Ingestion, Retrieval |
| `QDRANT_COLLECTION` | `ocr_rag` | Ingestion, Retrieval |
| `RAG_CHUNK_SIZE` | `1200` | Ingestion |
| `RAG_CHUNK_OVERLAP` | `150` | Ingestion |
| `RAG_TOP_K` | `30` | Retrieval |

---

## Models Evaluated

| Model | Role | Strengths | Tradeoffs |
|---|---|---|---|
| **Qwen3-VL-2B-Instruct** | Early OCR candidate | Good generalization, solid layout understanding | Heavier, slower; overkill for pure OCR |
| **PaddleOCR-VL-1.5** | Primary OCR engine | High accuracy on printed text, good table reconstruction, ~430 tok/s | Less semantic reasoning; limited Markdown table formatting |
| **LightOnOCR-1.5** | Optimized OCR layer | Consistent output, faster throughput, cost-efficient | Narrower scope; relies on clean inputs |

---

## Benchmarks

### Context Size vs. Throughput
- **Hardware:** Mac Mini M4 Pro
- **Model:** Qwen3-VL-2B-Instruct
- **Result:** 8K context → ~230 tok/s. 16K context → ~184 tok/s. Extraction DPI heavily impacts processing speed.

### Processing Strategy
- **Model:** Qwen3-VL-2B-Instruct
- **Result:** Page-by-page chunked processing adopted over full-document processing. Bypasses memory bottlenecks and prevents hallucination drift with larger context windows.

### Model Change — PaddleOCR-VL-1.5
- **Result:** ~430 tok/s throughput. Accurate text extraction but does not generate proper Markdown table formatting.

---

## Getting Started

### 1. Start the OCR inference server

Run a vision-language model via [llama.cpp](https://github.com/ggerganov/llama.cpp) or [LM Studio](https://lmstudio.ai/) on your host machine, serving the OpenAI-compatible chat completions endpoint.

### 2. Start supporting services

```bash
# Ollama (for RAG embeddings + chat)
ollama serve
ollama pull qwen3-embedding:8b

# Qdrant (for vector storage)
docker run -p 6333:6333 qdrant/qdrant
```

### 3. Install Python dependencies

```bash
pip install fastapi uvicorn python-multipart PyMuPDF requests streamlit qdrant-client pandas
```

### 4. Launch the API server

```bash
uvicorn Fast_API_Integration:app --host 0.0.0.0 --port 8000
```

### 5. Launch the UI

```bash
streamlit run ui.py
```

### 6. Use it

1. Enter an API key in the sidebar (e.g., `test_key_0000`)
2. Upload a PDF or image
3. Click **Execute OCR** to extract Markdown
4. Optionally ingest into Qdrant and query via the Chat Dashboard

---

## Project Structure

```
.
├── Fast_API_Integration.py      # FastAPI backend — OCR endpoint, auth, telemetry
├── Ingestion_Pipeline.py        # Chunk + embed + store pipeline for RAG
├── Retrieval_Pipeline.py        # Semantic search + LLM answer generation
├── ui.py                        # Streamlit control center (OCR + Chat tabs)
├── Model Differentiation.md     # Model comparison table
├── OCR_FlowChart_05-25-26.md    # Detailed OCR flowchart (Mermaid)
├── OCR_APIFlowChart_05-25-26.md # API-level architecture diagram (Mermaid)
├── SYSTEM_PIPELINE_VISUAL.md    # Full system pipeline visual documentation
├── Test_Ouputs/                 # Sample OCR extraction results
└── qdrant_data/                 # Local Qdrant persistence
```