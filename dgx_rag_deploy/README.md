# RAG Pipeline — NVIDIA DGX Spark

Standalone RAG ingestion and retrieval service. Runs **alongside** the existing OCR pipeline (`~/ocr-pipeline/`) without touching it.

---

## Architecture

```
DGX Spark (192.168.50.153)
├── ~/ocr-pipeline/          ← EXISTING, UNTOUCHED
│   ├── llama-server :8001   (LightOnOCR-2-1B, OCR vision)
│   └── FastAPI      :8080   (POST /v1/ocr, GET /v1/metrics)
│
└── ~/rag-pipeline/          ← THIS DEPLOYMENT
    ├── llama-server :8002   (Qwen3-Embedding-8B, embeddings)
    ├── llama-server :8003   (Qwen3.6-35B-A3B, chat LLM)
    ├── Qdrant       :6333   (Docker, vector storage)
    └── FastAPI      :8081   (POST /v1/ingest, POST /v1/chat)
```

### Port Map

| Port | Service | Pipeline |
|---|---|---|
| 8001 | OCR Vision model | ocr-pipeline (untouched) |
| 8080 | OCR FastAPI | ocr-pipeline (untouched) |
| 8002 | Embedding model | rag-pipeline |
| 8003 | Chat LLM | rag-pipeline |
| 6333 | Qdrant | rag-pipeline |
| 8081 | RAG FastAPI | rag-pipeline |

---

## What's Included

| File | Purpose |
|---|---|
| `setup.sh` | Downloads embedding + chat models, starts Qdrant Docker, creates venv. Reuses llama.cpp from ocr-pipeline. |
| `rag_service.py` | FastAPI with `/v1/ingest` and `/v1/chat` endpoints |
| `start.sh` | Launches 4 services (Qdrant + 2 llama-servers + FastAPI) |
| `stop.sh` | Stops RAG services only (does NOT touch ocr-pipeline) |
| `.env.example` | Configuration template |
| `requirements.txt` | Python dependencies |
| `example_ui.py` | Streamlit UI connecting to both OCR (:8080) and RAG (:8081) |

---

## Setup Guide

### Step 1: Transfer to DGX Spark

```bash
scp -r dgx_rag_deploy/. jcmakigod@192.168.50.153:~/rag-pipeline/
```

### Step 2: Run setup

```bash
ssh jcmakigod@192.168.50.153
cd ~/rag-pipeline
sudo ./setup.sh
```

This will:
- Locate the existing llama-server binary in `~/ocr-pipeline/llama.cpp/`
- Download Qwen3-Embedding-8B-Q4_K_M.gguf (~5 GB)
- Download Qwen3.6-35B-A3B-Uncensored-Q4_K_M.gguf (~14 GB)
- Start Qdrant Docker container
- Create Python venv
- Generate `.env` with correct llama-server path

### Step 3: Start

```bash
chmod +x start.sh stop.sh
./start.sh
```

Expected output:
```
========================================================
  RAG Pipeline — DGX Spark
========================================================
[1/4] Starting Qdrant...
  ✓ Qdrant already running
[2/4] Starting Embedding model on :8002...
  ✓ Embeddings ready on :8002
[3/4] Starting Chat LLM on :8003...
  ✓ Chat LLM ready on :8003
[4/4] Starting RAG service on :8081...

========================================================
  RAG Pipeline is LIVE
  RAG API:  http://0.0.0.0:8081
  Swagger:  http://0.0.0.0:8081/docs
  OCR Pipeline: separate (~/ocr-pipeline/)
========================================================
```

---

## API Reference

### `POST /v1/ingest` — Ingest text into vector store

```bash
curl -X POST http://192.168.50.153:8081/v1/ingest \
  -H "X-API-KEY: test_key_0000" \
  -H "Content-Type: application/json" \
  -d '{"filename": "doc.pdf", "markdown_content": "# Hello\nWorld"}'
```

| Param | Default | Description |
|---|---|---|
| `filename` | required | Source document name |
| `markdown_content` | required | Text to chunk and embed |
| `collection` | ocr_rag | Qdrant collection |
| `chunk_size` | 1200 | Characters per chunk |
| `chunk_overlap` | 150 | Overlap between chunks |

### `POST /v1/chat` — Query ingested documents

```bash
curl -X POST http://192.168.50.153:8081/v1/chat \
  -H "X-API-KEY: test_key_0000" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the billing terms?"}'
```

| Param | Default | Description |
|---|---|---|
| `query` | required | Question |
| `collection` | ocr_rag | Qdrant collection |
| `top_k` | 30 | Chunks to retrieve |
| `system_prompt` | (RAG default) | Override system prompt |

### `GET /healthz` — Health check

### `GET /v1/metrics` — Usage metrics

---

## Typical Workflow

```
1. OCR Pipeline (:8080)          2. RAG Pipeline (:8081)
   Upload PDF → /v1/ocr             Send markdown → /v1/ingest
   Get Markdown output               Chunks embedded & stored
                                     
                                  3. RAG Pipeline (:8081)
                                     Ask question → /v1/chat
                                     Get grounded answer
```

The `example_ui.py` handles this flow automatically — OCR tab sends to `:8080`, ingestion and chat go to `:8081`.

---

## Running the Client UI

From any LAN machine:

```bash
pip install streamlit requests pandas
streamlit run example_ui.py
```

The UI has two URL inputs in the sidebar:
- **OCR Pipeline URL** → `http://192.168.50.153:8080`
- **RAG Pipeline URL** → `http://192.168.50.153:8081`

---

## Configuration

All settings in `.env`:

| Variable | Default | Description |
|---|---|---|
| `LLAMA_SERVER_PATH` | (from ocr-pipeline) | Path to llama-server binary |
| `EMBED_MODEL_PATH` | `./models/Qwen3-Embedding-8B-Q4_K_M.gguf` | Embedding model |
| `EMBED_PORT` | `8002` | Embedding server port |
| `CHAT_MODEL_PATH` | `./models/Qwen3.6-...Q4_K_M.gguf` | Chat LLM |
| `CHAT_PORT` | `8003` | Chat server port |
| `API_PORT` | `8081` | RAG FastAPI port |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant address |
| `API_KEYS` | (see .env.example) | Auth keys |

---

## Managing

**Start RAG:**
```bash
cd ~/rag-pipeline && ./start.sh
```

**Stop RAG (OCR untouched):**
```bash
cd ~/rag-pipeline && ./stop.sh
```

**Start both pipelines:**
```bash
cd ~/ocr-pipeline && ./start.sh &
cd ~/rag-pipeline && ./start.sh
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `llama-server not found` | Run `sudo ./setup.sh` or set `LLAMA_SERVER_PATH` in `.env` |
| Port 8081 in use | Change `API_PORT` in `.env` |
| Embedding empty | Ensure `--embeddings` flag in start.sh for port 8002 |
| OCR not working | Check ocr-pipeline separately at `:8080/healthz` |
| Permission denied | `sudo chown -R jcmakigod:jcmakigod ~/rag-pipeline/models` |
