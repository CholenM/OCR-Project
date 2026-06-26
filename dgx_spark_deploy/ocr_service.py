"""
OCR Pipeline Service — DGX Spark Production Deployment
=======================================================
Single autonomous FastAPI service that provides API-based OCR.
Converts PDFs and images to structured Markdown via a local
llama.cpp model server (LightOnOCR-2-1B on NVIDIA CUDA GPU).

Usage:
    python ocr_service.py          # Reads config from .env
    uvicorn ocr_service:app        # Alternative via uvicorn CLI
"""

import os
import base64
import time
import asyncio
import logging
import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status, Header, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import fitz  # PyMuPDF
import requests

# ---------------------------------------------------------------------------
# Configuration — all values sourced from .env
# ---------------------------------------------------------------------------
load_dotenv()

MODEL_URL = os.getenv("MODEL_URL", "http://127.0.0.1:8001/v1/chat/completions")
MODEL_NAME = os.getenv("MODEL_NAME", "LightOnOCR-2-1B")
MODEL_API_KEY = os.getenv("MODEL_API_KEY", "sk-ocr-layer1")
API_PORT = int(os.getenv("API_PORT", "8080"))
API_HOST = os.getenv("API_HOST", "0.0.0.0")
MAX_PAGE_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", "4"))
OCR_JOB_DIR = Path(os.getenv("OCR_JOB_DIR", "./ocr_jobs"))
OCR_JOB_CONCURRENCY = max(1, min(int(os.getenv("OCR_JOB_CONCURRENCY", "3")), 3))
OCR_RECOVER_JOBS_ON_STARTUP = os.getenv("OCR_RECOVER_JOBS_ON_STARTUP", "true").lower() == "true"
OCR_JOB_RETENTION_HOURS = int(os.getenv("OCR_JOB_RETENTION_HOURS", "24"))

_job_queue = asyncio.Queue()
_job_workers = []


class OCRJobCancelled(Exception):
    """Raised when a queued or running OCR job is cancelled."""

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ocr_service")

# ---------------------------------------------------------------------------
# API Key Database — loaded from .env, kept in-memory
# ---------------------------------------------------------------------------
def _parse_api_keys() -> dict:
    """
    Parse API_KEYS env var.
    Format: key:user:monthly_cap:rate_per_page,key2:user2:cap2:rate2,...
    """
    raw = os.getenv("API_KEYS", "test_key_0000:Internal Benchmark Test:1.00:0.00")
    db = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split(":")
        if len(parts) != 4:
            logger.warning(f"Skipping malformed API key entry: {entry}")
            continue
        key, user, cap, rate = parts
        db[key.strip()] = {
            "user": user.strip(),
            "active": True,
            "monthly_spend_cap": float(cap.strip()),
            "current_month_spend": 0.00,
            "rate_per_page": float(rate.strip()),
            "metrics": {
                "total_documents": 0,
                "total_pages_processed": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
            },
            "audit_logs": [],
        }
    logger.info(f"Loaded {len(db)} API key(s): {[v['user'] for v in db.values()]}")
    return db


API_KEY_DB = _parse_api_keys()

# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="OCR Pipeline API",
    description=(
        "Production OCR service running on NVIDIA DGX Spark. "
        "Converts PDFs and images to structured Markdown via LightOnOCR-2-1B."
    ),
    version="1.0.0",
)

# CORS — allow any origin on the local network
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Security — API Key Verification
# ---------------------------------------------------------------------------
async def verify_api_key(
    x_api_key: str = Header(..., description="API key for authentication and tracking"),
):
    if x_api_key not in API_KEY_DB:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid API Key",
        )

    key_info = API_KEY_DB[x_api_key]

    if not key_info["active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account Deactivated.",
        )

    if key_info["current_month_spend"] >= key_info["monthly_spend_cap"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Quota Exceeded: Monthly spend cap reached. Please contact IT to increase budget.",
        )

    return x_api_key


# ---------------------------------------------------------------------------
# Core Inference — calls llama.cpp model server
# ---------------------------------------------------------------------------
def query_model_ocr(base64_image: str, mime_type: str = "image/png"):
    """Send a single image to the model server and return (text, prompt_tokens, completion_tokens)."""
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an OCR extraction engine for legal documents. Output ONLY raw Markdown."
                    "Goal: Recover ALL visible text, including faint or decorative headers, letterheads, page titles, and top-margin content."
                    "Rules: First pass: read the entire page and capture all text included logos and structure. "
                    "Second pass: re-scan the top of the page specifically for headers, letterheads, and page titles; add anything missing."
                    "Preserve reading order from top-to-bottom, left-to-right."
                    "Reconstruct tables accurately in Markdown."
                    "Table rules: use pipe-delimited Markdown tables only; no prose inside tables."
                    "Each table row MUST have the same number of columns; use empty cells ("
                    '""'
                    ") to fill missing or merged cells."
                    "If a header spans multiple columns, duplicate the header text across those columns."
                    "Do a final table-only recovery pass to fix column alignment and ensure stable row widths."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all text and structure into Markdown."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                    },
                ],
            },
        ],
        "temperature": 0.0,
    }

    try:
        headers = {"Authorization": f"Bearer {MODEL_API_KEY}"}
        response = requests.post(MODEL_URL, json=payload, headers=headers, timeout=120)
        if response.status_code == 200:
            result = response.json()
            text = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            prompt_toks = usage.get("prompt_tokens", 0)
            comp_toks = usage.get("completion_tokens", 0)
            return text, prompt_toks, comp_toks
        else:
            raise RuntimeError(f"Model server error {response.status_code}: {response.text[:200]}")
    except Exception as e:
        logger.error(f"Model server connection failed: {e}")
        raise RuntimeError(f"Model server request failed: {e}") from e


async def query_model_ocr_async(
    base64_image: str,
    mime_type: str,
    semaphore: asyncio.Semaphore,
):
    """Async wrapper for concurrent page processing."""
    async with semaphore:
        return await asyncio.to_thread(query_model_ocr, base64_image, mime_type)


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _job_dir(job_id: str) -> Path:
    return OCR_JOB_DIR / job_id


def _job_metadata_path(job_id: str) -> Path:
    return _job_dir(job_id) / "job.json"


def _read_job(job_id: str) -> dict:
    path = _job_metadata_path(job_id)
    if not path.exists():
        raise FileNotFoundError(job_id)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_job(job_id: str, data: dict):
    path = _job_metadata_path(job_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    tmp.replace(path)


def _public_job(data: dict) -> dict:
    hidden = {"api_key", "source_path", "result_path"}
    return {key: value for key, value in data.items() if key not in hidden}


def _job_for_api_key(job_id: str, api_key: str) -> dict:
    try:
        job = _read_job(job_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="OCR job not found.")
    if job.get("api_key") != api_key:
        raise HTTPException(status_code=403, detail="Not authorized to access this OCR job.")
    return job


def _job_cancel_requested(job_id: str) -> bool:
    try:
        return bool(_read_job(job_id).get("cancel_requested"))
    except FileNotFoundError:
        return False


def _mark_job_cancelled(job_id: str, reason: str = "Cancelled by user") -> dict:
    job = _read_job(job_id)
    if job.get("status") == "completed":
        return job
    if job.get("status") != "cancelled":
        job.update({
            "status": "cancelled",
            "cancel_requested": True,
            "cancelled_at": _now(),
            "cancel_reason": reason,
            "finished_at": _now(),
            "updated_at": _now(),
            "error": None,
        })
        _write_job(job_id, job)
        logger.info(f"OCR JOB CANCELLED | id={job_id} | file={job.get('filename')} | reason={reason}")
    return job


def _request_job_cancel(job_id: str, reason: str = "Cancelled by user") -> dict:
    job = _read_job(job_id)
    if job.get("status") in {"completed", "failed", "cancelled"}:
        return job
    job.update({
        "cancel_requested": True,
        "cancel_reason": reason,
        "cancelled_at": _now(),
        "updated_at": _now(),
    })
    if job.get("status") == "queued":
        job["status"] = "cancelled"
        job["finished_at"] = _now()
    elif job.get("status") == "running":
        job["status"] = "cancelling"
    _write_job(job_id, job)
    logger.info(f"OCR JOB CANCEL REQUESTED | id={job_id} | file={job.get('filename')} | status={job.get('status')}")
    return job


def _cleanup_expired_jobs():
    OCR_JOB_DIR.mkdir(parents=True, exist_ok=True)
    expiry = time.time() - (OCR_JOB_RETENTION_HOURS * 3600)
    for job_path in OCR_JOB_DIR.iterdir():
        if not job_path.is_dir() or job_path.stat().st_mtime >= expiry:
            continue
        try:
            shutil.rmtree(job_path)
            logger.info(f"OCR job cleanup: removed {job_path.name}")
        except Exception as exc:
            logger.warning(f"OCR job cleanup failed for {job_path.name}: {exc}")


def _record_usage(api_key: str, filename: str, pages: int, input_tokens: int, output_tokens: int, execution_time: float):
    total_tokens = input_tokens + output_tokens
    tokens_per_sec = round(total_tokens / execution_time, 2) if execution_time > 0 else 0
    db_ref = API_KEY_DB[api_key]
    session_cost = pages * db_ref["rate_per_page"]
    db_ref["current_month_spend"] += session_cost
    db_ref["metrics"]["total_documents"] += 1
    db_ref["metrics"]["total_pages_processed"] += pages
    db_ref["metrics"]["total_input_tokens"] += input_tokens
    db_ref["metrics"]["total_output_tokens"] += output_tokens
    db_ref["audit_logs"].append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename": filename,
            "pages": pages,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_sec": execution_time,
            "tokens_per_sec": tokens_per_sec,
            "cost_usd": session_cost,
        }
    )
    return total_tokens, tokens_per_sec, session_cost


async def _process_ocr_bytes(
    file_bytes: bytes,
    filename: str,
    content_type: str,
    dpi: int,
    mode: str,
    max_concurrency: int,
    progress_callback=None,
    cancel_check=None,
) -> dict:
    """Extract OCR text with bounded page batches and optional progress reporting."""
    mode = mode.lower().strip()
    if mode not in {"serial", "concurrent"}:
        raise ValueError("Invalid mode. Use 'serial' or 'concurrent'.")

    effective_concurrency = max(1, min(max_concurrency or MAX_PAGE_CONCURRENCY, 8))
    page_text = {}
    page_failures = []
    input_tokens = 0
    output_tokens = 0

    async def report(total: int, completed: int):
        if progress_callback:
            await progress_callback(total, completed, input_tokens, output_tokens, page_failures)

    def check_cancelled():
        if cancel_check and cancel_check():
            raise OCRJobCancelled("OCR job cancelled by user")

    async def process_page(index: int, payload: str):
        try:
            text, prompt_tokens, completion_tokens = await query_model_ocr_async(payload, "image/jpeg", semaphore)
            if not text or not text.strip():
                raise RuntimeError("Model returned an empty OCR response")
            return index, text, prompt_tokens, completion_tokens, None
        except Exception as exc:
            return index, "", 0, 0, str(exc)

    if content_type == "application/pdf":
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        total_pages = len(doc)
        if total_pages == 0:
            doc.close()
            raise RuntimeError("PDF contains no pages")
        logger.info(f"OCR rendering: {filename} | {total_pages} pages | {dpi} DPI | {mode}")
        semaphore = asyncio.Semaphore(effective_concurrency)
        completed = 0
        batch_size = 1 if mode == "serial" else effective_concurrency
        try:
            for batch_start in range(0, total_pages, batch_size):
                check_cancelled()
                batch = []
                for index in range(batch_start, min(batch_start + batch_size, total_pages)):
                    pix = doc[index].get_pixmap(dpi=dpi)
                    payload = base64.b64encode(pix.tobytes("jpeg")).decode("utf-8")
                    batch.append((index, payload))
                tasks = [asyncio.create_task(process_page(index, payload)) for index, payload in batch]
                for task in asyncio.as_completed(tasks):
                    index, text, p_tok, c_tok, error = await task
                    completed += 1
                    input_tokens += p_tok
                    output_tokens += c_tok
                    if error:
                        page_failures.append({"page": index + 1, "error": error})
                        logger.warning(f"OCR page failed: {filename} | page {index + 1}/{total_pages} | {error}")
                    else:
                        page_text[index] = text
                        logger.info(f"OCR page complete: {filename} | page {index + 1}/{total_pages}")
                    await report(total_pages, completed)
                check_cancelled()
        finally:
            doc.close()
        if not page_text:
            raise RuntimeError("OCR failed for every PDF page")
        markdown = "".join(
            f"\n<!-- SECTION: PAGE {index + 1} -->\n{text}\n"
            for index, text in sorted(page_text.items())
        )
        return {
            "markdown": _normalize_markdown_tables(markdown),
            "pages": total_pages,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "page_failures": page_failures,
        }

    if content_type in {"image/jpeg", "image/jpg", "image/png"}:
        mime_type = content_type or "image/png"
        check_cancelled()
        try:
            text, input_tokens, output_tokens = await asyncio.to_thread(
                query_model_ocr, base64.b64encode(file_bytes).decode("utf-8"), mime_type
            )
        except Exception as exc:
            raise RuntimeError(f"OCR failed for image: {exc}") from exc
        check_cancelled()
        if not text or not text.strip():
            raise RuntimeError("Model returned an empty OCR response")
        await report(1, 1)
        return {
            "markdown": _normalize_markdown_tables(text),
            "pages": 1,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "page_failures": [],
        }

    raise ValueError(f"Unsupported file format: {content_type}. Use PDF, JPG, or PNG.")


# ---------------------------------------------------------------------------
# Markdown Table Normalization
# ---------------------------------------------------------------------------
def _normalize_markdown_tables(markdown_text: str) -> str:
    """Normalizes Markdown tables so each row has a consistent column count."""
    lines = markdown_text.splitlines()
    output = []
    in_table = False
    table_rows = []

    def flush_table():
        if not table_rows:
            return

        max_cols = max(row[1] for row in table_rows)
        for raw_line, col_count in table_rows:
            stripped = raw_line.strip()
            if set(stripped.replace("|", "").replace(":", "").replace("-", "")) == {""}:
                output.append(raw_line)
                continue

            parts = [p.strip() for p in stripped.strip("|").split("|")]
            if len(parts) < max_cols:
                parts.extend([""] * (max_cols - len(parts)))
            elif len(parts) > max_cols:
                parts = parts[:max_cols]

            rebuilt = "| " + " | ".join(parts) + " |"
            output.append(rebuilt)

        table_rows.clear()

    for line in lines:
        stripped = line.strip()
        if "|" in stripped and stripped.startswith("|") and stripped.endswith("|"):
            in_table = True
            col_count = len(stripped.strip("|").split("|"))
            table_rows.append((line, col_count))
            continue

        if in_table:
            flush_table()
            in_table = False

        output.append(line)

    if in_table:
        flush_table()

    return "\n".join(output)


# ---------------------------------------------------------------------------
# Disk-backed OCR jobs
# ---------------------------------------------------------------------------
async def _run_ocr_job(job_id: str):
    job = _read_job(job_id)
    if job.get("cancel_requested") or job.get("status") == "cancelled":
        _mark_job_cancelled(job_id, job.get("cancel_reason") or "Cancelled before start")
        return
    job.update({"status": "running", "started_at": _now(), "error": None})
    _write_job(job_id, job)
    logger.info(f"OCR JOB START | id={job_id} | file={job['filename']}")
    started = time.time()

    async def progress(total, completed, input_tokens, output_tokens, page_failures):
        current = _read_job(job_id)
        current.update(
            {
                "status": "cancelling" if current.get("cancel_requested") else "running",
                "pages_total": total,
                "pages_completed": completed,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "page_failures": page_failures,
                "elapsed_seconds": round(time.time() - started, 2),
                "updated_at": _now(),
            }
        )
        _write_job(job_id, current)
        logger.info(f"OCR JOB PROGRESS | id={job_id} | pages={completed}/{total}")

    try:
        source_bytes = Path(job["source_path"]).read_bytes()
        result = await _process_ocr_bytes(
            source_bytes,
            job["filename"],
            job["content_type"],
            int(job["dpi"]),
            job["mode"],
            int(job["max_concurrency"]),
            progress,
            lambda: _job_cancel_requested(job_id),
        )
        if _job_cancel_requested(job_id):
            raise OCRJobCancelled("OCR job cancelled by user")
        elapsed = round(time.time() - started, 2)
        total_tokens, tokens_per_sec, session_cost = _record_usage(
            job["api_key"], job["filename"], result["pages"], result["input_tokens"], result["output_tokens"], elapsed
        )
        result_path = _job_dir(job_id) / "result.md"
        result_path.write_text(result["markdown"], encoding="utf-8")
        job = _read_job(job_id)
        job.update(
            {
                "status": "completed",
                "finished_at": _now(),
                "updated_at": _now(),
                "elapsed_seconds": elapsed,
                "pages_total": result["pages"],
                "pages_completed": result["pages"],
                "input_tokens": result["input_tokens"],
                "output_tokens": result["output_tokens"],
                "total_tokens": total_tokens,
                "tokens_per_sec": tokens_per_sec,
                "cost_usd": session_cost,
                "page_failures": result["page_failures"],
                "result_path": str(result_path),
            }
        )
        _write_job(job_id, job)
        logger.info(
            f"OCR JOB COMPLETE | id={job_id} | file={job['filename']} | pages={result['pages']} | "
            f"tokens={total_tokens} | elapsed={elapsed}s | page_failures={len(result['page_failures'])}"
        )
    except OCRJobCancelled as exc:
        elapsed = round(time.time() - started, 2)
        job = _mark_job_cancelled(job_id, str(exc))
        job.update({
            "elapsed_seconds": elapsed,
            "updated_at": _now(),
            "finished_at": job.get("finished_at") or _now(),
        })
        _write_job(job_id, job)
    except Exception as exc:
        elapsed = round(time.time() - started, 2)
        job = _read_job(job_id)
        job.update(
            {
                "status": "failed",
                "finished_at": _now(),
                "updated_at": _now(),
                "elapsed_seconds": elapsed,
                "error": str(exc),
            }
        )
        _write_job(job_id, job)
        logger.error(f"OCR JOB FAILED | id={job_id} | file={job['filename']} | error={exc}", exc_info=True)
    finally:
        _cleanup_expired_jobs()


async def _ocr_job_worker(worker_number: int):
    logger.info(f"OCR job worker {worker_number} started")
    while True:
        job_id = await _job_queue.get()
        try:
            await _run_ocr_job(job_id)
        except Exception as exc:
            logger.error(f"OCR job worker {worker_number} unexpected failure for {job_id}: {exc}", exc_info=True)
        finally:
            _job_queue.task_done()


@app.on_event("startup")
async def start_ocr_job_workers():
    OCR_JOB_DIR.mkdir(parents=True, exist_ok=True)
    _cleanup_expired_jobs()
    for metadata_path in OCR_JOB_DIR.glob("*/job.json"):
        try:
            job = json.loads(metadata_path.read_text(encoding="utf-8"))
            if job.get("status") in {"queued", "running", "cancelling"} and Path(job.get("source_path", "")).exists():
                if job.get("cancel_requested") or not OCR_RECOVER_JOBS_ON_STARTUP:
                    reason = job.get("cancel_reason") or "Cancelled during startup recovery"
                    if not OCR_RECOVER_JOBS_ON_STARTUP:
                        reason = "Cancelled because OCR_RECOVER_JOBS_ON_STARTUP=false"
                    _mark_job_cancelled(job["job_id"], reason)
                    continue
                job.update({"status": "queued", "updated_at": _now(), "recovered_after_restart": True})
                _write_job(job["job_id"], job)
                await _job_queue.put(job["job_id"])
                logger.info(f"OCR JOB RECOVERED | id={job['job_id']} | file={job['filename']}")
        except Exception as exc:
            logger.warning(f"OCR job recovery skipped for {metadata_path}: {exc}")
    for worker_number in range(OCR_JOB_CONCURRENCY):
        _job_workers.append(asyncio.create_task(_ocr_job_worker(worker_number + 1)))


@app.on_event("shutdown")
async def stop_ocr_job_workers():
    for worker in _job_workers:
        worker.cancel()
    if _job_workers:
        await asyncio.gather(*_job_workers, return_exceptions=True)
    _job_workers.clear()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/healthz", tags=["System"])
async def health_check():
    """Liveness probe — also verifies model server connectivity."""
    model_status = "unreachable"
    try:
        # Try the llama.cpp health endpoint first
        r = requests.get(
            MODEL_URL.replace("/v1/chat/completions", "/health"),
            timeout=5,
        )
        if r.status_code == 200:
            model_status = "ready"
        else:
            model_status = f"responding (status {r.status_code})"
    except requests.exceptions.ConnectionError:
        model_status = "unreachable"
    except Exception as e:
        model_status = f"error: {str(e)}"

    healthy = model_status == "ready"
    return {
        "status": "healthy" if healthy else "degraded",
        "model_server": model_status,
        "model_name": MODEL_NAME,
        "model_url": MODEL_URL,
        "api_keys_loaded": len(API_KEY_DB),
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/v1/ocr/jobs", status_code=status.HTTP_202_ACCEPTED, tags=["OCR Jobs"])
async def submit_ocr_job(
    file: UploadFile = File(..., description="PDF, JPG, or PNG file to process"),
    api_key: str = Depends(verify_api_key),
    dpi: int = Query(200, ge=72, le=400, description="Render DPI for PDF pages"),
    mode: str = Query("concurrent", description="Processing mode: 'serial' or 'concurrent'"),
    max_concurrency: int = Query(None, ge=1, le=8, description="Max parallel pages"),
):
    """Submit an OCR job and return immediately with a pollable job identifier."""
    mode = mode.lower().strip()
    if mode not in {"serial", "concurrent"}:
        raise HTTPException(status_code=400, detail="Invalid mode. Use 'serial' or 'concurrent'.")
    content_type = file.content_type or ""
    if content_type not in {"application/pdf", "image/jpeg", "image/jpg", "image/png"}:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {content_type}. Use PDF, JPG, or PNG.")

    job_id = uuid.uuid4().hex
    job_path = _job_dir(job_id)
    job_path.mkdir(parents=True, exist_ok=False)
    suffix = Path(file.filename or "upload").suffix.lower() or ".bin"
    source_path = job_path / f"source{suffix}"
    source_path.write_bytes(await file.read())
    job = {
        "job_id": job_id,
        "status": "queued",
        "filename": file.filename or source_path.name,
        "content_type": content_type,
        "dpi": dpi,
        "mode": mode,
        "max_concurrency": max_concurrency or MAX_PAGE_CONCURRENCY,
        "pages_total": 0,
        "pages_completed": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "page_failures": [],
        "error": None,
        "created_at": _now(),
        "updated_at": _now(),
        "source_path": str(source_path),
        "api_key": api_key,
    }
    _write_job(job_id, job)
    await _job_queue.put(job_id)
    logger.info(f"OCR JOB SUBMITTED | id={job_id} | file={job['filename']} | mode={mode} | dpi={dpi}")
    return _public_job(job)


@app.get("/v1/ocr/jobs/{job_id}", tags=["OCR Jobs"])
async def get_ocr_job(job_id: str, api_key: str = Depends(verify_api_key)):
    """Return status and progress for a submitted OCR job."""
    return _public_job(_job_for_api_key(job_id, api_key))


@app.delete("/v1/ocr/jobs/{job_id}", tags=["OCR Jobs"])
async def cancel_ocr_job(job_id: str, api_key: str = Depends(verify_api_key)):
    """Cancel a queued or running OCR job."""
    _job_for_api_key(job_id, api_key)
    job = _request_job_cancel(job_id)
    return _public_job(job)


@app.post("/v1/ocr/jobs/cancel", tags=["OCR Jobs"])
async def cancel_ocr_jobs(payload: dict = Body(...), api_key: str = Depends(verify_api_key)):
    """Cancel multiple queued or running OCR jobs."""
    job_ids = payload.get("job_ids") or []
    if not isinstance(job_ids, list):
        raise HTTPException(status_code=400, detail="job_ids must be a list.")
    cancelled = []
    errors = []
    for job_id in job_ids:
        try:
            _job_for_api_key(str(job_id), api_key)
            cancelled.append(_public_job(_request_job_cancel(str(job_id))))
        except HTTPException as exc:
            errors.append({"job_id": job_id, "status_code": exc.status_code, "error": exc.detail})
    return {"status": "ok", "cancelled": cancelled, "errors": errors}


@app.get("/v1/ocr/jobs/{job_id}/result", response_class=Response, tags=["OCR Jobs"])
async def get_ocr_job_result(job_id: str, api_key: str = Depends(verify_api_key)):
    """Return completed Markdown output for an OCR job."""
    job = _job_for_api_key(job_id, api_key)
    if job["status"] == "failed":
        raise HTTPException(status_code=422, detail=job.get("error") or "OCR job failed.")
    if job["status"] != "completed":
        raise HTTPException(status_code=409, detail=f"OCR job is {job['status']}; result is not ready.")
    result_path = Path(job.get("result_path", ""))
    if not result_path.exists():
        raise HTTPException(status_code=500, detail="OCR job completed without a result file.")
    return Response(
        content=result_path.read_text(encoding="utf-8"),
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="{job["filename"]}.md"',
            "X-Process-Time": str(job.get("elapsed_seconds", 0)),
            "X-Total-Tokens": str(job.get("total_tokens", 0)),
            "X-Tokens-Per-Sec": str(job.get("tokens_per_sec", 0)),
        },
    )


@app.post("/v1/ocr", response_class=Response, tags=["OCR"])
async def process_document(
    file: UploadFile = File(..., description="PDF, JPG, or PNG file to process"),
    api_key: str = Depends(verify_api_key),
    dpi: int = Query(200, ge=72, le=400, description="Render DPI for PDF pages"),
    mode: str = Query("concurrent", description="Processing mode: 'serial' or 'concurrent'"),
    max_concurrency: int = Query(
        None, ge=1, le=8, description="Max parallel pages (concurrent mode only)"
    ),
):
    """
    Core OCR endpoint. Accepts a PDF or image file and returns structured Markdown.

    Response headers include processing telemetry:
    - `X-Process-Time`: Total processing time in seconds
    - `X-Total-Tokens`: Combined input + output tokens
    - `X-Tokens-Per-Sec`: Throughput metric
    """
    start_time = time.time()
    file_bytes = await file.read()
    content_type = file.content_type or ""
    logger.info(
        f"OCR request: file={file.filename}, type={content_type}, "
        f"dpi={dpi}, mode={mode}, concurrency={max_concurrency or MAX_PAGE_CONCURRENCY}"
    )
    try:
        result = await _process_ocr_bytes(
            file_bytes, file.filename or "upload", content_type, dpi, mode,
            max_concurrency or MAX_PAGE_CONCURRENCY,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error(f"Processing failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing Exception: {exc}")

    execution_time = round(time.time() - start_time, 2)
    total_tokens, tokens_per_sec, _ = _record_usage(
        api_key, file.filename or "upload", result["pages"], result["input_tokens"], result["output_tokens"], execution_time
    )
    generated_markdown = result["markdown"]
    logger.info(
        f"OCR complete: {file.filename} | {result['pages']} pages | "
        f"{total_tokens} tokens | {tokens_per_sec} tok/s | {execution_time}s | "
        f"page_failures={len(result['page_failures'])}"
    )

    return Response(
        content=generated_markdown,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="{file.filename}.md"',
            "X-Process-Time": str(execution_time),
            "X-Total-Tokens": str(total_tokens),
            "X-Tokens-Per-Sec": str(tokens_per_sec),
        },
    )


@app.get("/v1/metrics", tags=["Monitoring"])
async def get_billing_metrics(api_key: str = Depends(verify_api_key)):
    """Returns usage metrics, spend tracking, and audit logs for the authenticated API key."""
    return API_KEY_DB[api_key]


# ---------------------------------------------------------------------------
# Standalone Runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting OCR Pipeline API on {API_HOST}:{API_PORT}")
    logger.info(f"Model server: {MODEL_URL} ({MODEL_NAME})")
    logger.info(f"Max page concurrency: {MAX_PAGE_CONCURRENCY}")
    logger.info(f"Max document concurrency: {OCR_JOB_CONCURRENCY}")
    logger.info(f"Swagger UI: http://{API_HOST}:{API_PORT}/docs")

    uvicorn.run(
        "ocr_service:app",
        host=API_HOST,
        port=API_PORT,
        log_level="info",
    )
