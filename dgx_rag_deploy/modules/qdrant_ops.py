"""
Qdrant Operations — Connection, Collection Management, Dedup, BM25
==================================================================
Centralized Qdrant client factory and operations with improved
BM25 tokenization (stopword removal + basic stemming).
"""

import re
import logging
from collections import Counter
from typing import List, Optional, Dict

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance, PointStruct, VectorParams, Filter, FieldCondition, MatchValue,
    SparseVectorParams, SparseVector, Modifier, PayloadSchemaType,
)

log = logging.getLogger("rag-pipeline")

# ---------------------------------------------------------------------------
# Stopwords — common English words that add noise to BM25
# ---------------------------------------------------------------------------
STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "as", "be", "was", "were",
    "been", "are", "am", "do", "does", "did", "has", "had", "have",
    "will", "would", "could", "should", "may", "might", "shall", "can",
    "not", "no", "nor", "so", "if", "then", "than", "that", "this",
    "these", "those", "he", "she", "we", "they", "you", "me", "him",
    "her", "us", "them", "my", "your", "his", "its", "our", "their",
    "what", "which", "who", "whom", "when", "where", "why", "how",
    "all", "each", "every", "both", "few", "more", "most", "other",
    "some", "such", "only", "own", "same", "too", "very", "just",
    "also", "about", "above", "after", "before", "between", "into",
    "through", "during", "out", "up", "down", "over", "under", "again",
    "further", "once", "here", "there", "any", "because", "while",
})

# ---------------------------------------------------------------------------
# Basic suffix stemmer (Porter-lite)
# ---------------------------------------------------------------------------
_SUFFIX_RULES = [
    ("ational", "ate"), ("tional", "tion"), ("enci", "ence"),
    ("anci", "ance"), ("izer", "ize"), ("ising", "ise"),
    ("izing", "ize"), ("ation", "ate"), ("ator", "ate"),
    ("iveness", "ive"), ("fulness", "ful"), ("ousness", "ous"),
    ("ality", "al"), ("ivity", "ive"), ("ibility", "ible"),
    ("ness", ""), ("ment", ""), ("ing", ""), ("ies", "y"),
    ("tion", "t"), ("sion", "s"), ("able", ""), ("ible", ""),
    ("ally", "al"), ("ful", ""), ("ous", ""), ("ive", ""),
    ("ly", ""), ("ed", ""), ("er", ""), ("es", ""), ("s", ""),
]


def _stem(word: str) -> str:
    """Apply basic suffix stripping. Returns stemmed word (min 3 chars)."""
    if len(word) <= 3:
        return word
    for suffix, replacement in _SUFFIX_RULES:
        if word.endswith(suffix):
            candidate = word[:-len(suffix)] + replacement
            if len(candidate) >= 3:
                return candidate
            break
    return word


# ---------------------------------------------------------------------------
# BM25 Tokenizer
# ---------------------------------------------------------------------------
def tokenize_bm25(text: str) -> SparseVector:
    """
    Convert text to sparse vector for BM25 keyword matching.
    Improvements over v2:
      - Stopword removal
      - Basic suffix stemming
      - Minimum word length = 2
      - Case-normalized
    """
    words = re.findall(r'\b[a-zA-Z0-9]{2,}\b', text.lower())
    # Filter stopwords and stem
    stemmed = [_stem(w) for w in words if w not in STOPWORDS and len(w) >= 2]
    counts = Counter(stemmed)

    if not counts:
        # Return a minimal sparse vector if no tokens
        return SparseVector(indices=[0], values=[0.0])

    indices = []
    values = []
    for word, count in counts.items():
        indices.append(abs(hash(word)) % (2 ** 30))
        values.append(float(count))
    return SparseVector(indices=indices, values=values)


# ---------------------------------------------------------------------------
# Client Factory
# ---------------------------------------------------------------------------
_client_cache: Dict[str, QdrantClient] = {}


def get_client(url: str = "http://localhost:6333") -> QdrantClient:
    """Get or create a Qdrant client (connection reuse)."""
    if url not in _client_cache:
        _client_cache[url] = QdrantClient(url=url, timeout=30)
        log.info(f"Qdrant client created: {url}")
    return _client_cache[url]


# ---------------------------------------------------------------------------
# Collection Management
# ---------------------------------------------------------------------------
def ensure_collection(client: QdrantClient, name: str, vector_size: int):
    """Create hybrid collection (dense + BM25 sparse) if it doesn't exist."""
    existing = {c.name for c in client.get_collections().collections}
    if name not in existing:
        client.create_collection(
            collection_name=name,
            vectors_config={"dense": VectorParams(size=vector_size, distance=Distance.COSINE)},
            sparse_vectors_config={"bm25": SparseVectorParams(modifier=Modifier.IDF)},
        )
        log.info(f"Created hybrid collection: {name} (dense={vector_size}, sparse=BM25)")


def ensure_indexes(client: QdrantClient, collection: str):
    """Create payload indexes for filtered search (idempotent)."""
    for field in ["metadata.doc_type", "metadata.tags", "metadata.date"]:
        try:
            client.create_payload_index(
                collection_name=collection,
                field_name=field,
                field_schema=PayloadSchemaType.KEYWORD,
            )
        except Exception:
            pass
    # Keyword index on filename for exact match
    try:
        client.create_payload_index(
            collection_name=collection,
            field_name="filename",
            field_schema=PayloadSchemaType.KEYWORD,
        )
    except Exception:
        pass


def is_hybrid_collection(client: QdrantClient, collection: str) -> bool:
    """Check if collection has named vectors (hybrid) or legacy unnamed."""
    try:
        info = client.get_collection(collection)
        cfg = info.config.params.vectors
        return isinstance(cfg, dict) and "dense" in cfg
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------
def delete_document_chunks(client: QdrantClient, collection: str, filename: str) -> int:
    """
    Delete all existing chunks for a filename before re-ingest.
    Returns count of deleted points.
    """
    try:
        existing = {c.name for c in client.get_collections().collections}
        if collection not in existing:
            return 0

        filt = Filter(must=[FieldCondition(key="filename", match=MatchValue(value=filename))])
        points, _ = client.scroll(
            collection_name=collection, scroll_filter=filt,
            limit=10000, with_payload=False,
        )
        if not points:
            return 0

        ids = [p.id for p in points]
        client.delete(collection_name=collection, points_selector=ids)
        log.info(f"Dedup: deleted {len(ids)} old chunks for '{filename}' from {collection}")
        return len(ids)
    except Exception as e:
        log.warning(f"Dedup delete failed for '{filename}': {e}")
        return 0


# ---------------------------------------------------------------------------
# Search Operations
# ---------------------------------------------------------------------------
def search_hybrid(
    client: QdrantClient,
    collection: str,
    dense_vector: List[float],
    query_text: str,
    limit: int,
    filt: Optional[Filter] = None,
) -> list:
    """
    Hybrid search: dense + BM25 with RRF fusion.
    Falls back to dense-only for legacy collections or on error.
    """
    hybrid = is_hybrid_collection(client, collection)

    if hybrid and query_text:
        try:
            from qdrant_client.http.models import Prefetch, FusionQuery, Fusion
            sparse_vec = tokenize_bm25(query_text)
            prefetch_kw = [
                {"query": dense_vector, "using": "dense", "limit": limit * 2},
                {"query": sparse_vec, "using": "bm25", "limit": limit * 2},
            ]
            if filt:
                prefetch_kw = [{**p, "filter": filt} for p in prefetch_kw]
            prefetches = [Prefetch(**p) for p in prefetch_kw]
            resp = client.query_points(
                collection_name=collection, prefetch=prefetches,
                query=FusionQuery(fusion=Fusion.RRF), limit=limit, with_payload=True,
            )
            pts = resp.points if hasattr(resp, "points") else resp
            log.info(f"Hybrid search: {len(pts)} results (dense+BM25 RRF)")
            return pts
        except Exception as e:
            log.warning(f"Hybrid search failed, falling back to dense: {e}")

    return search_dense(client, collection, dense_vector, limit, filt, named=hybrid)


def search_dense(
    client: QdrantClient,
    collection: str,
    vector: List[float],
    limit: int,
    filt: Optional[Filter] = None,
    named: bool = False,
) -> list:
    """Dense-only vector search."""
    qv = ("dense", vector) if named else vector
    if hasattr(client, "search"):
        kw = {"collection_name": collection, "query_vector": qv, "limit": limit, "with_payload": True}
        if filt:
            kw["query_filter"] = filt
        return client.search(**kw)
    if hasattr(client, "query_points"):
        kw = {"collection_name": collection, "query": qv, "limit": limit, "with_payload": True}
        if filt:
            kw["query_filter"] = filt
        resp = client.query_points(**kw)
        return resp.points if hasattr(resp, "points") else resp
    raise AttributeError("No supported search method on Qdrant client")


# ---------------------------------------------------------------------------
# Filter Builder
# ---------------------------------------------------------------------------
def build_qdrant_filter(filters: dict) -> Optional[Filter]:
    """Convert user-friendly filters dict into a Qdrant Filter object."""
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
