import os
import time
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams


@dataclass
class IngestionConfig:
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_EMBED_MODEL", "qwen3-embedding:8b")
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    collection: str = os.getenv("QDRANT_COLLECTION", "ocr_rag")
    chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "1200"))
    chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "150"))


def chunk_markdown(text: str, chunk_size: int, overlap: int) -> List[str]:
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


def _embed_batch_ollama(texts: List[str], config: IngestionConfig) -> List[List[float]]:
    url = f"{config.ollama_url}/api/embed"
    response = requests.post(
        url,
        json={"model": config.ollama_model, "input": texts},
        timeout=120,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Ollama embed failed: {response.status_code} {response.text}")

    payload = response.json()
    embeddings = payload.get("embeddings")
    if not embeddings:
        raise RuntimeError("Ollama embed returned no embeddings")

    return embeddings


def _embed_single_ollama(text: str, config: IngestionConfig) -> List[float]:
    url = f"{config.ollama_url}/api/embeddings"
    response = requests.post(
        url,
        json={"model": config.ollama_model, "prompt": text},
        timeout=120,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Ollama embeddings failed: {response.status_code} {response.text}")

    payload = response.json()
    embedding = payload.get("embedding")
    if not embedding:
        raise RuntimeError("Ollama embeddings returned no vector")

    return embedding


def embed_texts(texts: List[str], config: IngestionConfig) -> List[List[float]]:
    if not texts:
        return []

    try:
        return _embed_batch_ollama(texts, config)
    except Exception:
        return [_embed_single_ollama(text, config) for text in texts]


def ensure_collection(client: QdrantClient, name: str, vector_size: int) -> None:
    collections = client.get_collections().collections
    existing = {collection.name for collection in collections}
    if name in existing:
        return

    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )


def ingest_markdown(
    filename: str,
    markdown_text: str,
    config: Optional[IngestionConfig] = None,
    metadata: Optional[Dict[str, str]] = None,
) -> Dict[str, int]:
    config = config or IngestionConfig()
    chunks = chunk_markdown(markdown_text, config.chunk_size, config.chunk_overlap)
    embeddings = embed_texts(chunks, config)

    if len(chunks) != len(embeddings):
        raise RuntimeError("Embedding count mismatch with chunks")

    client = QdrantClient(url=config.qdrant_url)
    ensure_collection(client, config.collection, len(embeddings[0]))

    now = int(time.time())
    points: List[PointStruct] = []

    for index, (chunk, vector) in enumerate(zip(chunks, embeddings)):
        payload = {
            "source": "ocr",
            "filename": filename,
            "chunk_index": index,
            "text": chunk,
            "created_at": now,
        }
        if metadata:
            payload.update(metadata)

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=payload,
            )
        )

    client.upsert(collection_name=config.collection, points=points)
    return {"chunks": len(points), "collection": config.collection}
