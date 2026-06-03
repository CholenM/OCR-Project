"""
OCR + RAG Control Center — Session-Based UI
=============================================
Features:
  - Multi-file upload with batch queue (3 at a time)
  - Per-session Qdrant collections
  - Conversational memory
  - Dynamic processing feedback

Usage:
    pip install streamlit requests pandas
    streamlit run example_ui.py
"""

import os, time, uuid, json
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
import requests
import pandas as pd

DEFAULT_OCR_URL = os.getenv("OCR_API_URL", "http://192.168.50.153:8080")
DEFAULT_RAG_URL = os.getenv("RAG_API_URL", "http://192.168.50.153:8081")
QDRANT_DASHBOARD = os.getenv("QDRANT_DASHBOARD", "http://192.168.50.153:6333/dashboard")
BATCH_SIZE = 3  # Process N files concurrently

st.set_page_config(page_title="OCR + RAG Control Center", page_icon="", layout="wide")
st.title("OCR + RAG Control Center")
st.markdown("---")

# --- Sidebar: Connection & Auth ---
st.sidebar.header("Connection")
ocr_url = st.sidebar.text_input("OCR Pipeline URL", value=DEFAULT_OCR_URL)
rag_url = st.sidebar.text_input("RAG Pipeline URL", value=DEFAULT_RAG_URL)

st.sidebar.header("Authentication")
api_key_input = st.sidebar.text_input("API Key", type="password")
st.sidebar.markdown("### Sandbox Keys")
st.sidebar.code("legal_team_secret_abc123\ntest_key_0000", language="text")

if st.sidebar.button("Health Check"):
    for name, url in [("OCR", ocr_url), ("RAG", rag_url)]:
        try:
            r = requests.get(f"{url}/healthz", timeout=5)
            if r.status_code == 200:
                h = r.json()
                icon = "✅" if h["status"] == "ok" else "⚠️"
                st.sidebar.success(f"{icon} {name}: {h['status']}")
                for svc, state in h.get("services", {}).items():
                    st.sidebar.write(f"  {'✅' if state == 'up' else '❌'} {svc}: {state}")
            else:
                st.sidebar.error(f"{name}: HTTP {r.status_code}")
        except Exception as e:
            st.sidebar.error(f"{name}: {e}")

# --- Sidebar: Session Management ---
st.sidebar.markdown("---")
st.sidebar.header("Session Management")

def _headers():
    return {"X-API-KEY": api_key_input} if api_key_input else {}

def load_sessions():
    if not api_key_input:
        return []
    try:
        r = requests.get(f"{rag_url}/v1/sessions", headers=_headers(), timeout=5)
        if r.status_code == 200:
            return r.json().get("sessions", [])
    except Exception:
        pass
    return []

# Initialize session state
for key, default in [("ocr_results", {}), ("chat_messages", []),
                     ("active_session", None), ("session_list", [])]:
    if key not in st.session_state:
        st.session_state[key] = default

if st.sidebar.button("🔄 Refresh Sessions"):
    st.session_state.session_list = load_sessions()

with st.sidebar.expander("➕ Create New Session"):
    new_name = st.text_input("Session Name", placeholder="e.g. Legal Contracts Q4")
    if st.button("Create", use_container_width=True):
        if not api_key_input:
            st.error("Enter API key first.")
        elif not new_name.strip():
            st.error("Enter a session name.")
        else:
            try:
                r = requests.post(f"{rag_url}/v1/sessions", headers=_headers(),
                                  json={"name": new_name.strip()})
                if r.status_code == 200:
                    res = r.json()
                    st.success(f"Session '{res['session']}' {res['status']}")
                    st.session_state.active_session = res["session"]
                    st.session_state.chat_messages = []
                    st.session_state.session_list = load_sessions()
                    st.rerun()
                else:
                    st.error(f"Failed: {r.text}")
            except Exception as e:
                st.error(str(e))

sessions = st.session_state.session_list
session_names = [s["name"] for s in sessions]
if session_names:
    active = st.session_state.active_session
    idx = session_names.index(active) if active in session_names else 0
    selected = st.sidebar.selectbox("Active Session", session_names, index=idx)
    if selected != st.session_state.active_session:
        st.session_state.active_session = selected
        st.session_state.chat_messages = []
        st.rerun()
    match = next((s for s in sessions if s["name"] == selected), None)
    if match:
        st.sidebar.caption(f"📊 {match.get('points', 0)} vectors stored")
else:
    st.sidebar.info("No sessions yet. Create one above.")

if st.session_state.active_session and api_key_input:
    if st.sidebar.button("🗑️ Delete Active Session", type="secondary"):
        try:
            r = requests.delete(f"{rag_url}/v1/sessions/{st.session_state.active_session}",
                                headers=_headers())
            if r.status_code == 200:
                st.sidebar.success(f"Deleted '{st.session_state.active_session}'")
                st.session_state.active_session = None
                st.session_state.chat_messages = []
                st.session_state.session_list = load_sessions()
                st.rerun()
        except Exception as e:
            st.sidebar.error(str(e))


# ========================================================================
# OCR Processing Worker (runs in thread)
# ========================================================================

def _ocr_single_file(file_name, file_bytes, content_type, ocr_endpoint, headers, params):
    """Process one file through OCR. Returns (name, markdown, latency, tps, error)."""
    try:
        files = {"file": (file_name, file_bytes, content_type)}
        r = requests.post(ocr_endpoint, headers=headers, files=files, params=params, timeout=300)
        if r.status_code == 200:
            lat = float(r.headers.get("X-Process-Time", 0))
            tps = float(r.headers.get("X-Tokens-Per-Sec", 0))
            return (file_name, r.text, lat, tps, None)
        else:
            return (file_name, None, 0, 0, f"HTTP {r.status_code}")
    except Exception as e:
        return (file_name, None, 0, 0, str(e))


# ========================================================================
# Tabs
# ========================================================================
tab_ocr, tab_chat = st.tabs(["OCR Dashboard", "Chat Dashboard"])

# ========================================================================
# OCR Dashboard
# ========================================================================
with tab_ocr:
    st.header("OCR Dashboard")

    with st.expander("⚙️ Advanced Settings"):
        adv_c1, adv_c2 = st.columns(2)
        with adv_c1:
            st.link_button("🔗 Open Qdrant Vector Store", QDRANT_DASHBOARD, use_container_width=True)
        with adv_c2:
            st.link_button("🔗 Open Swagger UI", f"{rag_url}/docs", use_container_width=True)

    col_dash, col_act = st.columns([1.3, 1], gap="large")

    with col_dash:
        st.subheader("OCR Metrics")
        if api_key_input:
            try:
                resp = requests.get(f"{ocr_url}/v1/metrics", headers=_headers())
                if resp.status_code == 200:
                    data = resp.json()
                    metrics = data["metrics"]
                    st.markdown(f"**Identity:** {data['user']}")
                    spend = data["current_month_spend"]
                    cap = data["monthly_spend_cap"]
                    st.progress(min(spend / cap, 1.0) if cap > 0 else 0)
                    st.caption(f"**${spend:.2f}** of **${cap:.2f}**")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Docs", metrics["total_documents"])
                    c2.metric("Pages", metrics["total_pages_processed"])
                    tok = metrics["total_input_tokens"] + metrics["total_output_tokens"]
                    c3.metric("Tokens", f"{tok:,}")
                    if data["audit_logs"]:
                        st.dataframe(pd.DataFrame(data["audit_logs"]),
                                     use_container_width=True, hide_index=True, height=240)
                elif resp.status_code == 401:
                    st.error("Invalid API Key.")
            except requests.exceptions.ConnectionError:
                st.error(f"Cannot connect to {ocr_url}")
        else:
            st.info("Enter API Key in sidebar.")

    with col_act:
        st.subheader("Document Processing")

        # --- Multi-file upload ---
        uploaded_files = st.file_uploader(
            "Upload Documents (PDF, JPG, PNG)",
            type=["pdf", "jpg", "png"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            st.caption(f"**{len(uploaded_files)} file(s)** queued • Batch size: {BATCH_SIZE}")

        # PDF-specific settings
        has_pdf = any(f.type == "application/pdf" for f in (uploaded_files or []))
        if has_pdf:
            dpi_value = st.slider("Render DPI", 120, 350, 200, 10)
            mode_value = st.selectbox("Mode", ["serial", "concurrent"], index=1)
            max_conc = st.number_input("Max Concurrency", 1, 8, 4, 1) if mode_value == "concurrent" else None
        else:
            dpi_value, mode_value, max_conc = 200, "concurrent", 4

        # --- Execute OCR with Queue ---
        if st.button("🚀 Execute OCR", use_container_width=True, type="primary"):
            if not api_key_input:
                st.warning("Enter API key in sidebar.")
            elif not uploaded_files:
                st.warning("Upload at least one file.")
            else:
                total = len(uploaded_files)
                completed = 0
                results = {}
                errors = []

                # Build params
                params = {"dpi": dpi_value, "mode": mode_value}
                if max_conc:
                    params["max_concurrency"] = int(max_conc)

                # Prepare file data (read bytes before threading)
                file_data = []
                for f in uploaded_files:
                    file_data.append((f.name, f.getvalue(), f.type))

                with st.status(f"Processing {total} file(s)...", expanded=True) as status_box:
                    overall_start = time.time()
                    progress_bar = st.progress(0, text=f"0 / {total} files processed")

                    # Process in batches
                    for batch_start in range(0, total, BATCH_SIZE):
                        batch = file_data[batch_start:batch_start + BATCH_SIZE]
                        batch_num = (batch_start // BATCH_SIZE) + 1
                        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

                        st.write(f"**Batch {batch_num}/{total_batches}** — {len(batch)} file(s)")

                        # Show "processing" for each file in this batch
                        file_slots = {}
                        for fname, _, _ in batch:
                            file_slots[fname] = st.empty()
                            file_slots[fname].markdown(f"🔄 `{fname}` — *Processing...*")

                        # Process batch concurrently
                        with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
                            futures = {}
                            for fname, fbytes, ftype in batch:
                                future = executor.submit(
                                    _ocr_single_file, fname, fbytes, ftype,
                                    f"{ocr_url}/v1/ocr", _headers(), params,
                                )
                                futures[future] = fname

                            for future in as_completed(futures):
                                fname = futures[future]
                                name, markdown, latency, tps, error = future.result()

                                if error:
                                    file_slots[fname].markdown(f"❌ `{name}` — **Failed:** {error}")
                                    errors.append(name)
                                else:
                                    file_slots[fname].markdown(
                                        f"✅ `{name}` — **Done** in {latency:.1f}s ({tps:.0f} tok/s)"
                                    )
                                    results[name] = markdown

                                completed += 1
                                pct = completed / total
                                elapsed = time.time() - overall_start
                                eta = (elapsed / completed) * (total - completed) if completed > 0 else 0
                                progress_bar.progress(
                                    pct,
                                    text=f"{completed} / {total} files • "
                                         f"Elapsed: {elapsed:.0f}s • ETA: {eta:.0f}s",
                                )

                    # Final summary
                    total_time = time.time() - overall_start
                    if errors:
                        status_box.update(
                            label=f"Completed: {len(results)} ✅ | Failed: {len(errors)} ❌ | {total_time:.1f}s",
                            state="error",
                        )
                    else:
                        status_box.update(
                            label=f"All {total} files processed in {total_time:.1f}s ✅",
                            state="complete",
                        )

                # Store results
                if results:
                    st.session_state.ocr_results.update(results)
                    st.rerun()

        # --- Results Display & Ingestion ---
        if st.session_state.ocr_results:
            result_names = list(st.session_state.ocr_results.keys())
            st.markdown(f"### Processed Files ({len(result_names)})")

            # Combined download
            combined = ""
            for fname, md in st.session_state.ocr_results.items():
                combined += f"\n<!-- FILE: {fname} -->\n{md}\n"
            st.download_button(
                "📥 Download All (Combined Markdown)",
                data=combined,
                file_name=f"ocr_batch_{int(time.time())}.md",
                mime="text/markdown",
                use_container_width=True,
            )

            # Ingestion
            st.markdown("### Ingest to Session")
            target = st.session_state.active_session
            if target:
                st.info(f"Will ingest **{len(result_names)} file(s)** into session: **{target}**")
                chunk_size = st.number_input("Max Chunk Size", 200, 4000, 1200, 50)

                ingest_mode = st.radio(
                    "Ingestion mode",
                    ["All files together", "Each file separately"],
                    index=1,
                    horizontal=True,
                )

                if st.button("📤 Ingest to Vector Store", use_container_width=True, type="primary"):
                    with st.status(f"Ingesting {len(result_names)} file(s)...", expanded=True) as ing_status:

                        if ingest_mode == "All files together":
                            st.write("Sending combined markdown...")
                            payload = {
                                "filename": "batch_" + "_".join(result_names[:3]),
                                "markdown_content": combined,
                                "collection": target,
                                "chunk_size": int(chunk_size),
                            }
                            r = requests.post(f"{rag_url}/v1/ingest", headers=_headers(), json=payload)
                            if r.status_code == 200:
                                res = r.json()
                                st.write(f"✅ Ingested {res['chunks']} chunks")
                            else:
                                st.write(f"❌ Failed: {r.text}")
                        else:
                            total_chunks = 0
                            for i, (fname, md) in enumerate(st.session_state.ocr_results.items()):
                                st.write(f"🔄 Ingesting `{fname}` ({i+1}/{len(result_names)})...")
                                payload = {
                                    "filename": fname,
                                    "markdown_content": md,
                                    "collection": target,
                                    "chunk_size": int(chunk_size),
                                }
                                try:
                                    r = requests.post(f"{rag_url}/v1/ingest",
                                                      headers=_headers(), json=payload, timeout=120)
                                    if r.status_code == 200:
                                        res = r.json()
                                        chunks = res["chunks"]
                                        total_chunks += chunks
                                        st.write(f"✅ `{fname}` — {chunks} chunks")
                                    else:
                                        st.write(f"❌ `{fname}` — {r.text}")
                                except Exception as e:
                                    st.write(f"❌ `{fname}` — {e}")

                            ing_status.update(
                                label=f"Ingested {total_chunks} total chunks from {len(result_names)} files ✅",
                                state="complete",
                            )
                        st.session_state.session_list = load_sessions()
            else:
                st.warning("Create or select a session in the sidebar first.")

            # Per-file preview
            st.markdown("### Document Preview")
            preview_file = st.selectbox("Select file to preview", result_names)
            if preview_file:
                md_content = st.session_state.ocr_results[preview_file]
                left, right = st.columns(2, gap="large")
                with left:
                    st.subheader("Raw Markdown")
                    st.text_area("raw_md", value=md_content, height=520, label_visibility="collapsed")
                with right:
                    st.subheader("Rendered Markdown")
                    st.markdown(md_content, unsafe_allow_html=True)

            # Clear results
            if st.button("🗑️ Clear All OCR Results"):
                st.session_state.ocr_results = {}
                st.rerun()


# ========================================================================
# Chat Dashboard
# ========================================================================
with tab_chat:
    st.header("Chat Dashboard")

    active = st.session_state.active_session
    if active:
        st.caption(f"Chatting with session: **{active}**")
    else:
        st.warning("Select or create a session in the sidebar to start chatting.")

    with st.expander("⚙️ Advanced Settings"):
        adv_c1, adv_c2 = st.columns(2)
        with adv_c1:
            st.link_button("🔗 Open Qdrant Vector Store", QDRANT_DASHBOARD, use_container_width=True)
        with adv_c2:
            st.link_button("🔗 Open Swagger UI", f"{rag_url}/docs", use_container_width=True)
        st.markdown("---")
        cl, cr = st.columns(2, gap="medium")
        with cl:
            chat_top_k = st.number_input("Top K", 1, 50, 30, 1)
            memory_enabled = st.checkbox("Enable Memory", value=True)
        with cr:
            memory_top_k = st.number_input("Memory Top K", 1, 20, 5, 1)
            system_prompt = st.text_area(
                "System Prompt",
                value="You are a local RAG assistant. Answer using only the context. "
                      "Use conversation history for follow-up context when available. "
                      "If the answer is not in the context, say you do not know.",
                height=100,
            )

        if active and api_key_input:
            try:
                r = requests.get(f"{rag_url}/v1/sessions/{active}", headers=_headers(), timeout=5)
                if r.status_code == 200:
                    info = r.json()
                    st.markdown(f"**Session Info:** {info['points']} vectors | "
                                f"Files: {', '.join(info.get('files', [])) or 'none'}")
            except Exception:
                pass

    if "chat_top_k" not in dir():
        chat_top_k, memory_enabled, memory_top_k, system_prompt = 30, True, 5, None

    if st.button("Clear Chat & Memory", type="secondary"):
        if api_key_input and active:
            try:
                requests.delete(f"{rag_url}/v1/memory/{active}", headers=_headers(), timeout=5)
            except Exception:
                pass
        st.session_state.chat_messages = []
        st.rerun()

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                if msg.get("sources"):
                    with st.expander(f"📄 Document Sources ({len(msg['sources'])})"):
                        for s in msg["sources"]:
                            st.markdown(f"- **{s['filename']}** | {s.get('section', '')} | "
                                        f"{s.get('content_type', '')} | score {s['score']:.4f}")
                if msg.get("memories"):
                    with st.expander(f"🧠 Memory ({len(msg['memories'])})"):
                        for m in msg["memories"]:
                            st.markdown(f"- **Q:** {m['query'][:80]}...")
                            st.markdown(f"  **A:** {m['answer'][:120]}...")

    prompt = st.chat_input("Ask about documents in this session")
    if prompt and active:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.spinner("Querying RAG Pipeline..."):
            try:
                payload = {
                    "query": prompt, "collection": active,
                    "top_k": int(chat_top_k), "session_id": active,
                    "memory_enabled": memory_enabled, "memory_top_k": int(memory_top_k),
                }
                if system_prompt:
                    payload["system_prompt"] = system_prompt
                r = requests.post(f"{rag_url}/v1/chat", headers=_headers(), json=payload, timeout=180)
                if r.status_code == 200:
                    res = r.json()
                    answer, sources, memories = res["answer"], res.get("sources", []), res.get("memories", [])
                else:
                    answer, sources, memories = f"Error: {r.text}", [], []
            except Exception as e:
                answer, sources, memories = f"Failed: {e}", [], []
        st.session_state.chat_messages.append({
            "role": "assistant", "content": answer, "sources": sources, "memories": memories,
        })
        st.rerun()
    elif prompt and not active:
        st.warning("Select or create a session first.")
