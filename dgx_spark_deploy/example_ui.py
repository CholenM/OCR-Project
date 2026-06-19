"""
Example UI — OCR Pipeline Client (Streamlit)
=============================================
A reference Streamlit UI that connects to the OCR Pipeline API
running on the DGX Spark. Run this from ANY machine on the
local network.

Usage:
    pip install streamlit requests pandas
    streamlit run example_ui.py

Configure the API URL via the sidebar or set the environment variable:
    OCR_API_URL=http://<dgx-spark-ip>:8080  streamlit run example_ui.py
"""

import os
import streamlit as st
import requests
import time
import pandas as pd

# --- CONFIGURATION ---
# Update this to the DGX Spark's IP address
DEFAULT_API_URL = os.getenv("OCR_API_URL", "http://localhost:8080")
OCR_STATUS_POLL_SECONDS = float(os.getenv("OCR_STATUS_POLL_SECONDS", "2"))

st.set_page_config(page_title="OCR Control Center", page_icon="🔍", layout="wide")
st.title("🔍 OCR Dashboard")
st.markdown("---")

# --- SIDEBAR CONTROL UNIT ---
st.sidebar.header("⚙️ Connection")
api_url = st.sidebar.text_input("API Base URL", value=DEFAULT_API_URL)
st.sidebar.markdown("---")

st.sidebar.header("🔑 Authentication")
api_key_input = st.sidebar.text_input("Enter Service API Key", type="password")
st.sidebar.markdown("### Developer Sandbox Keys")
st.sidebar.code("legal_team_secret_abc123\ntest_key_0000", language="text")

# --- Connection Status ---
st.sidebar.markdown("---")
st.sidebar.header("📡 Status")
if st.sidebar.button("Check Connection"):
    try:
        health_resp = requests.get(f"{api_url}/healthz", timeout=5)
        if health_resp.status_code == 200:
            health_data = health_resp.json()
            if health_data.get("status") == "healthy":
                st.sidebar.success(f"✅ Connected — Model: {health_data.get('model_name', 'Unknown')}")
            else:
                st.sidebar.warning(f"⚠️ Degraded — Model server: {health_data.get('model_server', 'unknown')}")
        else:
            st.sidebar.error(f"❌ API returned {health_resp.status_code}")
    except requests.exceptions.ConnectionError:
        st.sidebar.error(f"❌ Cannot reach {api_url}")
    except Exception as e:
        st.sidebar.error(f"❌ {str(e)}")

if "ocr_result" not in st.session_state:
    st.session_state.ocr_result = None
if "ocr_result_filename" not in st.session_state:
    st.session_state.ocr_result_filename = None
if "ocr_job" not in st.session_state:
    st.session_state.ocr_job = None
if "ocr_job_error" not in st.session_state:
    st.session_state.ocr_job_error = None

# --- VIEW SPLIT LAYOUT ---
col_dashboard, col_actions = st.columns([1.3, 1], gap="large")

with col_dashboard:
    st.header("📊 API Tracking Usage")

    if api_key_input:
        headers = {"X-API-KEY": api_key_input}
        try:
            metrics_resp = requests.get(f"{api_url}/v1/metrics", headers=headers)

            if metrics_resp.status_code == 200:
                data = metrics_resp.json()
                metrics = data["metrics"]

                st.subheader(f"Identity: {data['user']}")

                # Financial Guardrails UI
                st.markdown("##### 💰 API Usage")
                spend = data["current_month_spend"]
                cap = data["monthly_spend_cap"]
                progress = min(spend / cap, 1.0) if cap > 0 else 0

                st.progress(progress)
                st.caption(f"**${spend:.2f}** accrued of **${cap:.2f}** soft limit (Rate: ${data['rate_per_page']}/page)")

                # Token & Usage Metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Docs Processed", metrics["total_documents"])
                col2.metric("Total Pages", metrics["total_pages_processed"])
                total_tokens = metrics["total_input_tokens"] + metrics["total_output_tokens"]
                col3.metric("Tokens Computed", f"{total_tokens:,}")

                # Transaction Ledger Matrix (With Speed TPS Mapping)
                st.markdown("### 📋 Activity Tracker")
                if data["audit_logs"]:
                    df = pd.DataFrame(data["audit_logs"])

                    df = df[[
                        "timestamp", "filename", "pages",
                        "tokens_per_sec", "latency_sec",
                        "cost_usd", "input_tokens", "output_tokens"
                    ]]

                    df.columns = [
                        "Date & Time", "Document", "Pages",
                        "Speed (TPS)", "Latency (s)",
                        "Cost ($)", "Input Tokens", "Output Tokens"
                    ]

                    st.dataframe(df, use_container_width=True, hide_index=True, height=240)
                else:
                    st.info("No documents have been processed under this key yet.")

            elif metrics_resp.status_code == 401:
                st.error("🔒 Authentication Error: Invalid API Key.")
            elif metrics_resp.status_code == 403:
                st.error("🚫 Access Forbidden: Account Deactivated.")
            elif metrics_resp.status_code == 402:
                st.error("💳 Quota Exceeded: Your monthly wallet balance has been exhausted.")

        except requests.exceptions.ConnectionError:
            st.error(f"🔌 Connection Interrupted: Cannot reach {api_url}. Ensure the OCR Pipeline is running.")
    else:
        st.info("🔑 Input API Key in the sidebar to load telemetry.")


with col_actions:
    st.header("📄 Batch Pipeline Ingestion")

    active_job = st.session_state.ocr_job
    if active_job:
        st.subheader("OCR Job Progress")
        if not api_key_input:
            st.warning("Enter the API key to resume polling this OCR job.")
        else:
            try:
                job_resp = requests.get(
                    f"{api_url}/v1/ocr/jobs/{active_job['job_id']}",
                    headers={"X-API-KEY": api_key_input},
                    timeout=10,
                )
                if job_resp.status_code != 200:
                    st.error(f"Job status failed ({job_resp.status_code}): {job_resp.text[:300]}")
                else:
                    job = job_resp.json()
                    st.session_state.ocr_job = job
                    total = int(job.get("pages_total", 0))
                    completed = int(job.get("pages_completed", 0))
                    status_text = job.get("status", "queued")
                    st.caption(f"{job.get('filename', 'document')} | {status_text}")
                    if total:
                        st.progress(min(completed / total, 1.0), text=f"{completed} / {total} pages")
                    else:
                        st.info("Queued for OCR processing...")
                    st.caption(f"Elapsed: {job.get('elapsed_seconds', 0)}s | Tokens: {job.get('input_tokens', 0) + job.get('output_tokens', 0):,}")

                    if status_text == "completed":
                        result_resp = requests.get(
                            f"{api_url}/v1/ocr/jobs/{job['job_id']}/result",
                            headers={"X-API-KEY": api_key_input},
                            timeout=30,
                        )
                        if result_resp.status_code == 200:
                            st.session_state.ocr_result = result_resp.text
                            st.session_state.ocr_result_filename = job.get("filename")
                            st.session_state.ocr_job = None
                            st.success(f"✅ OCR completed in {job.get('elapsed_seconds', 0)}s.")
                            st.rerun()
                        else:
                            st.error(f"Could not fetch completed OCR result: {result_resp.text[:300]}")
                    elif status_text == "failed":
                        st.session_state.ocr_job_error = job.get("error", "OCR job failed.")
                        st.session_state.ocr_job = None
                        st.error(f"OCR job failed: {st.session_state.ocr_job_error}")
                    else:
                        if job.get("page_failures"):
                            st.warning(f"Page failures: {len(job['page_failures'])}. The job will retain successful pages.")
                        time.sleep(OCR_STATUS_POLL_SECONDS)
                        st.rerun()
            except Exception as e:
                st.error(f"Job polling error: {e}")

    uploaded_file = st.file_uploader("Upload Legal Asset", type=["pdf", "jpg", "jpeg", "png"])
    is_pdf = uploaded_file is not None and uploaded_file.type == "application/pdf"

    if is_pdf:
        dpi_value = st.slider("Render DPI", min_value=120, max_value=350, value=200, step=10)
        mode_label = st.selectbox("Processing Mode", ["Serial", "Concurrent"], index=1)
        mode_value = mode_label.lower()

        if mode_value == "concurrent":
            max_concurrency = st.number_input("Max Concurrency", min_value=1, max_value=8, value=4, step=1)
            st.caption("Concurrent improves throughput when hardware allows it.")
        else:
            max_concurrency = None
            st.caption("Serial uses lower memory and is more stable.")
    else:
        dpi_value = None
        mode_value = None
        max_concurrency = None

    trigger_ocr = st.button("⚡ Execute OCR", use_container_width=True)

    if trigger_ocr and api_key_input and uploaded_file:
        with st.spinner("Submitting OCR job to DGX Spark..."):
            headers = {"X-API-KEY": api_key_input}
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

            params = {}
            if is_pdf:
                params["dpi"] = dpi_value
                params["mode"] = mode_value
                if mode_value == "concurrent" and max_concurrency is not None:
                    params["max_concurrency"] = int(max_concurrency)

            try:
                ocr_resp = requests.post(
                    f"{api_url}/v1/ocr/jobs",
                    headers=headers,
                    files=files,
                    params=params,
                    timeout=60,
                )

                if ocr_resp.status_code == 202:
                    st.session_state.ocr_job = ocr_resp.json()
                    st.session_state.ocr_result = None
                    st.session_state.ocr_result_filename = None
                    st.session_state.ocr_job_error = None
                    st.success("✅ OCR job submitted. Progress will update automatically.")
                    st.rerun()
                else:
                    st.error(f"OCR job submission failed ({ocr_resp.status_code}): {ocr_resp.text[:500]}")
            except Exception as e:
                st.error(f"Pipeline Fault: {str(e)}")

    if st.session_state.ocr_result:
        st.download_button(
            label="📥 Download Rendered Markdown",
            data=st.session_state.ocr_result,
            file_name=f"ocr_export_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=True
        )

        # --- N8N INTEGRATION ---
        st.markdown("### 🔗 Export Integrations")
        n8n_webhook_url = st.text_input(
            "n8n Webhook URL",
            placeholder="http://your-n8n-instance/webhook/ocr-ingest",
            help="Enter the production or test webhook URL from your n8n workflow."
        )

        if st.button("Upload to Vector Store via n8n", use_container_width=True, type="primary"):
            if not n8n_webhook_url:
                st.warning("Please provide a valid n8n Webhook URL.")
            else:
                with st.spinner("Pushing payload to n8n workflow..."):
                    payload = {
                        "filename": st.session_state.ocr_result_filename or (uploaded_file.name if uploaded_file else f"document_{int(time.time())}"),
                        "markdown_content": st.session_state.ocr_result,
                        "timestamp": time.time()
                    }
                    try:
                        n8n_resp = requests.post(n8n_webhook_url, json=payload, timeout=10)
                        if n8n_resp.status_code == 200:
                            st.success("✅ Successfully pushed to n8n pipeline!")
                        else:
                            st.error(f"n8n Rejected the payload ({n8n_resp.status_code}): {n8n_resp.text}")
                    except Exception as e:
                        st.error(f"Network error connecting to n8n: {str(e)}")

st.markdown("### 📝 Document Preview")
preview_left, preview_right = st.columns([1, 1], gap="large")

with preview_left:
    st.subheader("Raw Markdown")
    if st.session_state.ocr_result:
        st.text_area("", value=st.session_state.ocr_result, height=520)
    else:
        st.info("Run OCR to see the raw Markdown output.")

with preview_right:
    st.subheader("Rendered Markdown")
    if st.session_state.ocr_result:
                rendered_css = """
                <style>
                    .streamlit-expanderContent, .stMarkdown {
                        color: #e5e7eb;
                    }
                    .stMarkdown table {
                        width: 100%;
                        border-collapse: collapse;
                        margin: 12px 0 16px 0;
                        font-size: 0.9rem;
                    }
                    .stMarkdown th, .stMarkdown td {
                        border: 1px solid #2a2f3a;
                        padding: 6px 8px;
                        vertical-align: top;
                        text-align: left;
                    }
                    .stMarkdown th {
                        background: #151925;
                        font-weight: 600;
                    }
                    .stMarkdown hr {
                        border: 0;
                        border-top: 1px solid #2a2f3a;
                        margin: 12px 0;
                    }
                </style>
                """
                st.markdown(rendered_css, unsafe_allow_html=True)
                st.markdown(st.session_state.ocr_result, unsafe_allow_html=True)
    else:
        st.info("Run OCR to see the rendered Markdown.")
