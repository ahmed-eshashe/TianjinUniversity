#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec /home/omen/miniconda3/envs/isaaclab_6/bin/python scripts/load_scene.py "$@"
