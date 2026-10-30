# Native integration and Phase 3 physical-task checks

19 October 2026. The user authorized dependency repair, native integration checks and continuation of Phase 3. **No full training was started. Phase 3 is still open.** In particular, a wrapped pickup from a flat, central placement has not yet been physically validated in the new native scene.

## Dependencies

The original `isaaclab_6` environment and accepted scripted demonstrations were preserved. A project-local `.venv-native` overlay inherits that environment and shadows only selected packages. It is not a standalone environment: it depends on the existing base environment and editable `/home/omen/IsaacLab` checkout.

The overlay installs Click 8.1.7, psutil 5.9.8, Numba 0.64.0 with llvmlite 0.46.0, and torchaudio 2.11.0. Compatible versions of IPython, Rerun and Hugging Face Hub avoid introducing new conflicts with those utility pins. Exact local packages and the effective environment are saved under `rl/dependencies/`.

The installed Lab checkout explicitly overrides Isaac Sim's older Torch, TorchVision, Newton and MuJoCo pins. Those newer Lab versions were retained. `pip check` still reports six metadata conflicts involving those overrides, including the older MuJoCo converter constraint; it is **not clean**. `rl/dependencies/verify_runtime.py` requires exactly that known set, verifies the corresponding overrides in Lab's configuration, and rejects additional mismatches. The unused MuJoCo importer is not validated by a PhysX test.

Actual CUDA matrix multiplication, Numba compilation, audio resampling, utility imports, native environment imports and the native RL adapter passed. This is evidence for the exercised PhysX stack, not every installed optional backend. `isaaclab` package version 19.0.0 matches its own source package metadata; the checkout's top-level VERSION is 3.0.0. No upstream version files were edited.

## Native integration

`rl/native_env.py` subclasses the installed **DirectRLEnv**, uses the **PhysX backend**, registers native Articulation and RigidObject assets, and steps through **RslRlVecEnvWrapper**. One environment runs CPU physics at 240 Hz and controls at 20 simulated Hz. No optimizer, policy runner or training loop exists in this path.

The 13-action joint probe and 39-value proprioceptive observation validate the interface only. They do not replace the proposed 12-action palm/hand task contract, and they do not identify or approach the knife using vision. Camera resource evidence remains the separate Phase 2 result; this native physical test has no camera.

Isaac Lab interprets actuator gains in SI units. Explicit native gains prevent accidental reuse of degree-based USD values at roughly 57 times the intended gain. The arm/hand limits remain provisional simulation settings, not verified hardware capabilities.

## Collision repair and dynamics

Self-collision is enabled in the separate `rl/scene/phase3.usda` layer. Arm and torso collision meshes use convex decomposition; hand and compound knife collisions retain their existing geometry. Source robot/kitchen assets and the Phase 2 scene are unchanged.

The original ready posture produced severe internal contacts. Diagnostics identified fixed base/TCP/adapter assemblies and a right upper-arm/torso intersection. The derived scene expands normal adjacent-joint exclusions through **fixed-link assemblies only**. It does not exclude arbitrary colliding links, cross-arm contacts, the hand/knife, or the kitchen. Every filtered pair and its reason is recorded in `phase3_physics.json`. A separate Phase 3 ready posture changes right shoulder joint 2 by +0.3 rad; an offline geometry search and subsequent native test verified the startup clearance. Full trajectory collision safety is not established by a stable starting posture.

The knife remains the existing kitchen knife, one free rigid body with separate blade and handle collision shapes. Uniform scale is baked into derived mesh coordinates without changing its world geometry. Provisional mass is 0.25 kg, split 0.10/0.15 kg between handle and blade for explicit COM/inertia calculation. Positive inertia and the triangle inequality pass; runtime PhysX values match the authored values. Friction is provisionally 0.8 static / 0.6 dynamic, with zero restitution. These assumptions require later measurement and robustness testing.

Raw native contact reporting must explicitly turn off Lab's default `disableContactProcessing` setting. The evaluator does so. Knife sleeping is disabled to retain board-support measurements. An initial settling test with missing force reports is retained as a failed diagnostic, followed by the corrected test.

## Completed physical and logic checks

- 28 isolated knife fixtures settled on the board, with central placements included. Each remained fully within the board, nearly motionless, with approximately 2.45 N board support and no counter support. The robot was inactive in this fixture; this is not a robot pickup result.
- A seeded sampler checked 1,000 valid flat placements with a 20 mm full-footprint margin. Rejected proposals are counted, not silently treated as policy failures. All 20 sampled pre-approach IK targets solved within the declared tolerances; their routes and grasp contacts remain unvalidated.
- Native tests passed with self-collision enabled, the left arm parked, and all 36 joints present. A separate empty-hand cycle closed the four fingers before thumb flexion and exercised passive finger coupling. This is not evidence of contact sequencing around a knife.
- The independent detector rejected actual board-supported knife samples during the native runs, with no false success. Unit fixtures reject fingertip-only contact, board support even when force is zero, drops, insufficient/transient lift, excessive slip, blade/unsafe contact, attachments, limit violations and contact-buffer saturation. Synthetic wrap fixtures pass across rotated cross-sections. **Synthetic positives are not physical positive examples.**

The original knife is approximately **43.8 cm long**, while the board is **46.9 × 29.9 cm**. With the full knife and a 2 cm margin inside the board, valid centres and yaws occupy a restricted region. The 1,000 accepted centres span only about 14.3 × 6.6 cm. Do not claim arbitrary positions/yaws across the entire board. No source asset was rescaled to hide this limitation.

## Frozen provisional success definition

The reward-independent evaluator requires the handle to rise at least 5 cm above its settled initial height and remain held continuously for 3 seconds. Final contact must include the palm, an opposed thumb and at least three curled, contacting fingers; at least two fingers must contact proximal links or at least 15 mm away from their tips. Contact points must surround the handle cross-section, with no angular gap over approximately 180 degrees. Total finger curl must be at least 115 degrees. Slip relative to the palm must stay within 10 mm throughout the hold window.

Both measured support forces and geometric clearance are checked; a sleeping body reporting zero force cannot masquerade as unsupported. Blade/unsafe contact, attachments, limit violations and saturated contact buffers invalidate the episode. Simulated contacts and object truth are evaluator-only and are excluded from the probe actor observations. The fingertip PCA estimate and cross-section test still require visual and physical-positive validation before they can be trusted as a training acceptance oracle.

## Remaining Phase 3 acceptance work

1. Demonstrate a representative physical wrap and lift in the new native scene, then validate the detector against synchronized contact points and images. The old scripted edge demonstration uses different dynamics and is not a new-scene positive.
2. Establish acquisition from a flat, central placement. Controlled nudging/rotation is allowed, but no attachment or in-episode knife teleport is permitted. Neither an empty-hand closure nor IK reachability establishes this feasibility.
3. Exercise blade contact, slipping, drops and failed acquisition as actual physical negative examples, not only unit fixtures. Confirm buffer capacity and hand/handle surface classification during rich contact.
4. Validate collision-free routes and reachable placement/orientation groups, including the away-from-edge subset. Record exclusions and decide whether the oversized knife/board combination represents the intended physical setup before widening the distribution.
5. Calibrate or explicitly bound uncertain actuator, mass and friction properties. Hardware tactile capability remains unknown and is not assumed.

**Training readiness is NO-GO until these Phase 3 checks pass.** There is no trained pickup policy or trained vision system in these results.

## Memory safeguards and reproduction

All simulator launches use the same controller lock and existing RAM/VRAM guard. Startup still requires 10 GB available RAM and 4 GiB free VRAM. Checkpoint/stop reserves remain 3,000,000 / 2,000,000 Linux kB for RAM and 1.5 / 1 GiB for VRAM. The watchdog has bounded runtime, process-group termination, monitoring-failure handling, and requires an explicit passed result rather than relying on the simulator's exit code.

Use `run_rl_benchmark.sh --native` for the small native interface check, `--phase3` for the derived collision scene, `--phase3 --hand-cycle` for the empty-hand diagnostic, or `--phase3-fixtures` for isolated knife settling. Always supply a new `--output` directory and a bounded `--seconds` value. These modes do not train. See `rl/README.md` for concrete commands and `phase3_summary.json` for the final evidence paths and resource measurements.
