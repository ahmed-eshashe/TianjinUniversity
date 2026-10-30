#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec /usr/bin/python3 scripts/guarded_grasp.py \
  --adjust-stance --stance-seed work/grasp_stance_55.json \
  --handle-overhang --overhang-edge -.035 \
  --palm-height .073 --finger-offset .028 --handle-offset -.01 \
  --preclose-deg 50 --close-deg 60 --pinky-close-deg 90 \
  --thumb-pitch-deg 0 --close-thumb-pitch-deg 10 \
  --thumb-yaw-deg 60 --prethumb-yaw-deg 60 \
  --finger-torque .6 --finger-stiffness 6 \
  --thumb-torque 3 --thumb-stiffness 20 \
  --insert-distance .03 --approach-axis x \
  --pad-stiffness 15000 --pad-damping 60 --torsional-radius .006 \
  "$@"
