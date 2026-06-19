"""
Batch Ingest — CLI Tool for Bulk Document Ingestion
====================================================
Ingests supported document files from a folder into a collection.

Usage:
    python batch_ingest.py ./documents my_collection
    python batch_ingest.py ./documents my_collection --autotag
"""

import os
import sys
import time
import base64
import argparse
import logging
from pathlib import Path

from dotenv import load_dotenv
import requests

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("batch-ingest")

RAG_API_URL = os.getenv("RAG_API_URL", "http://127.0.0.1:8081")
API_KEY = os.getenv("WATCH_API_KEY", os.getenv("API_KEYS", "test_key_0000").split(":")[0])

SUPPORTED = {
    ".md", ".txt", ".csv",
    ".docx", ".doc", ".dotx", ".odt", ".rtf",
    ".xls", ".xlsx", ".xlsm", ".xlsb", ".xlt",
    ".ppt", ".pptx",
}


def _headers():
    return {"X-API-KEY": API_KEY}


def ingest_file(filepath: Path, collection: str, autotag: bool = False) -> dict:
    """Ingest a single file into the collection."""
    ext = filepath.suffix.lower()

    if ext == ".md":
        content = filepath.read_text(encoding="utf-8", errors="replace")
        payload = {
            "filename": filepath.name,
            "markdown_content": content,
            "collection": collection,
        }
    elif ext in SUPPORTED:
        raw = filepath.read_bytes()
        payload = {
            "filename": filepath.name,
            "raw_content_b64": base64.b64encode(raw).decode("utf-8"),
            "collection": collection,
        }
    else:
        return {"status": "skipped", "file": filepath.name, "reason": "unsupported format"}

    # Optional: auto-tag first when content is already local markdown.
    if autotag and ext == ".md":
        try:
            tag_resp = requests.post(
                f"{RAG_API_URL}/v1/autotag",
                headers=_headers(),
                json={"markdown_content": content},
                timeout=60,
            )
            if tag_resp.status_code == 200:
                payload["metadata"] = tag_resp.json().get("metadata", {})
        except Exception:
            pass

    try:
        resp = requests.post(
            f"{RAG_API_URL}/v1/ingest",
            headers=_headers(),
            json=payload,
            timeout=300,
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"status": "error", "file": filepath.name, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        return {"status": "error", "file": filepath.name, "error": str(e)}


def main():
    global RAG_API_URL

    parser = argparse.ArgumentParser(description="Batch ingest documents into RAG pipeline")
    parser.add_argument("folder", help="Folder containing documents to ingest")
    parser.add_argument("collection", help="Target Qdrant collection name")
    parser.add_argument("--autotag", action="store_true", help="Auto-tag documents with LLM")
    parser.add_argument("--api-url", default=RAG_API_URL, help="RAG API URL")
    args = parser.parse_args()

    RAG_API_URL = args.api_url

    folder = Path(args.folder).resolve()
    if not folder.is_dir():
        log.error(f"Not a directory: {folder}")
        sys.exit(1)

    files = sorted([f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED])
    if not files:
        log.info(f"No supported files found in {folder}")
        log.info(f"Supported: {', '.join(sorted(SUPPORTED))}")
        sys.exit(0)

    log.info(f"Found {len(files)} file(s) in {folder}")
    log.info(f"Target collection: {args.collection}")
    log.info(f"Auto-tag: {'ON' if args.autotag else 'OFF'}")
    log.info("")

    t0 = time.time()
    success, errors = 0, 0
    total_chunks = 0

    for i, filepath in enumerate(files, 1):
        log.info(f"[{i}/{len(files)}] {filepath.name}")
        result = ingest_file(filepath, args.collection, args.autotag)

        if result.get("status") == "ok":
            chunks = result.get("chunks", 0)
            total_chunks += chunks
            success += 1
            log.info(f"  ✓ {chunks} chunks ingested")
        elif result.get("status") == "skipped":
            log.info(f"  → Skipped: {result.get('reason', '')}")
        else:
            errors += 1
            log.error(f"  ✗ {result.get('error', 'unknown error')}")

    elapsed = time.time() - t0
    log.info("")
    log.info(f"Done in {elapsed:.1f}s — {success} succeeded, {errors} failed, {total_chunks} total chunks")


if __name__ == "__main__":
    main()
