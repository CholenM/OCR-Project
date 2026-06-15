"""
Retriever — Hybrid Search, Optional Re-rank, Optional Agentic Planning
=======================================================================
Core retrieval logic. Fast by default (single embed + search).
Re-ranking and agentic query decomposition are available but OFF
by default to avoid cascading LLM latency.
"""

import os
import json
import logging
from typing import List, Dict, Optional

import requests

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
    Fast retrieval: embed query → hybrid search → return sources.
    Returns (query_vector, sources_list).
    """
    query_vector = embed_single(query, embed_url, embed_model, embed_api_key)
    qdrant_filter = build_qdrant_filter(filters)

    results = search_hybrid(client, collection, query_vector, query, top_k, filt=qdrant_filter)

    # Fallback: if filtered search returns nothing, try unfiltered
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
    return query_vector, sources


# ---------------------------------------------------------------------------
# Context Assembly (smart truncation by score, not position)
# ---------------------------------------------------------------------------
def build_context(
    sources: List[dict],
    memories: List[dict],
    max_context_tokens: int = 30720,
) -> tuple:
    """
    Build context string from sources and memories.
    Truncates by score (drops lowest-scoring sources first).
    Returns (context_string, final_sources).
    """
    context_parts = []

    if memories:
        context_parts.append("=== CONVERSATION HISTORY ===")
        for m in memories:
            context_parts.append(f"[Previous Q&A | relevance {m['score']:.4f}]")
            context_parts.append(f"Q: {m['query']}\nA: {m['answer']}")

    # Sources are already sorted by score (highest first)
    working_sources = list(sources)

    if working_sources:
        context_parts.append("\n=== DOCUMENT CONTEXT ===")
        for s in working_sources:
            header = f"[{s['filename']} | {s['section']} | {s['content_type']} | score {s['score']:.4f}]"
            context_parts.append(f"{header}\n{s['text']}")

    context = "\n\n".join(context_parts)
    est_tokens = len(context) // 3

    # Truncate by removing lowest-scoring sources
    original_count = len(working_sources)
    while est_tokens > max_context_tokens and working_sources:
        working_sources.pop()  # Remove lowest-scored (last in sorted list)
        context_parts = []
        if memories:
            context_parts.append("=== CONVERSATION HISTORY ===")
            for m in memories:
                context_parts.append(f"[Previous Q&A | relevance {m['score']:.4f}]")
                context_parts.append(f"Q: {m['query']}\nA: {m['answer']}")
        if working_sources:
            context_parts.append("\n=== DOCUMENT CONTEXT ===")
            for s in working_sources:
                header = f"[{s['filename']} | {s['section']} | {s['content_type']} | score {s['score']:.4f}]"
                context_parts.append(f"{header}\n{s['text']}")
        context = "\n\n".join(context_parts)
        est_tokens = len(context) // 3

    if original_count != len(working_sources):
        log.info(f"Context truncated: {original_count} -> {len(working_sources)} sources ({est_tokens} est. tokens)")

    # Hard truncation as last resort
    if est_tokens > max_context_tokens:
        max_chars = (max_context_tokens - 300) * 3
        context = context[:max_chars]
        log.warning(f"Context hard-truncated to {max_chars} chars")

    return context, working_sources
