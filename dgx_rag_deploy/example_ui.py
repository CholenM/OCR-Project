"""
OCR + RAG Control Center — Session-Based UI
=============================================
Each chat session creates its own Qdrant vector store.
Users choose what documents to ingest per session.

Usage:
    pip install streamlit requests pandas
    streamlit run example_ui.py
"""

import os, time, uuid, json
import streamlit as st
import requests
import pandas as pd

DEFAULT_OCR_URL = os.getenv("OCR_API_URL", "http://192.168.50.153:8080")
DEFAULT_RAG_URL = os.getenv("RAG_API_URL", "http://192.168.50.153:8081")
QDRANT_DASHBOARD = os.getenv("QDRANT_DASHBOARD", "http://192.168.50.153:6333/dashboard")

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
    """Fetch session list from RAG pipeline."""
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
if "ocr_result" not in st.session_state:
    st.session_state.ocr_result = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "active_session" not in st.session_state:
    st.session_state.active_session = None
if "session_list" not in st.session_state:
    st.session_state.session_list = []

# Refresh sessions
if st.sidebar.button("🔄 Refresh Sessions"):
    st.session_state.session_list = load_sessions()

# Create new session
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

# Session selector
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

    # Show session info
    match = next((s for s in sessions if s["name"] == selected), None)
    if match:
        st.sidebar.caption(f"📊 {match.get('points', 0)} vectors stored")
else:
    st.sidebar.info("No sessions yet. Create one above.")

# Delete session
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
# Tabs
# ========================================================================
tab_ocr, tab_chat = st.tabs(["OCR Dashboard", "Chat Dashboard"])

# ========================================================================
# OCR Dashboard
# ========================================================================
with tab_ocr:
    st.header("OCR Dashboard")

    # --- Advanced Settings ---
    with st.expander("⚙️ Advanced Settings"):
        adv_c1, adv_c2 = st.columns(2)
        with adv_c1:
            st.markdown(f"**Qdrant Dashboard**")
            st.link_button("🔗 Open Qdrant Vector Store", QDRANT_DASHBOARD, use_container_width=True)
        with adv_c2:
            st.markdown(f"**RAG API Docs**")
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
        uploaded_file = st.file_uploader("Upload Document", type=["pdf", "jpg", "png"])
        is_pdf = uploaded_file is not None and uploaded_file.type == "application/pdf"

        if is_pdf:
            dpi_value = st.slider("Render DPI", 120, 350, 200, 10)
            mode_value = st.selectbox("Mode", ["serial", "concurrent"], index=1)
            max_conc = st.number_input("Max Concurrency", 1, 8, 4, 1) if mode_value == "concurrent" else None
        else:
            dpi_value = mode_value = max_conc = None

        if st.button("Execute OCR", use_container_width=True, type="primary"):
            if not api_key_input or not uploaded_file:
                st.warning("Provide API key and upload a file.")
            else:
                with st.spinner("Processing via OCR Pipeline..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    params = {}
                    if is_pdf:
                        params["dpi"] = dpi_value
                        params["mode"] = mode_value
                        if max_conc:
                            params["max_concurrency"] = int(max_conc)
                    try:
                        r = requests.post(f"{ocr_url}/v1/ocr", headers=_headers(), files=files, params=params)
                        if r.status_code == 200:
                            st.session_state.ocr_result = r.text
                            lat = float(r.headers.get("X-Process-Time", 0))
                            tps = float(r.headers.get("X-Tokens-Per-Sec", 0))
                            st.success(f"Done in {lat}s | {tps:.1f} tok/s")
                            st.rerun()
                        else:
                            st.error(f"Error ({r.status_code}): {r.text}")
                    except Exception as e:
                        st.error(f"Failed: {e}")

        # Post-OCR: Ingest into active session
        if st.session_state.ocr_result:
            st.download_button("Download Markdown", data=st.session_state.ocr_result,
                               file_name=f"ocr_{int(time.time())}.md",
                               mime="text/markdown", use_container_width=True)

            st.markdown("### Ingest to Session")
            target = st.session_state.active_session
            if target:
                st.info(f"Will ingest into session: **{target}**")
                chunk_size = st.number_input("Max Chunk Size", 200, 4000, 1200, 50)
                if st.button("Ingest to Vector Store", use_container_width=True, type="primary"):
                    with st.spinner("Structural chunking + embedding..."):
                        try:
                            payload = {
                                "filename": uploaded_file.name if uploaded_file else f"doc_{int(time.time())}",
                                "markdown_content": st.session_state.ocr_result,
                                "collection": target,
                                "chunk_size": int(chunk_size),
                            }
                            r = requests.post(f"{rag_url}/v1/ingest", headers=_headers(), json=payload)
                            if r.status_code == 200:
                                res = r.json()
                                st.success(f"Ingested {res['chunks']} chunks → '{res['collection']}'")
                                if res.get("sections"):
                                    st.markdown("**Sections detected:**")
                                    for sec, cnt in res["sections"].items():
                                        st.write(f"  • {sec}: {cnt} chunk(s)")
                                st.session_state.session_list = load_sessions()
                            else:
                                st.error(f"Failed: {r.text}")
                        except Exception as e:
                            st.error(f"Error: {e}")
            else:
                st.warning("Create or select a session in the sidebar first.")

    # Document preview
    st.markdown("### Document Preview")
    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("Raw Markdown")
        if st.session_state.ocr_result:
            st.text_area("", value=st.session_state.ocr_result, height=520)
        else:
            st.info("Run OCR to see output.")
    with right:
        st.subheader("Rendered Markdown")
        if st.session_state.ocr_result:
            st.markdown(st.session_state.ocr_result, unsafe_allow_html=True)
        else:
            st.info("Run OCR to see rendered output.")

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

    # --- Advanced Settings ---
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
            system_prompt = st.text_area("System Prompt",
                value="You are a local RAG assistant. Answer using only the context. "
                      "Use conversation history for follow-up context when available. "
                      "If the answer is not in the context, say you do not know.",
                height=100)

        # Session info
        if active and api_key_input:
            try:
                r = requests.get(f"{rag_url}/v1/sessions/{active}", headers=_headers(), timeout=5)
                if r.status_code == 200:
                    info = r.json()
                    st.markdown(f"**Session Info:** {info['points']} vectors | "
                                f"Files: {', '.join(info.get('files', [])) or 'none'}")
            except Exception:
                pass

    # Use expander defaults if Advanced Settings is closed
    if "chat_top_k" not in dir():
        chat_top_k = 30
        memory_enabled = True
        memory_top_k = 5
        system_prompt = None

    # Clear chat + memory
    if st.button("Clear Chat & Memory", type="secondary"):
        if api_key_input and active:
            try:
                requests.delete(f"{rag_url}/v1/memory/{active}", headers=_headers(), timeout=5)
            except Exception:
                pass
        st.session_state.chat_messages = []
        st.rerun()

    # Chat messages
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
                    "query": prompt,
                    "collection": active,
                    "top_k": int(chat_top_k),
                    "session_id": active,  # Use collection name as session_id for memory
                    "memory_enabled": memory_enabled,
                    "memory_top_k": int(memory_top_k),
                }
                if system_prompt:
                    payload["system_prompt"] = system_prompt
                r = requests.post(f"{rag_url}/v1/chat", headers=_headers(), json=payload, timeout=180)
                if r.status_code == 200:
                    res = r.json()
                    answer = res["answer"]
                    sources = res.get("sources", [])
                    memories = res.get("memories", [])
                else:
                    answer = f"Error: {r.text}"
                    sources, memories = [], []
            except Exception as e:
                answer = f"Failed: {e}"
                sources, memories = [], []
        st.session_state.chat_messages.append({
            "role": "assistant", "content": answer,
            "sources": sources, "memories": memories,
        })
        st.rerun()
    elif prompt and not active:
        st.warning("Select or create a session first.")
