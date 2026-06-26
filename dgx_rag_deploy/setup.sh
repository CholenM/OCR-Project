#!/bin/bash
# ===========================================================================
# RAG Pipeline — One-Time Setup Script (DGX Spark)
# ===========================================================================
# Sets up the RAG pipeline ALONGSIDE the existing ocr-pipeline.
# Reuses the llama.cpp binary already compiled in ~/ocr-pipeline/.
#
#   1. Symlinks llama-server from ~/ocr-pipeline/llama.cpp/
#   2. Downloads embedding + chat + autotag models
#   3. Starts Qdrant Docker container
#   4. Checks LibreOffice headless conversion support
#   5. Creates Python venv & installs dependencies
#
# Usage: sudo ./setup.sh
# ===========================================================================

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC}  $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
ok()    { echo -e "${GREEN}[ OK ]${NC}  $1"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $1"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Detect the real user (even when running with sudo)
REAL_USER=$(logname 2>/dev/null || echo "${SUDO_USER:-$(whoami)}")
OCR_PIPELINE_DIR="/home/$REAL_USER/ocr-pipeline"

echo ""
echo "========================================================"
echo "  RAG Pipeline — Setup (DGX Spark)"
echo "========================================================"
echo "  OCR Pipeline:  $OCR_PIPELINE_DIR"
echo "  RAG Pipeline:  $SCRIPT_DIR"
echo ""

# -------------------------------------------------------
# 1. Locate or compile llama.cpp
# -------------------------------------------------------
LLAMA_BIN="$OCR_PIPELINE_DIR/llama.cpp/build/bin/llama-server"

if [ -f "$LLAMA_BIN" ]; then
    ok "Found llama-server in ocr-pipeline: $LLAMA_BIN"
else
    warn "llama-server not found in $OCR_PIPELINE_DIR"
    info "Compiling llama.cpp locally..."

    apt-get update -qq
    apt-get install -y -qq build-essential cmake git >/dev/null 2>&1

    if [ -d "$SCRIPT_DIR/llama.cpp" ]; then
        cd "$SCRIPT_DIR/llama.cpp" && git pull
    else
        git clone https://github.com/ggerganov/llama.cpp.git "$SCRIPT_DIR/llama.cpp"
    fi

    cd "$SCRIPT_DIR/llama.cpp"
    mkdir -p build && cd build

    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DGGML_CUDA=ON \
        -DGGML_CUDA_F16=ON \
        -DGGML_NATIVE=OFF \
        -DCMAKE_CUDA_ARCHITECTURES=121 \
        -DCMAKE_C_COMPILER=gcc \
        -DCMAKE_CXX_COMPILER=g++ \
        -DCMAKE_CUDA_COMPILER=nvcc

    make -j"$(nproc)"
    LLAMA_BIN="$SCRIPT_DIR/llama.cpp/build/bin/llama-server"
    ok "llama.cpp compiled locally."
fi

cd "$SCRIPT_DIR"

# -------------------------------------------------------
# 2. Download models
# -------------------------------------------------------
mkdir -p "$SCRIPT_DIR/models"

info "Downloading RAG models..."

# Embedding Model
if [ -f "$SCRIPT_DIR/models/Qwen3-Embedding-8B-Q4_K_M.gguf" ]; then
    ok "Embedding model already present."
else
    info "Downloading Qwen3-Embedding-8B-Q4_K_M..."
    wget -q --show-progress -O "$SCRIPT_DIR/models/Qwen3-Embedding-8B-Q4_K_M.gguf" \
        "https://huggingface.co/Qwen/Qwen3-Embedding-8B-GGUF/resolve/main/Qwen3-Embedding-8B-Q4_K_M.gguf"
    ok "Embedding model downloaded."
fi

# Chat LLM
if [ -f "$SCRIPT_DIR/models/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf" ]; then
    ok "Chat LLM already present."
else
    info "Downloading Qwen3.6-35B-A3B-Uncensored-Q4_K_M..."
    wget -q --show-progress -O "$SCRIPT_DIR/models/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf" \
        "https://huggingface.co/HauhauCS/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive/resolve/main/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf"
    ok "Chat LLM downloaded."
fi

# Auto-tagging LLM
if [ -f "$SCRIPT_DIR/models/Qwen3VL-8B-Instruct-F16.gguf" ]; then
    ok "Auto-tagging model already present."
else
    info "Downloading Qwen3-VL-8B-Instruct autotag model..."
    wget -q --show-progress -O "$SCRIPT_DIR/models/Qwen3VL-8B-Instruct-F16.gguf" \
        "https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct-GGUF/resolve/main/Qwen3VL-8B-Instruct-F16.gguf"
    ok "Auto-tagging model downloaded."
fi

# Auto-tagging projector (downloaded for completeness; not loaded by start.sh for text-only tagging)
if [ -f "$SCRIPT_DIR/models/mmproj-Qwen3VL-8B-Instruct-F16.gguf" ]; then
    ok "Auto-tagging mmproj already present."
else
    info "Downloading Qwen3-VL-8B-Instruct autotag mmproj..."
    wget -q --show-progress -O "$SCRIPT_DIR/models/mmproj-Qwen3VL-8B-Instruct-F16.gguf" \
        "https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct-GGUF/resolve/main/mmproj-Qwen3VL-8B-Instruct-F16.gguf"
    ok "Auto-tagging mmproj downloaded."
fi

# -------------------------------------------------------
# 3. Qdrant Docker container
# -------------------------------------------------------
info "Setting up Qdrant vector database..."
if docker ps --format '{{.Names}}' | grep -q '^qdrant$'; then
    ok "Qdrant container already running."
elif docker ps -a --format '{{.Names}}' | grep -q '^qdrant$'; then
    docker start qdrant
    ok "Qdrant container started."
else
    docker run -d \
        --name qdrant \
        --restart unless-stopped \
        -p 6333:6333 \
        -p 6334:6334 \
        -v "$SCRIPT_DIR/qdrant_data:/qdrant/storage" \
        qdrant/qdrant
    ok "Qdrant container created and running."
fi

# -------------------------------------------------------
# 4. LibreOffice document conversion
# -------------------------------------------------------
info "Checking LibreOffice headless converter..."
if command -v soffice >/dev/null 2>&1 || command -v libreoffice >/dev/null 2>&1; then
    ok "LibreOffice found."
else
    warn "LibreOffice not found. Installing libreoffice..."
    apt-get update -qq
    apt-get install -y -qq libreoffice >/dev/null 2>&1 || \
        fail "LibreOffice install failed. Install it manually or set LIBREOFFICE_BIN in .env."
    ok "LibreOffice installed."
fi

# -------------------------------------------------------
# 5. Python virtual environment
# -------------------------------------------------------
info "Setting up Python environment..."
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    python3 -m venv "$SCRIPT_DIR/.venv"
fi
source "$SCRIPT_DIR/.venv/bin/activate"
pip install --quiet --upgrade pip
pip install --quiet -r "$SCRIPT_DIR/requirements.txt"
ok "Python environment ready."

# -------------------------------------------------------
# 5. Generate .env
# -------------------------------------------------------
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    # Write .env with the correct llama-server path
    sed "s|LLAMA_SERVER_PATH=.*|LLAMA_SERVER_PATH=\"$LLAMA_BIN\"|" \
        "$SCRIPT_DIR/.env.example" > "$SCRIPT_DIR/.env"
    ok "Created .env (llama-server path: $LLAMA_BIN)"
else
    ok ".env already exists."
fi

ensure_env_var() {
    local key="$1"
    local value="$2"
    local old_pattern="${3:-}"
    if ! grep -q "^${key}=" "$SCRIPT_DIR/.env"; then
        echo "${key}=${value}" >> "$SCRIPT_DIR/.env"
        ok "Added ${key} to .env"
    elif [ -n "$old_pattern" ] && grep -Eq "^${key}=.*${old_pattern}" "$SCRIPT_DIR/.env"; then
        sed -i "s|^${key}=.*|${key}=${value}|" "$SCRIPT_DIR/.env"
        ok "Updated ${key} in .env"
    fi
}

ensure_env_var "AUTOTAG_MODEL_PATH" '"./models/Qwen3VL-8B-Instruct-F16.gguf"' 'Qwen3\.5-4B|HauhauCS'
ensure_env_var "AUTOTAG_MMPROJ_PATH" '"./models/mmproj-Qwen3VL-8B-Instruct-F16.gguf"' 'Qwen3\.5-4B|HauhauCS'
ensure_env_var "AUTOTAG_PORT" '"8005"'
ensure_env_var "AUTOTAG_CTX_SIZE" '"4096"'
ensure_env_var "AUTOTAG_API_KEY" '"sk-autotag-layer3b"'
ensure_env_var "AUTOTAG_MODEL_NAME" '"Qwen3VL-8B-Instruct-Autotag"' 'Qwen3\.5-4B-Autotag'
ensure_env_var "AUTOTAG_MAX_CHARS" '"800"' '"?3000"?'
ensure_env_var "AUTOTAG_CACHE_SIZE" '"512"'

# Fix ownership
if [ -n "$REAL_USER" ]; then
    chown -R "$REAL_USER":"$REAL_USER" "$SCRIPT_DIR/.venv" "$SCRIPT_DIR/models" 2>/dev/null || true
    chown -R "$REAL_USER":"$REAL_USER" "$SCRIPT_DIR/qdrant_data" 2>/dev/null || true
    [ -f "$SCRIPT_DIR/.env" ] && chown "$REAL_USER":"$REAL_USER" "$SCRIPT_DIR/.env" 2>/dev/null || true
fi

echo ""
echo "========================================================"
echo -e "  ${GREEN}RAG Pipeline setup complete!${NC}"
echo ""
echo "  Embedding model: $SCRIPT_DIR/models/Qwen3-Embedding-8B-Q4_K_M.gguf"
echo "  Chat LLM:        $SCRIPT_DIR/models/Qwen3.6-35B-A3B-...-Q4_K_M.gguf"
echo "  Auto-tag LLM:    $SCRIPT_DIR/models/Qwen3VL-8B-Instruct-F16.gguf"
echo "  llama-server:    $LLAMA_BIN"
echo "  Qdrant:          http://localhost:6333"
echo ""
echo "  Next: chmod +x start.sh stop.sh && ./start.sh"
echo "========================================================"
