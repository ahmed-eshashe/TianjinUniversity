#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
src="$PWD/CRESSim-MPM-09aa5009b8580351f516b6df7660e87821fc5eb6"
cuda=/home/omen/.cache/packman/chk/cuda/12.8.0-5-manylinux_2_35_x86_64-release
g++ -std=c++17 -O2 -DCRMPM_ENGINE_STATIC -I"$cuda/include" \
  -I"$src/include" -I"$src/include/core" -I"$src/include/math" -I"$src/include/solver" \
  -I"$src/include/utils" -I"$src/include/engine" -I"$src/include/geometry_utils" -Ibuild \
  feasibility.cpp build/bin/libcrmpm_engine.a -L"$cuda/lib64" -lcudart_static -ldl -lrt -pthread -o feasibility
