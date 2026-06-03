"""
RAG Pipeline Service — DGX Spark
==================================
Standalone FastAPI service for RAG ingestion and retrieval.
Runs ALONGSIDE the existing OCR pipeline (ocr-pipeline/).

Endpoints:
  POST /v1/ingest   — Chunk markdown, embed, store in Qdrant
  POST /v1/chat     — Embed query, retrieve chunks, LLM answer
  GET  /v1/metrics  — Usage telemetry
  GET  /healthz     — Health check (embedding server, chat server, Qdrant)

Model servers (llama.cpp):
  Port 8002: Qwen3-Embedding-8B  (embeddings)
  Port 8003: Qwen3.6-35B-A3B     (chat LLM)

Usage:
  uvicorn rag_service:app --host 0.0.0.0 --port 8081
"""

import os
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, Header, Body
from fastapi.middleware.cors import CORSMiddleware
import requests
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("rag-pipeline")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
EMBED_MODEL_URL = os.getenv("EMBED_MODEL_URL", "http://127.0.0.1:8002/v1/embeddings")
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "Qwen3-Embedding-8B")
EMBED_API_KEY = os.getenv("EMBED_API_KEY", "sk-embed-layer2")

CHAT_MODEL_URL = os.getenv("CHAT_MODEL_URL", "http://127.0.0.1:8003/v1/chat/completions")
CHAT_MODEL_NAME = os.getenv("CHAT_MODEL_NAME", "Qwen3.6-35B-A3B")
CHAT_API_KEY = os.getenv("CHAT_API_KEY", "sk-chat-layer3")

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "ocr_rag")

RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "1200"))
RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "150"))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "30"))

# ---------------------------------------------------------------------------
# API Key Database (in-memory)
# ---------------------------------------------------------------------------
def _parse_api_keys() -> dict:
    raw = os.getenv("API_KEYS", "test_key_0000:Internal Benchmark Test:1.00:0.00")
    db = {}
    for entry in raw.split(","):
        parts = entry.strip().split(":")
        if len(parts) >= 4:
            key, user, cap, rate = parts[0], parts[1], float(parts[2]), float(parts[3])
            db[key] = {
                "user": user,
                "active": True,
                "monthly_spend_cap": cap,
                "current_month_spend": 0.00,
                "rate_per_page": rate,
                "metrics": {
                    "total_queries": 0,
                    "total_ingestions": 0,
                    "total_chunks_ingested": 0,
                },
                "audit_logs": [],
            }
    return db

API_KEY_DB = _parse_api_keys()

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="RAG Pipeline API — DGX Spark",
    description="RAG ingestion and retrieval service. Runs alongside the OCR pipeline.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

log.info(f"Embed model: {EMBED_MODEL_URL} ({EMBED_MODEL_NAME})")
log.info(f"Chat model:  {CHAT_MODEL_URL} ({CHAT_MODEL_NAME})")
log.info(f"Qdrant:      {QDRANT_URL} (collection: {QDRANT_COLLECTION})")
log.info(f"API keys loaded: {len(API_KEY_DB)}")

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
async def verify_api_key(x_api_key: str = Header(..., description="API Key")):
    if x_api_key not in API_KEY_DB:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    key_info = API_KEY_DB[x_api_key]
    if not key_info["active"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account Deactivated.")
    return x_api_key


# ===========================================================================
# Embedding Layer (llama.cpp on :8002)
# ===========================================================================

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a list of texts via llama.cpp /v1/embeddings (OpenAI-compatible)."""
    if not texts:
        return []

    response = requests.post(
        EMBED_MODEL_URL,
        json={"input": texts, "model": EMBED_MODEL_NAME},
        headers={"Authorization": f"Bearer {EMBED_API_KEY}"},
        timeout=120,
    )

    if response.status_code != 200:
        raise RuntimeError(f"Embedding failed: {response.status_code} {response.text}")

    data = response.json().get("data", [])
    if not data:
        raise RuntimeError("Embedding returned no vectors")

    data.sort(key=lambda x: x.get("index", 0))
    return [item["embedding"] for item in data]


def embed_single(text: str) -> List[float]:
    """Embed a single text string."""
    results = embed_texts([text])
    if not results:
        raise RuntimeError("Embedding returned empty result")
    return results[0]


# ===========================================================================
# Chat LLM Layer (llama.cpp on :8003)
# ===========================================================================

def chat_completion(messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
    """Send messages to the chat LLM and return response content."""
    response = requests.post(
        CHAT_MODEL_URL,
        json={"model": CHAT_MODEL_NAME, "messages": messages, "temperature": temperature},
        headers={"Authorization": f"Bearer {CHAT_API_KEY}"},
        timeout=180,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Chat LLM failed: {response.status_code} {response.text}")

    return response.json()["choices"][0]["message"]["content"]


# ===========================================================================
# Chunking
# ===========================================================================

def chunk_markdown(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """Split text into overlapping chunks respecting paragraph boundaries."""
    chunk_size = chunk_size or RAG_CHUNK_SIZE
    overlap = overlap or RAG_CHUNK_OVERLAP

    cleaned = (text or "").strip()
    if not cleaned:
        return []

    paragraphs = [p for p in cleaned.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current = ""

    for para in paragraphs:
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= chunk_size:
            current = candidate
            continue
        if current:
            chunks.append(current)
            current = ""
        if len(para) <= chunk_size:
            current = para
            continue
        start = 0
        while start < len(para):
            end = min(start + chunk_size, len(para))
            chunks.append(para[start:end])
            if end == len(para):
                start = end
            else:
                start = max(end - overlap, end)

    if current:
        chunks.append(current)

    if overlap > 0 and len(chunks) > 1:
        for index in range(1, len(chunks)):
            prefix = chunks[index - 1][-overlap:]
            chunks[index] = f"{prefix}\n\n{chunks[index]}"

    return chunks


# ===========================================================================
# Qdrant Operations
# ===========================================================================

def _get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=QDRANT_URL)


def ensure_collection(client: QdrantClient, name: str, vector_size: int) -> None:
    collections = client.get_collections().collections
    existing = {c.name for c in collections}
    if name in existing:
        return
    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )


def _search_points(client, collection, vector, limit, score_threshold=None):
    """Search Qdrant with compatibility across client versions."""
    if hasattr(client, "search"):
        kwargs = {
            "collection_name": collection,
            "query_vector": vector,
            "limit": limit,
            "with_payload": True,
        }
        if score_threshold is not None:
            kwargs["score_threshold"] = score_threshold
        return client.search(**kwargs)

    if hasattr(client, "query_points"):
        kwargs = {
            "collection_name": collection,
            "query": vector,
            "limit": limit,
            "with_payload": True,
        }
        if score_threshold is not None:
            kwargs["score_threshold"] = score_threshold
        response = client.query_points(**kwargs)
        return response.points if hasattr(response, "points") else response

    raise AttributeError("Qdrant client has no supported search method")


# ===========================================================================
# Endpoints
# ===========================================================================

@app.get("/healthz", tags=["System"])
async def health_check():
    """Check all backend services."""
    health = {"status": "ok", "services": {}}

    # Embedding server
    try:
        r = requests.get(f"http://127.0.0.1:{os.getenv('EMBED_PORT', '8002')}/health", timeout=3)
        health["services"]["embed_model"] = "up" if r.status_code == 200 else "degraded"
    except Exception:
        health["services"]["embed_model"] = "down"

    # Chat server
    try:
        r = requests.get(f"http://127.0.0.1:{os.getenv('CHAT_PORT', '8003')}/health", timeout=3)
        health["services"]["chat_model"] = "up" if r.status_code == 200 else "degraded"
    except Exception:
        health["services"]["chat_model"] = "down"

    # Qdrant
    try:
        r = requests.get(f"{QDRANT_URL}/collections", timeout=3)
        health["services"]["qdrant"] = "up" if r.status_code == 200 else "degraded"
    except Exception:
        health["services"]["qdrant"] = "down"

    if any(v == "down" for v in health["services"].values()):
        health["status"] = "degraded"

    return health


@app.post("/v1/ingest", tags=["RAG"])
async def ingest_document(
    api_key: str = Depends(verify_api_key),
    filename: str = Body(..., embed=True),
    markdown_content: str = Body(..., embed=True),
    collection: str = Body(None, embed=True),
    chunk_size: int = Body(None, embed=True),
    chunk_overlap: int = Body(None, embed=True),
):
    """Ingest text into Qdrant: chunk → embed → store."""
    collection = collection or QDRANT_COLLECTION
    chunk_size = chunk_size or RAG_CHUNK_SIZE
    chunk_overlap = chunk_overlap or RAG_CHUNK_OVERLAP

    try:
        chunks = chunk_markdown(markdown_content, chunk_size, chunk_overlap)
        if not chunks:
            return {"status": "empty", "chunks": 0, "collection": collection}

        embeddings = embed_texts(chunks)
        if len(chunks) != len(embeddings):
            raise RuntimeError("Embedding count mismatch")

        client = _get_qdrant_client()
        ensure_collection(client, collection, len(embeddings[0]))

        now = int(time.time())
        points = []
        for index, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            payload = {
                "source": "ocr",
                "filename": filename,
                "chunk_index": index,
                "text": chunk,
                "created_at": now,
            }
            points.append(PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload))

        client.upsert(collection_name=collection, points=points)

        # Update metrics
        db_ref = API_KEY_DB[api_key]
        db_ref["metrics"]["total_ingestions"] += 1
        db_ref["metrics"]["total_chunks_ingested"] += len(points)
        db_ref["audit_logs"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": "ingest",
            "filename": filename,
            "chunks": len(points),
            "collection": collection,
        })

        log.info(f"Ingested: {filename} | {len(points)} chunks → {collection}")
        return {"status": "ok", "chunks": len(points), "collection": collection}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/v1/chat", tags=["RAG"])
async def chat_with_documents(
    api_key: str = Depends(verify_api_key),
    query: str = Body(..., embed=True),
    collection: str = Body(None, embed=True),
    top_k: int = Body(None, embed=True),
    system_prompt: str = Body(None, embed=True),
):
    """RAG chat: embed query → retrieve chunks → LLM answer."""
    collection = collection or QDRANT_COLLECTION
    top_k = top_k or RAG_TOP_K

    try:
        # Embed query
        query_vector = embed_single(query)

        # Retrieve from Qdrant
        client = _get_qdrant_client()
        results = _search_points(client, collection, query_vector, top_k)

        sources = []
        for point in results:
            p = point.payload or {}
            sources.append({
                "text": p.get("text", ""),
                "filename": p.get("filename", "unknown"),
                "chunk_index": p.get("chunk_index", 0),
                "score": point.score,
            })

        if not sources:
            return {"answer": "No relevant chunks found.", "sources": []}

        # Build context
        context_blocks = []
        for s in sources:
            header = f"[Source: {s['filename']} | chunk {s['chunk_index']} | score {s['score']:.4f}]"
            context_blocks.append(f"{header}\n{s['text']}")
        context = "\n\n".join(context_blocks)

        # LLM answer
        sys_text = system_prompt or (
            "You are a local RAG assistant. Answer using only the context. "
            "If the answer is not in the context, say you do not know."
        )
        user_text = (
            "Use the context to answer the question. Provide a concise answer and cite sources.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}"
        )
        messages = [
            {"role": "system", "content": sys_text},
            {"role": "user", "content": user_text},
        ]
        answer = chat_completion(messages)

        # Update metrics
        db_ref = API_KEY_DB[api_key]
        db_ref["metrics"]["total_queries"] += 1
        db_ref["audit_logs"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": "chat",
            "query": query[:100],
            "sources_count": len(sources),
            "collection": collection,
        })

        log.info(f"Chat: '{query[:50]}...' | {len(sources)} sources")
        return {"answer": answer, "sources": sources}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.get("/v1/metrics", tags=["System"])
async def get_metrics(api_key: str = Depends(verify_api_key)):
    """Return usage metrics for the authenticated key."""
    return API_KEY_DB[api_key]


# ---------------------------------------------------------------------------
# Standalone runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8081"))
    uvicorn.run("rag_service:app", host=host, port=port, log_level="info")
