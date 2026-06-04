"""
OCR + RAG Control Center — with Metadata & Auto-Tagging
=========================================================
3 Tabs: OCR Dashboard | Chat Dashboard | Data Manager

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
BATCH_SIZE = 3

st.set_page_config(page_title="OCR + RAG Control Center", page_icon="", layout="wide")
st.title("OCR + RAG Control Center")
st.markdown("---")

# --- Sidebar ---
st.sidebar.header("Connection")
ocr_url = st.sidebar.text_input("OCR Pipeline URL", value=DEFAULT_OCR_URL)
rag_url = st.sidebar.text_input("RAG Pipeline URL", value=DEFAULT_RAG_URL)
st.sidebar.header("Authentication")
api_key_input = st.sidebar.text_input("API Key", type="password")
st.sidebar.code("legal_team_secret_abc123\ntest_key_0000", language="text")

if st.sidebar.button("Health Check"):
    for name, url in [("OCR", ocr_url), ("RAG", rag_url)]:
        try:
            r = requests.get(f"{url}/healthz", timeout=5)
            if r.status_code == 200:
                h = r.json()
                st.sidebar.success(f"{'✅' if h['status']=='ok' else '⚠️'} {name}: {h['status']}")
        except Exception as e:
            st.sidebar.error(f"{name}: {e}")

def _h():
    return {"X-API-KEY": api_key_input} if api_key_input else {}

def load_sessions():
    if not api_key_input: return []
    try:
        r = requests.get(f"{rag_url}/v1/sessions", headers=_h(), timeout=5)
        return r.json().get("sessions", []) if r.status_code == 200 else []
    except: return []

# Session state
for k, v in [("ocr_results", {}), ("ocr_metadata", {}), ("chat_messages", []),
             ("active_session", None), ("session_list", [])]:
    if k not in st.session_state: st.session_state[k] = v

# --- Sidebar: Session Management ---
st.sidebar.markdown("---")
st.sidebar.header("Sessions")

if st.sidebar.button("🔄 Refresh"):
    st.session_state.session_list = load_sessions()

with st.sidebar.expander("➕ New Session"):
    new_name = st.text_input("Name", placeholder="e.g. Legal Contracts Q4")
    if st.button("Create", use_container_width=True):
        if api_key_input and new_name.strip():
            try:
                r = requests.post(f"{rag_url}/v1/sessions", headers=_h(), json={"name": new_name.strip()})
                if r.status_code == 200:
                    res = r.json()
                    st.session_state.active_session = res["session"]
                    st.session_state.chat_messages = []
                    st.session_state.session_list = load_sessions()
                    st.rerun()
            except Exception as e: st.error(str(e))

sessions = st.session_state.session_list
snames = [s["name"] for s in sessions]
if snames:
    active = st.session_state.active_session
    idx = snames.index(active) if active in snames else 0
    sel = st.sidebar.selectbox("Active Session", snames, index=idx)
    if sel != st.session_state.active_session:
        st.session_state.active_session = sel
        st.session_state.chat_messages = []
        st.rerun()
    m = next((s for s in sessions if s["name"] == sel), None)
    if m: st.sidebar.caption(f"📊 {m.get('points',0)} vectors")
else:
    st.sidebar.info("No sessions. Create one above.")

if st.session_state.active_session and api_key_input:
    if st.sidebar.button("🗑️ Delete Session"):
        requests.delete(f"{rag_url}/v1/sessions/{st.session_state.active_session}", headers=_h())
        st.session_state.active_session = None
        st.session_state.chat_messages = []
        st.session_state.session_list = load_sessions()
        st.rerun()


# --- Worker ---
def _ocr_file(name, data, ctype, endpoint, headers, params):
    try:
        r = requests.post(endpoint, headers=headers, files={"file": (name, data, ctype)}, params=params, timeout=300)
        if r.status_code == 200:
            return (name, r.text, float(r.headers.get("X-Process-Time",0)), float(r.headers.get("X-Tokens-Per-Sec",0)), None)
        return (name, None, 0, 0, f"HTTP {r.status_code}")
    except Exception as e: return (name, None, 0, 0, str(e))

def _autotag(name, markdown, endpoint, headers):
    try:
        r = requests.post(endpoint, headers=headers, json={"markdown_content": markdown}, timeout=60)
        if r.status_code == 200: return r.json().get("metadata", {})
    except: pass
    return {"doc_type": "other", "date": None, "parties": [], "tags": [], "summary": ""}


# ========================================================================
tab_ocr, tab_chat, tab_data = st.tabs(["OCR Dashboard", "Chat Dashboard", "Data Manager"])

# ========================================================================
# OCR Dashboard
# ========================================================================
with tab_ocr:
    st.header("OCR Dashboard")
    with st.expander("⚙️ Advanced Settings"):
        c1, c2 = st.columns(2)
        c1.link_button("🔗 Qdrant Dashboard", QDRANT_DASHBOARD, use_container_width=True)
        c2.link_button("🔗 Swagger UI", f"{rag_url}/docs", use_container_width=True)

    col_dash, col_act = st.columns([1.3, 1], gap="large")

    with col_dash:
        st.subheader("OCR Metrics")
        if api_key_input:
            try:
                resp = requests.get(f"{ocr_url}/v1/metrics", headers=_h())
                if resp.status_code == 200:
                    data = resp.json(); metrics = data["metrics"]
                    st.markdown(f"**Identity:** {data['user']}")
                    spend, cap = data["current_month_spend"], data["monthly_spend_cap"]
                    st.progress(min(spend/cap,1.0) if cap>0 else 0)
                    st.caption(f"**${spend:.2f}** of **${cap:.2f}**")
                    c1,c2,c3 = st.columns(3)
                    c1.metric("Docs", metrics["total_documents"])
                    c2.metric("Pages", metrics["total_pages_processed"])
                    c3.metric("Tokens", f"{metrics['total_input_tokens']+metrics['total_output_tokens']:,}")
                    if data["audit_logs"]:
                        st.dataframe(pd.DataFrame(data["audit_logs"]), use_container_width=True, hide_index=True, height=240)
            except: st.error(f"Cannot connect to {ocr_url}")
        else: st.info("Enter API Key.")

    with col_act:
        st.subheader("Document Processing")
        uploaded_files = st.file_uploader("Upload Documents", type=["pdf","jpg","png"], accept_multiple_files=True)
        if uploaded_files: st.caption(f"**{len(uploaded_files)}** file(s) queued • Batch: {BATCH_SIZE}")

        has_pdf = any(f.type=="application/pdf" for f in (uploaded_files or []))
        if has_pdf:
            dpi_value = st.slider("DPI", 120, 350, 200, 10)
            mode_value = st.selectbox("Mode", ["serial","concurrent"], index=1)
            max_conc = st.number_input("Concurrency", 1, 8, 4) if mode_value=="concurrent" else None
        else: dpi_value, mode_value, max_conc = 200, "concurrent", 4

        if st.button("🚀 Execute OCR + Auto-Tag", use_container_width=True, type="primary"):
            if not api_key_input or not uploaded_files:
                st.warning("Provide API key and files.")
            else:
                total = len(uploaded_files)
                results, meta_results = {}, {}
                params = {"dpi": dpi_value, "mode": mode_value}
                if max_conc: params["max_concurrency"] = int(max_conc)
                file_data = [(f.name, f.getvalue(), f.type) for f in uploaded_files]

                with st.status(f"Processing {total} file(s)...", expanded=True) as sb:
                    t0 = time.time()
                    prog = st.progress(0, text=f"0 / {total}")
                    done = 0

                    # Phase 1: OCR
                    for batch_start in range(0, total, BATCH_SIZE):
                        batch = file_data[batch_start:batch_start+BATCH_SIZE]
                        st.write(f"**OCR Batch {batch_start//BATCH_SIZE+1}** — {len(batch)} files")
                        slots = {n: st.empty() for n,_,_ in batch}
                        for n in slots: slots[n].markdown(f"🔄 `{n}` — *Processing...*")

                        with ThreadPoolExecutor(max_workers=BATCH_SIZE) as ex:
                            futs = {ex.submit(_ocr_file,n,d,t,f"{ocr_url}/v1/ocr",_h(),params): n for n,d,t in batch}
                            for f in as_completed(futs):
                                nm = futs[f]
                                n,md,lat,tps,err = f.result()
                                if err: slots[nm].markdown(f"❌ `{n}` — {err}")
                                else:
                                    slots[nm].markdown(f"✅ `{n}` — {lat:.1f}s ({tps:.0f} tok/s)")
                                    results[n] = md
                                done += 1
                                elapsed = time.time()-t0
                                eta = (elapsed/done)*(total-done)
                                prog.progress(done/total, text=f"{done}/{total} • {elapsed:.0f}s • ETA {eta:.0f}s")

                    # Phase 2: Auto-Tag
                    if results:
                        st.write(f"**🤖 Auto-tagging {len(results)} files...**")
                        for fname, md_text in results.items():
                            tag_slot = st.empty()
                            tag_slot.markdown(f"🏷️ Tagging `{fname}`...")
                            meta = _autotag(fname, md_text, f"{rag_url}/v1/autotag", _h())
                            meta_results[fname] = meta
                            tag_slot.markdown(f"🏷️ `{fname}` → **{meta.get('doc_type','?')}** | {meta.get('summary','')[:60]}")

                    tt = time.time()-t0
                    sb.update(label=f"Done: {len(results)} files in {tt:.1f}s ✅", state="complete")

                if results:
                    st.session_state.ocr_results.update(results)
                    st.session_state.ocr_metadata.update(meta_results)
                    st.rerun()

        # --- Results & Metadata Editor ---
        if st.session_state.ocr_results:
            rnames = list(st.session_state.ocr_results.keys())
            st.markdown(f"### Processed Files ({len(rnames)})")

            combined = "".join(f"\n<!-- FILE: {n} -->\n{md}\n" for n,md in st.session_state.ocr_results.items())
            st.download_button("📥 Download All", data=combined, file_name=f"ocr_batch_{int(time.time())}.md",
                               mime="text/markdown", use_container_width=True)

            # Metadata editor per file
            st.markdown("### Review & Edit Metadata")
            edit_file = st.selectbox("Select file", rnames, key="meta_edit_file")
            if edit_file:
                meta = st.session_state.ocr_metadata.get(edit_file, {})
                mc1, mc2 = st.columns(2)
                with mc1:
                    doc_type = st.selectbox("Doc Type", ["invoice","contract","report","letter","memo","receipt","policy","form","certificate","other"],
                                            index=["invoice","contract","report","letter","memo","receipt","policy","form","certificate","other"].index(meta.get("doc_type","other")) if meta.get("doc_type","other") in ["invoice","contract","report","letter","memo","receipt","policy","form","certificate","other"] else 9)
                    doc_date = st.text_input("Date (YYYY-MM-DD)", value=meta.get("date","") or "")
                    parties_str = st.text_input("Parties (comma-separated)", value=", ".join(meta.get("parties",[])))
                with mc2:
                    tags_str = st.text_input("Tags (comma-separated)", value=", ".join(meta.get("tags",[])))
                    summary = st.text_input("Summary", value=meta.get("summary",""))
                    # Custom fields
                    custom_json = st.text_area("Custom Fields (JSON)", value=json.dumps({k:v for k,v in meta.items() if k not in ["doc_type","date","parties","tags","summary","_error"]}, indent=2) if meta else "{}", height=80)

                if st.button("💾 Save Metadata", key=f"save_meta_{edit_file}"):
                    updated = {
                        "doc_type": doc_type,
                        "date": doc_date if doc_date else None,
                        "parties": [p.strip() for p in parties_str.split(",") if p.strip()],
                        "tags": [t.strip() for t in tags_str.split(",") if t.strip()],
                        "summary": summary,
                    }
                    try:
                        custom = json.loads(custom_json)
                        updated.update(custom)
                    except: pass
                    st.session_state.ocr_metadata[edit_file] = updated
                    st.success(f"Metadata saved for {edit_file}")

            # Ingestion
            st.markdown("### Ingest to Session")
            target = st.session_state.active_session
            if target:
                st.info(f"Session: **{target}** | Files: **{len(rnames)}**")
                chunk_size = st.number_input("Chunk Size", 200, 4000, 1200, 50)
                if st.button("📤 Ingest All with Metadata", use_container_width=True, type="primary"):
                    with st.status(f"Ingesting {len(rnames)} files...", expanded=True) as ing:
                        total_chunks = 0
                        for i, fname in enumerate(rnames):
                            st.write(f"🔄 `{fname}` ({i+1}/{len(rnames)})...")
                            meta = st.session_state.ocr_metadata.get(fname, {})
                            payload = {"filename": fname, "markdown_content": st.session_state.ocr_results[fname],
                                       "collection": target, "chunk_size": int(chunk_size), "metadata": meta}
                            try:
                                r = requests.post(f"{rag_url}/v1/ingest", headers=_h(), json=payload, timeout=120)
                                if r.status_code == 200:
                                    res = r.json(); total_chunks += res["chunks"]
                                    st.write(f"✅ `{fname}` — {res['chunks']} chunks | {meta.get('doc_type','?')}")
                                else: st.write(f"❌ `{fname}` — {r.text}")
                            except Exception as e: st.write(f"❌ `{fname}` — {e}")
                        ing.update(label=f"Ingested {total_chunks} chunks from {len(rnames)} files ✅", state="complete")
                        st.session_state.session_list = load_sessions()
            else: st.warning("Create a session first.")

            if st.button("🗑️ Clear OCR Results"):
                st.session_state.ocr_results = {}
                st.session_state.ocr_metadata = {}
                st.rerun()

    # Preview
    if st.session_state.ocr_results:
        st.markdown("### Document Preview")
        pf = st.selectbox("Preview file", list(st.session_state.ocr_results.keys()), key="preview_file")
        if pf:
            l, r_ = st.columns(2, gap="large")
            with l:
                st.subheader("Raw Markdown")
                st.text_area("raw", value=st.session_state.ocr_results[pf], height=400, label_visibility="collapsed")
            with r_:
                st.subheader("Rendered")
                st.markdown(st.session_state.ocr_results[pf], unsafe_allow_html=True)

# ========================================================================
# Chat Dashboard
# ========================================================================
with tab_chat:
    st.header("Chat Dashboard")
    active = st.session_state.active_session
    if active: st.caption(f"Session: **{active}**")
    else: st.warning("Select a session first.")

    with st.expander("⚙️ Advanced Settings"):
        c1, c2 = st.columns(2)
        c1.link_button("🔗 Qdrant Dashboard", QDRANT_DASHBOARD, use_container_width=True)
        c2.link_button("🔗 Swagger UI", f"{rag_url}/docs", use_container_width=True)
        st.markdown("---")
        cl, cr = st.columns(2)
        with cl:
            chat_top_k = st.number_input("Top K", 1, 50, 30, 1)
            memory_enabled = st.checkbox("Memory", value=True)
            memory_top_k = st.number_input("Memory Top K", 1, 20, 5, 1)
        with cr:
            auto_extract = st.checkbox("Auto-extract filters from query", value=False)
            system_prompt = st.text_area("System Prompt",
                value="You are a local RAG assistant. Answer using only the context. "
                      "Use conversation history for follow-up context. "
                      "If the answer is not in the context, say you do not know.", height=80)

        # Manual filters
        st.markdown("**Manual Filters** (override auto-extract)")
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            f_doc_type = st.selectbox("Doc Type Filter", ["(none)","invoice","contract","report","letter","memo","receipt","policy","form","certificate"])
        with fc2:
            f_tags = st.text_input("Tags Filter (comma-sep)", "")
        with fc3:
            f_date_from = st.text_input("Date From", "")
            f_date_to = st.text_input("Date To", "")

        manual_filters = {}
        if f_doc_type != "(none)": manual_filters["doc_type"] = f_doc_type
        if f_tags: manual_filters["tags"] = [t.strip() for t in f_tags.split(",") if t.strip()]
        if f_date_from: manual_filters["date_from"] = f_date_from
        if f_date_to: manual_filters["date_to"] = f_date_to

    if "chat_top_k" not in dir():
        chat_top_k, memory_enabled, memory_top_k, system_prompt = 30, True, 5, None
        auto_extract, manual_filters = True, {}

    if st.button("Clear Chat & Memory"):
        if api_key_input and active:
            try: requests.delete(f"{rag_url}/v1/memory/{active}", headers=_h(), timeout=5)
            except: pass
        st.session_state.chat_messages = []
        st.rerun()

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                if msg.get("sources"):
                    with st.expander(f"📄 Sources ({len(msg['sources'])})"):
                        for s in msg["sources"]:
                            st.markdown(f"- **{s['filename']}** | {s.get('section','')} | score {s['score']:.4f}")
                if msg.get("memories"):
                    with st.expander(f"🧠 Memory ({len(msg['memories'])})"):
                        for m in msg["memories"]:
                            st.markdown(f"- **Q:** {m['query'][:80]}...\n  **A:** {m['answer'][:120]}...")

    prompt = st.chat_input("Ask about documents in this session")
    if prompt and active:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.spinner("Querying..."):
            try:
                payload = {"query": prompt, "collection": active, "top_k": int(chat_top_k),
                           "session_id": active, "memory_enabled": memory_enabled,
                           "memory_top_k": int(memory_top_k),
                           "auto_extract_filters": auto_extract}
                if manual_filters: payload["filters"] = manual_filters
                if system_prompt: payload["system_prompt"] = system_prompt
                r = requests.post(f"{rag_url}/v1/chat", headers=_h(), json=payload, timeout=180)
                if r.status_code == 200:
                    res = r.json()
                    answer, sources, memories = res["answer"], res.get("sources",[]), res.get("memories",[])
                else: answer, sources, memories = f"Error: {r.text}", [], []
            except Exception as e: answer, sources, memories = f"Failed: {e}", [], []
        st.session_state.chat_messages.append({"role":"assistant","content":answer,"sources":sources,"memories":memories})
        st.rerun()

# ========================================================================
# Data Manager
# ========================================================================
with tab_data:
    st.header("Data Manager")
    st.caption("Browse and edit metadata for ingested documents — no re-ingestion needed.")

    with st.expander("⚙️ Advanced Settings"):
        c1, c2 = st.columns(2)
        c1.link_button("🔗 Qdrant Dashboard", QDRANT_DASHBOARD, use_container_width=True)
        c2.link_button("🔗 Swagger UI", f"{rag_url}/docs", use_container_width=True)

    active = st.session_state.active_session
    if not active:
        st.warning("Select a session to manage documents.")
    elif not api_key_input:
        st.info("Enter API key.")
    else:
        # Load documents
        if st.button("🔄 Refresh Documents"):
            pass  # Force re-fetch below

        try:
            r = requests.get(f"{rag_url}/v1/documents/{active}", headers=_h(), timeout=10)
            if r.status_code == 200:
                docs = r.json().get("documents", [])
                if not docs:
                    st.info("No documents ingested in this session yet.")
                else:
                    # Summary table
                    df_data = []
                    for d in docs:
                        m = d.get("metadata", {})
                        df_data.append({
                            "Filename": d["filename"],
                            "Type": m.get("doc_type", "—"),
                            "Date": m.get("date", "—") or "—",
                            "Tags": ", ".join(m.get("tags", [])),
                            "Chunks": d["chunks"],
                            "Summary": (m.get("summary", "") or "")[:60],
                        })
                    st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

                    # Edit selected document
                    st.markdown("### Edit Metadata")
                    doc_names = [d["filename"] for d in docs]
                    sel_doc = st.selectbox("Select document", doc_names, key="dm_select")

                    if sel_doc:
                        doc_info = next(d for d in docs if d["filename"] == sel_doc)
                        meta = doc_info.get("metadata", {})

                        ec1, ec2 = st.columns(2)
                        with ec1:
                            types = ["invoice","contract","report","letter","memo","receipt","policy","form","certificate","other"]
                            e_type = st.selectbox("Doc Type", types,
                                                  index=types.index(meta.get("doc_type","other")) if meta.get("doc_type","other") in types else 9,
                                                  key="dm_type")
                            e_date = st.text_input("Date", value=meta.get("date","") or "", key="dm_date")
                            e_parties = st.text_input("Parties", value=", ".join(meta.get("parties",[])), key="dm_parties")
                        with ec2:
                            e_tags = st.text_input("Tags", value=", ".join(meta.get("tags",[])), key="dm_tags")
                            e_summary = st.text_input("Summary", value=meta.get("summary",""), key="dm_summary")
                            custom_keys = {k:v for k,v in meta.items() if k not in ["doc_type","date","parties","tags","summary","_error"]}
                            e_custom = st.text_area("Custom Fields (JSON)", value=json.dumps(custom_keys, indent=2) if custom_keys else "{}", height=80, key="dm_custom")

                        if st.button("💾 Update Metadata (no re-ingest)", use_container_width=True, type="primary"):
                            updated = {
                                "doc_type": e_type,
                                "date": e_date if e_date else None,
                                "parties": [p.strip() for p in e_parties.split(",") if p.strip()],
                                "tags": [t.strip() for t in e_tags.split(",") if t.strip()],
                                "summary": e_summary,
                            }
                            try:
                                custom = json.loads(e_custom)
                                updated.update(custom)
                            except: pass

                            try:
                                r = requests.patch(f"{rag_url}/v1/metadata/{active}/{sel_doc}",
                                                   headers=_h(), json={"metadata": updated}, timeout=10)
                                if r.status_code == 200:
                                    res = r.json()
                                    st.success(f"✅ Updated {res['chunks_updated']} chunks — no re-embedding!")
                                else: st.error(f"Failed: {r.text}")
                            except Exception as e: st.error(str(e))
            else:
                st.error(f"Failed to load documents: {r.text}")
        except Exception as e:
            st.error(f"Cannot connect: {e}")
