#!/bin/bash
# OCR Pipeline — Launch Script (DGX Spark)
# Starts llama-server (CUDA) + FastAPI OCR service.
# Usage: ./start.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate venv if present
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Load .env
if [ -f .env ]; then
    set -a; source .env; set +a
else
    echo "ERROR: .env not found. Run ./setup.sh first or copy .env.example to .env."
    exit 1
fi

# Defaults
LLAMA_SERVER_PATH="${LLAMA_SERVER_PATH:-$SCRIPT_DIR/llama.cpp/build/bin/llama-server}"
MODEL_PATH="${MODEL_PATH:-}"
MMPROJ_PATH="${MMPROJ_PATH:-}"
GPU_LAYERS="${GPU_LAYERS:-99}"
CONTEXT_SIZE="${CONTEXT_SIZE:-16384}"
MODEL_PORT="${MODEL_PORT:-8001}"
MODEL_HOST="${MODEL_HOST:-0.0.0.0}"
MODEL_TEMP="${MODEL_TEMP:-0}"
IMAGE_MIN_TOKENS="${IMAGE_MIN_TOKENS:-1024}"
MODEL_API_KEY="${MODEL_API_KEY:-sk-ocr-layer1}"
API_PORT="${API_PORT:-8080}"
HEALTH_TIMEOUT="${HEALTH_TIMEOUT:-120}"

GREEN='\033[0;32m'; RED='\033[0;31m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'
LLAMA_PID=""; API_PID=""

cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down OCR Pipeline...${NC}"
    [ -n "$API_PID" ] && kill -0 "$API_PID" 2>/dev/null && kill "$API_PID" 2>/dev/null && wait "$API_PID" 2>/dev/null || true
    [ -n "$LLAMA_PID" ] && kill -0 "$LLAMA_PID" 2>/dev/null && kill "$LLAMA_PID" 2>/dev/null && wait "$LLAMA_PID" 2>/dev/null || true
    rm -f "$SCRIPT_DIR/.pids" 2>/dev/null
    echo -e "${GREEN}OCR Pipeline shut down cleanly.${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# Validate
echo -e "${CYAN}======== OCR Pipeline — DGX Spark ========${NC}"

# Check llama-server
if [ ! -x "$LLAMA_SERVER_PATH" ] && ! command -v "$LLAMA_SERVER_PATH" &>/dev/null; then
    echo -e "${RED}ERROR: llama-server not found at: $LLAMA_SERVER_PATH${NC}"
    echo "  Run ./setup.sh first to build llama.cpp"
    exit 1
fi
echo -e "${GREEN}✓${NC} llama-server: $LLAMA_SERVER_PATH"

# Check model files
[ -f "$MODEL_PATH" ] || { echo -e "${RED}ERROR: Model not found: $MODEL_PATH${NC}"; exit 1; }
[ -f "$MMPROJ_PATH" ] || { echo -e "${RED}ERROR: MMPROJ not found: $MMPROJ_PATH${NC}"; exit 1; }
echo -e "${GREEN}✓${NC} Model: $(basename "$MODEL_PATH")"
echo -e "${GREEN}✓${NC} MMPROJ: $(basename "$MMPROJ_PATH")"

# Check NVIDIA GPU
if command -v nvidia-smi &>/dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
    echo -e "${GREEN}✓${NC} GPU: $GPU_NAME"
else
    echo -e "${YELLOW}WARNING: nvidia-smi not found — GPU status unknown${NC}"
fi

command -v python3 &>/dev/null || { echo -e "${RED}ERROR: python3 not found${NC}"; exit 1; }
echo ""

# Start llama-server (CUDA)
echo -e "${CYAN}Starting llama-server on :$MODEL_PORT (CUDA, ${GPU_LAYERS} GPU layers)...${NC}"
"$LLAMA_SERVER_PATH" \
    -m "$MODEL_PATH" \
    --mmproj "$MMPROJ_PATH" \
    --host "$MODEL_HOST" \
    --port "$MODEL_PORT" \
    -ngl "$GPU_LAYERS" \
    --ctx-size "$CONTEXT_SIZE" \
    --temp "$MODEL_TEMP" \
    --image-min-tokens "$IMAGE_MIN_TOKENS" \
    --api-key "$MODEL_API_KEY" \
    2>&1 | sed "s/^/  [llama] /" &
LLAMA_PID=$!
echo -e "${GREEN}✓${NC} llama-server PID $LLAMA_PID"

# Wait for health
echo -e "${CYAN}Waiting for model to load (up to ${HEALTH_TIMEOUT}s)...${NC}"
ELAPSED=0
while [ $ELAPSED -lt "$HEALTH_TIMEOUT" ]; do
    curl -sf "http://127.0.0.1:$MODEL_PORT/health" >/dev/null 2>&1 && { echo -e "${GREEN}✓${NC} Model ready (${ELAPSED}s)"; break; }
    kill -0 "$LLAMA_PID" 2>/dev/null || { echo -e "${RED}llama-server crashed!${NC}"; exit 1; }
    sleep 2; ELAPSED=$((ELAPSED + 2))
done
[ $ELAPSED -ge "$HEALTH_TIMEOUT" ] && { echo -e "${RED}Model server timeout${NC}"; exit 1; }

# Start FastAPI
echo -e "${CYAN}Starting FastAPI OCR service on :$API_PORT...${NC}"
cd "$SCRIPT_DIR"
python3 ocr_service.py &
API_PID=$!
echo "LLAMA_PID=$LLAMA_PID" > "$SCRIPT_DIR/.pids"
echo "API_PID=$API_PID" >> "$SCRIPT_DIR/.pids"

sleep 3
echo ""
echo -e "${GREEN}======== OCR Pipeline is LIVE ========${NC}"
echo -e "  API:    http://0.0.0.0:$API_PORT"
echo -e "  Docs:   http://0.0.0.0:$API_PORT/docs"
echo -e "  Health: http://0.0.0.0:$API_PORT/healthz"
echo -e "  Press ${YELLOW}Ctrl+C${NC} to stop."
echo -e "${GREEN}======================================${NC}"

# Keep alive — poll both processes
while true; do
    if ! kill -0 "$LLAMA_PID" 2>/dev/null; then
        echo -e "${RED}llama-server exited unexpectedly.${NC}"
        break
    fi
    if ! kill -0 "$API_PID" 2>/dev/null; then
        echo -e "${RED}FastAPI exited unexpectedly.${NC}"
        break
    fi
    sleep 5
done
cleanup
