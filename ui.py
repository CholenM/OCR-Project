import streamlit as st
import requests
import time
import pandas as pd

# --- APPMANAGER CONFIGURATION ---
FASTAPI_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="OCR Control Center", page_icon="", layout="wide")
st.title("OCR Dashboard")
st.markdown("---")

# --- SIDEBAR CONTROL UNIT ---
st.sidebar.header("Authentication")
api_key_input = st.sidebar.text_input("Enter Service API Key", type="password")
st.sidebar.markdown("### Developer Sandbox Keys")
st.sidebar.code("legal_team_secret_abc123\ntest_key_0000", language="text")

if "ocr_result" not in st.session_state:
    st.session_state.ocr_result = None

# --- VIEW SPLIT LAYOUT ---
col_dashboard, col_actions = st.columns([1.3, 1], gap="large")

with col_dashboard:
    st.header("API Tracking Usage")
    
    if api_key_input:
        headers = {"X-API-KEY": api_key_input}
        try:
            metrics_resp = requests.get(f"{FASTAPI_BASE_URL}/v1/metrics", headers=headers)
            
            if metrics_resp.status_code == 200:
                data = metrics_resp.json()
                metrics = data["metrics"]
                
                st.subheader(f"Identity: {data['user']}")
                
                # Financial Guardrails UI
                st.markdown("##### API Usage")
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
                st.markdown("### Activity Tracker")
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
                st.error("Authentication Error: Invalid API Key.")
            elif metrics_resp.status_code == 403:
                st.error("Access Forbidden: Account Deactivated.")
            elif metrics_resp.status_code == 402:
                st.error("Quota Exceeded: Your monthly wallet balance has been exhausted.")
                
        except requests.exceptions.ConnectionError:
            st.error("Connection Interrupted: Ensure the FastAPI service is running on port 8000.")
    else:
        st.info("Input API Key in the sidebar to load telemetry.")


with col_actions:
    st.header("Batch Pipeline Ingestion")

    uploaded_file = st.file_uploader("Upload Legal Asset", type=["pdf", "jpg", "png"])
    is_pdf = uploaded_file is not None and uploaded_file.type == "application/pdf"

    if is_pdf:
        dpi_value = st.slider("Render DPI", min_value=120, max_value=350, value=200, step=10)
        mode_label = st.selectbox("Processing Mode", ["Serial", "Concurrent"], index=1)
        mode_value = mode_label.lower()

        if mode_value == "concurrent":
            max_concurrency = st.number_input("Max Concurrency", min_value=1, max_value=8, value=3, step=1)
            st.caption("Concurrent improves throughput when hardware allows it.")
        else:
            max_concurrency = None
            st.caption("Serial uses lower memory and is more stable.")
    else:
        dpi_value = None
        mode_value = None
        max_concurrency = None

    trigger_ocr = st.button("Execute OCR", use_container_width=True)
    
    if trigger_ocr and api_key_input and uploaded_file:
        with st.spinner("Streaming directly to Local GPU Pipeline..."):
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
                    f"{FASTAPI_BASE_URL}/v1/ocr",
                    headers=headers,
                    files=files,
                    params=params
                )
                
                if ocr_resp.status_code == 200:
                    st.session_state.ocr_result = ocr_resp.text
                    
                    latency = float(ocr_resp.headers.get("X-Process-Time", 0))
                    tps = float(ocr_resp.headers.get("X-Tokens-Per-Sec", 0))
                    
                    st.success(f"Successfully processed in {latency}s! Hardware speed: {tps:.1f} Tokens/Sec.")
                    st.rerun()
                else:
                    st.error(f"Inference Failure ({ocr_resp.status_code}): {ocr_resp.json().get('detail', ocr_resp.text)}")
            except Exception as e:
                st.error(f"Pipeline Fault: {str(e)}")

    if st.session_state.ocr_result:
        st.download_button(
            label="Download Rendered Markdown",
            data=st.session_state.ocr_result,
            file_name=f"legal_export_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=True
        )

st.markdown("### Document Preview")
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
                rendered_lower = st.session_state.ocr_result.lower()
                if "<table" in rendered_lower or "<tr" in rendered_lower or "<td" in rendered_lower:
            html_payload = f"""
                        <style>
                            .ocr-render {{
                                font-family: "Segoe UI", Arial, sans-serif;
                                color: #e5e7eb;
                                background: #0f1115;
                                padding: 16px;
                                line-height: 1.5;
                                font-size: 0.95rem;
                            }}
                            .ocr-render table {{
                                width: 100%;
                                border-collapse: collapse;
                                margin: 12px 0 16px 0;
                                font-size: 0.9rem;
                            }}
                            .ocr-render th, .ocr-render td {{
                                border: 1px solid #2a2f3a;
                                padding: 6px 8px;
                                vertical-align: top;
                                text-align: left;
                            }}
                            .ocr-render th {{
                                background: #151925;
                                font-weight: 600;
                            }}
                            .ocr-render hr {{
                                border: 0;
                                border-top: 1px solid #2a2f3a;
                                margin: 12px 0;
                            }}
                            .ocr-render p {{
                                margin: 8px 0;
                            }}
                        </style>
                        <div class="ocr-render">
              {st.session_state.ocr_result}
            </div>
            """
            st.components.v1.html(html_payload, height=520, scrolling=True)
        else:
            st.markdown(st.session_state.ocr_result, unsafe_allow_html=True)
    else:
        st.info("Run OCR to see the rendered Markdown.")
