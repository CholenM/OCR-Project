import os
import base64
import time
from datetime import datetime
from io import BytesIO
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status, Header
from fastapi.responses import Response
import fitz  # PyMuPDF
import requests

app = FastAPI(title="Enterprise Legal OCR Gateway API")

# --- LAYER 1 CONFIGURATION (LM STUDIO) ---
LM_STUDIO_URL = "http://192.168.1.91:0001/v1/chat/completions"
LM_STUDIO_API_KEY = "sk-ocr-layer1"
# --- BUSINESS LOGIC: ENTERPRISE DATABASE SCHEMA ---
API_KEY_DB = {
    "legal_team_secret_abc123": {
        "user": "Legal Department",
        "active": True,
        "monthly_spend_cap": 50.00,
        "current_month_spend": 0.00,
        "rate_per_page": 0.05,
        "metrics": {
            "total_documents": 0,
            "total_pages_processed": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
        },
        "audit_logs": []
    },
    "test_key_0000": {
        "user": "Internal Benchmark Test",
        "active": True,
        "monthly_spend_cap": 1.00,
        "current_month_spend": 0.00,
        "rate_per_page": 0.00,
        "metrics": {
            "total_documents": 0,
            "total_pages_processed": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
        },
        "audit_logs": []
    }
}

# --- SECURITY & FINANCIAL GUARDRAILS ---
async def verify_api_key(x_api_key: str = Header(..., description="Custom API Key for tracking")):
    if x_api_key not in API_KEY_DB:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid API Key"
        )
    
    key_info = API_KEY_DB[x_api_key]
    
    if not key_info["active"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account Deactivated.")
        
    if key_info["current_month_spend"] >= key_info["monthly_spend_cap"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Quota Exceeded: Monthly spend cap reached. Please contact IT to increase budget."
        )
    
    return x_api_key

# --- CORE INFERENCE CALL WITH TELEMETRY ---
def query_lm_studio_ocr(base64_image: str):
    payload = {
        "model": "qwen3vl-2b-instruct",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a legal document parsing expert. Convert the provided image "
                    "into structurally accurate Markdown text. Reconstruct data tables, "
                    "preserve formatting indicators, and output ONLY the raw Markdown."
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all text and structure into Markdown."},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }}
                ]
            }
        ],
        "temperature": 0.0
    }

    try:
        response = requests.post(
            LM_STUDIO_URL,
            json=payload,
            headers={"Authorization": f"Bearer {LM_STUDIO_API_KEY}"},
            timeout=120
        )
        if response.status_code == 200:
            result = response.json()
            text = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            prompt_toks = usage.get("prompt_tokens", 0)
            comp_toks = usage.get("completion_tokens", 0)
            return text, prompt_toks, comp_toks
        else:
            return f"\nError (Status {response.status_code}): {response.text}\n", 0, 0
    except Exception as e:
        return f"\nLocal Engine Failed: {str(e)}\n", 0, 0
    
# --- OCR PIPELINE ENDPOINT ---
@app.post("/v1/ocr", response_class=Response)
async def process_document(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    start_time = time.time()
    file_bytes = await file.read()
    content_type = file.content_type
    
    generated_markdown = ""
    session_pages = 0
    session_in_tokens = 0
    session_out_tokens = 0
    
    try:
        if content_type == "application/pdf":
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for index, page in enumerate(doc):
                session_pages += 1
                generated_markdown += f"\n<!-- SECTION: PAGE {index + 1} -->\n"
                
                pix = page.get_pixmap(dpi=200)
                jpeg_bytes = pix.tobytes("jpeg")
                base64_str = base64.b64encode(jpeg_bytes).decode("utf-8")
                
                text, p_tok, c_tok = query_lm_studio_ocr(base64_str)
                generated_markdown += text + "\n"
                session_in_tokens += p_tok
                session_out_tokens += c_tok
                
            doc.close()
                
        elif content_type in ["image/jpeg", "image/jpg", "image/png"]:
            session_pages += 1
            base64_str = base64.b64encode(file_bytes).decode("utf-8")
            text, p_tok, c_tok = query_lm_studio_ocr(base64_str)
            generated_markdown += text
            session_in_tokens += p_tok
            session_out_tokens += c_tok
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported File Format.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing Exception: {str(e)}")

    # CALCULATE HARDWARE TELEMETRY
    execution_time = round(time.time() - start_time, 2)
    total_tokens = session_in_tokens + session_out_tokens
    tokens_per_sec = round(total_tokens / execution_time, 2) if execution_time > 0 else 0
    session_cost = session_pages * API_KEY_DB[api_key]["rate_per_page"]

    # UPDATE ENTERPRISE DATABASE STATE
    db_ref = API_KEY_DB[api_key]
    db_ref["current_month_spend"] += session_cost
    db_ref["metrics"]["total_documents"] += 1
    db_ref["metrics"]["total_pages_processed"] += session_pages
    db_ref["metrics"]["total_input_tokens"] += session_in_tokens
    db_ref["metrics"]["total_output_tokens"] += session_out_tokens
    
    # APPEND TO AUDIT LEDGER WITH TPS MAPPING
    db_ref["audit_logs"].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": file.filename,
        "pages": session_pages,
        "input_tokens": session_in_tokens,
        "output_tokens": session_out_tokens,
        "latency_sec": execution_time,
        "tokens_per_sec": tokens_per_sec,
        "cost_usd": session_cost
    })
    
    return Response(
        content=generated_markdown,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename={file.filename}.md",
            "X-Process-Time": str(execution_time),
            "X-Total-Tokens": str(total_tokens),
            "X-Tokens-Per-Sec": str(tokens_per_sec)
        }
    )

@app.get("/v1/metrics")
async def get_billing_metrics(api_key: str = Depends(verify_api_key)):
    return API_KEY_DB[api_key]