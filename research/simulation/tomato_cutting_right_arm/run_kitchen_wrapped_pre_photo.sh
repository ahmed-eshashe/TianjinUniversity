#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
# Physical wrapped grip, validated in finite headless and visible runs. Strict checks remain enabled.
exec /usr/bin/python3 scripts/guarded_grasp.py \
  --adjust-stance --stance-seed work/grasp_stance_top_deep.json \
  --require-wrap --handle-overhang --overhang-edge -.035 \
  --palm-height .035 --finger-offset .020 --handle-offset .015 \
  --preclose-deg 0 --close-deg 90 \
  --thumb-pitch-deg 10 --close-thumb-pitch-deg 33 \
  --thumb-yaw-deg 60 --prethumb-yaw-deg 0 --support-fingers none \
  --finger-torque .3 --finger-stiffness 3 --thumb-torque 1 --thumb-stiffness 10 \
  --force-closure --align-thumb-yaw --thumb-yaw-force-limit 20 \
  --finger-contact-force 4 --thumb-contact-force 4 --closure-speed 6 \
  --insert-distance 0 --approach-clearance .08 --approach-axis z \
  --pad-stiffness 15000 --pad-damping 60 --torsional-radius .006 "$@"
