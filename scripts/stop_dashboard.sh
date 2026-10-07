#!/usr/bin/env bash
# ==============================================================================
# Stop Web UI Dashboard Daemon
# DEX-ROB Lab | Tianjin University
# ==============================================================================

PORT=${1:-8501}
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$ROOT_DIR/scripts/dashboard.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Stopping dashboard process (PID $PID)..."
        kill "$PID" 2>/dev/null || true
        sleep 1
    fi
    rm -f "$PID_FILE"
fi

# Ensure port is released
fuser -k "$PORT/tcp" > /dev/null 2>&1 || true
echo "✓ Dashboard stopped."
