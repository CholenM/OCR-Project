"""
Watch Daemon — Auto-Ingest Folder Monitor
==========================================
Monitors a folder for new files and automatically:
  - PDFs/Images → OCR → Auto-tag → Ingest
  - Office/OpenDocument/RTF/TXT/CSV → Convert → Ingest
  - .md files → Auto-tag → Ingest directly

Moves processed files to a 'processed/' subfolder.

Usage:
    Standalone:  python watch_daemon.py
    Via start.sh: Launched as background process when WATCH_ENABLED=true

Configure via .env:
    WATCH_DIR=./inbox
    WATCH_COLLECTION=ocr_rag
    WATCH_INTERVAL=10
    WATCH_ENABLED=true
"""

import os
import sys
import time
import shutil
import base64
import logging
from pathlib import Path

from dotenv import load_dotenv
import requests

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | [watch] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("watch-daemon")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
WATCH_DIR       = os.getenv("WATCH_DIR", "./inbox")
PROCESSED_DIR   = os.getenv("PROCESSED_DIR", "./processed")
WATCH_INTERVAL  = int(os.getenv("WATCH_INTERVAL", "10"))  # seconds
WATCH_COLLECTION = os.getenv("WATCH_COLLECTION", os.getenv("QDRANT_COLLECTION", "ocr_rag"))

OCR_API_URL = os.getenv("OCR_API_URL", "http://127.0.0.1:8080")
RAG_API_URL = os.getenv("RAG_API_URL", "http://127.0.0.1:8081")
API_KEY     = os.getenv("WATCH_API_KEY", os.getenv("API_KEYS", "test_key_0000").split(":")[0])

# Supported file extensions
OCR_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
DIRECT_EXTENSIONS = {
    ".md", ".txt", ".csv",
    ".docx", ".doc", ".dotx", ".odt", ".rtf",
    ".xls", ".xlsx", ".xlsm", ".xlsb", ".xlt",
    ".ppt", ".pptx",
}
ALL_EXTENSIONS = OCR_EXTENSIONS | DIRECT_EXTENSIONS


def _headers():
    return {"X-API-KEY": API_KEY}


def _process_ocr_file(filepath: Path) -> dict:
    """Send PDF/image to OCR service, then ingest the result."""
    log.info(f"OCR processing: {filepath.name}")
    content_type_map = {
        ".pdf": "application/pdf", ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg", ".png": "image/png",
    }
    ext = filepath.suffix.lower()
    ct = content_type_map.get(ext, "application/octet-stream")

    with open(filepath, "rb") as f:
        ocr_resp = requests.post(
            f"{OCR_API_URL}/v1/ocr",
            headers=_headers(),
            files={"file": (filepath.name, f, ct)},
            params={"dpi": 200, "mode": "concurrent"},
            timeout=600,
        )

    if ocr_resp.status_code != 200:
        return {"status": "error", "file": filepath.name, "error": f"OCR failed: {ocr_resp.status_code}"}

    markdown_content = ocr_resp.text
    return _ingest_markdown(filepath.name, markdown_content)


def _process_direct_file(filepath: Path) -> dict:
    """Process supported non-OCR files directly through the RAG converter."""
    log.info(f"Direct processing: {filepath.name}")
    ext = filepath.suffix.lower()

    if ext == ".md":
        markdown_content = filepath.read_text(encoding="utf-8", errors="replace")
        return _ingest_markdown(filepath.name, markdown_content)
    else:
        # Send as base64 to RAG service for conversion
        raw_bytes = filepath.read_bytes()
        b64_content = base64.b64encode(raw_bytes).decode("utf-8")
        try:
            resp = requests.post(
                f"{RAG_API_URL}/v1/ingest",
                headers=_headers(),
                json={
                    "filename": filepath.name,
                    "raw_content_b64": b64_content,
                    "collection": WATCH_COLLECTION,
                },
                timeout=300,
            )
            if resp.status_code == 200:
                result = resp.json()
                log.info(f"  Ingested {filepath.name}: {result.get('chunks', 0)} chunks")
                return result
            else:
                return {"status": "error", "file": filepath.name, "error": f"Ingest failed: {resp.status_code}"}
        except Exception as e:
            return {"status": "error", "file": filepath.name, "error": str(e)}


def _ingest_markdown(filename: str, markdown_content: str) -> dict:
    """Auto-tag and ingest markdown content."""
    # Step 1: Auto-tag
    metadata = {}
    try:
        tag_resp = requests.post(
            f"{RAG_API_URL}/v1/autotag",
            headers=_headers(),
            json={"markdown_content": markdown_content},
            timeout=60,
        )
        if tag_resp.status_code == 200:
            metadata = tag_resp.json().get("metadata", {})
            log.info(f"  Auto-tagged {filename}: {metadata.get('doc_type', 'unknown')}")
    except Exception as e:
        log.warning(f"  Auto-tag failed for {filename}: {e}")

    # Step 2: Ingest
    try:
        ingest_resp = requests.post(
            f"{RAG_API_URL}/v1/ingest",
            headers=_headers(),
            json={
                "filename": filename,
                "markdown_content": markdown_content,
                "collection": WATCH_COLLECTION,
                "metadata": metadata,
            },
            timeout=300,
        )
        if ingest_resp.status_code == 200:
            result = ingest_resp.json()
            log.info(f"  Ingested {filename}: {result.get('chunks', 0)} chunks")
            return result
        else:
            return {"status": "error", "file": filename, "error": f"Ingest failed: {ingest_resp.status_code}"}
    except Exception as e:
        return {"status": "error", "file": filename, "error": str(e)}


def _move_to_processed(filepath: Path, processed_dir: Path):
    """Move file to processed directory after successful processing."""
    processed_dir.mkdir(parents=True, exist_ok=True)
    dest = processed_dir / filepath.name
    # Handle name collision
    if dest.exists():
        stem = filepath.stem
        suffix = filepath.suffix
        counter = 1
        while dest.exists():
            dest = processed_dir / f"{stem}_{counter}{suffix}"
            counter += 1
    shutil.move(str(filepath), str(dest))
    log.info(f"  Moved to: {dest}")


def run_watch_loop():
    """Main watch loop — scans folder at regular intervals."""
    watch_path = Path(WATCH_DIR).resolve()
    processed_path = Path(PROCESSED_DIR).resolve()

    watch_path.mkdir(parents=True, exist_ok=True)
    processed_path.mkdir(parents=True, exist_ok=True)

    log.info(f"Watch daemon started")
    log.info(f"  Watch dir:     {watch_path}")
    log.info(f"  Processed dir: {processed_path}")
    log.info(f"  Collection:    {WATCH_COLLECTION}")
    log.info(f"  Interval:      {WATCH_INTERVAL}s")
    log.info(f"  Supported:     {', '.join(sorted(ALL_EXTENSIONS))}")

    while True:
        try:
            files = sorted(
                [f for f in watch_path.iterdir() if f.is_file() and f.suffix.lower() in ALL_EXTENSIONS],
                key=lambda f: f.stat().st_mtime,
            )

            if files:
                log.info(f"Found {len(files)} file(s) to process")

            for filepath in files:
                ext = filepath.suffix.lower()
                try:
                    if ext in OCR_EXTENSIONS:
                        result = _process_ocr_file(filepath)
                    elif ext in DIRECT_EXTENSIONS:
                        result = _process_direct_file(filepath)
                    else:
                        continue

                    if result.get("status") != "error":
                        _move_to_processed(filepath, processed_path)
                    else:
                        log.error(f"  Failed: {filepath.name} — {result.get('error', 'unknown')}")
                except Exception as e:
                    log.error(f"  Exception processing {filepath.name}: {e}")

        except Exception as e:
            log.error(f"Watch loop error: {e}")

        time.sleep(WATCH_INTERVAL)


if __name__ == "__main__":
    run_watch_loop()
