# OCR Pipeline — NVIDIA DGX Spark

Production OCR service that converts PDFs and images to structured Markdown via **LightOnOCR-2-1B** running on NVIDIA CUDA GPU. Fresh deployment guide — includes llama.cpp setup from scratch.

---

## Table of Contents

- [Architecture](#architecture)
- [What's Included](#whats-included)
- [DGX Spark Specifications](#dgx-spark-specifications)
- [Setup Guide (From Scratch)](#setup-guide-from-scratch)
  - [Step 1: Transfer Deployment Files](#step-1-transfer-deployment-files)
  - [Step 2: Run the Setup Script](#step-2-run-the-setup-script)
  - [Step 3: Transfer Model Files](#step-3-transfer-model-files)
  - [Step 4: Configure Environment](#step-4-configure-environment)
  - [Step 5: Launch the Pipeline](#step-5-launch-the-pipeline)
  - [Step 6: Verify It's Working](#step-6-verify-its-working)
- [Running the Example UI](#running-the-example-ui)
- [API Reference](#api-reference)
  - [Health Check](#health-check---get-healthz)
  - [OCR Processing](#ocr-processing---post-v1ocr)
  - [Asynchronous OCR Jobs](#asynchronous-ocr-jobs)
  - [Usage Metrics](#usage-metrics---get-v1metrics)
  - [Swagger UI](#swagger-ui)
- [Configuration Reference](#configuration-reference)
  - [Model Server Settings](#model-server-settings)
  - [OCR API Settings](#ocr-api-settings)
  - [API Keys](#api-keys)
- [Managing the Pipeline](#managing-the-pipeline)
  - [Starting](#starting)
  - [Stopping](#stopping)
  - [Auto-Start on Boot](#auto-start-on-boot-systemd)
- [Differences from Mac Mini Deployment](#differences-from-mac-mini-deployment)
- [Troubleshooting](#troubleshooting)

---

## Architecture

```
┌────────────────────────────────────────────────────┐
│                  DGX Spark (GB10)                  │
│                                                    │
│   setup.sh (one-time)                              │
│     ├── Compiles llama.cpp with CUDA               │
│     ├── Creates Python venv                        │
│     └── Generates .env config                      │
│                                                    │
│   start.sh                                         │
│     ├── llama-server (CUDA GPU, port 8001)          │
│     │     Model: LightOnOCR-2-1B-ocr-soup-F16      │
│     │     MMPROJ: mmproj-F32                        │
│     │                                              │
│     └── FastAPI OCR Service (uvicorn, port 8080)    │
│           │                                        │
│           └── calls localhost:8001/v1/chat/...      │
└────────────────────────────────────────────────────┘
         ▲            ▲            ▲
    Team A UI     n8n Flow     curl/Python
 (example_ui.py)
```

**How it works:**
1. `setup.sh` (run once) compiles llama.cpp with CUDA support targeting the Blackwell GPU
2. `start.sh` launches the **llama-server** with full GPU offloading, then the **FastAPI service**
3. Any client on the local network can send documents to the API and receive structured Markdown
4. The model server is not exposed directly — all access goes through the FastAPI gateway

---

## What's Included

| File | Purpose |
|---|---|
| `setup.sh` | **One-time setup** — installs deps, compiles llama.cpp with CUDA, creates Python venv, generates `.env` |
| `ocr_service.py` | The core FastAPI application — handles file uploads, PDF rendering, model inference, Markdown post-processing, API key auth, usage tracking |
| `start.sh` | Launch script — starts both llama-server and FastAPI, polls for model readiness, handles graceful shutdown |
| `stop.sh` | Shutdown script — kills both services cleanly |
| `example_ui.py` | Streamlit-based web UI for testing — connects to the API from any machine on the network |
| `.env.example` | Configuration template with all available settings and defaults |
| `requirements.txt` | Python dependencies for the API service (6 packages) |

---

## DGX Spark Specifications

| Spec | Details |
|---|---|
| **GPU** | NVIDIA GB10 Grace Blackwell Superchip (Blackwell architecture) |
| **Tensor Cores** | 5th Generation |
| **CPU** | 20-core ARM (10x Cortex-X925 + 10x Cortex-A725) |
| **Memory** | 128 GB LPDDR5x unified (273 GB/s bandwidth) |
| **Storage** | 1 TB or 4 TB NVMe M.2 |
| **Connectivity** | Wi-Fi 7, 10 GbE, ConnectX-7 |
| **OS** | DGX OS (Ubuntu-based) |

**Key advantage over Mac Mini:** 128 GB unified memory allows loading significantly larger models. The CUDA ecosystem also provides broader compatibility with AI tooling.

---

## Setup Guide (From Scratch)

### Step 1: Transfer Deployment Files

From your workstation, copy the deployment folder to the DGX Spark:

```bash
scp -r dgx_spark_deploy/ user@<dgx-spark-ip>:~/ocr-pipeline/
```

Then SSH in:
```bash
ssh user@<dgx-spark-ip>
cd ~/ocr-pipeline
```

### Step 2: Run the Setup Script

The setup script handles everything automatically:

```bash
chmod +x setup.sh
sudo ./setup.sh
```

> **Note:** `sudo` is needed for `apt-get install` of build dependencies. The script will:
> 1. ✅ Verify NVIDIA drivers and CUDA toolkit
> 2. ✅ Install build tools (cmake, git, etc.)
> 3. ✅ Clone and compile llama.cpp with CUDA support (targets Blackwell `sm_120` architecture)
> 4. ✅ Create Python virtual environment and install packages
> 5. ✅ Generate `.env` with correct paths

**Expected output:**
```
============================================
  DGX Spark — OCR Pipeline Setup
============================================

[1/5] Checking system dependencies...
✓ NVIDIA GPU detected:
    NVIDIA GB10, 550.54, 128 GB
✓ CUDA Toolkit: 13.0
✓ Build dependencies installed

[2/5] Building llama.cpp with CUDA support...
  Cloning llama.cpp...
  Configuring CMake with CUDA (Blackwell architecture)...
  Target architecture: sm_120 (Blackwell)
  Compiling (this may take 5-10 minutes)...
✓ llama.cpp built successfully

[3/5] Checking model files...
  Model files not found...
  (instructions to transfer shown)

[4/5] Setting up Python environment...
✓ Python packages installed

[5/5] Configuring environment...
✓ .env generated with correct paths

============================================
  Setup Complete!
============================================
```

### Step 3: Transfer Model Files

The model files need to be transferred from the Mac Mini (or downloaded from Hugging Face):

**From the Mac Mini:**
```bash
# Run this ON the Mac Mini (or any machine that has the models)
scp /Volumes/Raid_NVMe/lmstudio_models/noctrex/LightOnOCR-2-1B-GGUF/LightOnOCR-2-1B-ocr-soup-F16.gguf \
    user@<dgx-spark-ip>:~/ocr-pipeline/models/

scp /Volumes/Raid_NVMe/lmstudio_models/noctrex/LightOnOCR-2-1B-GGUF/mmproj-F32.gguf \
    user@<dgx-spark-ip>:~/ocr-pipeline/models/
```

**Or download from Hugging Face:**
```bash
# On the DGX Spark
cd ~/ocr-pipeline/models
wget https://huggingface.co/noctrex/LightOnOCR-2-1B-GGUF/resolve/main/LightOnOCR-2-1B-ocr-soup-F16.gguf
wget https://huggingface.co/noctrex/LightOnOCR-2-1B-GGUF/resolve/main/mmproj-F32.gguf
```

### Step 4: Configure Environment

If `setup.sh` already generated `.env`, review it:

```bash
nano .env
```

Otherwise, copy the template:
```bash
cp .env.example .env
```

The paths should already be correct if you used `setup.sh`. See [Configuration Reference](#configuration-reference) for all options.

### Step 5: Launch the Pipeline

```bash
source .venv/bin/activate
./start.sh
```

### Large PDFs

The Streamlit UI submits PDF/image uploads as asynchronous OCR jobs. This avoids browser request timeouts for large documents: the OCR service stores the upload and result on the DGX, while the UI polls job progress until the result is ready.

Job files are retained for 24 hours by default under `OCR_JOB_DIR`. Configure `OCR_JOB_CONCURRENCY` to control the number of document jobs processed at once; keep the default of `1` for large PDFs to protect GPU memory.

You should see:

```
======== OCR Pipeline — DGX Spark ========
✓ llama-server: ./llama.cpp/build/bin/llama-server
✓ Model: LightOnOCR-2-1B-ocr-soup-F16.gguf
✓ MMPROJ: mmproj-F32.gguf
✓ GPU: NVIDIA GB10

Starting llama-server on :8001 (CUDA, 99 GPU layers)...
✓ llama-server PID 12345
Waiting for model to load (up to 120s)...
✓ Model ready (12s)
Starting FastAPI OCR service on :8080...

======== OCR Pipeline is LIVE ========
  API:    http://0.0.0.0:8080
  Docs:   http://0.0.0.0:8080/docs
  Health: http://0.0.0.0:8080/healthz
  Press Ctrl+C to stop.
======================================
```

### Step 6: Verify It's Working

From any machine on the network:

```bash
# 1. Health check
curl http://<dgx-spark-ip>:8080/healthz

# 2. Quick OCR test
curl -X POST http://<dgx-spark-ip>:8080/v1/ocr \
  -H "X-API-KEY: test_key_0000" \
  -F "file=@test_image.png" \
  -o output.md

# 3. Check output
cat output.md
```

---

## Running the Example UI

The `example_ui.py` is a Streamlit web dashboard you can run on **any machine** on the network.

### Setup (One-Time)

```bash
# On your workstation (NOT on the DGX Spark)
cd dgx_spark_deploy
pip install streamlit requests pandas
```

### Launch the UI

```bash
# Set the DGX Spark's IP address
OCR_API_URL=http://<dgx-spark-ip>:8080 streamlit run example_ui.py
```

Or launch and set the URL in the sidebar at runtime:
```bash
streamlit run example_ui.py
```

### Using the UI

1. **Set API Base URL** in the sidebar to `http://<dgx-spark-ip>:8080`
2. **Enter an API Key** (use `test_key_0000` for testing)
3. **Click "Check Connection"** to verify connectivity
4. **Upload a document** (PDF, JPG, or PNG)
5. **Configure settings** (DPI, processing mode) for PDFs
6. **Click "Execute OCR"** to process
7. **View results** in the preview pane (raw + rendered Markdown)
8. **Download** the output or **export to n8n**

---

## API Reference

All endpoints are accessible at `http://<dgx-spark-ip>:8080`.

### Health Check — `GET /healthz`

```bash
curl http://<dgx-spark-ip>:8080/healthz
```

**Response:**
```json
{
  "status": "healthy",
  "model_server": "ready",
  "model_name": "LightOnOCR-2-1B",
  "model_url": "http://127.0.0.1:8001/v1/chat/completions",
  "api_keys_loaded": 2,
  "timestamp": "2026-06-03T08:00:00.000000"
}
```

---

### OCR Processing — `POST /v1/ocr`

**Headers:**
| Header | Required | Description |
|---|---|---|
| `X-API-KEY` | Yes | API key for authentication |

**Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `file` | File | — | PDF, JPG, or PNG (multipart upload) |
| `dpi` | int | `200` | PDF render resolution (72–400) |
| `mode` | string | `concurrent` | `serial` or `concurrent` |
| `max_concurrency` | int | `4` | Max parallel pages (1–8) |

**Examples:**

```bash
# Image
curl -X POST http://<dgx-spark-ip>:8080/v1/ocr \
  -H "X-API-KEY: test_key_0000" \
  -F "file=@scan.png" -o result.md

# PDF with settings
curl -X POST "http://<dgx-spark-ip>:8080/v1/ocr?dpi=250&mode=concurrent" \
  -H "X-API-KEY: legal_team_secret_abc123" \
  -F "file=@contract.pdf" -o contract.md
```

**Python:**
```python
import requests

url = "http://<dgx-spark-ip>:8080/v1/ocr"
headers = {"X-API-KEY": "test_key_0000"}

with open("document.pdf", "rb") as f:
    response = requests.post(
        url, headers=headers,
        files={"file": ("document.pdf", f, "application/pdf")},
        params={"dpi": 200, "mode": "concurrent"}
    )

print(response.text)  # Markdown output
print(f"Speed: {response.headers['X-Tokens-Per-Sec']} tok/s")
```

**Response headers:**
| Header | Description |
|---|---|
| `X-Process-Time` | Processing seconds |
| `X-Total-Tokens` | Input + output tokens |
| `X-Tokens-Per-Sec` | Throughput |

---

### Asynchronous OCR Jobs

Use OCR jobs for large PDFs. Submission returns immediately, allowing the client to poll progress instead of holding one HTTP connection open for the entire OCR run.

| Endpoint | Purpose |
|---|---|
| `POST /v1/ocr/jobs` | Upload a PDF/image and receive a queued `job_id` |
| `GET /v1/ocr/jobs/{job_id}` | Read job status, page progress, tokens, and failures |
| `GET /v1/ocr/jobs/{job_id}/result` | Download Markdown once the job is complete |

```bash
# Submit a large PDF
curl -X POST "http://<dgx-spark-ip>:8080/v1/ocr/jobs?dpi=200&mode=concurrent" \
  -H "X-API-KEY: test_key_0000" \
  -F "file=@student_handbook.pdf"

# Poll status using the returned job_id
curl http://<dgx-spark-ip>:8080/v1/ocr/jobs/<job_id> \
  -H "X-API-KEY: test_key_0000"

# Download result after status is completed
curl http://<dgx-spark-ip>:8080/v1/ocr/jobs/<job_id>/result \
  -H "X-API-KEY: test_key_0000" -o handbook.md
```

Jobs store source files, metadata, and Markdown results under `OCR_JOB_DIR`. Queued/running jobs are recovered after service restart when their source file remains available.

---

### Usage Metrics — `GET /v1/metrics`

```bash
curl http://<dgx-spark-ip>:8080/v1/metrics -H "X-API-KEY: test_key_0000"
```

> Metrics are in-memory and reset on restart.

---

### Swagger UI

Interactive API docs: `http://<dgx-spark-ip>:8080/docs`

---

## Configuration Reference

All configuration via `.env` file.

### Model Server Settings

| Variable | Default | Description |
|---|---|---|
| `LLAMA_SERVER_PATH` | `./llama.cpp/build/bin/llama-server` | Path to llama-server binary |
| `MODEL_PATH` | `./models/LightOnOCR-2-1B-ocr-soup-F16.gguf` | Path to model weights |
| `MMPROJ_PATH` | `./models/mmproj-F32.gguf` | Path to vision projection weights |
| `GPU_LAYERS` | `99` | Layers offloaded to CUDA GPU (99 = all) |
| `CONTEXT_SIZE` | `16384` | Context window in tokens |
| `MODEL_PORT` | `8001` | llama-server port |
| `MODEL_HOST` | `0.0.0.0` | llama-server bind address |
| `MODEL_TEMP` | `0` | Sampling temperature (0 = deterministic) |
| `IMAGE_MIN_TOKENS` | `1024` | Minimum tokens for image processing |
| `MODEL_API_KEY` | `sk-ocr-layer1` | Bearer token for llama-server |
| `HEALTH_TIMEOUT` | `120` | Seconds to wait for model load |

### OCR API Settings

| Variable | Default | Description |
|---|---|---|
| `MODEL_URL` | `http://127.0.0.1:8001/v1/chat/completions` | Model endpoint URL |
| `MODEL_NAME` | `LightOnOCR-2-1B` | Model identifier |
| `API_PORT` | `8080` | FastAPI port |
| `API_HOST` | `0.0.0.0` | FastAPI bind address |
| `MAX_CONCURRENCY` | `4` | Default max parallel pages |
| `OCR_JOB_DIR` | `./ocr_jobs` | Disk location for queued uploads, job metadata, and Markdown results |
| `OCR_JOB_CONCURRENCY` | `1` | Concurrent document jobs; keep at 1 for large PDFs |
| `OCR_JOB_RETENTION_HOURS` | `24` | Retention period for completed/failed job files |
| `OCR_STATUS_POLL_SECONDS` | `2` | Streamlit UI polling interval |

### API Keys

Format in `.env`:
```
API_KEYS="key:user:monthly_cap:rate_per_page,key2:user2:cap:rate"
```

Add new keys by appending with a comma. Restart to apply changes.

---

## Managing the Pipeline

### Starting

```bash
cd ~/ocr-pipeline
source .venv/bin/activate
./start.sh
```

### Stopping

**Option A:** `Ctrl+C` in the terminal running `start.sh`

**Option B:** From another terminal:
```bash
cd ~/ocr-pipeline
./stop.sh
```

### Auto-Start on Boot (systemd)

Create a systemd service for automatic startup:

```bash
sudo tee /etc/systemd/system/ocr-pipeline.service << 'EOF'
[Unit]
Description=OCR Pipeline Service
After=network.target nvidia-persistenced.service

[Service]
Type=simple
User=<your-username>
WorkingDirectory=/home/<your-username>/ocr-pipeline
ExecStart=/bin/bash -lc '/home/<your-username>/ocr-pipeline/.venv/bin/activate && /home/<your-username>/ocr-pipeline/start.sh'
ExecStop=/home/<your-username>/ocr-pipeline/stop.sh
Restart=on-failure
RestartSec=10
Environment=PATH=/usr/local/cuda/bin:/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
EOF
```

Then enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ocr-pipeline
sudo systemctl start ocr-pipeline

# Check status
sudo systemctl status ocr-pipeline

# View logs
journalctl -u ocr-pipeline -f
```

---

## Differences from Mac Mini Deployment

| Aspect | Mac Mini M4 Pro | DGX Spark |
|---|---|---|
| **GPU** | Apple M4 Pro (Metal) | NVIDIA GB10 (CUDA) |
| **GPU framework** | Metal | CUDA |
| **Memory** | 24/48 GB unified | 128 GB unified |
| **OS** | macOS | DGX OS (Ubuntu) |
| **llama.cpp build** | `brew install` | Compiled from source with `-DGGML_CUDA=ON` |
| **Auto-start** | launchd plist | systemd service |
| **Setup** | Manual | `setup.sh` automates everything |
| **OCR service** | Identical code | Identical code |
| **API contract** | Same endpoints | Same endpoints |

The `ocr_service.py` and API contract are **identical** between both deployments. Any client built for one works with the other — just change the IP address.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `nvidia-smi not found` | NVIDIA drivers not installed | Install NVIDIA drivers: `sudo apt install nvidia-driver-550` |
| `nvcc not found` | CUDA toolkit missing | `sudo apt install nvidia-cuda-toolkit` |
| CMake build fails | Wrong CUDA arch | Try `cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=native` |
| `sm_120` not supported | Older CUDA toolkit | Upgrade to CUDA 13.x, or use `sm_100` or `sm_80` as fallback |
| Model timeout on startup | Model loading slowly | Increase `HEALTH_TIMEOUT` in `.env` |
| `Connection refused` on OCR | Port mismatch | Check `MODEL_PORT` in `.env` matches llama-server |
| 401 Unauthorized | Wrong API key | Verify `X-API-KEY` header matches a key in `API_KEYS` |
| Low throughput | GPU not being used | Run `nvidia-smi` during inference — GPU utilization should be >0% |
| `CUDA out of memory` | Context too large | Reduce `CONTEXT_SIZE` in `.env` |
| `example_ui.py` can't connect | Wrong IP / firewall | Check `API_HOST=0.0.0.0`, verify with `curl` from client |
