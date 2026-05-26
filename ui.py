import base64
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
if "last_pdf_bytes" not in st.session_state:
    st.session_state.last_pdf_bytes = None
if "last_pdf_name" not in st.session_state:
    st.session_state.last_pdf_name = None

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

        st.markdown("### Document Preview")
        preview_left, preview_right = st.columns(2, gap="large")

        with preview_left:
                st.subheader("Original PDF")
                if st.session_state.last_pdf_bytes:
                        pdf_base64 = base64.b64encode(st.session_state.last_pdf_bytes).decode("utf-8")
                        pdf_html = f"""
                        <div style='border:1px solid #ddd; height:600px; overflow:auto;'>
                            <div id='pdf-viewer'></div>
                        </div>
                        <script src='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js'></script>
                        <script>
                            const pdfData = "{pdf_base64}";
                            const pdfjsLib = window['pdfjs-dist/build/pdf'];
                            pdfjsLib.GlobalWorkerOptions.workerSrc =
                                'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

                            const container = document.getElementById('pdf-viewer');
                            const loadingTask = pdfjsLib.getDocument({ data: atob(pdfData) });

                            loadingTask.promise.then(async function(pdf) {{
                                for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {{
                                    const page = await pdf.getPage(pageNum);
                                    const viewport = page.getViewport({ scale: 1.25 });

                                    const canvas = document.createElement('canvas');
                                    const context = canvas.getContext('2d');
                                    canvas.height = viewport.height;
                                    canvas.width = viewport.width;
                                    canvas.style.display = 'block';
                                    canvas.style.margin = '0 auto 12px auto';

                                    container.appendChild(canvas);

                                    const renderContext = {{
                                        canvasContext: context,
                                        viewport: viewport
                                    }};
                                    await page.render(renderContext).promise;
                                }}
                            }});
                        </script>
                        """
                        st.components.v1.html(pdf_html, height=620, scrolling=True)
                else:
                        st.info("Upload a PDF to enable side-by-side preview.")

        with preview_right:
                st.subheader("Rendered Markdown")
                if st.session_state.ocr_result:
                        st.markdown(st.session_state.ocr_result)
                else:
                        st.info("Run OCR to see the rendered Markdown.")

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
                st.session_state.last_pdf_bytes = uploaded_file.getvalue()
                st.session_state.last_pdf_name = uploaded_file.name
            else:
                st.session_state.last_pdf_bytes = None
                st.session_state.last_pdf_name = None

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

    # --- DOCUMENT PREVIEW ---
    st.markdown("### Document Preview")
    preview_left, preview_right = st.columns(2, gap="large")

    with preview_left:
        st.subheader("Original PDF")
        if st.session_state.last_pdf_bytes:
            pdf_base64 = base64.b64encode(st.session_state.last_pdf_bytes).decode("utf-8")
            pdf_html = (
                f"<iframe src='data:application/pdf;base64,{pdf_base64}' "
                "width='100%' height='600' style='border:1px solid #ddd;'></iframe>"
            )
            st.components.v1.html(pdf_html, height=620, scrolling=True)
        else:
            st.info("Upload a PDF to enable side-by-side preview.")

    with preview_right:
        st.subheader("Rendered Markdown")
        if st.session_state.ocr_result:
            st.markdown(st.session_state.ocr_result)
        else:
            st.info("Run OCR to see the rendered Markdown.")