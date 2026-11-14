#!/usr/bin/env bash
set -euo pipefail
export DISPLAY="${DISPLAY:-:1}"
export PYTHONDONTWRITEBYTECODE=1
exec /home/omen/teamwork_projects/tomato_cutting_right_arm/.venv-native/bin/python /home/omen/Documents/Codex/experiments/tomato_v06_isaac_view_20261110_v01/view.py
