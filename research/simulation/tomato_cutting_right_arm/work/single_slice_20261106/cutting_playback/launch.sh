#!/usr/bin/env bash
set -euo pipefail
export DISPLAY="${DISPLAY:-:1}"
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
exec /home/omen/teamwork_projects/tomato_cutting_right_arm/.venv-native/bin/python /home/omen/teamwork_projects/tomato_cutting_right_arm/work/single_slice_20261106/cutting_playback/view.py
