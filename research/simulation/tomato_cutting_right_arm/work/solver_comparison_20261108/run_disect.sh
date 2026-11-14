#!/bin/bash
cd /home/omen/teamwork_projects/tomato_cutting_right_arm
export PATH="$PWD/work/solver_comparison_20261108/env311/bin:$PATH"
export CUDA_HOME=/home/omen/.cache/packman/chk/cuda/12.8.0-5-manylinux_2_35_x86_64-release
export MAX_JOBS=2 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
exec timeout 900 work/solver_comparison_20261108/env311/bin/python work/solver_comparison_20261108/disect_benchmark.py
