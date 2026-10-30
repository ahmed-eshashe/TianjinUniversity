#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
# Experimental photo-orientation grip; strict physical checks remain enabled.
exec /usr/bin/python3 scripts/guarded_grasp.py \
  --adjust-stance --stance-seed work/grasp_stance_cooking_clear.json \
  --fingers-first --finger-seating-force 1 --index-close-delay 1 \
  --finger-support-count 2 --finger-support-force .1 --finger-support-seconds .15 \
  --knife-setup-yaw-deg 120 --knife-setup-roll-deg 180 --post-lift-roll-deg -75 --lift-height .06 --require-cutting-orientation \
  --require-wrap --handle-overhang --overhang-edge -.055 \
  --palm-height .035 --finger-offset .040 --handle-offset -.035 \
  --preclose-deg 0 --close-deg 90 \
  --thumb-pitch-deg 10 --close-thumb-pitch-deg 33 \
  --thumb-yaw-deg 60 --prethumb-yaw-deg 0 --support-fingers none \
  --finger-torque .3 --finger-stiffness 3 --thumb-torque 1 --thumb-stiffness 10 \
  --force-closure --align-thumb-yaw --thumb-yaw-force-limit 20 \
  --finger-contact-force 4 --thumb-contact-force 4 --closure-speed 6 \
  --insert-distance 0 --approach-clearance .08 --approach-axis z \
  --pad-stiffness 15000 --pad-damping 60 --torsional-radius .006 "$@"
