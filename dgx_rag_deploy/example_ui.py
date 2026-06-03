"""
Example UI — OCR + RAG Pipeline Client (Streamlit)
====================================================
Connects to TWO separate services on the DGX Spark:
  - OCR Pipeline at :8080 (~/ocr-pipeline/)
  - RAG Pipeline at :8081 (~/rag-pipeline/)

Usage:
    pip install streamlit requests pandas
    streamlit run example_ui.py
"""

import os
import time
import streamlit as st
import requests
import pandas as pd

# --- Defaults ---
DEFAULT_OCR_URL = os.getenv("OCR_API_URL", "http://192.168.50.153:8080")
DEFAULT_RAG_URL = os.getenv("RAG_API_URL", "http://192.168.50.153:8081")

st.set_page_config(page_title="OCR + RAG Control Center", page_icon="", layout="wide")
st.title("OCR + RAG Control Center")
st.markdown("---")

# --- Sidebar ---
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

# Session state
if "ocr_result" not in st.session_state:
    st.session_state.ocr_result = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

tab_ocr, tab_chat = st.tabs(["OCR Dashboard", "Chat Dashboard"])

# ===========================================================================
# OCR Dashboard (talks to ocr-pipeline :8080)
# ===========================================================================
with tab_ocr:
    st.header("OCR Dashboard")
    col_dash, col_act = st.columns([1.3, 1], gap="large")

    with col_dash:
        st.header("OCR Metrics")
        if api_key_input:
            try:
                resp = requests.get(f"{ocr_url}/v1/metrics",
                                    headers={"X-API-KEY": api_key_input})
                if resp.status_code == 200:
                    data = resp.json()
                    metrics = data["metrics"]
                    st.subheader(f"Identity: {data['user']}")
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
                        df = pd.DataFrame(data["audit_logs"])
                        st.dataframe(df, use_container_width=True, hide_index=True, height=240)
                elif resp.status_code == 401:
                    st.error("Invalid API Key.")
            except requests.exceptions.ConnectionError:
                st.error(f"Cannot connect to OCR pipeline at {ocr_url}")
        else:
            st.info("Enter API Key in sidebar.")

    with col_act:
        st.header("Document Processing")
        uploaded_file = st.file_uploader("Upload Document", type=["pdf", "jpg", "png"])
        is_pdf = uploaded_file is not None and uploaded_file.type == "application/pdf"

        if is_pdf:
            dpi_value = st.slider("Render DPI", 120, 350, 200, 10)
            mode_label = st.selectbox("Mode", ["Serial", "Concurrent"], index=1)
            mode_value = mode_label.lower()
            if mode_value == "concurrent":
                max_conc = st.number_input("Max Concurrency", 1, 8, 4, 1)
            else:
                max_conc = None
        else:
            dpi_value = mode_value = max_conc = None

        if st.button("Execute OCR", use_container_width=True, type="primary"):
            if not api_key_input or not uploaded_file:
                st.warning("Provide API key and upload a file.")
            else:
                with st.spinner("Processing via OCR Pipeline..."):
                    headers = {"X-API-KEY": api_key_input}
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    params = {}
                    if is_pdf:
                        params["dpi"] = dpi_value
                        params["mode"] = mode_value
                        if max_conc:
                            params["max_concurrency"] = int(max_conc)
                    try:
                        r = requests.post(f"{ocr_url}/v1/ocr",
                                          headers=headers, files=files, params=params)
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

        # Post-OCR actions
        if st.session_state.ocr_result:
            st.download_button("Download Markdown", data=st.session_state.ocr_result,
                               file_name=f"ocr_{int(time.time())}.md",
                               mime="text/markdown", use_container_width=True)

            # RAG Ingestion (talks to rag-pipeline :8081)
            st.markdown("### RAG Ingestion")
            col_l, col_r = st.columns(2, gap="medium")
            with col_l:
                collection = st.text_input("Collection", value="ocr_rag")
                chunk_size = st.number_input("Chunk Size", 200, 4000, 1200, 50)
            with col_r:
                chunk_overlap = st.number_input("Overlap", 0, 1000, 150, 25)

            if st.button("Ingest to Vector Store", use_container_width=True, type="primary"):
                with st.spinner("Sending to RAG Pipeline for embedding..."):
                    try:
                        payload = {
                            "filename": uploaded_file.name if uploaded_file else f"doc_{int(time.time())}",
                            "markdown_content": st.session_state.ocr_result,
                            "collection": collection,
                            "chunk_size": int(chunk_size),
                            "chunk_overlap": int(chunk_overlap),
                        }
                        r = requests.post(f"{rag_url}/v1/ingest",
                                          headers={"X-API-KEY": api_key_input},
                                          json=payload)
                        if r.status_code == 200:
                            res = r.json()
                            st.success(f"Ingested {res['chunks']} chunks → '{res['collection']}'")
                        else:
                            st.error(f"Ingestion failed: {r.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # Preview
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

# ===========================================================================
# Chat Dashboard (talks to rag-pipeline :8081)
# ===========================================================================
with tab_chat:
    st.header("Chat Dashboard")

    show_settings = st.toggle("Show Settings", value=False)
    if show_settings:
        cl, cr = st.columns(2, gap="medium")
        with cl:
            chat_collection = st.text_input("Collection", value="ocr_rag", key="chat_col")
            chat_top_k = st.number_input("Top K", 1, 50, 30, 1)
        with cr:
            system_prompt = st.text_area("System Prompt",
                value="You are a local RAG assistant. Answer using only the context. "
                      "If the answer is not in the context, say you do not know.",
                height=100)
    else:
        chat_collection = "ocr_rag"
        chat_top_k = 30
        system_prompt = ("You are a local RAG assistant. Answer using only the context. "
                         "If the answer is not in the context, say you do not know.")

    if st.button("Clear Chat", type="secondary"):
        st.session_state.chat_messages = []

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("Sources"):
                    for s in msg["sources"]:
                        st.markdown(f"- **{s['filename']}** (chunk {s['chunk_index']}, score {s['score']:.4f})")

    prompt = st.chat_input("Ask about ingested documents")
    if prompt:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.spinner("Querying RAG Pipeline..."):
            try:
                payload = {
                    "query": prompt,
                    "collection": chat_collection,
                    "top_k": int(chat_top_k),
                    "system_prompt": system_prompt,
                }
                r = requests.post(f"{rag_url}/v1/chat",
                                  headers={"X-API-KEY": api_key_input},
                                  json=payload, timeout=180)
                if r.status_code == 200:
                    res = r.json()
                    answer, sources = res["answer"], res["sources"]
                else:
                    answer = f"Error: {r.text}"
                    sources = []
            except Exception as e:
                answer = f"Failed: {e}"
                sources = []

        st.session_state.chat_messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )
        st.rerun()
