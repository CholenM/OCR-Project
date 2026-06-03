#!/bin/bash
# RAG Pipeline — Stop Script (DGX Spark)
# Stops RAG services only (does NOT touch ocr-pipeline).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
PID_FILE="$SCRIPT_DIR/.pids"

echo -e "${YELLOW}Stopping RAG Pipeline...${NC}"

if [ -f "$PID_FILE" ]; then
    while read -r pid; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "  Stopping PID $pid..."
            kill "$pid" 2>/dev/null || true
        fi
    done < "$PID_FILE"
    rm -f "$PID_FILE"
    echo -e "${GREEN}RAG Pipeline stopped.${NC}"
else
    echo -e "${YELLOW}No PID file. Fallback pkill...${NC}"
    pkill -f "uvicorn rag_service" 2>/dev/null || true
    # Only kill llama-servers on RAG ports (not OCR port 8001)
    fuser -k 8002/tcp 2>/dev/null || true
    fuser -k 8003/tcp 2>/dev/null || true
    echo -e "${GREEN}Fallback cleanup done.${NC}"
fi

echo -e "${GREEN}Done. OCR pipeline (~/ocr-pipeline/) is untouched.${NC}"
