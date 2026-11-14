#!/bin/bash
set -eu
cd /home/omen/teamwork_projects/tomato_cutting_right_arm/work/disect_stability_20261108_v03
export PATH=/home/omen/teamwork_projects/tomato_cutting_right_arm/work/solver_comparison_20261108/env311/bin:$PATH
export CUDA_HOME=/home/omen/.cache/packman/chk/cuda/12.8.0-5-manylinux_2_35_x86_64-release
export MAX_JOBS=2 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
exec timeout 300 python -X faulthandler short_gravity.py
