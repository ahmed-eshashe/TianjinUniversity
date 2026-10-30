# Contact-only in-place tilt and regrasp diagnostics

19 October 2026. **Supported handle clearance was demonstrated; firm wrapped pickup did not pass. Phase 3 remains incomplete. No full training was started.**

Seven bounded native Isaac Lab experiments started the existing kitchen knife flat at the central board placement. The robot moved only through joint drives and physical contact. The knife stayed a free rigid body: no attachment, duplicate knife, or in-episode knife-pose command was used. These were scripted feasibility tests, not learned or vision-based pickup.

## Controller and findings

The experimental hand path pitches up to 8° about a blade support point, optionally adding up to ±12° roll. The latest path first requests 3 mm hand clearance, uses provisional 2 N finger / 3 N thumb preload targets, and begins an early finger wrap once measured handle rise reaches 10 mm. These are contact-controller targets, not increased actuator effort limits. Small subsequent seating moves may lower the hand by at most 3 mm.

An important controller defect was found: solving a tiny move directly from sagged measured arm joints discarded the prior load-holding command offset. A requested upward motion could therefore initially reduce support and let the thumb dip into the board. Relative contact moves now preserve the existing command offset, with a 2 cm position-offset rejection limit. A regression test checks that zero relative movement preserves the existing command. Offline forward kinematics agreed with recorded palm positions to sub-micrometre numerical accuracy; a gross coordinate-frame discrepancy was not found.

| Run | Outcome |
| --- | --- |
| 01 | Initial pinch, then thumb/board stop at approximately 35.4 N as the tilt began. |
| 02 | Another approach angle encountered thumb/board contact at approximately 65.7 N during descent. |
| 03 | No opposed physical pinch; lift refused. |
| 04 | Adding 3 mm hand clearance alone did not resolve the board-contact stop. |
| 05 | Lighter provisional preload alone also did not resolve the stop; thumb/board contact reached approximately 36.1 N. |
| 06 | With relative command compensation, the handle rose approximately **15.0 mm**. The next measured state exceeded the **20° rotation** boundary (21.1°), so the run stopped. |
| 07 | An earlier transition to wrapping maintained approximately **10.85–10.88 mm handle rise for 5 simulated seconds**. Support remained on the board; thumb and index contact persisted but the other fingers did not establish the requested wrap. Seating then crossed the **3 cm translation** boundary (30.52 mm), so the run stopped. Rotation at that stop was 7.45°, and the complete knife footprint remained at least 22.7 mm inside the board. |

The last two failures triggered different bounds. Neither result is an unsupported lift or a successful human-like grip. Run 07's five-second plateau was board-supported; it must not be described as a passed hold. The remaining acquisition problem is seating the handle into the palm and establishing multiple inner-finger contacts without further sliding or rolling.

## Safeguards and acceptance

The original blade, board-contact, self-contact, speed and joint checks remain active. Additional measured in-place limits check the full knife footprint (at least 5 mm board margin), centre displacement (at most 3 cm) and rotation from the settled pose (at most 20°). The final grasp oracle remains frozen: palm and opposed thumb, at least three wrapping fingers with at least two contacts away from the tips, 5 cm unsupported lift, 3 seconds continuous hold, limited slip and no unsafe event. No run passed that oracle.

The shared controller lock and RAM/VRAM watchdog guarded all seven processes. Startup reserves remain 10 GB available RAM and 4 GiB free VRAM; no reserve was lowered. Peak process RAM was **2.517 GB**, minimum available RAM **8.769 GB**, and peak total GPU use **673 MiB**. There were **zero memory warnings**. Every simulator exited normally after its diagnostic stop; all grasp results correctly remain failed. A normal simulator exit does not mean the pickup succeeded.

All **27 automated tests pass**, including the new relative-command regression, bounded arc/knife-motion checks, launcher mode validation and existing grasp-oracle/memory tests. The original robot, accepted demonstration files and frozen grasp criteria were verified unchanged. These checks do not certify physical hardware or training readiness.

## Evidence and next work

`in_place_tilt_results.json` records every outcome, resource report, preservation check and measured motion limit. Runs, actual contact trajectories, source snapshots and stop events are under `runs/rl/phase3/in_place_tilt_01` through `07`. Run 06 and 07 `physics_evidence.png` files reconstruct recorded meshes and are explicitly labelled **not camera images**.

The next physical-development step is a coordinated palm-seating and finger-regrasp controller from the supported clearance state, with explicit feedback for object sliding and rotation. The current initial pinch and additional finger curl alone do not achieve a wrap. Thumb/palm collision-model validation and calibrated contact/actuator parameters also remain open before training readiness. Keep full training stopped until a positive physical grasp and independent visual/contact validation pass.
