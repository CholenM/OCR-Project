"""
Metadata — Auto-Tagging & Filter Extraction
============================================
LLM-powered document metadata generation.
Used during ingestion (not in the chat hot path).
"""

import json
import logging
import re
from typing import Dict, List

import requests

log = logging.getLogger("rag-pipeline")

AUTOTAG_PROMPT_VERSION = "autotag-v2"
AUTOTAG_SCHEMA = {"doc_type": "other", "date": None, "parties": [], "tags": [], "summary": ""}


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------
AUTOTAG_PROMPT = """Return ONLY compact JSON for this document.
Fields: doc_type, date, parties, tags, summary.
doc_type must be one of: invoice, contract, report, letter, memo, receipt, policy, form, certificate, other.
Use null/[] when unknown. Lowercase doc_type and tags.

Filename: {filename}
Text:
{text}"""

FILTER_EXTRACT_PROMPT = """Given this user query, extract metadata filters to narrow document search.
Return ONLY a valid JSON object. Only include fields you can confidently extract.
Return {} if no filters can be extracted.

Available filters:
- "doc_type": string (invoice, contract, report, letter, memo, receipt, policy, form, certificate)
- "tags": list of keyword strings
- "parties": list of people/organization names
- "date_from": "YYYY-MM-DD" (documents from this date onwards)
- "date_to": "YYYY-MM-DD" (documents up to this date)
- "filename": partial filename match

Query: {query}"""


# ---------------------------------------------------------------------------
# Chat LLM Helper
# ---------------------------------------------------------------------------
def _chat_completion(
    messages: List[Dict],
    chat_url: str,
    chat_model: str,
    chat_api_key: str,
    temperature: float = 0.7,
    max_tokens: int = None,
) -> str:
    """Call the chat LLM and return content string."""
    payload = {"model": chat_model, "messages": messages, "temperature": temperature}
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    r = requests.post(
        chat_url,
        json=payload,
        headers={"Authorization": f"Bearer {chat_api_key}"},
        timeout=180,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Chat failed: {r.status_code} {r.text[:200]}")
    return r.json()["choices"][0]["message"]["content"]


def _clean_json_response(raw: str) -> str:
    """Return the first JSON object from a model response."""
    if raw is None:
        raise ValueError("LLM returned an empty response")
    cleaned = str(raw).strip()
    if not cleaned:
        raise ValueError("LLM returned an empty response")

    fence = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.IGNORECASE | re.DOTALL)
    if fence:
        cleaned = fence.group(1).strip()

    decoder = json.JSONDecoder()
    for idx, char in enumerate(cleaned):
        if char != "{":
            continue
        try:
            parsed, end = decoder.raw_decode(cleaned[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return cleaned[idx:idx + end].strip()

    excerpt = re.sub(r"\s+", " ", cleaned)[:200]
    raise ValueError(f"LLM did not return a JSON object. Raw response: {excerpt}")


def build_autotag_snippet(markdown_text: str, max_chars: int = 3000) -> str:
    """Sample the start and end of long documents for faster metadata extraction."""
    text = re.sub(r"[ \t]+", " ", markdown_text or "")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if max_chars <= 0 or len(text) <= max_chars:
        return text

    head_chars = max(1, int(max_chars * 0.7))
    tail_chars = max(1, max_chars - head_chars)
    return (
        text[:head_chars].rstrip()
        + "\n\n[... middle omitted for faster metadata extraction ...]\n\n"
        + text[-tail_chars:].lstrip()
    )


def normalize_autotag_result(result: dict) -> dict:
    """Coerce model output into the public metadata schema."""
    if not isinstance(result, dict):
        result = {}

    normalized = dict(AUTOTAG_SCHEMA)
    normalized.update({k: result.get(k, v) for k, v in AUTOTAG_SCHEMA.items()})

    doc_type = normalized.get("doc_type") or "other"
    normalized["doc_type"] = str(doc_type).strip().lower() or "other"

    date = normalized.get("date")
    normalized["date"] = str(date).strip() if date else None

    for field in ("parties", "tags"):
        value = normalized.get(field)
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            value = []
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        if field == "tags":
            cleaned = [item.lower() for item in cleaned]
        normalized[field] = cleaned

    summary = normalized.get("summary") or ""
    normalized["summary"] = str(summary).strip()
    return normalized


# ---------------------------------------------------------------------------
# Auto-Tagging
# ---------------------------------------------------------------------------
def autotag_document(
    markdown_text: str,
    chat_url: str,
    chat_model: str,
    chat_api_key: str,
    max_chars: int = 800,
    filename: str = "",
) -> dict:
    """Use Chat LLM to auto-generate metadata tags from document text."""
    if not (markdown_text or "").strip():
        return {}

    def run_once(char_budget: int) -> dict:
        snippet = build_autotag_snippet(markdown_text, char_budget)
        if not snippet.strip():
            return {}
        prompt = AUTOTAG_PROMPT.replace("{filename}", filename or "unknown").replace("{text}", snippet)
        raw = _chat_completion(
            [{"role": "user", "content": prompt}],
            chat_url, chat_model, chat_api_key,
            temperature=0.0,
            max_tokens=256,
        )
        result = json.loads(_clean_json_response(raw))
        return normalize_autotag_result(result)

    try:
        return run_once(max_chars)
    except Exception as e:
        if "Context size has been exceeded" in str(e) and max_chars > 200:
            try:
                return run_once(max(200, max_chars // 2))
            except Exception as retry_error:
                e = retry_error
        log.warning(f"Auto-tag failed: {e}")
        fallback = dict(AUTOTAG_SCHEMA)
        fallback["_error"] = str(e)
        return fallback


# ---------------------------------------------------------------------------
# Filter Extraction (opt-in, not in hot path)
# ---------------------------------------------------------------------------
def extract_filters_from_query(
    query: str,
    chat_url: str,
    chat_model: str,
    chat_api_key: str,
) -> dict:
    """Use Chat LLM to extract metadata filters from a natural language query."""
    try:
        prompt = FILTER_EXTRACT_PROMPT.replace("{query}", query)
        raw = _chat_completion(
            [{"role": "user", "content": prompt}],
            chat_url, chat_model, chat_api_key,
            temperature=0.0,
        )
        return json.loads(_clean_json_response(raw))
    except Exception as e:
        log.warning(f"Filter extraction failed: {e}")
        return {}
