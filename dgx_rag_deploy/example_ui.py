"""
OCR + RAG Control Center v3
Usage: streamlit run example_ui.py
"""
import os, time, uuid, json, base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st, requests, pandas as pd

DEFAULT_OCR_URL = os.getenv("OCR_API_URL", "http://192.168.50.153:8080")
DEFAULT_RAG_URL = os.getenv("RAG_API_URL", "http://192.168.50.153:8081")
QDRANT_DASHBOARD = os.getenv("QDRANT_DASHBOARD", "http://192.168.50.153:6333/dashboard")
BATCH_SIZE = 3

st.set_page_config(page_title="OCR + RAG Control Center v3", page_icon="", layout="wide")
st.title("OCR + RAG Control Center v3")
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
                d = r.json()
                ver = d.get("version", "")
                st.sidebar.success(f"✅ {name}: {d['status']} {f'(v{ver})' if ver else ''}")
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

for k, v in [("ocr_results", {}), ("ocr_metadata", {}), ("chat_messages", []),
             ("active_session", None), ("session_list", []),
             ("uploader_key", 0), ("ocr_step", 1)]:
    if k not in st.session_state:
        st.session_state[k] = v

# --- Sidebar: Sessions ---
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
                    st.session_state.active_session = r.json()["session"]
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

# Workers
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

DOC_TYPES = ["invoice","contract","report","letter","memo","receipt","policy","form","certificate","other"]

# ========================================================================
tab_ocr, tab_chat, tab_data = st.tabs(["OCR Dashboard", "Chat Dashboard", "Data Manager"])

# ========================================================================
# OCR DASHBOARD
# ========================================================================
with tab_ocr:
    st.header("OCR Dashboard")
    with st.expander("⚙️ Advanced Settings"):
        c1, c2 = st.columns(2)
        c1.link_button("🔗 Qdrant Dashboard", QDRANT_DASHBOARD, use_container_width=True)
        c2.link_button("🔗 Swagger UI", f"{rag_url}/docs", use_container_width=True)

    has_results = bool(st.session_state.ocr_results)

    # ── Step 1: Upload & OCR ──
    st.subheader(f"Step 1: Upload & Process {'✅' if has_results else ''}")
    if not has_results:
        uploaded_files = st.file_uploader("Upload Documents (PDF, JPG, PNG)",
            type=["pdf","jpg","png"], accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_key}")
        if uploaded_files:
            st.caption(f"**{len(uploaded_files)}** file(s) selected")
        has_pdf = any(f.type == "application/pdf" for f in (uploaded_files or []))
        if has_pdf:
            dpi_value = st.slider("DPI", 120, 350, 200, 10)
            mode_value = st.selectbox("Mode", ["serial","concurrent"], index=1)
        else:
            dpi_value, mode_value = 200, "concurrent"

        if st.button("🚀 Execute OCR + Auto-Tag", use_container_width=True, type="primary"):
            if not api_key_input or not uploaded_files:
                st.warning("Provide API key and upload files.")
            else:
                total = len(uploaded_files)
                results, meta_results = {}, {}
                params = {"dpi": dpi_value, "mode": mode_value}
                if mode_value == "concurrent": params["max_concurrency"] = 4
                file_data = [(f.name, f.getvalue(), f.type) for f in uploaded_files]

                with st.status(f"Processing {total} file(s)...", expanded=True) as sb:
                    t0 = time.time()
                    prog = st.progress(0, text=f"0 / {total}")
                    elapsed_ph = st.empty()
                    done = 0
                    for batch_start in range(0, total, BATCH_SIZE):
                        batch = file_data[batch_start:batch_start+BATCH_SIZE]
                        slots = {n: st.empty() for n,_,_ in batch}
                        for n in slots: slots[n].markdown(f"🔄 `{n}` — *Processing...*")
                        with ThreadPoolExecutor(max_workers=BATCH_SIZE) as ex:
                            futs = {ex.submit(_ocr_file,n,d,t,f"{ocr_url}/v1/ocr",_h(),params): n for n,d,t in batch}
                            for f in as_completed(futs):
                                nm = futs[f]; n,md,lat,tps,err = f.result()
                                if err: slots[nm].markdown(f"❌ `{n}` — {err}")
                                else:
                                    slots[nm].markdown(f"✅ `{n}` — {lat:.1f}s | {tps:.0f} tok/s")
                                    results[n] = md
                                done += 1
                                prog.progress(done/total, text=f"{done}/{total}")
                                elapsed_ph.caption(f"⏱️ Elapsed: {time.time()-t0:.1f}s")
                    if results:
                        st.write("🤖 **Auto-tagging...**")
                        for fname, md_text in results.items():
                            meta_results[fname] = _autotag(fname, md_text, f"{rag_url}/v1/autotag", _h())
                    sb.update(label=f"Done: {len(results)} files in {time.time()-t0:.1f}s ✅", state="complete")

                if results:
                    st.session_state.ocr_results = results
                    st.session_state.ocr_metadata = meta_results
                    st.session_state.ocr_step = 2
                    st.session_state.uploader_key += 1
                    st.rerun()
    else:
        rnames = list(st.session_state.ocr_results.keys())
        st.success(f"**{len(rnames)}** file(s) processed: {', '.join(rnames)}")
        col_dl, col_clr = st.columns(2)

        # Individual downloads
        for i, fname in enumerate(rnames):
            base = os.path.splitext(fname)[0]
            st.download_button(f"📄 {base}.md", data=st.session_state.ocr_results[fname],
                file_name=f"{base}.md", mime="text/markdown", use_container_width=True, key=f"dl_{i}")

        # Batch download
        if len(rnames) > 1:
            import io, zipfile
            zbuf = io.BytesIO()
            with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as zf:
                for fname, md in st.session_state.ocr_results.items():
                    zf.writestr(os.path.splitext(fname)[0] + ".md", md)
            zbuf.seek(0)
            col_dl.download_button("📦 Download All (ZIP)", data=zbuf.getvalue(),
                file_name=f"ocr_batch_{int(time.time())}.zip", mime="application/zip", use_container_width=True)

        if col_clr.button("🔄 Start New OCR", use_container_width=True):
            st.session_state.ocr_results = {}
            st.session_state.ocr_metadata = {}
            st.session_state.ocr_step = 1
            st.session_state.uploader_key += 1
            st.rerun()

    # ── Step 2: Review Metadata ──
    if has_results:
        st.markdown("---")
        st.subheader("Step 2: Review & Edit Metadata")
        rnames = list(st.session_state.ocr_results.keys())
        edit_file = st.selectbox("Select file", rnames, key="meta_edit_file")
        if edit_file:
            meta = st.session_state.ocr_metadata.get(edit_file, {})
            mc1, mc2 = st.columns(2)
            with mc1:
                dt_idx = DOC_TYPES.index(meta.get("doc_type","other")) if meta.get("doc_type","other") in DOC_TYPES else 9
                doc_type = st.selectbox("Doc Type", DOC_TYPES, index=dt_idx)
                doc_date = st.text_input("Date (YYYY-MM-DD)", value=meta.get("date","") or "")
                parties_str = st.text_input("Parties (comma-separated)", value=", ".join(meta.get("parties",[])))
            with mc2:
                tags_str = st.text_input("Tags (comma-separated)", value=", ".join(meta.get("tags",[])))
                summary = st.text_input("Summary", value=meta.get("summary",""))
                custom_keys = {k:v for k,v in meta.items() if k not in ["doc_type","date","parties","tags","summary","_error"]}
                custom_json = st.text_area("Custom Fields (JSON)", value=json.dumps(custom_keys, indent=2) if custom_keys else "{}", height=68)
            if st.button("💾 Save Metadata", key="save_meta"):
                updated = {"doc_type": doc_type, "date": doc_date or None,
                    "parties": [p.strip() for p in parties_str.split(",") if p.strip()],
                    "tags": [t.strip() for t in tags_str.split(",") if t.strip()], "summary": summary}
                try: updated.update(json.loads(custom_json))
                except: pass
                st.session_state.ocr_metadata[edit_file] = updated
                st.success(f"Saved for {edit_file}")

        with st.expander("📄 Document Preview"):
            pf = st.selectbox("File", rnames, key="preview_sel")
            if pf:
                l, r_ = st.columns(2, gap="large")
                l.text_area("raw", value=st.session_state.ocr_results[pf], height=300, label_visibility="collapsed")
                r_.markdown(st.session_state.ocr_results[pf], unsafe_allow_html=True)

    # ── Step 3: Ingest ──
    if has_results:
        st.markdown("---")
        st.subheader("Step 3: Ingest to Session")
        target = st.session_state.active_session
        if not target:
            st.warning("Create or select a session in the sidebar first.")
        else:
            rnames = list(st.session_state.ocr_results.keys())
            st.info(f"**{len(rnames)}** file(s) → session **{target}** (dedup enabled: re-ingest overwrites)")
            chunk_size = st.number_input("Chunk Size", 200, 4000, 1200, 50)
            if st.button("📤 Ingest to Vector Store", use_container_width=True, type="primary"):
                total_chunks = 0; errors = []
                with st.status(f"Ingesting {len(rnames)} file(s)...", expanded=True) as sb:
                    t0 = time.time()
                    for i, fname in enumerate(rnames):
                        meta = st.session_state.ocr_metadata.get(fname, {})
                        payload = {"filename": fname, "markdown_content": st.session_state.ocr_results[fname],
                                   "collection": target, "chunk_size": int(chunk_size), "metadata": meta}
                        st.write(f"[{i+1}/{len(rnames)}] `{fname}`...")
                        try:
                            r = requests.post(f"{rag_url}/v1/ingest", headers=_h(), json=payload, timeout=120)
                            if r.status_code == 200:
                                c = r.json()["chunks"]
                                total_chunks += c
                                st.write(f"  ✅ {c} chunks")
                            else: errors.append(fname)
                        except: errors.append(fname)
                    elapsed = time.time() - t0
                    sb.update(label=f"Ingested {total_chunks} chunks in {elapsed:.1f}s", state="complete")
                if errors:
                    st.error(f"Failed: {', '.join(errors)}")
                else:
                    st.success(f"✅ {total_chunks} chunks from {len(rnames)} file(s) in {elapsed:.1f}s")
                st.session_state.session_list = load_sessions()

# ========================================================================
# CHAT DASHBOARD
# ========================================================================
with tab_chat:
    st.header("Chat Dashboard")
    active = st.session_state.active_session
    if active: st.caption(f"Session: **{active}**")
    else: st.warning("Select a session first.")
    with st.expander("⚙️ Retrieval Engine Settings"):
        c1, c2 = st.columns(2)
        c1.link_button("🔗 Qdrant Dashboard", QDRANT_DASHBOARD, use_container_width=True)
        c2.link_button("🔗 Swagger UI", f"{rag_url}/docs", use_container_width=True)
        st.markdown("---")
        st.markdown("**🧠 Retrieval Engine** — Toggle features that add LLM calls (slower but more precise)")
        re1, re2, re3 = st.columns(3)
        with re1:
            rerank_enabled = st.checkbox("Re-ranking", value=False, help="⚠️ +5-15s latency. LLM re-scores chunks.")
        with re2:
            agentic_enabled = st.checkbox("Agentic RAG", value=False, help="⚠️ +3-8s latency. Decomposes complex queries.")
        with re3:
            auto_extract = st.checkbox("Auto-extract filters", value=False, help="⚠️ +3-8s latency. LLM extracts metadata filters.")

        if rerank_enabled or agentic_enabled or auto_extract:
            enabled = [x for x, v in [("Re-rank", rerank_enabled), ("Agentic", agentic_enabled), ("Auto-filter", auto_extract)] if v]
            st.warning(f"⚡ **Slow mode**: {', '.join(enabled)} enabled. Each adds an LLM call (+3-15s).")

        st.markdown("---")
        cl, cr = st.columns(2)
        with cl:
            chat_top_k = st.number_input("Top K", 1, 50, 15, 1)
            memory_enabled = st.checkbox("Memory", value=True)
            memory_top_k = st.number_input("Memory Top K", 1, 20, 5, 1)
        with cr:
            system_prompt = st.text_area("System Prompt",
                value="You are a helpful RAG assistant. Use the provided context to answer accurately. "
                      "For basic questions, answer naturally. Cite sources when referencing documents.", height=80)
        st.markdown("**Manual Filters** (override auto-extract)")
        fc1, fc2, fc3 = st.columns(3)
        with fc1: f_doc_type = st.selectbox("Doc Type Filter", ["(none)"]+DOC_TYPES)
        with fc2: f_tags = st.text_input("Tags Filter (comma-sep)", "")
        with fc3:
            f_date_from = st.text_input("Date From", "")
            f_date_to = st.text_input("Date To", "")
        manual_filters = {}
        if f_doc_type != "(none)": manual_filters["doc_type"] = f_doc_type
        if f_tags: manual_filters["tags"] = [t.strip() for t in f_tags.split(",") if t.strip()]
        if f_date_from: manual_filters["date_from"] = f_date_from
        if f_date_to: manual_filters["date_to"] = f_date_to

    if "chat_top_k" not in dir():
        chat_top_k, memory_enabled, memory_top_k, system_prompt = 15, True, 5, None
        auto_extract, manual_filters, rerank_enabled, agentic_enabled = False, {}, False, False

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
                lat = msg.get("latency")
                if lat: st.caption(f"⏱️ {lat}s")
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
                           "memory_top_k": int(memory_top_k), "auto_extract_filters": auto_extract,
                           "rerank": rerank_enabled, "agentic": agentic_enabled}
                if manual_filters: payload["filters"] = manual_filters
                if system_prompt: payload["system_prompt"] = system_prompt
                r = requests.post(f"{rag_url}/v1/chat", headers=_h(), json=payload, timeout=300)
                if r.status_code == 200:
                    res = r.json()
                    answer = res["answer"]
                    sources = res.get("sources", [])
                    memories = res.get("memories", [])
                    latency = res.get("latency", None)
                else: answer, sources, memories, latency = f"Error: {r.text}", [], [], None
            except Exception as e: answer, sources, memories, latency = f"Failed: {e}", [], [], None
        st.session_state.chat_messages.append({"role":"assistant","content":answer,"sources":sources,"memories":memories,"latency":latency})
        st.rerun()

# ========================================================================
# DATA MANAGER
# ========================================================================
with tab_data:
    st.header("Data Manager")
    st.caption("Browse and edit metadata for ingested documents — no re-ingestion needed.")
    with st.expander("⚙️ Advanced Settings"):
        c1, c2 = st.columns(2)
        c1.link_button("🔗 Qdrant Dashboard", QDRANT_DASHBOARD, use_container_width=True)
        c2.link_button("🔗 Swagger UI", f"{rag_url}/docs", use_container_width=True)
    active = st.session_state.active_session
    if not active: st.warning("Select a session to manage documents.")
    elif not api_key_input: st.info("Enter API key.")
    else:
        st.button("🔄 Refresh Documents")
        try:
            r = requests.get(f"{rag_url}/v1/documents/{active}", headers=_h(), timeout=10)
            if r.status_code == 200:
                docs = r.json().get("documents", [])
                if not docs: st.info("No documents ingested yet.")
                else:
                    df_data = [{"Filename": d["filename"], "Type": d.get("metadata",{}).get("doc_type","—"),
                        "Date": d.get("metadata",{}).get("date","—") or "—",
                        "Tags": ", ".join(d.get("metadata",{}).get("tags",[])),
                        "Chunks": d["chunks"]} for d in docs]
                    st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)
                    st.markdown("### Edit Metadata")
                    doc_names = [d["filename"] for d in docs]
                    sel_doc = st.selectbox("Select document", doc_names, key="dm_select")
                    if sel_doc:
                        meta = next(d for d in docs if d["filename"]==sel_doc).get("metadata",{})
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            e_type = st.selectbox("Doc Type", DOC_TYPES,
                                index=DOC_TYPES.index(meta.get("doc_type","other")) if meta.get("doc_type","other") in DOC_TYPES else 9, key="dm_type")
                            e_date = st.text_input("Date", value=meta.get("date","") or "", key="dm_date")
                            e_parties = st.text_input("Parties", value=", ".join(meta.get("parties",[])), key="dm_parties")
                        with ec2:
                            e_tags = st.text_input("Tags", value=", ".join(meta.get("tags",[])), key="dm_tags")
                            e_summary = st.text_input("Summary", value=meta.get("summary",""), key="dm_summary")
                            custom_keys = {k:v for k,v in meta.items() if k not in ["doc_type","date","parties","tags","summary","_error"]}
                            e_custom = st.text_area("Custom Fields (JSON)", value=json.dumps(custom_keys, indent=2) if custom_keys else "{}", height=68, key="dm_custom")
                        if st.button("💾 Update Metadata (no re-ingest)", use_container_width=True, type="primary"):
                            updated = {"doc_type": e_type, "date": e_date or None,
                                "parties": [p.strip() for p in e_parties.split(",") if p.strip()],
                                "tags": [t.strip() for t in e_tags.split(",") if t.strip()], "summary": e_summary}
                            try: updated.update(json.loads(e_custom))
                            except: pass
                            try:
                                r = requests.patch(f"{rag_url}/v1/metadata/{active}/{sel_doc}",
                                    headers=_h(), json={"metadata": updated}, timeout=10)
                                if r.status_code == 200: st.success(f"✅ Updated {r.json()['chunks_updated']} chunks")
                                else: st.error(f"Failed: {r.text}")
                            except Exception as e: st.error(str(e))
        except Exception as e: st.error(f"Cannot connect: {e}")
