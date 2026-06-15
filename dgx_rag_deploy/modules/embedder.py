"""
Embedder — Batch-Aware Embedding with Retry
============================================
Handles communication with the llama.cpp embedding server.
Supports batched requests, automatic retry with backoff, and
connection pooling.
"""

import time
import logging
from typing import List

import requests

log = logging.getLogger("rag-pipeline")

# ---------------------------------------------------------------------------
# Connection Pool
# ---------------------------------------------------------------------------
_session: requests.Session = None


def _get_session() -> requests.Session:
    """Reuse HTTP session for connection pooling."""
    global _session
    if _session is None:
        _session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=4, pool_maxsize=8, max_retries=0,
        )
        _session.mount("http://", adapter)
    return _session


# ---------------------------------------------------------------------------
# Core Embedding
# ---------------------------------------------------------------------------
def embed_batch(
    texts: List[str],
    model_url: str,
    model_name: str,
    api_key: str,
    batch_size: int = 32,
    max_retries: int = 3,
    timeout: int = 120,
) -> List[List[float]]:
    """
    Embed a list of texts with automatic batching and retry.

    For large documents (100+ chunks), sends in batches of `batch_size`
    to avoid OOM/timeout on the embedding server.
    """
    if not texts:
        return []

    all_embeddings = []
    session = _get_session()
    headers = {"Authorization": f"Bearer {api_key}"}

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(texts) + batch_size - 1) // batch_size

        for attempt in range(1, max_retries + 1):
            try:
                r = session.post(
                    model_url,
                    json={"input": batch, "model": model_name},
                    headers=headers,
                    timeout=timeout,
                )
                if r.status_code != 200:
                    raise RuntimeError(f"Embedding failed: {r.status_code} {r.text[:200]}")

                data = r.json().get("data", [])
                if not data:
                    raise RuntimeError("Embedding returned no vectors")

                # Sort by index to preserve order
                data.sort(key=lambda x: x.get("index", 0))
                batch_vectors = [item["embedding"] for item in data]

                if len(batch_vectors) != len(batch):
                    raise RuntimeError(
                        f"Embedding count mismatch: sent {len(batch)}, got {len(batch_vectors)}"
                    )

                all_embeddings.extend(batch_vectors)

                if total_batches > 1:
                    log.info(f"Embedded batch {batch_num}/{total_batches} ({len(batch)} texts)")
                break

            except Exception as e:
                if attempt < max_retries:
                    wait = 2 ** attempt
                    log.warning(f"Embed batch {batch_num} attempt {attempt} failed: {e}. Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    log.error(f"Embed batch {batch_num} failed after {max_retries} attempts: {e}")
                    raise

    return all_embeddings


def embed_single(
    text: str,
    model_url: str,
    model_name: str,
    api_key: str,
    timeout: int = 60,
) -> List[float]:
    """Embed a single text string. Convenience wrapper around embed_batch."""
    results = embed_batch([text], model_url, model_name, api_key, batch_size=1, timeout=timeout)
    if not results:
        raise RuntimeError("Empty embedding result")
    return results[0]
