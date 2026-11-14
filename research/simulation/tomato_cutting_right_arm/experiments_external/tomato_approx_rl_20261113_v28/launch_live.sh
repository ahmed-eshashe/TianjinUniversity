#!/usr/bin/env bash
set -euo pipefail
export DISPLAY="${DISPLAY:-:1}"
export OPENBLAS_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
exec /home/omen/teamwork_projects/tomato_cutting_right_arm/.venv-native/bin/python /home/omen/Documents/Codex/experiments/tomato_approx_rl_20261113_v28/view_live.py
