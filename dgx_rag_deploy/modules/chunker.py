"""
Chunker — Markdown-Aware Structural Chunking
=============================================
Splits markdown documents into semantically coherent chunks,
preserving tables as atomic units and respecting header boundaries.

Extracted from rag_service.py v2 for modularity.
"""

import re
import logging
from typing import Dict, List

log = logging.getLogger("rag-pipeline")

# Default chunk size
DEFAULT_CHUNK_SIZE = 1200


# ---------------------------------------------------------------------------
# Header Splitting
# ---------------------------------------------------------------------------
def _split_by_headers(text: str) -> List[tuple]:
    """Split text into (header, body) tuples at Markdown header boundaries."""
    pattern = re.compile(r'^(#{1,6}\s+.+)$', re.MULTILINE)
    parts = pattern.split(text)
    sections = []
    i = 0
    # Content before first header
    if parts and not parts[0].strip().startswith('#'):
        if parts[0].strip():
            sections.append(("", parts[0]))
        i = 1
    while i < len(parts):
        if parts[i].strip().startswith('#'):
            header = parts[i].strip()
            body = parts[i + 1] if i + 1 < len(parts) else ""
            sections.append((header, body))
            i += 2
        else:
            if parts[i].strip():
                sections.append(("", parts[i]))
            i += 1
    return sections


# ---------------------------------------------------------------------------
# Table Extraction
# ---------------------------------------------------------------------------
def _extract_tables_and_text(text: str) -> List[tuple]:
    """Split section body into [(content, type)] preserving tables as atomic units."""
    results = []
    # Handle HTML tables first
    html_pattern = re.compile(r'(<table\b.*?</table>)', re.DOTALL | re.IGNORECASE)
    last = 0
    for m in html_pattern.finditer(text):
        before = text[last:m.start()].strip()
        if before:
            results.extend(_extract_md_tables(before))
        results.append((m.group(0), "table"))
        last = m.end()
    after = text[last:].strip()
    if after:
        results.extend(_extract_md_tables(after))
    if not results and text.strip():
        results = _extract_md_tables(text)
    return results if results else [(text, _detect_type(text))]


def _extract_md_tables(text: str) -> List[tuple]:
    """Extract Markdown pipe-delimited tables from text."""
    lines = text.split('\n')
    parts, buf, table_buf, in_table = [], [], [], False
    for line in lines:
        s = line.strip()
        is_tbl = s.startswith('|') and s.endswith('|') and '|' in s[1:-1]
        if is_tbl:
            if not in_table:
                joined = '\n'.join(buf).strip()
                if joined:
                    parts.append((joined, _detect_type(joined)))
                buf = []
                in_table = True
            table_buf.append(line)
        else:
            if in_table:
                joined = '\n'.join(table_buf).strip()
                if joined:
                    parts.append((joined, "table"))
                table_buf = []
                in_table = False
            buf.append(line)
    if in_table and table_buf:
        parts.append(('\n'.join(table_buf).strip(), "table"))
    elif buf:
        joined = '\n'.join(buf).strip()
        if joined:
            parts.append((joined, _detect_type(joined)))
    return parts


def _detect_type(text: str) -> str:
    """Detect if text is primarily a list or prose."""
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    if not lines:
        return "prose"
    list_ct = sum(1 for l in lines if re.match(r'^[-*•]\s|^\d+\.\s', l))
    return "list" if lines and list_ct / len(lines) > 0.4 else "prose"


# ---------------------------------------------------------------------------
# Sentence Splitting
# ---------------------------------------------------------------------------
def _split_sentences(text: str, max_size: int, header: str = "") -> List[str]:
    """Split large prose at sentence/line boundaries, prepending header."""
    units = re.split(r'(?<=[.!?])\s+|\n', text)
    units = [u.strip() for u in units if u.strip()]
    chunks, current = [], header + "\n" if header else ""
    for unit in units:
        candidate = f"{current}\n{unit}" if current.strip() else (f"{header}\n{unit}" if header else unit)
        if len(candidate) <= max_size:
            current = candidate
        else:
            if current.strip() and current.strip() != header:
                chunks.append(current)
            current = f"{header}\n{unit}" if header else unit
    if current.strip() and current.strip() != header:
        chunks.append(current)
    return chunks


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def chunk_markdown_structural(text: str, max_chunk_size: int = None) -> List[Dict]:
    """
    Markdown-aware chunking. Returns list of:
      {"text": str, "section": str, "content_type": str}

    Rules:
      - Tables are NEVER split (kept as atomic chunks)
      - Section headers are chunk boundaries
      - Each chunk is prefixed with its section header
      - Large prose is split at sentence boundaries
    """
    max_chunk_size = max_chunk_size or DEFAULT_CHUNK_SIZE
    cleaned = (text or "").strip()
    if not cleaned:
        return []

    sections = _split_by_headers(cleaned)
    chunks = []

    for header, body in sections:
        if not body.strip():
            continue

        parts = _extract_tables_and_text(body)

        for part_text, part_type in parts:
            if not part_text.strip():
                continue

            enriched = f"{header}\n{part_text}" if header else part_text

            if part_type == "table" or len(enriched) <= max_chunk_size:
                chunks.append({
                    "text": enriched,
                    "section": header or "(preamble)",
                    "content_type": part_type,
                })
            else:
                for sc in _split_sentences(part_text, max_chunk_size, header):
                    chunks.append({
                        "text": sc,
                        "section": header or "(preamble)",
                        "content_type": part_type,
                    })

    return chunks
