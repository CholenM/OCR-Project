"""
RAG Pipeline Service v2 — DGX Spark
=====================================
Session-based RAG with per-chat vector stores, conversational memory,
and Markdown-aware structural chunking.

Endpoints:
  POST   /v1/sessions          — Create a new session (vector store)
  GET    /v1/sessions          — List all sessions
  GET    /v1/sessions/{name}   — Get session info (doc count, etc.)
  DELETE /v1/sessions/{name}   — Delete session + its memory
  POST   /v1/ingest            — Structural chunk + embed + store
  POST   /v1/chat              — Memory-augmented RAG chat
  GET    /v1/memory/{sid}      — List memories for a session
  DELETE /v1/memory/{sid}      — Clear session memory
  GET    /v1/metrics           — Usage telemetry
  GET    /healthz              — Health check
"""

import os, re, time, uuid, logging, math, json
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, Header, Body
from fastapi.middleware.cors import CORSMiddleware
import requests
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance, PointStruct, VectorParams, Filter, FieldCondition, MatchValue,
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
RAG_TOP_K         = int(os.getenv("RAG_TOP_K", "30"))
MEMORY_TOP_K      = int(os.getenv("MEMORY_TOP_K", "5"))
MEMORY_ENABLED    = os.getenv("MEMORY_ENABLED", "true").lower() == "true"
AUTOTAG_MAX_CHARS = int(os.getenv("AUTOTAG_MAX_CHARS", "3000"))

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
app = FastAPI(title="RAG Pipeline API v2 — DGX Spark", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

log.info(f"Embed: {EMBED_MODEL_URL} | Chat: {CHAT_MODEL_URL} | Qdrant: {QDRANT_URL}")
log.info(f"Memory: collection={MEMORY_COLLECTION}, enabled={MEMORY_ENABLED}, top_k={MEMORY_TOP_K}")

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key not in API_KEY_DB:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    if not API_KEY_DB[x_api_key]["active"]:
        raise HTTPException(status_code=403, detail="Account Deactivated.")
    return x_api_key

# ===========================================================================
# Embedding + Chat LLM (unchanged from v1)
# ===========================================================================
def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    r = requests.post(EMBED_MODEL_URL, json={"input": texts, "model": EMBED_MODEL_NAME},
                      headers={"Authorization": f"Bearer {EMBED_API_KEY}"}, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"Embedding failed: {r.status_code} {r.text}")
    data = r.json().get("data", [])
    if not data:
        raise RuntimeError("Embedding returned no vectors")
    data.sort(key=lambda x: x.get("index", 0))
    return [item["embedding"] for item in data]

def embed_single(text: str) -> List[float]:
    res = embed_texts([text])
    if not res:
        raise RuntimeError("Empty embedding")
    return res[0]

def chat_completion(messages: List[Dict], temperature: float = 0.7) -> str:
    r = requests.post(CHAT_MODEL_URL, json={"model": CHAT_MODEL_NAME, "messages": messages, "temperature": temperature},
                      headers={"Authorization": f"Bearer {CHAT_API_KEY}"}, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"Chat failed: {r.status_code} {r.text}")
    return r.json()["choices"][0]["message"]["content"]


# ===========================================================================
# Metadata: Auto-Tagging & Filter Extraction
# ===========================================================================

AUTOTAG_PROMPT = """Analyze this document and return ONLY a valid JSON object with these fields:
{
  "doc_type": "invoice|contract|report|letter|memo|receipt|policy|form|certificate|other",
  "date": "YYYY-MM-DD or null if not found",
  "parties": ["list of people or organizations mentioned"],
  "tags": ["3-7 relevant topic keywords"],
  "summary": "One concise sentence describing the document"
}

Rules:
- Return ONLY the JSON, no explanation
- Use lowercase for doc_type and tags
- If a field cannot be determined, use null or empty list

Document:
---
{text}
---"""

FILTER_EXTRACT_PROMPT = """Given this user query, extract metadata filters to narrow document search.
Return ONLY a valid JSON object. Only include fields you can confidently extract.
Return {} if no filters can be extracted.

Available filters:
- "doc_type": string (invoice, contract, report, letter, memo, receipt, policy, form, certificate)
- "tags": list of keyword strings
- "parties": list of people/organization names
- "date_from": "YYYY-MM-DD" (documents from this date onwards)
- "date_to": "YYYY-MM-DD" (documents up to this date)
- "filename": partial filename match

Query: {query}"""


def autotag_document(markdown_text: str) -> dict:
    """Use Chat LLM to auto-generate metadata tags from document text."""
    snippet = (markdown_text or "")[:AUTOTAG_MAX_CHARS]
    if not snippet.strip():
        return {}
    try:
        prompt = AUTOTAG_PROMPT.replace("{text}", snippet)
        raw = chat_completion([{"role": "user", "content": prompt}], temperature=0.1)
        # Extract JSON from response (handle markdown code blocks)
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0]
        result = json.loads(cleaned)
        # Ensure expected fields exist
        schema = {"doc_type": "other", "date": None, "parties": [], "tags": [], "summary": ""}
        for k, default in schema.items():
            if k not in result:
                result[k] = default
        return result
    except Exception as e:
        log.warning(f"Auto-tag failed: {e}")
        return {"doc_type": "other", "date": None, "parties": [], "tags": [], "summary": "", "_error": str(e)}


def extract_filters_from_query(query: str) -> dict:
    """Use Chat LLM to extract metadata filters from a natural language query."""
    try:
        prompt = FILTER_EXTRACT_PROMPT.replace("{query}", query)
        raw = chat_completion([{"role": "user", "content": prompt}], temperature=0.0)
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0]
        return json.loads(cleaned)
    except Exception as e:
        log.warning(f"Filter extraction failed: {e}")
        return {}

# ===========================================================================
# IMPROVEMENT 2: Markdown-Aware Structural Chunking
# ===========================================================================

def _split_by_headers(text: str) -> List[tuple]:
    """Split text into (header, body) tuples at Markdown header boundaries."""
    pattern = re.compile(r'^(#{1,6}\s+.+)$', re.MULTILINE)
    parts = pattern.split(text)
    sections = []
    i = 0
    # Content before first header
    if parts and not parts[0].strip().startswith('#'):
        if parts[0].strip():
            sections.append(("", parts[0]))
        i = 1
    while i < len(parts):
        if parts[i].strip().startswith('#'):
            header = parts[i].strip()
            body = parts[i + 1] if i + 1 < len(parts) else ""
            sections.append((header, body))
            i += 2
        else:
            if parts[i].strip():
                sections.append(("", parts[i]))
            i += 1
    return sections


def _extract_tables_and_text(text: str) -> List[tuple]:
    """Split section body into [(content, type)] preserving HTML/Markdown tables as atomic units."""
    results = []
    # Handle HTML tables first
    html_pattern = re.compile(r'(<table\b.*?</table>)', re.DOTALL | re.IGNORECASE)
    last = 0
    for m in html_pattern.finditer(text):
        before = text[last:m.start()].strip()
        if before:
            results.extend(_extract_md_tables(before))
        results.append((m.group(0), "table"))
        last = m.end()
    after = text[last:].strip()
    if after:
        results.extend(_extract_md_tables(after))
    if not results and text.strip():
        results = _extract_md_tables(text)
    return results if results else [(text, _detect_type(text))]


def _extract_md_tables(text: str) -> List[tuple]:
    """Extract Markdown pipe-delimited tables from text."""
    lines = text.split('\n')
    parts, buf, table_buf, in_table = [], [], [], False
    for line in lines:
        s = line.strip()
        is_tbl = s.startswith('|') and s.endswith('|') and '|' in s[1:-1]
        if is_tbl:
            if not in_table:
                joined = '\n'.join(buf).strip()
                if joined:
                    parts.append((joined, _detect_type(joined)))
                buf = []
                in_table = True
            table_buf.append(line)
        else:
            if in_table:
                joined = '\n'.join(table_buf).strip()
                if joined:
                    parts.append((joined, "table"))
                table_buf = []
                in_table = False
            buf.append(line)
    if in_table and table_buf:
        parts.append(('\n'.join(table_buf).strip(), "table"))
    elif buf:
        joined = '\n'.join(buf).strip()
        if joined:
            parts.append((joined, _detect_type(joined)))
    return parts


def _detect_type(text: str) -> str:
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    if not lines:
        return "prose"
    list_ct = sum(1 for l in lines if re.match(r'^[-*•]\s|^\d+\.\s', l))
    return "list" if lines and list_ct / len(lines) > 0.4 else "prose"


def _split_sentences(text: str, max_size: int, header: str = "") -> List[str]:
    """Split large prose at sentence/line boundaries, prepending header."""
    units = re.split(r'(?<=[.!?])\s+|\n', text)
    units = [u.strip() for u in units if u.strip()]
    chunks, current = [], header + "\n" if header else ""
    for unit in units:
        candidate = f"{current}\n{unit}" if current.strip() else (f"{header}\n{unit}" if header else unit)
        if len(candidate) <= max_size:
            current = candidate
        else:
            if current.strip() and current.strip() != header:
                chunks.append(current)
            current = f"{header}\n{unit}" if header else unit
    if current.strip() and current.strip() != header:
        chunks.append(current)
    return chunks


def chunk_markdown_structural(text: str, max_chunk_size: int = None) -> List[Dict]:
    """
    Markdown-aware chunking. Returns list of:
      {"text": str, "section": str, "content_type": str}

    Rules:
      - Tables are NEVER split (kept as atomic chunks)
      - Section headers are chunk boundaries
      - Each chunk is prefixed with its section header
      - Large prose is split at sentence boundaries
    """
    max_chunk_size = max_chunk_size or RAG_CHUNK_SIZE
    cleaned = (text or "").strip()
    if not cleaned:
        return []

    sections = _split_by_headers(cleaned)
    chunks = []

    for header, body in sections:
        if not body.strip():
            continue

        parts = _extract_tables_and_text(body)

        for part_text, part_type in parts:
            if not part_text.strip():
                continue

            enriched = f"{header}\n{part_text}" if header else part_text

            if part_type == "table" or len(enriched) <= max_chunk_size:
                # Tables never split; small content stays intact
                chunks.append({"text": enriched, "section": header or "(preamble)", "content_type": part_type})
            else:
                # Large prose/list: split at sentence boundaries
                for sc in _split_sentences(part_text, max_chunk_size, header):
                    chunks.append({"text": sc, "section": header or "(preamble)", "content_type": part_type})

    return chunks


# ===========================================================================
# Qdrant Operations
# ===========================================================================
def _qclient() -> QdrantClient:
    return QdrantClient(url=QDRANT_URL)

def ensure_collection(client, name, vector_size):
    existing = {c.name for c in client.get_collections().collections}
    if name not in existing:
        client.create_collection(collection_name=name,
                                 vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE))

def _search(client, collection, vector, limit, filt=None):
    """Search Qdrant, compatible with multiple client versions."""
    if hasattr(client, "search"):
        kw = {"collection_name": collection, "query_vector": vector, "limit": limit, "with_payload": True}
        if filt:
            kw["query_filter"] = filt
        return client.search(**kw)
    if hasattr(client, "query_points"):
        kw = {"collection_name": collection, "query": vector, "limit": limit, "with_payload": True}
        if filt:
            kw["query_filter"] = filt
        resp = client.query_points(**kw)
        return resp.points if hasattr(resp, "points") else resp
    raise AttributeError("No supported search method")


def build_qdrant_filter(filters: dict) -> Optional[Filter]:
    """Convert a user-friendly filters dict into a Qdrant Filter object."""
    if not filters:
        return None
    must = []
    if filters.get("doc_type"):
        must.append(FieldCondition(key="metadata.doc_type", match=MatchValue(value=filters["doc_type"])))
    for tag in (filters.get("tags") or []):
        must.append(FieldCondition(key="metadata.tags", match=MatchValue(value=tag)))
    for party in (filters.get("parties") or []):
        must.append(FieldCondition(key="metadata.parties", match=MatchValue(value=party)))
    if filters.get("filename"):
        must.append(FieldCondition(key="filename", match=MatchValue(value=filters["filename"])))
    # Date filtering: stored as string YYYY-MM-DD, use range on metadata.date
    if filters.get("date_from") or filters.get("date_to"):
        from qdrant_client.http.models import Range
        range_kw = {}
        if filters.get("date_from"):
            range_kw["gte"] = filters["date_from"]
        if filters.get("date_to"):
            range_kw["lte"] = filters["date_to"]
        if range_kw:
            must.append(FieldCondition(key="metadata.date", range=Range(**range_kw)))
    return Filter(must=must) if must else None

# ===========================================================================
# IMPROVEMENT 1: Conversational Memory
# ===========================================================================

def store_memory(client, session_id: str, query: str, answer: str, vector: List[float]):
    """Store a Q&A pair in the memory collection."""
    ensure_collection(client, MEMORY_COLLECTION, len(vector))
    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=vector,
        payload={
            "session_id": session_id,
            "query": query,
            "answer": answer,
            "timestamp": int(time.time()),
        },
    )
    client.upsert(collection_name=MEMORY_COLLECTION, points=[point])


def search_memory(client, session_id: str, vector: List[float], top_k: int) -> List[dict]:
    """Retrieve relevant past Q&A from memory, filtered by session."""
    try:
        existing = {c.name for c in client.get_collections().collections}
        if MEMORY_COLLECTION not in existing:
            return []

        filt = Filter(must=[FieldCondition(key="session_id", match=MatchValue(value=session_id))])
        results = _search(client, MEMORY_COLLECTION, vector, top_k, filt=filt)

        memories = []
        for pt in results:
            p = pt.payload or {}
            memories.append({
                "query": p.get("query", ""),
                "answer": p.get("answer", ""),
                "score": pt.score,
                "timestamp": p.get("timestamp", 0),
            })
        return memories
    except Exception as e:
        log.warning(f"Memory search failed: {e}")
        return []


def clear_session_memory(client, session_id: str) -> int:
    """Delete all memory points for a session. Returns count deleted."""
    try:
        existing = {c.name for c in client.get_collections().collections}
        if MEMORY_COLLECTION not in existing:
            return 0

        # Scroll to find all points with this session_id, then delete by IDs
        filt = Filter(must=[FieldCondition(key="session_id", match=MatchValue(value=session_id))])
        points, _ = client.scroll(collection_name=MEMORY_COLLECTION, scroll_filter=filt, limit=1000, with_payload=False)
        if not points:
            return 0
        ids = [p.id for p in points]
        client.delete(collection_name=MEMORY_COLLECTION, points_selector=ids)
        return len(ids)
    except Exception as e:
        log.warning(f"Memory clear failed: {e}")
        return 0

# ===========================================================================
# Endpoints
# ===========================================================================

# --- Session Management ---

@app.post("/v1/sessions", tags=["Sessions"])
async def create_session(
    api_key: str = Depends(verify_api_key),
    name: str = Body(..., embed=True, description="Session/collection name"),
    description: str = Body("", embed=True),
):
    """Create a new session. Each session is a dedicated Qdrant collection."""
    # Sanitize name: lowercase, replace spaces with underscores, strip special chars
    clean = re.sub(r'[^a-z0-9_]', '', name.lower().replace(' ', '_').replace('-', '_'))
    if not clean:
        raise HTTPException(status_code=400, detail="Invalid session name.")
    try:
        client = _qclient()
        existing = {c.name for c in client.get_collections().collections}
        if clean in existing:
            return {"status": "exists", "session": clean, "message": "Session already exists."}
        # Create with a placeholder — real vector size set on first ingest
        # We'll use a temporary size; ensure_collection in /v1/ingest handles the real creation
        log.info(f"Session created: {clean}")
        return {"status": "created", "session": clean, "description": description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/sessions", tags=["Sessions"])
async def list_sessions(api_key: str = Depends(verify_api_key)):
    """List all sessions (Qdrant collections) with point counts."""
    try:
        client = _qclient()
        collections = client.get_collections().collections
        sessions = []
        for c in collections:
            if c.name == MEMORY_COLLECTION:
                continue  # Skip internal memory collection
            try:
                info = client.get_collection(c.name)
                count = info.points_count if hasattr(info, 'points_count') else 0
            except Exception:
                count = 0
            sessions.append({"name": c.name, "points": count})
        return {"sessions": sessions, "count": len(sessions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/sessions/{name}", tags=["Sessions"])
async def get_session_info(name: str, api_key: str = Depends(verify_api_key)):
    """Get details about a session: point count, stored filenames, sections."""
    try:
        client = _qclient()
        existing = {c.name for c in client.get_collections().collections}
        if name not in existing:
            raise HTTPException(status_code=404, detail=f"Session '{name}' not found.")
        info = client.get_collection(name)
        count = info.points_count if hasattr(info, 'points_count') else 0

        # Get unique filenames
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/v1/sessions/{name}", tags=["Sessions"])
async def delete_session(name: str, api_key: str = Depends(verify_api_key)):
    """Delete a session and its associated memory."""
    try:
        client = _qclient()
        existing = {c.name for c in client.get_collections().collections}
        deleted_items = []
        if name in existing:
            client.delete_collection(name)
            deleted_items.append(name)
        # Also clear any memory tied to this session name
        cleared = clear_session_memory(client, name)
        log.info(f"Session deleted: {name} (memory cleared: {cleared})")
        return {"status": "deleted", "session": name, "memory_cleared": cleared}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Health ---

@app.get("/healthz", tags=["System"])
async def health_check():
    health = {"status": "ok", "services": {}}
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


# --- Auto-Tag & Metadata ---

@app.post("/v1/autotag", tags=["Metadata"])
async def autotag_endpoint(
    api_key: str = Depends(verify_api_key),
    markdown_content: str = Body(..., embed=True),
):
    """Auto-generate metadata tags from document text using LLM."""
    try:
        metadata = autotag_document(markdown_content)
        return {"status": "ok", "metadata": metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/metadata/{collection}/{filename}", tags=["Metadata"])
async def get_metadata(collection: str, filename: str, api_key: str = Depends(verify_api_key)):
    """Get metadata for all chunks of a document."""
    try:
        client = _qclient()
        filt = Filter(must=[FieldCondition(key="filename", match=MatchValue(value=filename))])
        points, _ = client.scroll(collection_name=collection, scroll_filter=filt,
                                  limit=1, with_payload=True)
        if not points:
            raise HTTPException(status_code=404, detail=f"No chunks found for '{filename}'")
        p = points[0].payload or {}
        return {
            "filename": filename, "collection": collection,
            "metadata": p.get("metadata", {}),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/v1/metadata/{collection}/{filename}", tags=["Metadata"])
async def update_metadata(
    collection: str, filename: str,
    api_key: str = Depends(verify_api_key),
    metadata: dict = Body(..., embed=True),
):
    """Update metadata on all chunks of a document WITHOUT re-embedding."""
    try:
        client = _qclient()
        filt = Filter(must=[FieldCondition(key="filename", match=MatchValue(value=filename))])
        # Count affected points
        points, _ = client.scroll(collection_name=collection, scroll_filter=filt,
                                  limit=1000, with_payload=False)
        if not points:
            raise HTTPException(status_code=404, detail=f"No chunks found for '{filename}'")
        # Update payload on all matching points — vectors untouched
        client.set_payload(
            collection_name=collection,
            payload={"metadata": metadata},
            points=filt,
        )
        log.info(f"Metadata updated: {filename} | {len(points)} chunks | {collection}")
        return {"status": "ok", "filename": filename, "chunks_updated": len(points),
                "metadata": metadata}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/documents/{collection}", tags=["Metadata"])
async def list_documents(collection: str, api_key: str = Depends(verify_api_key)):
    """List all unique documents in a collection with their metadata."""
    try:
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
                docs[fn] = {
                    "filename": fn,
                    "metadata": p.get("metadata", {}),
                    "chunks": 0,
                    "created_at": p.get("created_at", 0),
                }
            docs[fn]["chunks"] += 1
        return {"documents": list(docs.values()), "count": len(docs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Ingest ---

@app.post("/v1/ingest", tags=["RAG"])
async def ingest_document(
    api_key: str = Depends(verify_api_key),
    filename: str = Body(..., embed=True),
    markdown_content: str = Body(..., embed=True),
    collection: str = Body(None, embed=True),
    chunk_size: int = Body(None, embed=True),
    metadata: dict = Body(None, embed=True),
):
    """Ingest markdown with metadata. Structural chunking, tables intact."""
    collection = collection or QDRANT_COLLECTION
    chunk_size = chunk_size or RAG_CHUNK_SIZE
    metadata = metadata or {}
    try:
        structured_chunks = chunk_markdown_structural(markdown_content, chunk_size)
        if not structured_chunks:
            return {"status": "empty", "chunks": 0, "collection": collection}

        texts = [c["text"] for c in structured_chunks]
        embeddings = embed_texts(texts)
        if len(texts) != len(embeddings):
            raise RuntimeError("Embedding count mismatch")

        client = _qclient()
        ensure_collection(client, collection, len(embeddings[0]))

        now = int(time.time())
        points = []
        for i, (chunk_meta, vector) in enumerate(zip(structured_chunks, embeddings)):
            payload = {
                "source": "ocr",
                "filename": filename,
                "chunk_index": i,
                "text": chunk_meta["text"],
                "section": chunk_meta["section"],
                "content_type": chunk_meta["content_type"],
                "created_at": now,
                "metadata": metadata,
            }
            points.append(PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload))

        client.upsert(collection_name=collection, points=points)

        # Create payload indexes for filtered search (idempotent)
        try:
            from qdrant_client.http.models import PayloadSchemaType
            for field in ["metadata.doc_type", "metadata.tags", "metadata.date", "filename"]:
                client.create_payload_index(collection_name=collection, field_name=field,
                                            field_schema=PayloadSchemaType.KEYWORD)
        except Exception:
            pass  # Indexes may already exist

        db = API_KEY_DB[api_key]
        db["metrics"]["total_ingestions"] += 1
        db["metrics"]["total_chunks_ingested"] += len(points)
        db["audit_logs"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": "ingest", "filename": filename,
            "chunks": len(points), "collection": collection,
        })

        sections_summary = {}
        for c in structured_chunks:
            sections_summary[c["section"]] = sections_summary.get(c["section"], 0) + 1

        log.info(f"Ingested: {filename} | {len(points)} chunks | meta: {metadata.get('doc_type', 'none')}")
        return {"status": "ok", "chunks": len(points), "collection": collection,
                "sections": sections_summary, "metadata": metadata}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


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
):
    """Memory-augmented RAG chat with metadata filtering."""
    collection = collection or QDRANT_COLLECTION
    top_k = top_k or RAG_TOP_K
    memory_top_k = memory_top_k or MEMORY_TOP_K
    use_memory = bool(session_id) and memory_enabled and MEMORY_ENABLED

    try:
        # --- Auto-extract filters from query if enabled ---
        active_filters = filters or {}
        extracted_filters = {}
        if auto_extract_filters and not filters:
            try:
                extracted_filters = extract_filters_from_query(query)
                active_filters = extracted_filters
                if extracted_filters:
                    log.info(f"Auto-extracted filters: {extracted_filters}")
            except Exception as e:
                log.warning(f"Filter extraction skipped: {e}")

        qdrant_filter = build_qdrant_filter(active_filters)
        query_vector = embed_single(query)
        client = _qclient()

        # --- Document retrieval (with filters + fallback) ---
        doc_results = _search(client, collection, query_vector, top_k, filt=qdrant_filter)

        # Fallback: if filters returned nothing, retry without filters
        if not doc_results and qdrant_filter:
            log.info("Filtered search returned 0 results — retrying without filters")
            doc_results = _search(client, collection, query_vector, top_k)

        sources = []
        for pt in doc_results:
            p = pt.payload or {}
            sources.append({
                "text": p.get("text", ""), "filename": p.get("filename", "unknown"),
                "chunk_index": p.get("chunk_index", 0), "section": p.get("section", ""),
                "content_type": p.get("content_type", ""), "score": pt.score,
                "type": "document",
            })

        # --- Memory retrieval ---
        memories = []
        if use_memory:
            memories = search_memory(client, session_id, query_vector, memory_top_k)

        # --- Build context ---
        context_parts = []

        if memories:
            context_parts.append("=== CONVERSATION HISTORY ===")
            for m in memories:
                context_parts.append(f"[Previous Q&A | relevance {m['score']:.4f}]")
                context_parts.append(f"Q: {m['query']}\nA: {m['answer']}")

        if sources:
            context_parts.append("\n=== DOCUMENT CONTEXT ===")
            for s in sources:
                header = f"[{s['filename']} | {s['section']} | {s['content_type']} | score {s['score']:.4f}]"
                context_parts.append(f"{header}\n{s['text']}")

        if not sources and not memories:
            return {"answer": "No relevant information found.", "sources": [], "memories": []}

        context = "\n\n".join(context_parts)

        sys_text = system_prompt or (
            "You are a helpful RAG assistant with access to document context. "
            "Use the provided context to answer questions accurately. "
            "If conversation history is available, use it for follow-up context. "
            "Cite sources when referencing specific documents. "
            "For basic or general questions, answer naturally. "
            "If the question requires document-specific information that is not in the context, "
            "let the user know the information was not found in the available documents."
        )
        user_text = (
            "Answer the question using the context below. Cite sources when possible.\n\n"
            f"{context}\n\nQuestion: {query}"
        )
        answer = chat_completion([{"role": "system", "content": sys_text}, {"role": "user", "content": user_text}])

        # --- Store memory ---
        if use_memory:
            qa_text = f"Q: {query}\nA: {answer}"
            qa_vector = embed_single(qa_text)
            store_memory(client, session_id, query, answer, qa_vector)
            log.info(f"Memory stored for session {session_id[:8]}...")

        # --- Metrics ---
        db = API_KEY_DB[api_key]
        db["metrics"]["total_queries"] += 1
        db["audit_logs"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": "chat", "query": query[:100],
            "sources_count": len(sources), "memories_used": len(memories),
            "session_id": session_id or "(none)", "collection": collection,
        })

        log.info(f"Chat: '{query[:50]}...' | {len(sources)} docs | {len(memories)} memories")
        return {"answer": answer, "sources": sources, "memories": memories}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.get("/v1/memory/{session_id}", tags=["Memory"])
async def list_memory(session_id: str, api_key: str = Depends(verify_api_key)):
    """List stored memories for a session."""
    try:
        client = _qclient()
        existing = {c.name for c in client.get_collections().collections}
        if MEMORY_COLLECTION not in existing:
            return {"session_id": session_id, "memories": [], "count": 0}

        filt = Filter(must=[FieldCondition(key="session_id", match=MatchValue(value=session_id))])
        points, _ = client.scroll(collection_name=MEMORY_COLLECTION, scroll_filter=filt, limit=100, with_payload=True)

        memories = []
        for pt in points:
            p = pt.payload or {}
            memories.append({"query": p.get("query"), "answer": p.get("answer"),
                             "timestamp": p.get("timestamp")})
        memories.sort(key=lambda x: x.get("timestamp", 0))
        return {"session_id": session_id, "memories": memories, "count": len(memories)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/v1/memory/{session_id}", tags=["Memory"])
async def delete_memory(session_id: str, api_key: str = Depends(verify_api_key)):
    """Clear all memories for a session."""
    try:
        client = _qclient()
        count = clear_session_memory(client, session_id)
        log.info(f"Cleared {count} memories for session {session_id[:8]}...")
        return {"session_id": session_id, "cleared": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/metrics", tags=["System"])
async def get_metrics(api_key: str = Depends(verify_api_key)):
    return API_KEY_DB[api_key]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("rag_service:app", host=os.getenv("API_HOST", "0.0.0.0"),
                port=int(os.getenv("API_PORT", "8081")), log_level="info")
