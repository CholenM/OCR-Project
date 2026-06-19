"""
Memory — Conversational Memory Store & Retrieval
=================================================
Isolated memory operations for session-based chat.
Uses dense-only vectors (BM25 not useful for Q&A memory).
"""

import uuid
import time
import logging
import threading
from typing import List, Dict, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance, PointStruct, VectorParams, Filter, FieldCondition, MatchValue,
)

log = logging.getLogger("rag-pipeline")


# ---------------------------------------------------------------------------
# Memory Collection Setup (dense-only — BM25 not useful for Q&A memory)
# ---------------------------------------------------------------------------
def _ensure_memory_collection(client: QdrantClient, collection: str, vector_size: int):
    """Create dense-only memory collection if it doesn't exist."""
    existing = {c.name for c in client.get_collections().collections}
    if collection not in existing:
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        log.info(f"Created memory collection: {collection} (dense={vector_size})")


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------
def store_memory(
    client: QdrantClient,
    collection: str,
    session_id: str,
    query: str,
    answer: str,
    vector: List[float],
):
    """Store a Q&A pair in the memory collection."""
    _ensure_memory_collection(client, collection, len(vector))
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
    client.upsert(collection_name=collection, points=[point])


def store_memory_async(
    client_factory,
    collection: str,
    session_id: str,
    query: str,
    answer: str,
    embed_fn,
):
    """Non-blocking memory storage in a background thread."""
    def _bg():
        try:
            qa_text = f"Q: {query}\nA: {answer}"
            vector = embed_fn(qa_text)
            client = client_factory()
            store_memory(client, collection, session_id, query, answer, vector)
            log.info(f"Memory stored (async) for session {session_id[:8]}...")
        except Exception as e:
            log.warning(f"Async memory storage failed: {e}")
    threading.Thread(target=_bg, daemon=True).start()


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------
def search_memory(
    client: QdrantClient,
    collection: str,
    session_id: str,
    vector: List[float],
    top_k: int,
) -> List[dict]:
    """Retrieve relevant past Q&A from memory, filtered by session."""
    try:
        existing = {c.name for c in client.get_collections().collections}
        if collection not in existing:
            return []

        filt = Filter(must=[FieldCondition(key="session_id", match=MatchValue(value=session_id))])

        # Dense-only search for memory (no BM25)
        if hasattr(client, "search"):
            results = client.search(
                collection_name=collection, query_vector=vector,
                limit=top_k, with_payload=True, query_filter=filt,
            )
        elif hasattr(client, "query_points"):
            resp = client.query_points(
                collection_name=collection, query=vector,
                limit=top_k, with_payload=True, query_filter=filt,
            )
            results = resp.points if hasattr(resp, "points") else resp
        else:
            return []

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


# ---------------------------------------------------------------------------
# Clear
# ---------------------------------------------------------------------------
def clear_session_memory(client: QdrantClient, collection: str, session_id: str) -> int:
    """Delete all memory points for a session. Returns count deleted."""
    try:
        existing = {c.name for c in client.get_collections().collections}
        if collection not in existing:
            return 0

        filt = Filter(must=[FieldCondition(key="session_id", match=MatchValue(value=session_id))])
        points, _ = client.scroll(
            collection_name=collection, scroll_filter=filt,
            limit=1000, with_payload=False,
        )
        if not points:
            return 0
        ids = [p.id for p in points]
        client.delete(collection_name=collection, points_selector=ids)
        return len(ids)
    except Exception as e:
        log.warning(f"Memory clear failed: {e}")
        return 0


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------
def list_session_memory(
    client: QdrantClient,
    collection: str,
    session_id: str,
) -> List[dict]:
    """List all stored memories for a session, sorted by time."""
    try:
        existing = {c.name for c in client.get_collections().collections}
        if collection not in existing:
            return []

        filt = Filter(must=[FieldCondition(key="session_id", match=MatchValue(value=session_id))])
        points, _ = client.scroll(
            collection_name=collection, scroll_filter=filt,
            limit=100, with_payload=True,
        )
        memories = []
        for pt in points:
            p = pt.payload or {}
            memories.append({
                "query": p.get("query"),
                "answer": p.get("answer"),
                "timestamp": p.get("timestamp"),
            })
        memories.sort(key=lambda x: x.get("timestamp", 0))
        return memories
    except Exception as e:
        log.warning(f"Memory list failed: {e}")
        return []
