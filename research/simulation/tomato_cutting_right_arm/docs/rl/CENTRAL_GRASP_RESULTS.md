# Flat central knife pickup: physical test results

19 October 2026. **The firm central pickup test did not pass. Phase 3 remains incomplete and full training remains stopped.** These were scripted physical-feasibility diagnostics, not RL training or camera-based knife recognition.

## What was tested

The existing kitchen knife started flat at the cutting board's centre, with its full footprint inside the board. The board and counter stayed fixed. Each episode settled under gravity before the arm approached. The knife was one free rigid body: no attachment, extra knife asset, or in-episode knife-position command was used.

The native Isaac Lab environment retained self-collision, joint/speed checks, contact-force stops and the RAM/VRAM watchdog. Several hand angles, finger preshapes and handle locations were screened against the original meshes, then tested physically. Later diagnostics checked blade and excessive-contact events at physics-substep frequency, rather than only at the control rate.

The final success criteria were unchanged: at least 5 cm lift, 3 seconds of continuous unsupported hold, palm support, opposed thumb, at least three wrapping fingers, at least two contacts away from the tips, at most 10 mm relative slip, and no blade contact, attachment or unsafe event. **No attempt satisfied these criteria.**

## Findings

- The arm can reach the central handle. Physical thumb/finger contact was established, including an opposed pinch using closing-side finger contact. One recorded preload produced approximately 3 N finger contact and 4 N thumb contact. That is an initial pinch, not the requested final grip.
- The knife did not follow the subsequent 3.5 cm clearance motion reliably. The control stopped rather than proceeding as if the knife had been lifted. The final wrap-and-hold was therefore not validated.
- Some earlier contacts were on outer finger surfaces: contact force alone was misleading. The planner now considers whether closing moves a surface toward the handle, and the initial contact check also requires a resisting closing load. Reported drive torques are PD estimates, not confirmed hardware torque sensing.
- Alternative approaches encountered wrist or palm/thumb internal contact. Refining palm/thumb collision approximation with convex decomposition did **not** establish that the remaining mount interference was resolved. No extra collision-exclusion pairs were added to obtain a pass. Thumb goal angles were kept within a smaller experimental range; this is not a newly calibrated hardware limit.
- The final nearer-blade trial contacted the board with the thumb. The physics-substep contact stop fired; the reported peak offending contact was about 77.7 N. The run was rejected.

The results do not prove central pickup is mechanically impossible. They show that the tested direct approaches and initial-pinch controllers are insufficient under the current model and dynamics. A controlled in-place tilt/reposition before wrapping, and a review of the thumb/palm collision geometry, remain necessary development work. Merely increasing a reward or treating contact as grasp success would conceal these failures.

## Evidence and implementation

`central_grasp_results.json` summarizes every bounded run, its stop reason, recorded handle motion, resource measurements and preservation checks. Detailed trajectories, contact points/normals, friction samples where enabled, checkpoints and configuration/source snapshots are stored under `runs/rl/phase3/central_grasp_*/`.

Representative evidence:

- `central_grasp_10`: nearer-blade thumb/finger contact, followed by loss of contact during clearance.
- `central_grasp_13`: opposed closing-side pinch with preload, followed by failed clearance lift.
- `central_grasp_14`: nearer-blade pad-directed approach stopped by thumb/board contact.
- `central_changes_regression`: the native environment/adapter/empty-hand regression still passes; this does not certify pickup.

`central_grasp_13/physics_evidence.png` reconstructs recorded states using meshes. It is explicitly labelled **not a camera image** and is a diagnostic illustration, not a rendered training-camera observation. Raw joint/contact/object data remain the primary evidence.

Two harness defects encountered during development—numeric tensor type mismatch and JSON serialization of a nonempty-contact flag—were fixed. A separate diagnostic was intentionally stopped to correct preservation of finger targets while closing the thumb. Those stops are not successful or failed-grasp examples. The automated suite now passes 23 tests, including serialization and refusal of conflicting/learner-resume launcher modes.

The source robot, accepted scripted demonstrations and frozen success-criteria file were verified unchanged. The experimental grasp layer only changes selected collision approximations and retains the existing knife/dynamics. Its remaining collision limitations must be resolved before calling it training-ready.

## Memory safeguard

The first launch was refused because available RAM was below the 10 GB startup reserve. The user freed memory and the retry proceeded. The reserve was not lowered. All later simulator processes remained guarded by the shared controller lock, RAM/VRAM limits, runtime bounds and explicit-result checks.

Across the central diagnostic runs, peak process RAM was approximately **3.95 GB**, minimum available RAM **7.48 GB**, and peak total GPU memory **707 MiB**. There were **zero mid-run memory warnings**. These are headless physical diagnostics without a rendering camera, not a repeat of the earlier RGB-D soak. Every simulator has exited and the controller lock is released.

Full training is still **NO-GO**. The next acceptance milestone is a physically verified wrap and lift from a central flat placement, with synchronized positive contact and visual evidence; it has not been achieved here.
