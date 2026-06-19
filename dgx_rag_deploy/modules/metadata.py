"""
Metadata — Auto-Tagging & Filter Extraction
============================================
LLM-powered document metadata generation.
Used during ingestion (not in the chat hot path).
"""

import json
import logging
from typing import Dict, List

import requests

log = logging.getLogger("rag-pipeline")


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------
AUTOTAG_PROMPT = """Analyze this document and return ONLY a valid JSON object with these fields:
{
  "doc_type": "invoice|contract|report|letter|memo|receipt|policy|form|certificate|other",
  "date": "YYYY-MM-DD or null if not found",
  "parties": ["list of people or organizations mentioned"],
  "tags": ["3-7 relevant topic keywords"],
  "summary": "One concise sentence describing the document"
}

Rules:
- Return ONLY the JSON, no explanation
- Use lowercase for doc_type and tags
- If a field cannot be determined, use null or empty list

Document:
---
{text}
---"""

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
) -> str:
    """Call the chat LLM and return content string."""
    r = requests.post(
        chat_url,
        json={"model": chat_model, "messages": messages, "temperature": temperature},
        headers={"Authorization": f"Bearer {chat_api_key}"},
        timeout=180,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Chat failed: {r.status_code} {r.text[:200]}")
    return r.json()["choices"][0]["message"]["content"]


def _clean_json_response(raw: str) -> str:
    """Strip markdown code fences from LLM JSON responses."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0]
    return cleaned.strip()


# ---------------------------------------------------------------------------
# Auto-Tagging
# ---------------------------------------------------------------------------
def autotag_document(
    markdown_text: str,
    chat_url: str,
    chat_model: str,
    chat_api_key: str,
    max_chars: int = 3000,
) -> dict:
    """Use Chat LLM to auto-generate metadata tags from document text."""
    snippet = (markdown_text or "")[:max_chars]
    if not snippet.strip():
        return {}
    try:
        prompt = AUTOTAG_PROMPT.replace("{text}", snippet)
        raw = _chat_completion(
            [{"role": "user", "content": prompt}],
            chat_url, chat_model, chat_api_key,
            temperature=0.1,
        )
        result = json.loads(_clean_json_response(raw))
        # Ensure expected fields exist
        schema = {"doc_type": "other", "date": None, "parties": [], "tags": [], "summary": ""}
        for k, default in schema.items():
            if k not in result:
                result[k] = default
        return result
    except Exception as e:
        log.warning(f"Auto-tag failed: {e}")
        return {"doc_type": "other", "date": None, "parties": [], "tags": [], "summary": "", "_error": str(e)}


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
