#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
src="/home/omen/Documents/Codex/experiments/tomato_persistent_mpm_20261110_v01/upstream_diagnostic/source"
cuda=/home/omen/.cache/packman/chk/cuda/12.8.0-5-manylinux_2_35_x86_64-release
g++ -std=c++17 -O2 -DCRMPM_ENGINE_STATIC -I"$cuda/include" \
  -I"$src/include" -I"$src/include/core" -I"$src/include/math" -I"$src/include/solver" \
  -I"$src/include/utils" -I"$src/include/engine" -I"$src/include/geometry_utils" -I/home/omen/Documents/Codex/experiments/tomato_persistent_mpm_20261110_v01/upstream_diagnostic/build \
  src/cressim_control.cpp /home/omen/Documents/Codex/experiments/tomato_persistent_mpm_20261110_v01/upstream_diagnostic/build/bin/libcrmpm_engine.a -L"$cuda/lib64" -lcudart_static -ldl -lrt -pthread -o upstream_diagnostic/cressim_cutoff_corrected
