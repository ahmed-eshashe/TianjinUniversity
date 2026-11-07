#!/usr/bin/env bash
set -euo pipefail
export DISPLAY="${DISPLAY:-:1}"
export TOMATO_PICKUP_INTERACTIVE=1
PICKUP_ROOT=/home/omen/teamwork_projects/tomato_cutting_right_arm
PICKUP_OUTPUT="$PICKUP_ROOT/work/outward_elbow_20261104/user_runs/$(date +%Y%m%d_%H%M%S)_$$"
echo "Opening the outward-elbow kitchen demo. Press Play when ready. Close the window when finished."
echo "Knife starts in an ideal clamped cradle; a fixed hand attachment engages after finger closure."
exec "$PICKUP_ROOT/.venv-native/bin/python" "$PICKUP_ROOT/rl/tomato_outward_elbow_guard_v01.py" --mode demo_grip --output "$PICKUP_OUTPUT"
