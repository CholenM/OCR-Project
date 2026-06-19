#!/bin/bash
# ===========================================================================
# DGX Spark — One-Time Setup Script
# ===========================================================================
# Installs llama.cpp with CUDA support, sets up Python environment,
# and downloads model files.
#
# Usage: ./setup.sh
# ===========================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'; RED='\033[0;31m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}  DGX Spark — OCR Pipeline Setup${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# ===========================================================================
# Step 1: System Dependencies
# ===========================================================================
echo -e "${CYAN}[1/5] Checking system dependencies...${NC}"

# Check for NVIDIA GPU
if command -v nvidia-smi &>/dev/null; then
    echo -e "${GREEN}✓${NC} NVIDIA GPU detected:"
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>/dev/null | sed 's/^/    /'
else
    echo -e "${RED}ERROR: nvidia-smi not found. NVIDIA drivers must be installed.${NC}"
    exit 1
fi

# Check for CUDA toolkit
if command -v nvcc &>/dev/null; then
    CUDA_VER=$(nvcc --version | grep "release" | sed 's/.*release //' | sed 's/,.*//')
    echo -e "${GREEN}✓${NC} CUDA Toolkit: $CUDA_VER"
else
    echo -e "${YELLOW}WARNING: nvcc not found. Installing CUDA toolkit...${NC}"
    sudo apt-get update
    sudo apt-get install -y nvidia-cuda-toolkit
fi

# Install build dependencies
echo -e "${CYAN}  Installing build tools...${NC}"
sudo apt-get update -qq
sudo apt-get install -y -qq build-essential cmake git curl python3 python3-venv python3-pip
echo -e "${GREEN}✓${NC} Build dependencies installed"
echo ""

# ===========================================================================
# Step 2: Build llama.cpp with CUDA
# ===========================================================================
echo -e "${CYAN}[2/5] Building llama.cpp with CUDA support...${NC}"

LLAMA_DIR="$SCRIPT_DIR/llama.cpp"

if [ -f "$LLAMA_DIR/build/bin/llama-server" ]; then
    echo -e "${YELLOW}  llama.cpp already built. Skipping. Delete $LLAMA_DIR to rebuild.${NC}"
else
    if [ -d "$LLAMA_DIR" ]; then
        echo -e "  Updating existing llama.cpp repo..."
        cd "$LLAMA_DIR"
        git pull
    else
        echo -e "  Cloning llama.cpp..."
        git clone https://github.com/ggerganov/llama.cpp "$LLAMA_DIR"
        cd "$LLAMA_DIR"
    fi

    echo -e "  Configuring CMake with CUDA (Blackwell architecture)..."

    # Detect CUDA architecture — try sm_120 (Blackwell/GB10) first,
    # fall back to native detection
    CUDA_ARCH=""
    if nvcc --list-gpu-arch 2>/dev/null | grep -q "sm_120"; then
        CUDA_ARCH="120"
        echo -e "  Target architecture: sm_120 (Blackwell)"
    elif nvcc --list-gpu-arch 2>/dev/null | grep -q "sm_100"; then
        CUDA_ARCH="100"
        echo -e "  Target architecture: sm_100 (Blackwell)"
    else
        echo -e "  Target architecture: native (auto-detect)"
    fi

    if [ -n "$CUDA_ARCH" ]; then
        cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="$CUDA_ARCH"
    else
        cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=native
    fi

    echo -e "  Compiling (this may take 5-10 minutes)..."
    NPROC=$(nproc 2>/dev/null || echo 8)
    cmake --build build --config Release -j "$NPROC"

    echo -e "${GREEN}✓${NC} llama.cpp built successfully"
    echo -e "  Binary: $LLAMA_DIR/build/bin/llama-server"
fi

cd "$SCRIPT_DIR"
echo ""

# ===========================================================================
# Step 3: Model Files
# ===========================================================================
echo -e "${CYAN}[3/5] Checking model files...${NC}"

MODEL_DIR="$SCRIPT_DIR/models"
mkdir -p "$MODEL_DIR"

MODEL_FILE="$MODEL_DIR/LightOnOCR-2-1B-ocr-soup-F16.gguf"
MMPROJ_FILE="$MODEL_DIR/mmproj-F32.gguf"

if [ -f "$MODEL_FILE" ] && [ -f "$MMPROJ_FILE" ]; then
    echo -e "${GREEN}✓${NC} Model files found:"
    echo -e "    Model:  $(basename "$MODEL_FILE") ($(du -h "$MODEL_FILE" | cut -f1))"
    echo -e "    MMPROJ: $(basename "$MMPROJ_FILE") ($(du -h "$MMPROJ_FILE" | cut -f1))"
else
    echo -e "${YELLOW}Model files not found in $MODEL_DIR${NC}"
    echo ""
    echo -e "  You need to transfer the model files to this directory."
    echo -e "  From the Mac Mini (or any machine that has them):"
    echo ""
    echo -e "  ${CYAN}scp /Volumes/Raid_NVMe/lmstudio_models/noctrex/LightOnOCR-2-1B-GGUF/LightOnOCR-2-1B-ocr-soup-F16.gguf \\${NC}"
    echo -e "  ${CYAN}    user@<dgx-spark-ip>:$MODEL_DIR/${NC}"
    echo ""
    echo -e "  ${CYAN}scp /Volumes/Raid_NVMe/lmstudio_models/noctrex/LightOnOCR-2-1B-GGUF/mmproj-F32.gguf \\${NC}"
    echo -e "  ${CYAN}    user@<dgx-spark-ip>:$MODEL_DIR/${NC}"
    echo ""
    echo -e "  Or download from Hugging Face:"
    echo -e "  ${CYAN}https://huggingface.co/noctrex/LightOnOCR-2-1B-GGUF${NC}"
    echo ""

    read -p "  Have you transferred the model files? Press Enter to re-check, or Ctrl+C to abort... "

    if [ ! -f "$MODEL_FILE" ] || [ ! -f "$MMPROJ_FILE" ]; then
        echo -e "${RED}ERROR: Model files still not found. Please transfer them and re-run setup.${NC}"
        exit 1
    fi
fi

echo ""

# ===========================================================================
# Step 4: Python Environment
# ===========================================================================
echo -e "${CYAN}[4/5] Setting up Python environment...${NC}"

VENV_DIR="$SCRIPT_DIR/.venv"

if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}  Virtual environment already exists. Updating packages...${NC}"
else
    echo -e "  Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip -q
pip install -r "$SCRIPT_DIR/requirements.txt" -q
echo -e "${GREEN}✓${NC} Python packages installed"

echo ""

# ===========================================================================
# Step 5: Generate .env
# ===========================================================================
echo -e "${CYAN}[5/5] Configuring environment...${NC}"

if [ -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${YELLOW}  .env already exists. Skipping. Edit manually if needed.${NC}"
else
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"

    # Patch paths to match this installation
    sed -i "s|LLAMA_SERVER_PATH=.*|LLAMA_SERVER_PATH=\"$LLAMA_DIR/build/bin/llama-server\"|" "$SCRIPT_DIR/.env"
    sed -i "s|MODEL_PATH=.*|MODEL_PATH=\"$MODEL_FILE\"|" "$SCRIPT_DIR/.env"
    sed -i "s|MMPROJ_PATH=.*|MMPROJ_PATH=\"$MMPROJ_FILE\"|" "$SCRIPT_DIR/.env"

    echo -e "${GREEN}✓${NC} .env generated with correct paths"
fi

chmod +x "$SCRIPT_DIR/start.sh" "$SCRIPT_DIR/stop.sh"

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  Next steps:"
echo -e "    1. Transfer model files if not done (see Step 3 above)"
echo -e "    2. Review .env:  ${CYAN}nano .env${NC}"
echo -e "    3. Launch:       ${CYAN}source .venv/bin/activate && ./start.sh${NC}"
echo ""
