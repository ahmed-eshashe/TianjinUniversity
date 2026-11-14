#!/usr/bin/env bash
set -euo pipefail
DEMO_DIR=/home/omen/Documents/Codex/experiments/tomato_robot_integration_20261113_v31
RUN_DIR="$DEMO_DIR/runs/live_$(date +%Y%m%d_%H%M%S)"
exec 9>"$DEMO_DIR/.launch.lock"
flock -n 9 || { echo "This demo is already open. Close its window before launching again."; exit 1; }
mkdir -p "$RUN_DIR"
export OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
exec /home/omen/teamwork_projects/tomato_cutting_right_arm/.venv-native/bin/python -u "$DEMO_DIR/robot_worker.py" --mode cut --interactive --output "$RUN_DIR" "$@"
