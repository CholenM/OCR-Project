"""
Retriever — Hybrid Search, Optional Re-rank, Optional Agentic Planning
=======================================================================
Core retrieval logic. Fast by default (single embed + search).
Re-ranking and agentic query decomposition are available but OFF
by default to avoid cascading LLM latency.
"""

import os
import re
import json
import logging
from collections import Counter, defaultdict
from typing import List, Dict, Optional

import requests
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

from modules.qdrant_ops import search_hybrid, build_qdrant_filter
from modules.embedder import embed_single

log = logging.getLogger("rag-pipeline")


# ---------------------------------------------------------------------------
# Chat LLM Helper
# ---------------------------------------------------------------------------
def _chat_completion(
    messages: List[Dict],
    chat_url: str,
    chat_model: str,
    chat_api_key: str,
    temperature: float = 0.7,
) -> str:
    r = requests.post(
        chat_url,
        json={"model": chat_model, "messages": messages, "temperature": temperature},
        headers={"Authorization": f"Bearer {chat_api_key}"},
        timeout=180,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Chat failed: {r.status_code} {r.text[:200]}")
    return r.json()["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# Fix 2: Filename / Document ID Detection
# ---------------------------------------------------------------------------
_DOC_ID_PATTERNS = [
    re.compile(r'[A-Z]{2,}\d{8,}'),           # OST10618202482736145
    re.compile(r'[A-Z]+-\d{4}-\d+'),           # RES-2024-001
    re.compile(r'\b\d{4}-\d{3,}-\d{2,}\b'),    # 2024-001-123
]


def _detect_document_id(query: str, client, collection: str) -> Optional[str]:
    """Check if query references a specific document by name/ID.
    Uses scroll + Python-side matching (reliable with any index config)."""
    for pattern in _DOC_ID_PATTERNS:
        match = pattern.search(query)
        if match:
            candidate = match.group(0).lower()
            try:
                # Scroll unique filenames and match in Python
                points, _ = client.scroll(
                    collection_name=collection,
                    limit=500,
                    with_payload=["filename"],
                )
                seen = set()
                for pt in points:
                    fname = (pt.payload or {}).get("filename", "")
                    if fname and fname not in seen:
                        seen.add(fname)
                        if candidate in fname.lower():
                            log.info(f"Document ID detected: '{candidate}' → filename '{fname}'")
                            return fname
            except Exception as e:
                log.warning(f"Document ID detection scroll failed: {e}")
    return None


def _fetch_all_document_chunks(client, collection: str, filename: str) -> list:
    """Fetch ALL chunks for a specific document by filename."""
    filt = Filter(must=[FieldCondition(key="filename", match=MatchValue(value=filename))])
    points, _ = client.scroll(
        collection_name=collection, scroll_filter=filt,
        limit=500, with_payload=True,
    )
    sources = []
    for pt in points:
        p = pt.payload or {}
        sources.append({
            "text": p.get("text", ""),
            "filename": p.get("filename", ""),
            "chunk_index": p.get("chunk_index", 0),
            "section": p.get("section", ""),
            "content_type": p.get("content_type", ""),
            "score": 1.0,  # Direct match = highest relevance
            "type": "direct_match",
        })
    sources.sort(key=lambda x: x["chunk_index"])
    log.info(f"Direct retrieval: {len(sources)} chunks from '{filename}'")
    return sources


# ---------------------------------------------------------------------------
# Context Expansion — Neighbor-Based (±3 chunks)
# ---------------------------------------------------------------------------
def _expand_document_context(
    client, collection: str, sources: list,
    neighbor_range: int = 3, max_expansion: int = 5,
) -> list:
    """
    For high-signal documents, fetch neighboring chunks (±3 by chunk_index)
    instead of dumping ALL chunks. Much more surgical.
    """
    if not sources:
        return sources

    # Group matched chunk_indices by filename
    filename_chunks = defaultdict(set)
    for s in sources:
        filename_chunks[s["filename"]].add(s["chunk_index"])

    # Decide which documents to expand
    expand_files = [f for f, idxs in filename_chunks.items() if len(idxs) >= 2]
    for s in sources:
        if s["score"] > 0.55 and s["filename"] not in expand_files:
            expand_files.append(s["filename"])
    expand_files = expand_files[:max_expansion]

    if not expand_files:
        return sources

    existing_keys = {f"{s['filename']}__{s['chunk_index']}" for s in sources}
    expanded_count = 0

    for fname in expand_files:
        matched_idxs = filename_chunks[fname]
        # Compute neighbor indices needed
        need_idxs = set()
        for idx in matched_idxs:
            for offset in range(-neighbor_range, neighbor_range + 1):
                need_idxs.add(idx + offset)
        need_idxs -= matched_idxs  # Don't re-fetch what we have
        need_idxs = {i for i in need_idxs if i >= 0}  # No negative indices

        if not need_idxs:
            continue

        # Fetch chunks for this document
        filt = Filter(must=[FieldCondition(key="filename", match=MatchValue(value=fname))])
        points, _ = client.scroll(
            collection_name=collection, scroll_filter=filt,
            limit=200, with_payload=True,
        )
        for pt in points:
            p = pt.payload or {}
            ci = p.get("chunk_index", -1)
            if ci in need_idxs:
                key = f"{p.get('filename', '')}__{ci}"
                if key not in existing_keys:
                    sources.append({
                        "text": p.get("text", ""),
                        "filename": p.get("filename", ""),
                        "chunk_index": ci,
                        "section": p.get("section", ""),
                        "content_type": p.get("content_type", ""),
                        "score": 0.5,
                        "type": "neighbor",
                    })
                    existing_keys.add(key)
                    expanded_count += 1

    if expanded_count:
        log.info(f"Neighbor expansion: +{expanded_count} chunks from {len(expand_files)} docs")

    return sources


# ---------------------------------------------------------------------------
# Core Retrieval (fast path — no LLM calls)
# ---------------------------------------------------------------------------
def retrieve(
    query: str,
    client,
    collection: str,
    embed_url: str,
    embed_model: str,
    embed_api_key: str,
    top_k: int = 15,
    filters: Optional[dict] = None,
) -> tuple:
    """
    Fast retrieval: embed query → hybrid search → expand context → return.
    Includes document ID detection, neighbor expansion, and broad query boost.
    Returns (query_vector, sources_list).
    """
    # 2C: Broad query auto-boost
    _BROAD_PATTERNS = ["list all", "list down", "create a table", "show all",
                       "how many", "every document", "all documents", "summarize all"]
    if any(p in query.lower() for p in _BROAD_PATTERNS):
        top_k = max(top_k, 30)
        log.info(f"Broad query detected, boosted top_k to {top_k}")

    query_vector = embed_single(query, embed_url, embed_model, embed_api_key)

    # Fix 2: Check if query references a specific document
    doc_filename = _detect_document_id(query, client, collection)
    if doc_filename:
        # Direct retrieval: get ALL chunks from the identified document
        direct_sources = _fetch_all_document_chunks(client, collection, doc_filename)
        if direct_sources:
            # Also run normal search to find related context from other docs
            qdrant_filter = build_qdrant_filter(filters)
            other_results = search_hybrid(client, collection, query_vector, query, top_k, filt=qdrant_filter)
            existing_keys = {f"{s['filename']}__{s['chunk_index']}" for s in direct_sources}
            for pt in other_results:
                p = pt.payload or {}
                key = f"{p.get('filename', '')}__{p.get('chunk_index', 0)}"
                if key not in existing_keys:
                    direct_sources.append({
                        "text": p.get("text", ""),
                        "filename": p.get("filename", "unknown"),
                        "chunk_index": p.get("chunk_index", 0),
                        "section": p.get("section", ""),
                        "content_type": p.get("content_type", ""),
                        "score": pt.score,
                        "type": "document",
                    })
            return query_vector, direct_sources

    # Standard path: hybrid search
    qdrant_filter = build_qdrant_filter(filters)
    results = search_hybrid(client, collection, query_vector, query, top_k, filt=qdrant_filter)

    if not results and qdrant_filter:
        log.info("Filtered search empty, retrying without filters")
        results = search_hybrid(client, collection, query_vector, query, top_k)

    sources = []
    for pt in results:
        p = pt.payload or {}
        sources.append({
            "text": p.get("text", ""),
            "filename": p.get("filename", "unknown"),
            "chunk_index": p.get("chunk_index", 0),
            "section": p.get("section", ""),
            "content_type": p.get("content_type", ""),
            "score": pt.score,
            "type": "document",
        })

    # Fix 1: Expand context for high-signal documents
    sources = _expand_document_context(client, collection, sources)

    return query_vector, sources


# ---------------------------------------------------------------------------
# Optional: LLM Re-ranking (OFF by default)
# ---------------------------------------------------------------------------
RERANK_PROMPT = """Score each chunk's relevance to the query (0-10). Return ONLY a JSON array of integers.
Query: {query}
{chunks}
Scores:"""


def rerank_chunks(
    query: str,
    sources: list,
    chat_url: str,
    chat_model: str,
    chat_api_key: str,
    min_score: int = 4,
) -> list:
    """Use Chat LLM to re-score and filter retrieved chunks."""
    if not sources or len(sources) <= 3:
        return sources
    try:
        chunk_text = "\n".join(f"[{i}] {s['text'][:300]}" for i, s in enumerate(sources))
        prompt = RERANK_PROMPT.replace("{query}", query).replace("{chunks}", chunk_text)
        raw = _chat_completion(
            [{"role": "user", "content": prompt}],
            chat_url, chat_model, chat_api_key,
            temperature=0.0,
        )
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0]
        scores = json.loads(cleaned)
        if not isinstance(scores, list) or len(scores) != len(sources):
            return sources
        for i, s in enumerate(sources):
            s["rerank_score"] = scores[i] if i < len(scores) else 5
        reranked = [s for s in sources if s.get("rerank_score", 5) >= min_score]
        reranked.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
        log.info(f"Reranked: {len(sources)} -> {len(reranked)} chunks (min_score={min_score})")
        return reranked if reranked else sources[:5]
    except Exception as e:
        log.warning(f"Rerank failed: {e}")
        return sources


# ---------------------------------------------------------------------------
# Optional: Agentic Query Planning (OFF by default)
# ---------------------------------------------------------------------------
PLAN_PROMPT = """Analyze this query and determine the best retrieval strategy.
Return ONLY a valid JSON object:
{
  "strategy": "simple" or "decompose",
  "sub_queries": ["query1", "query2"],
  "reasoning": "brief explanation"
}

Rules:
- "simple": Direct search. Use for factual, single-source questions.
- "decompose": Break into 2-4 sub-queries. Use for multi-faceted questions, table-building, or comparison queries.
- For "simple", sub_queries should contain just the original query.
- Sub-queries should be specific and self-contained.

Query: {query}"""


def plan_query(
    query: str,
    client,
    collection: str,
    embed_url: str,
    embed_model: str,
    embed_api_key: str,
    chat_url: str,
    chat_model: str,
    chat_api_key: str,
    top_k: int = 15,
    filters: Optional[dict] = None,
) -> tuple:
    """
    Agentic retrieval: LLM plans sub-queries, retrieves for each, merges results.
    Returns (query_vector, merged_sources).
    """
    try:
        prompt = PLAN_PROMPT.replace("{query}", query)
        raw = _chat_completion(
            [{"role": "user", "content": prompt}],
            chat_url, chat_model, chat_api_key,
            temperature=0.0,
        )
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0]
        plan = json.loads(cleaned)
        sub_queries = plan.get("sub_queries", [query])
        if not sub_queries:
            sub_queries = [query]
        log.info(f"Query plan: {plan.get('strategy', 'simple')} | {len(sub_queries)} sub-queries")
    except Exception as e:
        log.warning(f"Query planning failed: {e}")
        sub_queries = [query]

    # Retrieve for each sub-query and merge (deduplicate by filename+chunk_index)
    all_sources = {}
    query_vector = None

    for sq in sub_queries:
        sq_vector, sq_sources = retrieve(
            sq, client, collection,
            embed_url, embed_model, embed_api_key,
            top_k, filters,
        )
        if query_vector is None:
            query_vector = sq_vector  # Use first sub-query vector for memory

        for s in sq_sources:
            key = f"{s['filename']}__{s['chunk_index']}"
            if key not in all_sources:
                all_sources[key] = s
            else:
                all_sources[key]["score"] = max(all_sources[key]["score"], s["score"])

    # If query_vector is still None (shouldn't happen), embed the original query
    if query_vector is None:
        query_vector = embed_single(query, embed_url, embed_model, embed_api_key)

    sources = sorted(all_sources.values(), key=lambda x: x["score"], reverse=True)

    # Fix 1: Expand context for high-signal documents
    sources = _expand_document_context(client, collection, sources)

    return query_vector, sources


# ---------------------------------------------------------------------------
# Context Assembly — Memory-Capped, O(n) Greedy Selection
# ---------------------------------------------------------------------------
def build_context(
    sources: List[dict],
    memories: List[dict],
    max_context_tokens: int = 28672,
) -> tuple:
    """
    Build context string with document-first priority.
    Memory gets max 20% of budget, documents get 80%.
    Uses single-pass greedy selection (O(n) instead of O(n²)).
    Returns (context_string, final_sources).
    """
    CHARS_PER_TOKEN = 2.8  # Conservative for structured text with filenames/headers

    # --- Memory section (capped at 20% of budget) ---
    max_memory_tokens = max_context_tokens // 5
    memory_parts = []
    memory_tokens = 0

    if memories:
        memory_parts.append("=== CONVERSATION HISTORY (for follow-up context only) ===")
        memory_tokens = int(len(memory_parts[0]) / CHARS_PER_TOKEN)
        kept_memories = []
        for m in memories:
            entry = f"[Previous Q&A]\nQ: {m['query']}\nA: {m['answer']}"
            entry_tokens = int(len(entry) / CHARS_PER_TOKEN)
            if memory_tokens + entry_tokens <= max_memory_tokens:
                memory_parts.append(entry)
                memory_tokens += entry_tokens
                kept_memories.append(m)
            else:
                break  # Memory is sorted by relevance, so stop
        memories = kept_memories

    if memory_tokens > 0:
        log.info(f"Memory budget: {memory_tokens}/{max_memory_tokens} tokens ({len(memories)} memories)")

    # --- Document section (gets remaining 80%+) ---
    remaining_budget = max_context_tokens - memory_tokens

    # Pre-compute cost per source, sort by score descending
    source_costs = []
    for s in sources:
        header = f"[{s['filename']} | {s['section']} | {s['content_type']} | score {s['score']:.4f}]"
        text = f"{header}\n{s['text']}"
        cost = int(len(text) / CHARS_PER_TOKEN)
        source_costs.append((s, text, cost))
    source_costs.sort(key=lambda x: x[0]["score"], reverse=True)

    # Greedy fill: pick sources by score until budget exhausted
    selected_sources = []
    doc_parts = []
    doc_tokens = 0

    for source, text, cost in source_costs:
        if doc_tokens + cost <= remaining_budget:
            selected_sources.append(source)
            doc_parts.append(text)
            doc_tokens += cost

    if len(selected_sources) < len(sources):
        log.info(f"Context: {len(selected_sources)}/{len(sources)} sources fit ({doc_tokens} tokens, budget {remaining_budget})")

    # --- Assemble final context ---
    context_sections = []
    if memory_parts:
        context_sections.append("\n\n".join(memory_parts))
    if doc_parts:
        context_sections.append("=== DOCUMENT CONTEXT ===\n\n" + "\n\n".join(doc_parts))

    context = "\n\n".join(context_sections)

    # Hard truncation as absolute last resort
    total_tokens = int(len(context) / CHARS_PER_TOKEN)
    if total_tokens > max_context_tokens:
        max_chars = int((max_context_tokens - 300) * CHARS_PER_TOKEN)
        context = context[:max_chars]
        log.warning(f"Context hard-truncated to {max_chars} chars")

    return context, selected_sources
