#!/usr/bin/env bash
# ==============================================================================
# Start Web UI Dashboard Daemon
# DEX-ROB Lab | Tianjin University
# ==============================================================================

PORT=${1:-8501}
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$ROOT_DIR/scripts/dashboard.pid"
LOG_FILE="$ROOT_DIR/scripts/dashboard.log"
PYTHON_BIN="/home/omen/miniforge3/envs/tianjin-robotics/bin/python"

if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

# Stop existing instance if running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "Stopping previous dashboard instance (PID $OLD_PID)..."
        kill "$OLD_PID" 2>/dev/null || true
        sleep 1
    fi
    rm -f "$PID_FILE"
fi

# Also kill anything on the port if still busy
fuser -k "$PORT/tcp" > /dev/null 2>&1 || true

echo "Starting Multi-Agent Research Dashboard on port $PORT..."
nohup "$PYTHON_BIN" -u "$ROOT_DIR/scripts/dashboard_server.py" "$PORT" </dev/null > "$LOG_FILE" 2>&1 &
NEW_PID=$!
disown "$NEW_PID" 2>/dev/null || true
echo "$NEW_PID" > "$PID_FILE"

sleep 1.5

if ps -p "$NEW_PID" > /dev/null 2>&1; then
    echo "✓ Dashboard is running successfully!"
    echo "  URL: http://localhost:$PORT"
    echo "  PID: $NEW_PID (saved in scripts/dashboard.pid)"
    echo "  Log: scripts/dashboard.log"
else
    echo "✗ Dashboard failed to start. Check scripts/dashboard.log:"
    cat "$LOG_FILE"
    exit 1
fi
