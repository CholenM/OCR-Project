"""
Reranker — Dedicated Cross-Encoder Reranking
=============================================
Uses a llama-server running with --reranking flag on a dedicated port.
Falls back to LLM-based scoring if the reranker server is unavailable.
"""

import json
import logging
from typing import List

import requests

log = logging.getLogger("rag-pipeline")


def rerank_with_server(
    query: str,
    sources: list,
    reranker_url: str,
    reranker_model: str,
    reranker_api_key: str,
    top_n: int = 15,
    min_score: float = 0.01,
) -> list:
    """
    Re-rank chunks using the dedicated reranker server (/v1/rerank endpoint).
    Much faster than LLM-as-reranker (~200ms vs ~10s).
    """
    if not sources or len(sources) <= 2:
        return sources

    documents = [s["text"][:1000] for s in sources]  # Truncate to avoid overflow

    try:
        r = requests.post(
            reranker_url,
            json={
                "model": reranker_model,
                "query": query,
                "documents": documents,
                "top_n": min(top_n, len(documents)),
            },
            headers={"Authorization": f"Bearer {reranker_api_key}"},
            timeout=30,
        )
        if r.status_code != 200:
            log.warning(f"Reranker server returned {r.status_code}: {r.text[:200]}")
            return sources

        results = r.json().get("results", [])
        if not results:
            return sources

        # Map reranker scores back to sources
        scored = []
        for item in results:
            idx = item.get("index", 0)
            score = item.get("relevance_score", 0.0)
            if idx < len(sources) and score >= min_score:
                s = sources[idx].copy()
                s["rerank_score"] = score
                scored.append(s)

        scored.sort(key=lambda x: x["rerank_score"], reverse=True)
        log.info(f"Reranked: {len(sources)} → {len(scored)} chunks (server)")
        return scored if scored else sources[:5]

    except requests.exceptions.ConnectionError:
        log.warning("Reranker server not available, skipping re-rank")
        return sources
    except Exception as e:
        log.warning(f"Reranker failed: {e}")
        return sources


def rerank_with_llm(
    query: str,
    sources: list,
    chat_url: str,
    chat_model: str,
    chat_api_key: str,
    min_score: int = 4,
) -> list:
    """
    Fallback: use Chat LLM to score chunks (slow but always available).
    """
    if not sources or len(sources) <= 3:
        return sources

    RERANK_PROMPT = """Score each chunk's relevance to the query (0-10). Return ONLY a JSON array of integers.
Query: {query}
{chunks}
Scores:"""

    try:
        chunk_text = "\n".join(f"[{i}] {s['text'][:300]}" for i, s in enumerate(sources))
        prompt = RERANK_PROMPT.replace("{query}", query).replace("{chunks}", chunk_text)
        r = requests.post(
            chat_url,
            json={"model": chat_model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.0},
            headers={"Authorization": f"Bearer {chat_api_key}"},
            timeout=180,
        )
        if r.status_code != 200:
            return sources

        raw = r.json()["choices"][0]["message"]["content"].strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0]
        scores = json.loads(raw)
        if not isinstance(scores, list) or len(scores) != len(sources):
            return sources

        for i, s in enumerate(sources):
            s["rerank_score"] = scores[i] if i < len(scores) else 5
        reranked = [s for s in sources if s.get("rerank_score", 5) >= min_score]
        reranked.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
        log.info(f"Reranked: {len(sources)} → {len(reranked)} chunks (LLM fallback)")
        return reranked if reranked else sources[:5]
    except Exception as e:
        log.warning(f"LLM rerank failed: {e}")
        return sources
