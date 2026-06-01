import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests
from qdrant_client import QdrantClient


@dataclass
class RetrievalConfig:
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    embed_model: str = os.getenv("OLLAMA_EMBED_MODEL", "qwen3-embedding:8b")
    llm_model: str = os.getenv("OLLAMA_CHAT_MODEL", "nemotron-3-nano:30b-cloud")
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    collection: str = os.getenv("QDRANT_COLLECTION", "ocr_rag")
    top_k: int = int(os.getenv("RAG_TOP_K", "6"))
    score_threshold: Optional[float] = None


def embed_query(text: str, config: RetrievalConfig) -> List[float]:
    text = (text or "").strip()
    if not text:
        raise ValueError("Query text is empty")

    batch_url = f"{config.ollama_url}/api/embed"
    response = requests.post(
        batch_url,
        json={"model": config.embed_model, "input": [text]},
        timeout=120,
    )
    if response.status_code == 200:
        payload = response.json()
        embeddings = payload.get("embeddings")
        if embeddings and embeddings[0]:
            return embeddings[0]

    single_url = f"{config.ollama_url}/api/embeddings"
    response = requests.post(
        single_url,
        json={"model": config.embed_model, "prompt": text},
        timeout=120,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Ollama embeddings failed: {response.status_code} {response.text}")

    payload = response.json()
    embedding = payload.get("embedding")
    if not embedding:
        raise RuntimeError("Ollama embeddings returned no vector")

    return embedding


def retrieve_chunks(query: str, config: RetrievalConfig) -> List[Dict[str, object]]:
    vector = embed_query(query, config)
    client = QdrantClient(url=config.qdrant_url)

    results = _search_points(
        client,
        config.collection,
        vector,
        config.top_k,
        config.score_threshold,
    )

    sources: List[Dict[str, object]] = []
    for point in results:
        payload = point.payload or {}
        sources.append({
            "text": payload.get("text", ""),
            "filename": payload.get("filename", "unknown"),
            "chunk_index": payload.get("chunk_index", 0),
            "score": point.score,
        })

    return sources


def _search_points(
    client: QdrantClient,
    collection: str,
    vector: List[float],
    limit: int,
    score_threshold: Optional[float],
):
    if hasattr(client, "search"):
        search_kwargs = {
            "collection_name": collection,
            "query_vector": vector,
            "limit": limit,
            "with_payload": True,
        }
        if score_threshold is not None:
            search_kwargs["score_threshold"] = score_threshold
        return client.search(**search_kwargs)

    if hasattr(client, "query_points"):
        query_kwargs = {
            "collection_name": collection,
            "query": vector,
            "limit": limit,
            "with_payload": True,
        }
        if score_threshold is not None:
            query_kwargs["score_threshold"] = score_threshold
        response = client.query_points(**query_kwargs)
        return response.points if hasattr(response, "points") else response

    if hasattr(client, "search_points"):
        search_kwargs = {
            "collection_name": collection,
            "vector": vector,
            "limit": limit,
            "with_payload": True,
        }
        if score_threshold is not None:
            search_kwargs["score_threshold"] = score_threshold
        return client.search_points(**search_kwargs)

    raise AttributeError("Qdrant client has no supported search method")


def _build_context(sources: List[Dict[str, object]]) -> str:
    blocks = []
    for source in sources:
        header = f"[Source: {source['filename']} | chunk {source['chunk_index']} | score {source['score']:.4f}]"
        text = source["text"]
        blocks.append(f"{header}\n{text}")
    return "\n\n".join(blocks)


def _ollama_chat(messages: List[Dict[str, str]], config: RetrievalConfig) -> str:
    url = f"{config.ollama_url}/api/chat"
    response = requests.post(
        url,
        json={"model": config.llm_model, "messages": messages, "stream": False},
        timeout=180,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Ollama chat failed: {response.status_code} {response.text}")

    payload = response.json()
    message = payload.get("message", {})
    content = message.get("content")
    if not content:
        raise RuntimeError("Ollama chat returned no content")

    return content


def retrieve_answer(
    query: str,
    config: Optional[RetrievalConfig] = None,
    system_prompt: Optional[str] = None,
) -> Dict[str, object]:
    config = config or RetrievalConfig()
    sources = retrieve_chunks(query, config)

    if not sources:
        return {
            "answer": "No relevant chunks found in Qdrant. Try a different query or ingest more documents.",
            "sources": [],
        }

    context = _build_context(sources)
    system_text = system_prompt or (
        "You are a local RAG assistant. Answer using only the context. "
        "If the answer is not in the context, say you do not know."
    )

    user_text = (
        "Use the context to answer the question. Provide a concise answer and cite sources.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}"
    )

    messages = [
        {"role": "system", "content": system_text},
        {"role": "user", "content": user_text},
    ]

    answer = _ollama_chat(messages, config)
    return {"answer": answer, "sources": sources}
