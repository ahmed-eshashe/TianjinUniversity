# Supported palm seating and finger-wrap continuation

19 October 2026. **The handle can now be raised about 3.7 cm with the blade still supported on the board. Firm palm-supported wrap and unsupported pickup have not passed. Phase 3 remains incomplete; full training remains stopped.**

The diagnostics repeat the initial physical approach and supported clearance from a fresh central flat reset, then attempt the revised seating motion. They do not restore an in-flight contact checkpoint or teleport the knife into the supported pose. The existing kitchen knife remains one free rigid body, and only the right arm/hand drives manipulate it. No attachment or extra knife was introduced.

## What changed

- The adaptive clearance controller recomputes hand targets from the measured knife pose, preserving the initial hand/knife relationship while making small supported pitch increments. It reached approximately **36.8 mm handle rise**, compared with about 15 mm in the prior continuation. At a representative attained state, the board still supplied approximately **0.71 N**, and geometric bottom clearance was approximately zero. This is supported handle clearance, not a successful unsupported lift.
- Palm seating uses small arm motions with independent finger feedback. Missing contacts get bounded additional closure; excessive pad pressure is released. Existing holding pressure is preserved on loaded digits. An earlier version incorrectly capped away the thumb's load-holding command offset; a regression test now covers that case.
- Loaded index curl is coordinated with seating rather than held at the initial fingertip angle. Physical lateral recentering and smaller combined corrections were also tested without widening the knife-motion bounds. Those changes did not establish the final wrap.
- Persistent pinch loss stops motion/closure early. The new modes also reject measured thumb pitch above **0.32 rad**, and cap commanded thumb pitch at **0.38 rad** so a bounded holding preload can remain. These are conservative experimental software settings, not calibrated hardware limits. Source joint/effort limits remain unchanged.
- Native hand-link transforms were checked against the authored kinematic model at the attained clearance state. The maximum position discrepancy was approximately **0.54 micrometres**, and maximum orientation discrepancy about **6.9e-7 rad**. A large hand-frame mismatch does not explain the observed failures.

The object still tends to return to the board, lose opposed contact, or slide during the transfer from fingertip pinch toward palm seating. The measurements do not establish palm contact with three properly wrapping fingers or any valid final hold window. Arm motion and contact pressure alone are not reported as grasp success.

## Bounded trials

Every run retains the exact controller source snapshot and configuration. Later runs include safety and feedback corrections found in earlier tests; identical mode names do not imply identical source versions.

| Run | Main finding |
| --- | --- |
| palm_seating_01 | Independent feedback and vertical seating lost the pinch; continuing thumb closure exposed palm/thumb mount interference. Physics contact stop fired. |
| palm_seating_02 | A different near-tip arc lost support and also exposed the mount interference. Physics contact stop fired. |
| palm_seating_03 | Added support-loss monitoring stopped the test earlier. A very restrictive command cap also impaired acquisition. |
| palm_seating_04 | Adaptive pose feedback attained about 36.8 mm supported handle rise, then seating lost the pinch. |
| palm_seating_05 | Preserving loaded thumb pressure extended the transition, but seating still lost support. |
| palm_seating_06 | Coordinated loaded-finger curl retained the pinch longer but crossed the 3 cm centre-displacement boundary. |
| palm_seating_07 | Separate physical recentering reduced lateral drift with the handle raised, then lost the pinch. |
| palm_seating_08 | Orientation-following recentering still failed the subsequent seating transition. |
| palm_seating_09 | Smaller combined correction and reduced curl rate also lost support; native hand-frame audit passed. |
| palm_seating_10 | A geometry-guided wrist/finger transition retained the initial pinch but dragged the knife to the 3 cm boundary before seating; rejected. |

The first two rejected simulations recorded large internal mount-contact impulses (approximately 9.29 kN and 4.06 kN). These are unvalidated simulation/model events, not successful contact or hardware force measurements. Later tests added earlier pinch-loss and posture stops instead of disabling the colliding pair, raising force thresholds, or suppressing self-collision. Remaining mount-model validity is unresolved.

## Geometry checks and evidence

`thumb_mount_geometry_check.json` records a read-only triangle-mesh diagnostic. Both meshes are non-watertight; sampled vertex-inside tests therefore cannot certify collision clearance or justify excluding the palm/thumb pair. No source geometry or collision filters were changed in this continuation.

`supported_wrap_candidates.json`, `supported_wrap_high_clearance.json`, `refined_supported_wrap.json` and `seating_geometry_path.json` describe offline proposals and contact-gap estimates. They are not physical grasp validations. At the greater clearance, refinement found a near-contact endpoint with index/middle/ring at 70°, pinky at 60°, thumb yaw 40° and pitch 18°, a roughly −20° wrist roll change and handle centre [32, 33, 81] mm in the hand frame. Estimated minimum board clearance was about 6 mm. This screen does not validate blade clearance, inner-contact placement or final hold criteria. Run 10 tested a continuous transition toward that endpoint; it did not reach a valid wrap. Different digits require different trajectories, and an endpoint proposal cannot substitute for a feasible continuous regrasp path.

`palm_seating_results.json` contains every outcome, resource measurement and source/criteria preservation check. Each run under `runs/rl/phase3/palm_seating_*/` contains actual trajectories, contact forces, stop details and code snapshots. `palm_seating_09/seating_progress.png` and `palm_seating_10/seating_progress.png` plot the measured clearance, drift and digit contact loads. It is not a camera image or trained perception output.

## Acceptance and memory

The final grasp criteria remain frozen: palm support, opposed thumb, at least three wrapping fingers including two contacts away from the tips, 5 cm unsupported lift, 3 seconds continuous hold, bounded slip, and no unsafe contact, attachment or joint violation. No run satisfies these criteria.

The original 10 GB available-RAM / 4 GiB free-VRAM startup reserves, RAM/VRAM runtime stops, shared controller lock and explicit-result requirement remain active. Every completed simulator exited normally following its diagnostic stop; no run issued a memory warning. Across the ten runs, peak process RAM was **2.524 GB**, minimum available RAM **8.938 GB**, and peak total GPU use **683 MiB**. A normal process exit is not a passed grasp.

All **33 automated checks pass**. Original robot and accepted demonstration hashes, as well as the frozen success criteria, remain unchanged. No full training, perception training or physical-robot command was started.

The current software also exposes `--seating-mode mesh-guided` for the rejected geometry-guided diagnostic. Its proposal is snapshotted per run; it is not a validated controller.

The remaining task is a continuous, physically valid transfer from the supported pinch to palm and multiple inner-finger contacts. Positive grasp-oracle and independent visual validation remain mandatory before training readiness.
