"""
OCR + RAG Control Center v4
Usage: streamlit run example_ui.py
"""
import io
import base64
import json
import os
import re
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
import streamlit as st

DEFAULT_OCR_URL = os.getenv("OCR_API_URL", "http://192.168.50.153:8080")
DEFAULT_RAG_URL = os.getenv("RAG_API_URL", "http://192.168.50.153:8081")
QDRANT_DASHBOARD = os.getenv("QDRANT_DASHBOARD", "http://192.168.50.153:6333/dashboard")
BATCH_SIZE = 3
DOC_TYPES = ["invoice", "contract", "report", "letter", "memo", "receipt", "policy", "form", "certificate", "other"]
OCR_UPLOAD_TYPES = ["pdf", "jpg", "jpeg", "png"]
DOCUMENT_UPLOAD_TYPES = ["md", "txt", "csv", "docx", "doc", "dotx", "odt", "rtf", "xls", "xlsx", "xlsm", "xlsb", "xlt", "ppt", "pptx"]
DIRECT_UPLOAD_TYPES = set(DOCUMENT_UPLOAD_TYPES)


def _default_advanced_settings():
    return {
        "top_k": 15,
        "memory_enabled": True,
        "memory_top_k": 5,
        "streaming_enabled": True,
        "rerank": False,
        "agentic": False,
        "auto_extract": False,
        "hyde": False,
        "f_doc_type": "(none)",
        "f_tags": "",
        "f_date_from": "",
        "f_date_to": "",
        "system_prompt": (
            "You are a helpful RAG assistant. Use the provided context to answer accurately. "
            "For basic questions, answer naturally. Cite sources when referencing documents."
        ),
    }

st.set_page_config(page_title="OCR + RAG Workspace", page_icon="", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.25rem; max-width: 1180px; }
    section[data-testid="stSidebar"] .stButton > button {
        border-radius: 8px;
        justify-content: flex-start;
        min-height: 2.35rem;
    }
    div[data-testid="stChatMessage"] {
        border-radius: 8px;
        padding: .25rem 0;
    }
    .session-meta {
        color: #6b7280;
        font-size: .82rem;
        margin: -.35rem 0 .35rem .2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _init_state():
    advanced_defaults = _default_advanced_settings()
    defaults = {
        "ocr_results": {},
        "raw_documents": {},
        "ocr_metadata": {},
        "chat_messages": [],
        "active_session": None,
        "session_list": [],
        "uploader_key": 0,
        "ocr_step": 1,
        "chat_loaded_for": None,
        "nav": "Chat",
        "draft_settings": dict(advanced_defaults),
        "applied_settings": dict(advanced_defaults),
        "settings_applied_at": None,
        "settings_flash": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    for key, value in advanced_defaults.items():
        st.session_state.draft_settings.setdefault(key, value)
        st.session_state.applied_settings.setdefault(key, value)


_init_state()


def _headers():
    api_key = st.session_state.get("api_key_input", "")
    return {"X-API-KEY": api_key} if api_key else {}


def _safe_session_label(name: str) -> str:
    return name.replace("_", " ").strip() or name


def load_sessions():
    if not st.session_state.get("api_key_input"):
        return []
    try:
        r = requests.get(f"{st.session_state.rag_url}/v1/sessions", headers=_headers(), timeout=8)
        if r.status_code == 200:
            return sorted(r.json().get("sessions", []), key=lambda s: s["name"])
    except Exception:
        pass
    return []


def load_chat_history(session_name: str):
    if not session_name or not st.session_state.get("api_key_input"):
        return []
    try:
        r = requests.get(
            f"{st.session_state.rag_url}/v1/chat/history/{session_name}",
            headers=_headers(),
            timeout=8,
        )
        if r.status_code == 200:
            return r.json().get("messages", [])
    except Exception:
        pass
    return []


def refresh_sessions():
    st.session_state.session_list = load_sessions()
    names = [s["name"] for s in st.session_state.session_list]
    if st.session_state.active_session not in names:
        st.session_state.active_session = names[0] if names else None
        st.session_state.chat_loaded_for = None


def select_session(name: str):
    if name != st.session_state.active_session:
        st.session_state.active_session = name
        st.session_state.chat_messages = load_chat_history(name)
        st.session_state.chat_loaded_for = name


def create_session(name: str):
    if not name.strip():
        st.sidebar.warning("Enter a session name.")
        return
    try:
        r = requests.post(
            f"{st.session_state.rag_url}/v1/sessions",
            headers=_headers(),
            json={"name": name.strip()},
            timeout=60,
        )
        if r.status_code == 200:
            st.session_state.active_session = r.json()["session"]
            st.session_state.chat_messages = []
            st.session_state.chat_loaded_for = st.session_state.active_session
            refresh_sessions()
            st.rerun()
        else:
            st.sidebar.error(r.text)
    except Exception as e:
        st.sidebar.error(str(e))


def _ocr_file(name, data, ctype, endpoint, headers, params):
    try:
        r = requests.post(endpoint, headers=headers, files={"file": (name, data, ctype)}, params=params, timeout=300)
        if r.status_code == 200:
            return (name, r.text, float(r.headers.get("X-Process-Time", 0)), float(r.headers.get("X-Tokens-Per-Sec", 0)), None)
        return (name, None, 0, 0, f"HTTP {r.status_code}")
    except Exception as e:
        return (name, None, 0, 0, str(e))


def _autotag(name, markdown, endpoint, headers):
    try:
        r = requests.post(endpoint, headers=headers, json={"markdown_content": markdown}, timeout=60)
        if r.status_code == 200:
            return r.json().get("metadata", {})
    except Exception:
        pass
    return {"doc_type": "other", "date": None, "parties": [], "tags": [], "summary": ""}


def _is_direct_upload(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower().lstrip(".") in DIRECT_UPLOAD_TYPES


def _service_link(label: str, url: str):
    if hasattr(st, "link_button"):
        st.link_button(label, url, use_container_width=True)
    else:
        st.markdown(f"[{label}]({url})")


def _settings():
    return st.session_state.applied_settings


def _sync_draft_from_widgets():
    draft = st.session_state.draft_settings
    for key in _default_advanced_settings():
        widget_key = f"draft_{key}"
        if widget_key in st.session_state:
            draft[key] = st.session_state[widget_key]


def _sync_widgets_from_draft():
    for key, value in st.session_state.draft_settings.items():
        st.session_state[f"draft_{key}"] = value


def _ensure_draft_widget_keys():
    for key, value in st.session_state.draft_settings.items():
        st.session_state.setdefault(f"draft_{key}", value)


def _apply_advanced_settings():
    _sync_draft_from_widgets()
    st.session_state.applied_settings = dict(st.session_state.draft_settings)
    st.session_state.settings_applied_at = time.strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.settings_flash = ("success", "Advanced settings applied. Check the Streamlit terminal for the applied snapshot.")
    s = st.session_state.applied_settings
    print(
        "ADVANCED SETTINGS APPLIED | "
        f"session={st.session_state.get('active_session') or '(none)'} | "
        f"streaming={str(s['streaming_enabled']).lower()} | "
        f"rerank={str(s['rerank']).lower()} | "
        f"agentic={str(s['agentic']).lower()} | "
        f"top_k={int(s['top_k'])} | "
        f"memory={str(s['memory_enabled']).lower()} | "
        f"memory_top_k={int(s['memory_top_k'])} | "
        f"hyde={str(s['hyde']).lower()} | "
        f"auto_filters={str(s['auto_extract']).lower()} | "
        f"doc_type={s['f_doc_type']} | "
        f"tags={s['f_tags'] or '(none)'} | "
        f"date_from={s['f_date_from'] or '(none)'} | "
        f"date_to={s['f_date_to'] or '(none)'}",
        flush=True,
    )


def _reset_draft_to_applied():
    st.session_state.draft_settings = dict(st.session_state.applied_settings)
    _sync_widgets_from_draft()
    st.session_state.settings_flash = ("info", "Draft settings reset to the currently applied values.")


def _restore_default_settings():
    defaults = _default_advanced_settings()
    st.session_state.draft_settings = dict(defaults)
    st.session_state.applied_settings = dict(defaults)
    st.session_state.settings_applied_at = time.strftime("%Y-%m-%d %H:%M:%S")
    _sync_widgets_from_draft()
    st.session_state.settings_flash = ("warning", "Advanced settings restored to defaults.")
    print("ADVANCED SETTINGS RESTORED TO DEFAULTS", flush=True)


def manual_filters():
    settings = _settings()
    filters = {}
    if settings["f_doc_type"] != "(none)":
        filters["doc_type"] = settings["f_doc_type"]
    if settings["f_tags"]:
        filters["tags"] = [t.strip() for t in settings["f_tags"].split(",") if t.strip()]
    if settings["f_date_from"]:
        filters["date_from"] = settings["f_date_from"]
    if settings["f_date_to"]:
        filters["date_to"] = settings["f_date_to"]
    return filters


def render_sources_and_memory(msg):
    latency = msg.get("latency")
    if latency:
        st.caption(f"{latency}s")
    sources = msg.get("sources") or []
    if sources:
        with st.expander(f"Sources ({len(sources)})"):
            for s in sources:
                score = s.get("score", 0)
                st.markdown(f"- **{s.get('filename', 'unknown')}** | {s.get('section', '')} | score {score:.4f}")
    memories = msg.get("memories") or []
    if memories:
        with st.expander(f"Memory ({len(memories)})"):
            for m in memories:
                st.markdown(f"- **Q:** {m.get('query', '')[:80]}...\n  **A:** {m.get('answer', '')[:120]}...")


def render_chat_message(msg):
    with st.chat_message(msg["role"]):
        st.markdown(msg.get("content", ""))
        if msg["role"] == "assistant":
            render_sources_and_memory(msg)


def ask_streaming(prompt: str, active: str):
    settings = _settings()
    payload = {
        "query": prompt,
        "collection": active,
        "top_k": int(settings["top_k"]),
        "session_id": active,
        "memory_enabled": settings["memory_enabled"],
        "memory_top_k": int(settings["memory_top_k"]),
        "rerank": settings["rerank"],
        "agentic": settings["agentic"],
        "hyde": settings["hyde"],
    }
    filters = manual_filters()
    if filters:
        payload["filters"] = filters
    if settings["system_prompt"]:
        payload["system_prompt"] = settings["system_prompt"]

    answer_placeholder = st.empty()
    status_placeholder = st.empty()
    status_placeholder.caption("Searching documents...")
    display_answer, full_answer = "", ""
    sources, memories, latency = [], [], None
    in_think_block = False

    resp = requests.post(
        f"{st.session_state.rag_url}/v1/chat/stream",
        headers=_headers(),
        json=payload,
        stream=True,
        timeout=300,
    )
    if resp.status_code != 200:
        return {"role": "assistant", "content": f"Error ({resp.status_code}): {resp.text[:300]}"}

    for line in resp.iter_lines():
        if not line:
            continue
        line = line.decode("utf-8")
        if not line.startswith("data: "):
            continue
        try:
            data = json.loads(line[6:])
        except json.JSONDecodeError:
            continue

        evt = data.get("type", "")
        if evt == "sources":
            sources = data.get("sources", [])
            memories = data.get("memories", [])
            status_placeholder.caption(f"Found {len(sources)} sources. Generating answer...")
        elif evt == "token":
            token = data.get("content", "")
            full_answer += token
            if "<think>" in token:
                in_think_block = True
            if in_think_block:
                if "</think>" in token:
                    in_think_block = False
                continue
            display_answer += token
            if display_answer.strip():
                status_placeholder.empty()
                answer_placeholder.markdown(display_answer + "▌")
        elif evt == "complete":
            latency = data.get("latency")
            if data.get("answer"):
                display_answer = data["answer"]
                full_answer = data["answer"]
        elif evt == "error":
            display_answer = f"Error: {data.get('error', 'Unknown')}"

    resp.close()
    status_placeholder.empty()
    clean = re.sub(r"<think>.*?</think>", "", display_answer, flags=re.DOTALL).strip()
    display_answer = clean or display_answer.strip() or "The model returned an empty response."
    answer_placeholder.markdown(display_answer)
    return {
        "role": "assistant",
        "content": display_answer,
        "sources": sources,
        "memories": memories,
        "latency": latency,
    }


def ask_non_streaming(prompt: str, active: str):
    settings = _settings()
    payload = {
        "query": prompt,
        "collection": active,
        "top_k": int(settings["top_k"]),
        "session_id": active,
        "memory_enabled": settings["memory_enabled"],
        "memory_top_k": int(settings["memory_top_k"]),
        "auto_extract_filters": settings["auto_extract"],
        "rerank": settings["rerank"],
        "agentic": settings["agentic"],
        "hyde": settings["hyde"],
    }
    filters = manual_filters()
    if filters:
        payload["filters"] = filters
    if settings["system_prompt"]:
        payload["system_prompt"] = settings["system_prompt"]
    try:
        r = requests.post(f"{st.session_state.rag_url}/v1/chat", headers=_headers(), json=payload, timeout=300)
        if r.status_code == 200:
            res = r.json()
            return {
                "role": "assistant",
                "content": res.get("answer", ""),
                "sources": res.get("sources", []),
                "memories": res.get("memories", []),
                "latency": res.get("latency"),
            }
        return {"role": "assistant", "content": f"Error: {r.text}"}
    except Exception as e:
        return {"role": "assistant", "content": f"Failed: {e}"}


def render_sidebar():
    st.sidebar.title("OCR + RAG")
    st.sidebar.radio(
        "Workspace",
        ["Chat", "OCR Dashboard", "Data Manager", "Advanced Settings"],
        key="nav",
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    st.session_state.ocr_url = st.sidebar.text_input("OCR Pipeline URL", value=st.session_state.get("ocr_url", DEFAULT_OCR_URL))
    st.session_state.rag_url = st.sidebar.text_input("RAG Pipeline URL", value=st.session_state.get("rag_url", DEFAULT_RAG_URL))
    st.session_state.api_key_input = st.sidebar.text_input("API Key", value=st.session_state.get("api_key_input", ""), type="password")

    c1, c2 = st.sidebar.columns(2)
    if c1.button("Health", use_container_width=True):
        for name, url in [("OCR", st.session_state.ocr_url), ("RAG", st.session_state.rag_url)]:
            try:
                r = requests.get(f"{url}/healthz", timeout=5)
                if r.status_code == 200:
                    st.sidebar.success(f"{name}: {r.json().get('status', 'ok')}")
                else:
                    st.sidebar.error(f"{name}: HTTP {r.status_code}")
            except Exception as e:
                st.sidebar.error(f"{name}: {e}")
    if c2.button("Refresh", use_container_width=True):
        refresh_sessions()
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Sessions")
    if not st.session_state.api_key_input:
        st.sidebar.info("Enter an API key to load sessions.")
        return

    if not st.session_state.session_list:
        refresh_sessions()

    with st.sidebar.expander("New chat", expanded=not st.session_state.session_list):
        default_name = f"Chat {time.strftime('%Y-%m-%d %H%M')}"
        new_name = st.text_input("Session name", value="", placeholder=default_name)
        if st.button("Create session", use_container_width=True, type="primary"):
            create_session(new_name or default_name)

    query = st.sidebar.text_input("Search sessions", placeholder="Filter sessions")
    sessions = st.session_state.session_list
    if query:
        sessions = [s for s in sessions if query.lower() in s["name"].lower()]

    if not sessions:
        st.sidebar.caption("No matching sessions.")
    for sess in sessions:
        name = sess["name"]
        active = name == st.session_state.active_session
        label = f"{'● ' if active else ''}{_safe_session_label(name)}"
        if st.sidebar.button(label, key=f"session_{name}", use_container_width=True):
            select_session(name)
            st.rerun()
        st.sidebar.markdown(f"<div class='session-meta'>{sess.get('points', 0)} vectors</div>", unsafe_allow_html=True)

    if st.session_state.active_session:
        st.sidebar.caption(f"Active: {st.session_state.active_session}")
        if st.sidebar.button("Delete active session", use_container_width=True):
            try:
                requests.delete(
                    f"{st.session_state.rag_url}/v1/sessions/{st.session_state.active_session}",
                    headers=_headers(),
                    timeout=20,
                )
            except Exception:
                pass
            st.session_state.active_session = None
            st.session_state.chat_messages = []
            st.session_state.chat_loaded_for = None
            refresh_sessions()
            st.rerun()


def render_chat():
    active = st.session_state.active_session
    st.title("Chat")
    if active:
        st.caption(f"Session: {active}")
    else:
        st.info("Create or select a session from the sidebar.")

    if active and st.session_state.chat_loaded_for != active:
        st.session_state.chat_messages = load_chat_history(active)
        st.session_state.chat_loaded_for = active

    controls = st.columns([1, 1, 5])
    if controls[0].button("Clear chat", disabled=not active, use_container_width=True):
        if active:
            try:
                requests.delete(f"{st.session_state.rag_url}/v1/chat/history/{active}", headers=_headers(), timeout=10)
                requests.delete(f"{st.session_state.rag_url}/v1/memory/{active}", headers=_headers(), timeout=10)
            except Exception:
                pass
        st.session_state.chat_messages = []
        st.rerun()
    controls[1].button("Reload", disabled=not active, use_container_width=True, on_click=lambda: select_session(active) if active else None)

    if not st.session_state.chat_messages and active:
        st.markdown("Ask a question about the documents in this session.")

    for msg in st.session_state.chat_messages:
        render_chat_message(msg)

    prompt = st.chat_input("Ask about documents in this session", disabled=not bool(active))
    if prompt and active:
        user_msg = {"role": "user", "content": prompt, "ts": int(time.time())}
        st.session_state.chat_messages.append(user_msg)
        render_chat_message(user_msg)

        with st.chat_message("assistant"):
            assistant_msg = ask_streaming(prompt, active) if _settings()["streaming_enabled"] else ask_non_streaming(prompt, active)
            render_sources_and_memory(assistant_msg)

        st.session_state.chat_messages.append(assistant_msg)


def render_ocr_dashboard():
    st.title("OCR Dashboard")
    has_results = bool(st.session_state.ocr_results)

    st.subheader(f"Step 1: Upload & Process {'complete' if has_results else ''}")
    if not has_results:
        uploaded_files = st.file_uploader(
            "Upload Documents",
            type=OCR_UPLOAD_TYPES + DOCUMENT_UPLOAD_TYPES,
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_key}",
        )
        if uploaded_files:
            st.caption(f"{len(uploaded_files)} file(s) selected")
        ocr_uploads = [f for f in (uploaded_files or []) if not _is_direct_upload(f.name)]
        direct_uploads = [f for f in (uploaded_files or []) if _is_direct_upload(f.name)]
        has_pdf = any(f.type == "application/pdf" for f in ocr_uploads)
        if has_pdf:
            dpi_value = st.slider("DPI", 120, 350, 200, 10)
            mode_value = st.selectbox("Mode", ["serial", "concurrent"], index=1)
        else:
            dpi_value, mode_value = 200, "concurrent"

        if st.button("Process files", use_container_width=True, type="primary"):
            if not st.session_state.api_key_input or not uploaded_files:
                st.warning("Provide API key and upload files.")
            else:
                total = len(ocr_uploads)
                results, raw_documents, meta_results = {}, {}, {}
                params = {"dpi": dpi_value, "mode": mode_value}
                if mode_value == "concurrent":
                    params["max_concurrency"] = 4
                file_data = [(f.name, f.getvalue(), f.type) for f in ocr_uploads]

                with st.status(f"Processing {len(uploaded_files)} file(s)...", expanded=True) as sb:
                    t0 = time.time()
                    prog = st.progress(0, text=f"0 / {len(uploaded_files)}")
                    done = 0
                    for f in direct_uploads:
                        data = f.getvalue()
                        raw_documents[f.name] = {
                            "raw_content_b64": base64.b64encode(data).decode("utf-8"),
                            "size": len(data),
                        }
                        meta_results[f.name] = {"doc_type": "other", "date": None, "parties": [], "tags": [], "summary": ""}
                        done += 1
                        prog.progress(done / len(uploaded_files), text=f"{done}/{len(uploaded_files)}")
                        st.write(f"`{f.name}` ready for RAG conversion")
                    for batch_start in range(0, total, BATCH_SIZE):
                        batch = file_data[batch_start:batch_start + BATCH_SIZE]
                        slots = {n: st.empty() for n, _, _ in batch}
                        for n in slots:
                            slots[n].markdown(f"`{n}` processing...")
                        with ThreadPoolExecutor(max_workers=BATCH_SIZE) as ex:
                            futs = {
                                ex.submit(_ocr_file, n, d, t, f"{st.session_state.ocr_url}/v1/ocr", _headers(), params): n
                                for n, d, t in batch
                            }
                            for f in as_completed(futs):
                                nm = futs[f]
                                n, md, lat, tps, err = f.result()
                                if err:
                                    slots[nm].markdown(f"`{n}` failed: {err}")
                                else:
                                    slots[nm].markdown(f"`{n}` done: {lat:.1f}s | {tps:.0f} tok/s")
                                    results[n] = md
                                done += 1
                                prog.progress(done / len(uploaded_files), text=f"{done}/{len(uploaded_files)}")
                    if results:
                        st.write("Auto-tagging...")
                        for fname, md_text in results.items():
                            meta_results[fname] = _autotag(fname, md_text, f"{st.session_state.rag_url}/v1/autotag", _headers())
                    sb.update(label=f"Done: {len(results) + len(raw_documents)} files in {time.time() - t0:.1f}s", state="complete")

                if results or raw_documents:
                    st.session_state.ocr_results = results
                    st.session_state.raw_documents = raw_documents
                    st.session_state.ocr_metadata = meta_results
                    st.session_state.ocr_step = 2
                    st.session_state.uploader_key += 1
                    st.rerun()
    else:
        rnames = list(st.session_state.ocr_results.keys()) + list(st.session_state.raw_documents.keys())
        st.success(f"{len(rnames)} file(s) processed: {', '.join(rnames)}")
        col_dl, col_clr = st.columns(2)
        for i, fname in enumerate(st.session_state.ocr_results.keys()):
            base = os.path.splitext(fname)[0]
            st.download_button(
                f"{base}.md",
                data=st.session_state.ocr_results[fname],
                file_name=f"{base}.md",
                mime="text/markdown",
                use_container_width=True,
                key=f"dl_{i}",
            )
        if len(rnames) > 1:
            zbuf = io.BytesIO()
            with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as zf:
                for fname, md in st.session_state.ocr_results.items():
                    zf.writestr(os.path.splitext(fname)[0] + ".md", md)
            zbuf.seek(0)
            col_dl.download_button(
                "Download all as ZIP",
                data=zbuf.getvalue(),
                file_name=f"ocr_batch_{int(time.time())}.zip",
                mime="application/zip",
                use_container_width=True,
            )
        if col_clr.button("Start new OCR", use_container_width=True):
            st.session_state.ocr_results = {}
            st.session_state.raw_documents = {}
            st.session_state.ocr_metadata = {}
            st.session_state.ocr_step = 1
            st.session_state.uploader_key += 1
            st.rerun()

    if has_results:
        st.markdown("---")
        st.subheader("Step 2: Review & Edit Metadata")
        rnames = list(st.session_state.ocr_results.keys()) + list(st.session_state.raw_documents.keys())
        edit_file = st.selectbox("Select file", rnames, key="meta_edit_file")
        meta = st.session_state.ocr_metadata.get(edit_file, {})
        key_base = f"ocr_meta_{edit_file}"
        mc1, mc2 = st.columns(2)
        with mc1:
            dt_idx = DOC_TYPES.index(meta.get("doc_type", "other")) if meta.get("doc_type", "other") in DOC_TYPES else 9
            doc_type = st.selectbox("Doc Type", DOC_TYPES, index=dt_idx, key=f"{key_base}_type")
            doc_date = st.text_input("Date (YYYY-MM-DD)", value=meta.get("date", "") or "", key=f"{key_base}_date")
            parties_str = st.text_input("Parties (comma-separated)", value=", ".join(meta.get("parties", [])), key=f"{key_base}_parties")
        with mc2:
            tags_str = st.text_input("Tags (comma-separated)", value=", ".join(meta.get("tags", [])), key=f"{key_base}_tags")
            summary = st.text_input("Summary", value=meta.get("summary", ""), key=f"{key_base}_summary")
            custom_keys = {k: v for k, v in meta.items() if k not in ["doc_type", "date", "parties", "tags", "summary", "_error"]}
            custom_json = st.text_area(
                "Custom Fields (JSON)",
                value=json.dumps(custom_keys, indent=2) if custom_keys else "{}",
                height=72,
                key=f"{key_base}_custom",
            )
        if st.button("Save metadata", key=f"{key_base}_save"):
            updated = {
                "doc_type": doc_type,
                "date": doc_date or None,
                "parties": [p.strip() for p in parties_str.split(",") if p.strip()],
                "tags": [t.strip() for t in tags_str.split(",") if t.strip()],
                "summary": summary,
            }
            try:
                updated.update(json.loads(custom_json))
            except Exception:
                st.warning("Custom JSON was not valid, so custom fields were skipped.")
            st.session_state.ocr_metadata[edit_file] = updated
            st.success(f"Saved for {edit_file}")

        with st.expander("Document Preview"):
            pf = st.selectbox("File", rnames, key="preview_sel")
            l, r_ = st.columns(2, gap="large")
            if pf in st.session_state.ocr_results:
                l.text_area("raw", value=st.session_state.ocr_results[pf], height=300, label_visibility="collapsed")
                r_.markdown(st.session_state.ocr_results[pf], unsafe_allow_html=True)
            else:
                raw_meta = st.session_state.raw_documents.get(pf, {})
                l.text_area("raw", value=f"{pf}\n{raw_meta.get('size', 0)} bytes\nConverted during RAG ingestion.", height=300, label_visibility="collapsed")
                r_.info("This file will be converted to Markdown by the RAG API during ingestion.")

        st.markdown("---")
        st.subheader("Step 3: Ingest to Session")
        target = st.session_state.active_session
        if not target:
            st.warning("Create or select a session in the sidebar first.")
        else:
            rnames = list(st.session_state.ocr_results.keys()) + list(st.session_state.raw_documents.keys())
            st.info(f"{len(rnames)} file(s) will be ingested into session {target}. Re-ingest overwrites matching filenames.")
            chunk_size = st.number_input("Chunk Size", 200, 4000, 1200, 50)
            if st.button("Ingest to vector store", use_container_width=True, type="primary"):
                total_chunks, errors = 0, []
                with st.status(f"Ingesting {len(rnames)} file(s)...", expanded=True) as sb:
                    t0 = time.time()
                    for i, fname in enumerate(rnames):
                        meta = st.session_state.ocr_metadata.get(fname, {})
                        payload = {
                            "filename": fname,
                            "collection": target,
                            "chunk_size": int(chunk_size),
                            "metadata": meta,
                        }
                        if fname in st.session_state.ocr_results:
                            payload["markdown_content"] = st.session_state.ocr_results[fname]
                        else:
                            payload["raw_content_b64"] = st.session_state.raw_documents[fname]["raw_content_b64"]
                        st.write(f"[{i + 1}/{len(rnames)}] `{fname}`")
                        try:
                            r = requests.post(f"{st.session_state.rag_url}/v1/ingest", headers=_headers(), json=payload, timeout=120)
                            if r.status_code == 200:
                                total_chunks += r.json()["chunks"]
                            else:
                                errors.append(fname)
                        except Exception:
                            errors.append(fname)
                    elapsed = time.time() - t0
                    sb.update(label=f"Ingested {total_chunks} chunks in {elapsed:.1f}s", state="complete")
                if errors:
                    st.error(f"Failed: {', '.join(errors)}")
                else:
                    st.success(f"Ingested {total_chunks} chunks from {len(rnames)} file(s).")
                refresh_sessions()


def render_data_manager():
    st.title("Data Manager")
    st.caption("Browse and edit metadata for the active session without re-ingestion.")
    active = st.session_state.active_session
    if not active:
        st.warning("Select a session to manage documents.")
        return
    if not st.session_state.api_key_input:
        st.info("Enter API key.")
        return
    if st.button("Refresh documents"):
        st.rerun()
    try:
        r = requests.get(f"{st.session_state.rag_url}/v1/documents/{active}", headers=_headers(), timeout=10)
        if r.status_code != 200:
            st.error(r.text)
            return
        docs = r.json().get("documents", [])
        if not docs:
            st.info("No documents ingested yet.")
            return
        df_data = [
            {
                "Filename": d["filename"],
                "Type": d.get("metadata", {}).get("doc_type", "-"),
                "Date": d.get("metadata", {}).get("date", "-") or "-",
                "Tags": ", ".join(d.get("metadata", {}).get("tags", [])),
                "Chunks": d["chunks"],
            }
            for d in docs
        ]
        st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

        st.subheader("Edit Metadata")
        doc_names = [d["filename"] for d in docs]
        sel_doc = st.selectbox("Select document", doc_names, key="dm_select")
        meta = next(d for d in docs if d["filename"] == sel_doc).get("metadata", {})
        key_base = f"dm_{active}_{sel_doc}"
        ec1, ec2 = st.columns(2)
        with ec1:
            e_type = st.selectbox(
                "Doc Type",
                DOC_TYPES,
                index=DOC_TYPES.index(meta.get("doc_type", "other")) if meta.get("doc_type", "other") in DOC_TYPES else 9,
                key=f"{key_base}_type",
            )
            e_date = st.text_input("Date", value=meta.get("date", "") or "", key=f"{key_base}_date")
            e_parties = st.text_input("Parties", value=", ".join(meta.get("parties", [])), key=f"{key_base}_parties")
        with ec2:
            e_tags = st.text_input("Tags", value=", ".join(meta.get("tags", [])), key=f"{key_base}_tags")
            e_summary = st.text_input("Summary", value=meta.get("summary", ""), key=f"{key_base}_summary")
            custom_keys = {k: v for k, v in meta.items() if k not in ["doc_type", "date", "parties", "tags", "summary", "_error"]}
            e_custom = st.text_area(
                "Custom Fields (JSON)",
                value=json.dumps(custom_keys, indent=2) if custom_keys else "{}",
                height=72,
                key=f"{key_base}_custom",
            )
        if st.button("Update metadata", use_container_width=True, type="primary", key=f"{key_base}_save"):
            updated = {
                "doc_type": e_type,
                "date": e_date or None,
                "parties": [p.strip() for p in e_parties.split(",") if p.strip()],
                "tags": [t.strip() for t in e_tags.split(",") if t.strip()],
                "summary": e_summary,
            }
            try:
                updated.update(json.loads(e_custom))
            except Exception:
                st.warning("Custom JSON was not valid, so custom fields were skipped.")
            r = requests.patch(
                f"{st.session_state.rag_url}/v1/metadata/{active}/{sel_doc}",
                headers=_headers(),
                json={"metadata": updated},
                timeout=10,
            )
            if r.status_code == 200:
                st.success(f"Updated {r.json()['chunks_updated']} chunks.")
            else:
                st.error(f"Failed: {r.text}")
    except Exception as e:
        st.error(f"Cannot connect: {e}")


def render_advanced_settings():
    _ensure_draft_widget_keys()
    st.title("Advanced Settings")
    flash = st.session_state.get("settings_flash")
    if flash:
        level, message = flash
        getattr(st, level)(message)
        st.session_state.settings_flash = None
    st.subheader("Service Links")
    c1, c2 = st.columns(2)
    with c1:
        _service_link("Qdrant Dashboard", QDRANT_DASHBOARD)
    with c2:
        _service_link("Swagger UI", f"{st.session_state.rag_url}/docs")

    applied = st.session_state.applied_settings
    applied_at = st.session_state.settings_applied_at or "initial defaults"
    st.subheader("Currently Applied")
    st.caption(f"Last applied: {applied_at}")
    st.code(
        " | ".join([
            f"streaming={str(applied['streaming_enabled']).lower()}",
            f"rerank={str(applied['rerank']).lower()}",
            f"agentic={str(applied['agentic']).lower()}",
            f"hyde={str(applied['hyde']).lower()}",
            f"auto_filters={str(applied['auto_extract']).lower()}",
            f"top_k={int(applied['top_k'])}",
            f"memory={str(applied['memory_enabled']).lower()}",
            f"memory_top_k={int(applied['memory_top_k'])}",
        ]),
        language="text",
    )

    st.subheader("Retrieval Engine")
    cols = st.columns(5)
    with cols[0]:
        st.checkbox("Re-ranking", key="draft_rerank", help="LLM re-scores chunks for precision.")
    with cols[1]:
        st.checkbox("Agentic RAG", key="draft_agentic", help="Decomposes complex queries into sub-queries.")
    with cols[2]:
        st.checkbox("Auto Filters", key="draft_auto_extract", help="LLM extracts metadata filters from query in non-streaming mode.")
    with cols[3]:
        st.checkbox("HyDE", key="draft_hyde", help="Generates a hypothetical answer for better embeddings.")
    with cols[4]:
        st.checkbox("Streaming", key="draft_streaming_enabled", help="Stream tokens as they are generated.")

    cl, cr = st.columns(2)
    with cl:
        st.number_input("Top K", 1, 50, key="draft_top_k")
        st.checkbox("Memory", key="draft_memory_enabled")
        st.number_input("Memory Top K", 1, 20, key="draft_memory_top_k")
    with cr:
        st.text_area("System Prompt", key="draft_system_prompt", height=140)

    st.subheader("Manual Filters")
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        st.selectbox("Doc Type Filter", ["(none)"] + DOC_TYPES, key="draft_f_doc_type")
    with fc2:
        st.text_input("Tags Filter (comma-separated)", key="draft_f_tags")
    with fc3:
        st.text_input("Date From", key="draft_f_date_from")
        st.text_input("Date To", key="draft_f_date_to")

    ac1, ac2, ac3 = st.columns(3)
    if ac1.button("Apply Settings", type="primary", use_container_width=True):
        _apply_advanced_settings()
        st.rerun()
    if ac2.button("Reset Draft", use_container_width=True):
        _reset_draft_to_applied()
        st.rerun()
    if ac3.button("Restore Defaults", use_container_width=True):
        _restore_default_settings()
        st.rerun()


render_sidebar()

if st.session_state.nav == "Chat":
    render_chat()
elif st.session_state.nav == "OCR Dashboard":
    render_ocr_dashboard()
elif st.session_state.nav == "Data Manager":
    render_data_manager()
else:
    render_advanced_settings()
