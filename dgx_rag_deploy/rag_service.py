"""
RAG Pipeline Service v3 — DGX Spark
=====================================
Modular, fast-by-default RAG service. Slim router using modules/.

Endpoints:
  POST   /v1/sessions          — Create a new session
  GET    /v1/sessions          — List all sessions
  GET    /v1/sessions/{name}   — Get session info
  DELETE /v1/sessions/{name}   — Delete session + memory
  POST   /v1/ingest            — Chunk + embed + store (single doc)
  POST   /v1/ingest/batch      — Batch ingest multiple docs
  POST   /v1/chat              — RAG chat (fast default, opt-in re-rank/agentic)
  POST   /v1/autotag           — Auto-generate metadata
  GET    /v1/metadata/{c}/{f}  — Get document metadata
  PATCH  /v1/metadata/{c}/{f}  — Update metadata (no re-embed)
  GET    /v1/documents/{c}     — List documents in collection
  GET    /v1/memory/{sid}      — List session memories
  DELETE /v1/memory/{sid}      — Clear session memory
  GET    /v1/metrics           — Usage telemetry
  GET    /healthz              — Health check
"""

import os, re, time, uuid, json, logging
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, Header, Body
from fastapi.middleware.cors import CORSMiddleware
import requests

from modules.embedder import embed_batch, embed_single
from modules.chunker import chunk_markdown_structural
from modules.retriever import retrieve, rerank_chunks, plan_query, build_context
from modules.memory import (
    store_memory_async, search_memory, clear_session_memory, list_session_memory,
)
from modules.metadata import autotag_document, extract_filters_from_query
from modules.qdrant_ops import (
    get_client, ensure_collection, ensure_indexes,
    delete_document_chunks, search_hybrid, build_qdrant_filter, tokenize_bm25,
)

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger("rag-pipeline")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
EMBED_MODEL_URL  = os.getenv("EMBED_MODEL_URL", "http://127.0.0.1:8002/v1/embeddings")
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "Qwen3-Embedding-8B")
EMBED_API_KEY    = os.getenv("EMBED_API_KEY", "sk-embed-layer2")

CHAT_MODEL_URL  = os.getenv("CHAT_MODEL_URL", "http://127.0.0.1:8003/v1/chat/completions")
CHAT_MODEL_NAME = os.getenv("CHAT_MODEL_NAME", "Qwen3.6-35B-A3B")
CHAT_API_KEY    = os.getenv("CHAT_API_KEY", "sk-chat-layer3")

QDRANT_URL        = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "ocr_rag")
MEMORY_COLLECTION = os.getenv("MEMORY_COLLECTION", "chat_memory")

RAG_CHUNK_SIZE    = int(os.getenv("RAG_CHUNK_SIZE", "1200"))
RAG_TOP_K         = int(os.getenv("RAG_TOP_K", "15"))
MEMORY_TOP_K      = int(os.getenv("MEMORY_TOP_K", "5"))
MEMORY_ENABLED    = os.getenv("MEMORY_ENABLED", "true").lower() == "true"
AUTOTAG_MAX_CHARS = int(os.getenv("AUTOTAG_MAX_CHARS", "3000"))
MAX_CONTEXT_TOKENS = int(os.getenv("CHAT_CTX_SIZE", "32768")) - 4096

# ---------------------------------------------------------------------------
# API Key DB
# ---------------------------------------------------------------------------
def _parse_api_keys() -> dict:
    raw = os.getenv("API_KEYS", "test_key_0000:Internal Benchmark Test:1.00:0.00")
    db = {}
    for entry in raw.split(","):
        parts = entry.strip().split(":")
        if len(parts) >= 4:
            db[parts[0]] = {
                "user": parts[1], "active": True,
                "monthly_spend_cap": float(parts[2]), "current_month_spend": 0.0,
                "rate_per_page": float(parts[3]),
                "metrics": {"total_queries": 0, "total_ingestions": 0, "total_chunks_ingested": 0},
                "audit_logs": [],
            }
    return db

API_KEY_DB = _parse_api_keys()

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="RAG Pipeline API v3 — DGX Spark", version="3.0.0",
              description="Fast-by-default modular RAG. Re-ranking & agentic planning are opt-in.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

log.info(f"Embed: {EMBED_MODEL_URL} | Chat: {CHAT_MODEL_URL} | Qdrant: {QDRANT_URL}")

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key not in API_KEY_DB:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    if not API_KEY_DB[x_api_key]["active"]:
        raise HTTPException(status_code=403, detail="Account Deactivated.")
    return x_api_key

# Helpers
def _qclient():
    return get_client(QDRANT_URL)

def _embed(text):
    return embed_single(text, EMBED_MODEL_URL, EMBED_MODEL_NAME, EMBED_API_KEY)

def _embed_batch(texts):
    return embed_batch(texts, EMBED_MODEL_URL, EMBED_MODEL_NAME, EMBED_API_KEY)

def _chat(messages, temperature=0.7):
    r = requests.post(CHAT_MODEL_URL, json={"model": CHAT_MODEL_NAME, "messages": messages, "temperature": temperature},
                      headers={"Authorization": f"Bearer {CHAT_API_KEY}"}, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"Chat failed: {r.status_code} {r.text[:200]}")
    return r.json()["choices"][0]["message"]["content"]

# ===========================================================================
# File Format Converters (DOCX, TXT, CSV → Markdown)
# ===========================================================================
def _convert_to_markdown(filename: str, content_bytes: bytes) -> Optional[str]:
    """Convert DOCX/TXT/CSV bytes to markdown string. Returns None if unsupported."""
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".txt":
        return content_bytes.decode("utf-8", errors="replace")

    if ext == ".csv":
        text = content_bytes.decode("utf-8", errors="replace")
        lines = text.strip().split("\n")
        if not lines:
            return ""
        import csv, io
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        if not rows:
            return ""
        # Build markdown table
        header = rows[0]
        md = "| " + " | ".join(header) + " |\n"
        md += "| " + " | ".join(["---"] * len(header)) + " |\n"
        for row in rows[1:]:
            # Pad/truncate to header length
            padded = row + [""] * (len(header) - len(row))
            md += "| " + " | ".join(padded[:len(header)]) + " |\n"
        return md

    if ext == ".docx":
        try:
            import docx
            import io as _io
            doc = docx.Document(_io.BytesIO(content_bytes))
            parts = []
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue
                style = (para.style.name or "").lower()
                if "heading 1" in style:
                    parts.append(f"# {text}")
                elif "heading 2" in style:
                    parts.append(f"## {text}")
                elif "heading 3" in style:
                    parts.append(f"### {text}")
                elif "heading" in style:
                    parts.append(f"#### {text}")
                else:
                    parts.append(text)
            # Handle tables
            for table in doc.tables:
                rows = []
                for row in table.rows:
                    cells = [cell.text.strip() for cell in row.cells]
                    rows.append(cells)
                if rows:
                    md_table = "| " + " | ".join(rows[0]) + " |\n"
                    md_table += "| " + " | ".join(["---"] * len(rows[0])) + " |\n"
                    for r in rows[1:]:
                        padded = r + [""] * (len(rows[0]) - len(r))
                        md_table += "| " + " | ".join(padded[:len(rows[0])]) + " |\n"
                    parts.append(md_table)
            return "\n\n".join(parts)
        except ImportError:
            log.warning("python-docx not installed — DOCX support unavailable")
            return None

    return None  # Unsupported format

# ===========================================================================
# Endpoints: Sessions
# ===========================================================================
@app.post("/v1/sessions", tags=["Sessions"])
async def create_session(
    api_key: str = Depends(verify_api_key),
    name: str = Body(..., embed=True),
    description: str = Body("", embed=True),
):
    clean = re.sub(r'[^a-z0-9_]', '', name.lower().replace(' ', '_').replace('-', '_'))
    if not clean:
        raise HTTPException(status_code=400, detail="Invalid session name.")
    client = _qclient()
    existing = {c.name for c in client.get_collections().collections}
    if clean in existing:
        return {"status": "exists", "session": clean}
    log.info(f"Session created: {clean}")
    return {"status": "created", "session": clean, "description": description}

@app.get("/v1/sessions", tags=["Sessions"])
async def list_sessions(api_key: str = Depends(verify_api_key)):
    client = _qclient()
    sessions = []
    for c in client.get_collections().collections:
        if c.name == MEMORY_COLLECTION:
            continue
        try:
            info = client.get_collection(c.name)
            count = info.points_count if hasattr(info, 'points_count') else 0
        except Exception:
            count = 0
        sessions.append({"name": c.name, "points": count})
    return {"sessions": sessions, "count": len(sessions)}

@app.get("/v1/sessions/{name}", tags=["Sessions"])
async def get_session_info(name: str, api_key: str = Depends(verify_api_key)):
    client = _qclient()
    existing = {c.name for c in client.get_collections().collections}
    if name not in existing:
        raise HTTPException(status_code=404, detail=f"Session '{name}' not found.")
    info = client.get_collection(name)
    count = info.points_count if hasattr(info, 'points_count') else 0
    filenames = set()
    try:
        points, _ = client.scroll(collection_name=name, limit=200, with_payload=True)
        for pt in points:
            fn = (pt.payload or {}).get("filename")
            if fn:
                filenames.add(fn)
    except Exception:
        pass
    return {"session": name, "points": count, "files": sorted(filenames)}

@app.delete("/v1/sessions/{name}", tags=["Sessions"])
async def delete_session(name: str, api_key: str = Depends(verify_api_key)):
    client = _qclient()
    existing = {c.name for c in client.get_collections().collections}
    if name in existing:
        client.delete_collection(name)
    cleared = clear_session_memory(client, MEMORY_COLLECTION, name)
    log.info(f"Session deleted: {name} (memory cleared: {cleared})")
    return {"status": "deleted", "session": name, "memory_cleared": cleared}

# ===========================================================================
# Endpoints: Health
# ===========================================================================
@app.get("/healthz", tags=["System"])
async def health_check():
    health = {"status": "ok", "services": {}, "version": "3.0.0"}
    for name, port in [("embed_model", os.getenv("EMBED_PORT", "8002")),
                       ("chat_model", os.getenv("CHAT_PORT", "8003"))]:
        try:
            r = requests.get(f"http://127.0.0.1:{port}/health", timeout=3)
            health["services"][name] = "up" if r.status_code == 200 else "degraded"
        except Exception:
            health["services"][name] = "down"
    try:
        r = requests.get(f"{QDRANT_URL}/collections", timeout=3)
        health["services"]["qdrant"] = "up" if r.status_code == 200 else "degraded"
    except Exception:
        health["services"]["qdrant"] = "down"
    if any(v == "down" for v in health["services"].values()):
        health["status"] = "degraded"
    return health

# ===========================================================================
# Endpoints: Metadata
# ===========================================================================
@app.post("/v1/autotag", tags=["Metadata"])
async def autotag_endpoint(api_key: str = Depends(verify_api_key), markdown_content: str = Body(..., embed=True)):
    meta = autotag_document(markdown_content, CHAT_MODEL_URL, CHAT_MODEL_NAME, CHAT_API_KEY, AUTOTAG_MAX_CHARS)
    return {"status": "ok", "metadata": meta}

@app.get("/v1/metadata/{collection}/{filename}", tags=["Metadata"])
async def get_metadata(collection: str, filename: str, api_key: str = Depends(verify_api_key)):
    client = _qclient()
    from qdrant_client.http.models import Filter, FieldCondition, MatchValue
    filt = Filter(must=[FieldCondition(key="filename", match=MatchValue(value=filename))])
    points, _ = client.scroll(collection_name=collection, scroll_filter=filt, limit=1, with_payload=True)
    if not points:
        raise HTTPException(status_code=404, detail=f"No chunks found for '{filename}'")
    return {"filename": filename, "collection": collection, "metadata": (points[0].payload or {}).get("metadata", {})}

@app.patch("/v1/metadata/{collection}/{filename}", tags=["Metadata"])
async def update_metadata(collection: str, filename: str, api_key: str = Depends(verify_api_key), metadata: dict = Body(..., embed=True)):
    client = _qclient()
    from qdrant_client.http.models import Filter, FieldCondition, MatchValue
    filt = Filter(must=[FieldCondition(key="filename", match=MatchValue(value=filename))])
    points, _ = client.scroll(collection_name=collection, scroll_filter=filt, limit=1000, with_payload=False)
    if not points:
        raise HTTPException(status_code=404, detail=f"No chunks found for '{filename}'")
    client.set_payload(collection_name=collection, payload={"metadata": metadata}, points=filt)
    log.info(f"Metadata updated: {filename} | {len(points)} chunks | {collection}")
    return {"status": "ok", "filename": filename, "chunks_updated": len(points), "metadata": metadata}

@app.get("/v1/documents/{collection}", tags=["Metadata"])
async def list_documents(collection: str, api_key: str = Depends(verify_api_key)):
    client = _qclient()
    existing = {c.name for c in client.get_collections().collections}
    if collection not in existing:
        return {"documents": [], "count": 0}
    points, _ = client.scroll(collection_name=collection, limit=5000, with_payload=True)
    docs = {}
    for pt in points:
        p = pt.payload or {}
        fn = p.get("filename", "unknown")
        if fn not in docs:
            docs[fn] = {"filename": fn, "metadata": p.get("metadata", {}), "chunks": 0, "created_at": p.get("created_at", 0)}
        docs[fn]["chunks"] += 1
    return {"documents": list(docs.values()), "count": len(docs)}

# ===========================================================================
# Endpoints: Ingest
# ===========================================================================
def _do_ingest(filename: str, markdown_content: str, collection: str, chunk_size: int, metadata: dict, api_key: str) -> dict:
    """Core ingest logic used by both single and batch endpoints."""
    chunks = chunk_markdown_structural(markdown_content, chunk_size)
    if not chunks:
        return {"status": "empty", "chunks": 0, "collection": collection, "filename": filename}

    texts = [c["text"] for c in chunks]
    embeddings = _embed_batch(texts)
    if len(texts) != len(embeddings):
        raise RuntimeError("Embedding count mismatch")

    client = _qclient()
    ensure_collection(client, collection, len(embeddings[0]))

    # Dedup: remove old chunks for this filename
    delete_document_chunks(client, collection, filename)

    now = int(time.time())
    from qdrant_client.http.models import PointStruct
    points = []
    for i, (chunk_meta, vector) in enumerate(zip(chunks, embeddings)):
        sparse = tokenize_bm25(chunk_meta["text"])
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector={"dense": vector, "bm25": sparse},
            payload={
                "source": "ocr", "filename": filename, "chunk_index": i,
                "text": chunk_meta["text"], "section": chunk_meta["section"],
                "content_type": chunk_meta["content_type"], "created_at": now,
                "metadata": metadata,
            },
        ))

    client.upsert(collection_name=collection, points=points)
    ensure_indexes(client, collection)

    db = API_KEY_DB.get(api_key)
    if db:
        db["metrics"]["total_ingestions"] += 1
        db["metrics"]["total_chunks_ingested"] += len(points)
        db["audit_logs"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": "ingest", "filename": filename, "chunks": len(points), "collection": collection,
        })

    sections_summary = {}
    for c in chunks:
        sections_summary[c["section"]] = sections_summary.get(c["section"], 0) + 1

    log.info(f"Ingested: {filename} | {len(points)} chunks | meta: {metadata.get('doc_type', 'none')}")
    return {"status": "ok", "chunks": len(points), "collection": collection,
            "filename": filename, "sections": sections_summary, "metadata": metadata}


@app.post("/v1/ingest", tags=["RAG"])
async def ingest_document(
    api_key: str = Depends(verify_api_key),
    filename: str = Body(..., embed=True),
    markdown_content: str = Body(None, embed=True),
    raw_content_b64: str = Body(None, embed=True, description="Base64-encoded DOCX/TXT/CSV file"),
    collection: str = Body(None, embed=True),
    chunk_size: int = Body(None, embed=True),
    metadata: dict = Body(None, embed=True),
):
    """Ingest a document. Supports markdown directly, or DOCX/TXT/CSV via raw_content_b64."""
    collection = collection or QDRANT_COLLECTION
    chunk_size = chunk_size or RAG_CHUNK_SIZE
    metadata = metadata or {}

    # Handle non-markdown file formats
    if not markdown_content and raw_content_b64:
        import base64
        raw_bytes = base64.b64decode(raw_content_b64)
        markdown_content = _convert_to_markdown(filename, raw_bytes)
        if markdown_content is None:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {filename}")

    if not markdown_content:
        raise HTTPException(status_code=400, detail="No content provided (markdown_content or raw_content_b64 required)")

    try:
        return _do_ingest(filename, markdown_content, collection, chunk_size, metadata, api_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/v1/ingest/batch", tags=["RAG"])
async def ingest_batch(
    api_key: str = Depends(verify_api_key),
    documents: List[dict] = Body(..., embed=True, description="List of {filename, markdown_content, metadata?}"),
    collection: str = Body(None, embed=True),
    chunk_size: int = Body(None, embed=True),
):
    """Batch ingest multiple documents. Each item: {filename, markdown_content, metadata?}."""
    collection = collection or QDRANT_COLLECTION
    chunk_size = chunk_size or RAG_CHUNK_SIZE
    results = []
    for doc in documents:
        fname = doc.get("filename", "unknown")
        content = doc.get("markdown_content", "")
        meta = doc.get("metadata", {})
        try:
            r = _do_ingest(fname, content, collection, chunk_size, meta, api_key)
            results.append(r)
        except Exception as e:
            results.append({"status": "error", "filename": fname, "error": str(e)})
    total_chunks = sum(r.get("chunks", 0) for r in results)
    return {"status": "ok", "documents": len(results), "total_chunks": total_chunks, "results": results}

# ===========================================================================
# Endpoints: Chat (FAST by default)
# ===========================================================================
@app.post("/v1/chat", tags=["RAG"])
async def chat_with_documents(
    api_key: str = Depends(verify_api_key),
    query: str = Body(..., embed=True),
    collection: str = Body(None, embed=True),
    top_k: int = Body(None, embed=True),
    system_prompt: str = Body(None, embed=True),
    session_id: str = Body(None, embed=True),
    memory_enabled: bool = Body(True, embed=True),
    memory_top_k: int = Body(None, embed=True),
    filters: dict = Body(None, embed=True),
    auto_extract_filters: bool = Body(False, embed=True),
    rerank: bool = Body(False, embed=True),
    agentic: bool = Body(False, embed=True),
):
    """
    RAG chat. Fast by default (1 embed + 1 search + 1 answer).
    Set rerank=true and/or agentic=true for enhanced (but slower) retrieval.
    """
    collection = collection or QDRANT_COLLECTION
    top_k = top_k or RAG_TOP_K
    memory_top_k = memory_top_k or MEMORY_TOP_K
    use_memory = bool(session_id) and memory_enabled and MEMORY_ENABLED

    try:
        t0 = time.time()
        client = _qclient()

        # --- Optional: auto-extract filters (OFF by default) ---
        active_filters = filters or {}
        if auto_extract_filters and not filters:
            try:
                active_filters = extract_filters_from_query(query, CHAT_MODEL_URL, CHAT_MODEL_NAME, CHAT_API_KEY)
                if active_filters:
                    log.info(f"Auto-extracted filters: {active_filters}")
            except Exception:
                pass

        # --- Retrieve ---
        if agentic:
            query_vector, sources = plan_query(
                query, client, collection,
                EMBED_MODEL_URL, EMBED_MODEL_NAME, EMBED_API_KEY,
                CHAT_MODEL_URL, CHAT_MODEL_NAME, CHAT_API_KEY,
                top_k, active_filters,
            )
        else:
            query_vector, sources = retrieve(
                query, client, collection,
                EMBED_MODEL_URL, EMBED_MODEL_NAME, EMBED_API_KEY,
                top_k, active_filters,
            )

        # --- Optional: re-rank (OFF by default) ---
        if rerank and sources:
            sources = rerank_chunks(query, sources, CHAT_MODEL_URL, CHAT_MODEL_NAME, CHAT_API_KEY)

        # --- Memory ---
        memories = []
        if use_memory:
            memories = search_memory(client, MEMORY_COLLECTION, session_id, query_vector, memory_top_k)

        if not sources and not memories:
            return {"answer": "No relevant information found.", "sources": [], "memories": [], "latency": round(time.time() - t0, 2)}

        # --- Build context & answer ---
        context, sources = build_context(sources, memories, MAX_CONTEXT_TOKENS)

        sys_text = system_prompt or (
            "You are a helpful RAG assistant with access to document context. "
            "Use the provided context to answer questions accurately. "
            "If conversation history is available, use it for follow-up context. "
            "Cite sources when referencing specific documents. "
            "For basic or general questions, answer naturally. "
            "If the question requires document-specific information that is not in the context, "
            "let the user know the information was not found in the available documents."
        )
        user_text = f"Answer the question using the context below. Cite sources when possible.\n\n{context}\n\nQuestion: {query}"
        answer = _chat([{"role": "system", "content": sys_text}, {"role": "user", "content": user_text}])

        # --- Async memory storage ---
        if use_memory:
            store_memory_async(
                _qclient, MEMORY_COLLECTION, session_id, query, answer,
                lambda t: _embed(t),
            )

        # --- Metrics ---
        latency = round(time.time() - t0, 2)
        db = API_KEY_DB.get(api_key)
        if db:
            db["metrics"]["total_queries"] += 1
            db["audit_logs"].append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "action": "chat", "query": query[:100],
                "sources_count": len(sources), "memories_used": len(memories),
                "session_id": session_id or "(none)", "collection": collection,
                "latency": latency, "rerank": rerank, "agentic": agentic,
            })

        log.info(f"Chat: '{query[:50]}...' | {len(sources)} docs | {len(memories)} mem | {latency}s")
        return {"answer": answer, "sources": sources, "memories": memories, "latency": latency}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

# ===========================================================================
# Endpoints: Memory
# ===========================================================================
@app.get("/v1/memory/{session_id}", tags=["Memory"])
async def list_memory(session_id: str, api_key: str = Depends(verify_api_key)):
    memories = list_session_memory(_qclient(), MEMORY_COLLECTION, session_id)
    return {"session_id": session_id, "memories": memories, "count": len(memories)}

@app.delete("/v1/memory/{session_id}", tags=["Memory"])
async def delete_memory(session_id: str, api_key: str = Depends(verify_api_key)):
    count = clear_session_memory(_qclient(), MEMORY_COLLECTION, session_id)
    log.info(f"Cleared {count} memories for session {session_id[:8]}...")
    return {"session_id": session_id, "cleared": count}

@app.get("/v1/metrics", tags=["System"])
async def get_metrics(api_key: str = Depends(verify_api_key)):
    return API_KEY_DB[api_key]

# ===========================================================================
# Standalone Runner
# ===========================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("rag_service:app", host=os.getenv("API_HOST", "0.0.0.0"),
                port=int(os.getenv("API_PORT", "8081")), log_level="info")
