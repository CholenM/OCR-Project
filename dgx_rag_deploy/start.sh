#!/bin/bash
# ===========================================================================
# RAG Pipeline v3 — Launch Script (DGX Spark)
# ===========================================================================
# Starts RAG services:
#   1. Qdrant Docker container
#   2. llama-server (Embeddings) on :8002
#   3. llama-server (Chat LLM) on :8003
#   4. llama-server (Auto-tagging LLM) on :8005
#   5. FastAPI RAG service on :8081
#   6. Watch daemon (optional, if WATCH_ENABLED=true)
#
# Usage: ./start.sh
# ===========================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate venv
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Load .env
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

# Colors
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; NC='\033[0m'

# Defaults
LLAMA_SERVER_PATH="${LLAMA_SERVER_PATH:-./llama.cpp/build/bin/llama-server}"

EMBED_MODEL_PATH="${EMBED_MODEL_PATH:-./models/Qwen3-Embedding-8B-Q4_K_M.gguf}"
EMBED_PORT="${EMBED_PORT:-8002}"
EMBED_CTX_SIZE="${EMBED_CTX_SIZE:-8192}"
EMBED_API_KEY="${EMBED_API_KEY:-sk-embed-layer2}"

CHAT_MODEL_PATH="${CHAT_MODEL_PATH:-./models/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf}"
CHAT_PORT="${CHAT_PORT:-8003}"
CHAT_CTX_SIZE="${CHAT_CTX_SIZE:-32768}"
CHAT_API_KEY="${CHAT_API_KEY:-sk-chat-layer3}"

AUTOTAG_MODEL_PATH="${AUTOTAG_MODEL_PATH:-./models/Qwen3VL-8B-Instruct-F16.gguf}"
AUTOTAG_MMPROJ_PATH="${AUTOTAG_MMPROJ_PATH:-./models/mmproj-Qwen3VL-8B-Instruct-F16.gguf}"
AUTOTAG_PORT="${AUTOTAG_PORT:-8005}"
AUTOTAG_CTX_SIZE="${AUTOTAG_CTX_SIZE:-4096}"
AUTOTAG_API_KEY="${AUTOTAG_API_KEY:-sk-autotag-layer3b}"
AUTOTAG_MODEL_NAME="${AUTOTAG_MODEL_NAME:-Qwen3VL-8B-Instruct-Autotag}"

GPU_LAYERS="${GPU_LAYERS:-99}"
API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${API_PORT:-8081}"
WATCH_ENABLED="${WATCH_ENABLED:-false}"
PID_FILE="$SCRIPT_DIR/.pids"

RERANKER_MODEL_PATH="${RERANKER_MODEL_PATH:-./models/Qwen3-VL-Reranker-8B.Q8_0.gguf}"
RERANKER_PORT="${RERANKER_PORT:-8004}"
RERANKER_API_KEY="${RERANKER_API_KEY:-sk-rerank-layer4}"
RERANKER_ENABLED=false
if [ -f "$RERANKER_MODEL_PATH" ]; then
    RERANKER_ENABLED=true
fi

# Cleanup handler
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down RAG Pipeline...${NC}"
    if [ -f "$PID_FILE" ]; then
        while read -r pid; do
            kill -0 "$pid" 2>/dev/null && kill "$pid" 2>/dev/null || true
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi
    echo -e "${GREEN}RAG Pipeline shut down.${NC}"
}
trap cleanup EXIT INT TERM

# Validate
if [ ! -f "$LLAMA_SERVER_PATH" ]; then
    echo -e "${RED}ERROR: llama-server not found at $LLAMA_SERVER_PATH${NC}"
    echo "Run setup.sh first or update LLAMA_SERVER_PATH in .env"
    exit 1
fi
if [ ! -f "$AUTOTAG_MODEL_PATH" ]; then
    echo -e "${RED}ERROR: autotag model not found at $AUTOTAG_MODEL_PATH${NC}"
    echo "Run setup.sh first or update AUTOTAG_MODEL_PATH in .env"
    exit 1
fi

TOTAL_STEPS=5
if [ "$RERANKER_ENABLED" = "true" ]; then
    TOTAL_STEPS=$((TOTAL_STEPS + 1))
fi
if [ "$WATCH_ENABLED" = "true" ]; then
    TOTAL_STEPS=$((TOTAL_STEPS + 1))
fi

STEP=0

echo ""
echo "========================================================"
echo "  RAG Pipeline v3 — DGX Spark"
echo "========================================================"

if command -v nvidia-smi &>/dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
    echo -e "  GPU: ${GREEN}$GPU_NAME${NC}"
fi
echo ""

# Health poll
wait_for_server() {
    local name="$1" port="$2" max_wait="${3:-120}" elapsed=0
    while [ $elapsed -lt $max_wait ]; do
        if curl -s "http://127.0.0.1:$port/health" >/dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} $name ready on :$port"
            return 0
        fi
        sleep 2
        elapsed=$((elapsed + 2))
        echo -ne "  Waiting for $name... (${elapsed}s)\r"
    done
    echo -e "  ${RED}✗${NC} $name failed on :$port"
    return 1
}

# Create dirs
mkdir -p "$SCRIPT_DIR/logs"

# --- 1. Qdrant ---
STEP=$((STEP + 1))
echo -e "${CYAN}[${STEP}/${TOTAL_STEPS}]${NC} Starting Qdrant..."
if docker ps --format '{{.Names}}' | grep -q '^qdrant$'; then
    echo -e "  ${GREEN}✓${NC} Qdrant already running"
elif docker ps -a --format '{{.Names}}' | grep -q '^qdrant$'; then
    docker start qdrant >/dev/null 2>&1
    echo -e "  ${GREEN}✓${NC} Qdrant started"
else
    echo -e "  ${YELLOW}No Qdrant container found. Run setup.sh first.${NC}"
    exit 1
fi

# --- 2. Embedding Model ---
STEP=$((STEP + 1))
echo -e "${CYAN}[${STEP}/${TOTAL_STEPS}]${NC} Starting Embedding model on :${EMBED_PORT}..."
"$LLAMA_SERVER_PATH" \
    -m "$EMBED_MODEL_PATH" \
    --host 0.0.0.0 \
    --port "$EMBED_PORT" \
    -ngl "$GPU_LAYERS" \
    --ctx-size "$EMBED_CTX_SIZE" \
    --embeddings \
    -b 2048 \
    --threads 10 \
    --api-key "$EMBED_API_KEY" \
    > "$SCRIPT_DIR/logs/embed.log" 2>&1 &
echo $! >> "$PID_FILE"
wait_for_server "Embeddings" "$EMBED_PORT" 120

# --- 3. Chat LLM ---
STEP=$((STEP + 1))
echo -e "${CYAN}[${STEP}/${TOTAL_STEPS}]${NC} Starting Chat LLM on :${CHAT_PORT}..."
"$LLAMA_SERVER_PATH" \
    -m "$CHAT_MODEL_PATH" \
    --host 0.0.0.0 \
    --port "$CHAT_PORT" \
    -ngl "$GPU_LAYERS" \
    --ctx-size "$CHAT_CTX_SIZE" \
    --flash-attn on \
    --cache-type-k q8_0 \
    --cache-type-v q8_0 \
    -b 2048 \
    --threads 10 \
    --api-key "$CHAT_API_KEY" \
    > "$SCRIPT_DIR/logs/chat.log" 2>&1 &
echo $! >> "$PID_FILE"
wait_for_server "Chat LLM" "$CHAT_PORT" 180

# --- 4. Reranker (Optional — only if model exists) ---
if [ "$RERANKER_ENABLED" = "true" ]; then
    STEP=$((STEP + 1))
    echo -e "${CYAN}[${STEP}/${TOTAL_STEPS}]${NC} Starting Reranker on :${RERANKER_PORT}..."
    "$LLAMA_SERVER_PATH" \
        -m "$RERANKER_MODEL_PATH" \
        --host 0.0.0.0 \
        --port "$RERANKER_PORT" \
        -ngl "$GPU_LAYERS" \
        --ctx-size 8192 \
        --reranking \
        --threads 10 \
        --api-key "$RERANKER_API_KEY" \
        > "$SCRIPT_DIR/logs/reranker.log" 2>&1 &
    echo $! >> "$PID_FILE"
    wait_for_server "Reranker" "$RERANKER_PORT" 120
    export RERANKER_URL="http://127.0.0.1:${RERANKER_PORT}/v1/rerank"
fi

# --- 5. Auto-tagging LLM ---
STEP=$((STEP + 1))
echo -e "${CYAN}[${STEP}/${TOTAL_STEPS}]${NC} Starting Auto-tagging LLM on :${AUTOTAG_PORT}..."
"$LLAMA_SERVER_PATH" \
    -m "$AUTOTAG_MODEL_PATH" \
    --host 0.0.0.0 \
    --port "$AUTOTAG_PORT" \
    -ngl "$GPU_LAYERS" \
    --ctx-size "$AUTOTAG_CTX_SIZE" \
    --flash-attn on \
    --cache-type-k q8_0 \
    --cache-type-v q8_0 \
    -b 1024 \
    --threads 10 \
    --api-key "$AUTOTAG_API_KEY" \
    > "$SCRIPT_DIR/logs/autotag.log" 2>&1 &
echo $! >> "$PID_FILE"
wait_for_server "Auto-tagging LLM" "$AUTOTAG_PORT" 120

# --- 6. FastAPI ---
STEP=$((STEP + 1))
echo -e "${CYAN}[${STEP}/${TOTAL_STEPS}]${NC} Starting RAG service v4 on :${API_PORT}..."

export EMBED_MODEL_URL="http://127.0.0.1:${EMBED_PORT}/v1/embeddings"
export CHAT_MODEL_URL="http://127.0.0.1:${CHAT_PORT}/v1/chat/completions"
export AUTOTAG_MODEL_URL="http://127.0.0.1:${AUTOTAG_PORT}/v1/chat/completions"
export AUTOTAG_MODEL_NAME="$AUTOTAG_MODEL_NAME"
export AUTOTAG_API_KEY="$AUTOTAG_API_KEY"

uvicorn rag_service:app --host "$API_HOST" --port "$API_PORT" --log-level info &
echo $! >> "$PID_FILE"
sleep 2

# --- N. Watch Daemon (Optional) ---
if [ "$WATCH_ENABLED" = "true" ]; then
    STEP=$((STEP + 1))
    echo -e "${CYAN}[${STEP}/${TOTAL_STEPS}]${NC} Starting Watch daemon..."
    mkdir -p "${WATCH_DIR:-./inbox}" "${PROCESSED_DIR:-./processed}"
    python automation/watch_daemon.py > "$SCRIPT_DIR/logs/watch.log" 2>&1 &
    echo $! >> "$PID_FILE"
    echo -e "  ${GREEN}✓${NC} Watch daemon started (dir: ${WATCH_DIR:-./inbox})"
fi

echo ""
echo "========================================================"
echo -e "  ${GREEN}RAG Pipeline v4 is LIVE${NC}"
echo ""
echo "  RAG API:     http://${API_HOST}:${API_PORT}"
echo "  Swagger:     http://${API_HOST}:${API_PORT}/docs"
echo "  Health:      http://${API_HOST}:${API_PORT}/healthz"
echo ""
echo "  Embed Model: :${EMBED_PORT} (Qwen3-Embedding-8B)"
echo "  Chat Model:  :${CHAT_PORT} (Qwen3.6-35B-A3B)"
echo "  Autotag LLM: :${AUTOTAG_PORT} (${AUTOTAG_MODEL_NAME})"
if [ "$RERANKER_ENABLED" = "true" ]; then
echo "  Reranker:    :${RERANKER_PORT} (Qwen3-VL-Reranker-8B)"
else
echo "  Reranker:    DISABLED (model not found)"
fi
echo "  Qdrant:      :6333"
echo ""
echo "  OCR Pipeline: separate (~/ocr-pipeline/)"
if [ "$WATCH_ENABLED" = "true" ]; then
echo "  Watch Daemon: ACTIVE (${WATCH_DIR:-./inbox} → ${PROCESSED_DIR:-./processed})"
else
echo "  Watch Daemon: DISABLED (set WATCH_ENABLED=true in .env)"
fi
echo ""
echo "  Features: streaming, caching, HyDE, metadata-boosted BM25"
echo "  Defaults: rerank=OFF, agentic=OFF (fast mode)"
echo "  Press Ctrl+C to stop."
echo "========================================================"

# Keep alive
while true; do
    if [ -f "$PID_FILE" ]; then
        while read -r pid; do
            if ! kill -0 "$pid" 2>/dev/null; then
                echo -e "${RED}A service (PID $pid) exited unexpectedly.${NC}"
                cleanup
                exit 1
            fi
        done < "$PID_FILE"
    fi
    sleep 5
done
