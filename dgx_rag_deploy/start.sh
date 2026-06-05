#!/bin/bash
# ===========================================================================
# RAG Pipeline — Launch Script (DGX Spark)
# ===========================================================================
# Starts RAG services only (no OCR — that's in ~/ocr-pipeline/):
#   1. Qdrant Docker container
#   2. llama-server (Embeddings) on :8002
#   3. llama-server (Chat LLM) on :8003
#   4. FastAPI RAG service on :8081
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

GPU_LAYERS="${GPU_LAYERS:-99}"
API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${API_PORT:-8081}"
PID_FILE="$SCRIPT_DIR/.pids"

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

echo ""
echo "========================================================"
echo "  RAG Pipeline — DGX Spark"
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

# Create logs dir
mkdir -p "$SCRIPT_DIR/logs"

# --- 1. Qdrant ---
echo -e "${CYAN}[1/4]${NC} Starting Qdrant..."
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
echo -e "${CYAN}[2/4]${NC} Starting Embedding model on :${EMBED_PORT}..."
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
echo -e "${CYAN}[3/4]${NC} Starting Chat LLM on :${CHAT_PORT}..."
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

# --- 4. FastAPI ---
echo -e "${CYAN}[4/4]${NC} Starting RAG service on :${API_PORT}..."

export EMBED_MODEL_URL="http://127.0.0.1:${EMBED_PORT}/v1/embeddings"
export CHAT_MODEL_URL="http://127.0.0.1:${CHAT_PORT}/v1/chat/completions"

uvicorn rag_service:app --host "$API_HOST" --port "$API_PORT" --log-level info &
echo $! >> "$PID_FILE"
sleep 2

echo ""
echo "========================================================"
echo -e "  ${GREEN}RAG Pipeline is LIVE${NC}"
echo ""
echo "  RAG API:     http://${API_HOST}:${API_PORT}"
echo "  Swagger:     http://${API_HOST}:${API_PORT}/docs"
echo "  Health:      http://${API_HOST}:${API_PORT}/healthz"
echo ""
echo "  Embed Model: :${EMBED_PORT} (Qwen3-Embedding-8B)"
echo "  Chat Model:  :${CHAT_PORT} (Qwen3.6-35B-A3B)"
echo "  Qdrant:      :6333"
echo ""
echo "  OCR Pipeline: separate (~/ocr-pipeline/)"
echo ""
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
