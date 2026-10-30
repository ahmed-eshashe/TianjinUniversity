# Contact preserving palm seating results

The latest bounded physical test retained the thumb and index pinch through a small seating adjustment, but did not establish palm contact or a three-finger wrap. The lift was refused. Phase 3 remains incomplete and full task training remains prohibited.

## Controller changes

The offline planner now constrains material points on the thumb and index to stay near their measured handle contacts while moving toward the palm-seating pose. These are numerical planning constraints only; no physics joint, attachment or knife pose command is introduced. Wrist and finger targets advance by a shared fraction to reduce timing mismatch. Runtime checks stop the seating attempt above 3 mm material-point tracking error or 2 mm additional knife-centre lateral movement. Existing blade, force, joint, thumb-posture and footprint stops remain active.

The worker reads the selected plan once and snapshots those exact bytes. A bounded 96-sample physics-step trace records contact transitions without growing its storage over the run. Force/material parameters, source geometry and actuator limits were not changed.

## Physical tests

| Run | Change | Result |
| --- | --- | --- |
| contact_seating_01 | Point-constrained path with synchronized targets | Pinch lost during the first waypoint; drift stop |
| contact_seating_02 | Little finger held clear at 60 degrees | Same early pinch loss; little-finger contact is insufficient to explain the failure |
| contact_seating_03 | Same motion with physics-step recording | Reproduced loss; both pinch contacts disappeared within milliseconds, followed by falling; no preceding large contact-force spike was recorded |
| contact_seating_04 | Stronger contact-normal constraint and clear little finger | Completed all seven available waypoints through path fraction 0.20; pinch remained, but palm and three-finger contact were absent; lift refused |

At the end of the fourth test, additional knife-centre lateral movement from the supported reference was 0.807 mm and the maximum tracked hand-point displacement was 1.293 mm. Thumb and index normal forces were approximately 2.98 N and 2.77 N. The handle remained about 36 mm above its initial height with blade/board support. This is supported tilt, not unsupported lifting. No final grasp oracle passed and no unsupported hold was achieved.

The stronger-normal offline path predicts a reduction in palm/handle separating distance from about 49.5 to 47.2 mm. It is a limited intermediate path, not a complete power grasp. Holding the same two material points restricts further seating; continuing requires a validated transfer of load to additional fingers. A geometric angle sweep also found that curling the middle and ring fingers farther at the initial wrist pose eventually increases their distance from the handle. Closing them harder alone is therefore insufficient.

The contact-loss mechanism remains unresolved. The record identifies contact disappearance during motion before pressure balancing, but does not establish a unique cause such as friction saturation or contact-manifold refresh. Collision-surface and force-direction checks should precede larger seating moves. Once additional fingers carry load, replan using the newly measured contacts and require palm/three-finger contact before attempting the unchanged lift and hold test.

## Safeguards and verification

All four simulator workers exited normally, with zero memory warnings. Peak worker RAM was 2.520 GB, minimum available host RAM was 8.833 GB, and peak total GPU use was 688 MiB. These measurements describe these short tests only.

Startup reserves remain 10 GB available RAM and 4 GiB free VRAM. Runtime checkpoint and hard-stop reserves remain unchanged, as does the shared controller lock. All 36 automated tests pass. Source robot, accepted baseline demonstrations and frozen success criteria retain their recorded hashes. No camera policy, knife-pickup learner, attachment or in-episode knife teleport was used.

Machine-readable evidence: contact_seating_results.json. Individual trajectories, source/configuration snapshots, stop events and memory reports are under ../../runs/rl/phase3/contact_seating_01 through contact_seating_04. The last two runs also contain seating_substeps.json.
