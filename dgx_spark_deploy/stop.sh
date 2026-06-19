#!/bin/bash
# OCR Pipeline — Stop Script (DGX Spark)
# Gracefully stops both llama-server and FastAPI.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

PID_FILE="$SCRIPT_DIR/.pids"

if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}No .pids file found. Pipeline may not be running.${NC}"
    echo "Attempting to find processes by name..."

    # Fallback: find by process name
    pkill -f "ocr_service.py" 2>/dev/null && echo -e "${GREEN}✓${NC} Stopped FastAPI" || true
    pkill -f "llama-server" 2>/dev/null && echo -e "${GREEN}✓${NC} Stopped llama-server" || true
    exit 0
fi

echo -e "${YELLOW}Stopping OCR Pipeline...${NC}"

source "$PID_FILE"

if [ -n "${API_PID:-}" ] && kill -0 "$API_PID" 2>/dev/null; then
    kill "$API_PID" 2>/dev/null
    echo -e "${GREEN}✓${NC} FastAPI stopped (PID $API_PID)"
else
    echo "  FastAPI not running"
fi

if [ -n "${LLAMA_PID:-}" ] && kill -0 "$LLAMA_PID" 2>/dev/null; then
    kill "$LLAMA_PID" 2>/dev/null
    echo -e "${GREEN}✓${NC} llama-server stopped (PID $LLAMA_PID)"
else
    echo "  llama-server not running"
fi

rm -f "$PID_FILE"
echo -e "${GREEN}OCR Pipeline stopped.${NC}"
