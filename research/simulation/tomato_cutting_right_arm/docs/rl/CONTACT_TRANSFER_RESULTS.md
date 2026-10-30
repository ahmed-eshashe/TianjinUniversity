# Finger contact transfer and palm seating results

Stable transfer from the thumb and index pinch to the other fingers was not achieved. Six bounded simulator runs completed, and three further launches were refused by the unchanged memory reserve. The hand did not establish palm contact or a three-finger wrap, so no lift was attempted. Phase 3 remains incomplete; full training remains prohibited.

## Changes and findings

Unloaded fingers now follow their planned acquisition angles instead of continuously curling past a missed contact. Loaded-digit pressure remains bounded. A separate option preserves approximately 3 N index support during seating. Tests cover both changes.

The offline planner can resume a compatible path and use a measured thumb/finger contact pair as anchors for a later handoff. It rejects missing or insufficiently loaded anchors. The extended path still keeps the original thumb/index anchors until new support is actually measured. No new-support handoff was performed in these tests.

The first extended test briefly loaded the ring finger, peaking at 1.143 N. Its longest continuous interval above 0.3 N was 0.4 seconds; this did not constitute stable transfer. A finite-difference contact-direction check estimated ring-pad normal motion of +0.00077 m per radian of closing, versus -0.0658 m per radian for the index. The ring contact was nearly tangential and was not accepted as a useful wrapping contact. See contact_transfer_direction_audit.json.

Keeping the ring finger clear allowed the fixed-anchor path to complete waypoints through fraction 0.50 before the drift stop. This is half of a particular numerical path, not half of a validated grasp. A measured geometry sweep also showed that middle-finger overclosure can carry its pad away from the handle. Holding that finger more open alone did not establish contact.

A bounded translation correction then held tracked point errors below about 0.63 mm and additional knife-centre lateral movement below 0.10 mm immediately before a later contact loss. Its per-control-step correction is capped at 0.15 mm and its accumulated correction at 3 mm. It does not move the knife directly or disable the original drift checks.

A separate rolling controller projects small wrist/finger motions into the instantaneous no-slip contact constraint space and refreshes the material-point references from measured contacts each control step. Contacts are mathematical constraints used to choose commands, not physics joints. The knife remains free. The global knife-centre lateral bound remains 2 mm. This controller advanced the hand-root seating target by roughly 1.8 mm but then lost opposed contact. Other fingers did not take load. The small linearized contact residual does not demonstrate frictional stability, force closure, or a firm grasp.

## Completed physical tests

| Run | Motion or control change | Outcome |
| --- | --- | --- |
| contact_transfer_01 | Extended conservative path and bounded acquisition angles | Brief ring contact; drift stop after waypoint fraction 0.267 |
| contact_transfer_02 | Ring and little fingers kept clear | No middle contact; drift stop after fraction 0.50 |
| contact_transfer_03 | Middle finger held at 52.5 degrees during approach | No stable new contact; drift stop after fraction 0.367 |
| contact_transfer_04 | Bounded contact-point translation feedback and 3 N index target | Smaller tracking errors before abrupt pinch loss; drift stop after fraction 0.30 |
| contact_transfer_05 | Rolling contact controller with original contact model | Opposed contact lost after about 120 small steps; no new support |
| contact_transfer_07 | Rolling controller with provisional 2 mm nominal torsional patch radius and zero minimum radius | Same loss point and trajectory as the original contact model; no demonstrated benefit |

All six workers exited normally. Failures were reported as failed grasp tests even though the simulator process returned normally. No frozen oracle passed, and no unsupported lift or hold was achieved.

## Contact model sensitivity

The torsional-patch option changes only five right-hand distal collider attributes in the transient simulator stage. Original meshes, assets, friction coefficients, motor limits, and attachment rules remain unchanged. The 2 mm nominal-radius test used a zero minimum radius and did not improve the motion. Its configuration and exact collider list are recorded in contact_transfer_07/run_configuration.json.

NVIDIA describes torsional patch friction as an approximation for compression of contacting surfaces; a zero minimum radius leaves the effect dependent on penetration. See the [PhysX shape reference](https://nvidia-omniverse.github.io/PhysX/physx/5.5.0/_api_build/classPxShape.html). Authoring the attributes is not a calibrated fingertip-compliance model or a measured backend torsional-response test.

A further sensitivity with a 1 mm minimum patch radius remains unexecuted. Launches contact_transfer_08 and contact_transfer_09 were refused before simulator startup, including the user-authorized retry. Its configuration is retained in contact_transfer_plan_patch_min1mm.json and is explicitly uncalibrated. The active contact_seating_plan.json has been restored to the tested rolling configuration with the original zero-radius contact model. Full task training must not use this incomplete grasp as a success demonstration.

## Memory and verification

The watchdog code is byte-for-byte unchanged from the prior contact-seating continuation. Startup still requires 10 GB available host RAM and 4 GiB free VRAM. Runtime checkpoint/hard-stop reserves and the shared controller lock remain unchanged. The three refused launches are preserved as launcher-refusal records, not simulator trials. After the user's first memory cleanup, contact_transfer_07 started successfully; later launches remained below the startup reserve.

Across the six completed tests, there were 0 memory warnings. Peak worker RAM was 2.521 GB, minimum available host RAM was 7.939 GB, and peak total GPU use was 1041 MiB. These are short-run measurements, not a long-duration stability claim. All simulator workers are stopped and the controller lock is released.

All 42 automated tests pass, including unloaded-finger acquisition, bounded reference feedback, pressure retention, instantaneous contact projection, and refusal of invalid numerical inputs. Source robot, accepted demonstration baselines, and frozen success criteria retain their recorded hashes. The new contact-separation logging and optional 1 mm minimum patch branch compile but have not been exercised in a simulator because startup was refused.

Machine-readable results: contact_transfer_results.json and contact_transfer_final_checks.json. Individual trajectories, configuration/source snapshots, contact traces and memory reports are under ../../runs/rl/phase3/contact_transfer_01 through contact_transfer_09. The offline planner that generated the extended path is retained under contact_transfer_offline_01/source_snapshot.

## Remaining work

The next work is to establish a contact with a useful closing direction and sustained measured load before releasing or moving the original pinch. A brief contact-force reading or a zero kinematic residual is insufficient. The optional contact-patch sensitivity needs adequate startup memory and a measured torsional-response check before drawing conclusions about pad compliance. No setting from that sensitivity is validated for the physical robot. Palm seating, three-finger wrap, the unchanged 5 cm unsupported lift and 3 second hold remain unproven.
