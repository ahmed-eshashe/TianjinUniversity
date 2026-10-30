# Phase 1 and Phase 2 resource tools

These tools audit the existing robot and benchmark a single minimal simulated environment. They do not train knife pickup. The only learner is a small, bounded PPO allocation probe with a posture reward. Its RGB-D encoder is untrained and does not identify a knife.

## Audit and derived scene

Run the following with no simulator active:

```bash
cd /home/omen/teamwork_projects/tomato_cutting_right_arm
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /home/omen/miniconda3/envs/isaaclab_6/bin/python rl/audit.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /home/omen/miniconda3/envs/isaaclab_6/bin/python rl/prepare_benchmark_scene.py
```

The audit records package versions, source commit, joint limits, mimic relationships, hardware unknowns and baseline hashes under `docs/rl/`. It executes a small CUDA operation, without launching Isaac Sim or connecting to hardware. The scene preparation composes a separate derived USD and manifest in `rl/scene/`. It preserves the original geometry and does not save edits to the source robot or kitchen.

## Bounded benchmark

Every run requires a new output directory. The examples below are commands for future use, not additional test results.

```bash
# Physics and small PPO updates, no camera
bash /home/omen/teamwork_projects/tomato_cutting_right_arm/run_rl_benchmark.sh \
  --output /home/omen/teamwork_projects/tomato_cutting_right_arm/runs/rl/manual_state_probe \
  --seconds 60 --max-updates 4

# One RGB-D camera and a small untrained encoder
bash /home/omen/teamwork_projects/tomato_cutting_right_arm/run_rl_benchmark.sh \
  --output /home/omen/teamwork_projects/tomato_cutting_right_arm/runs/rl/manual_camera_probe \
  --seconds 60 --max-updates 4 --camera
```

Optional `--resume /absolute/path/to/checkpoint.pt` restores the learner, optimizer, running observation statistics, counters, resource-probe curriculum marker, and random-generator state. Resume begins a fresh physical episode; in-flight contact solver state is not restored. Only load checkpoints created and trusted by this project.

Camera resolution is selectable with `--width 64`, `96` or `128`. One environment, CPU PhysX at 240 Hz, GPU PyTorch, 20 Hz simulated action and camera rates, and 13 bounded independent-joint targets are fixed for this probe. Wall-clock throughput is measured separately. This Core World benchmark is not a native Isaac Lab vectorized task.

Run length is bounded to 10–1800 seconds and at most 24 tiny PPO updates. Full grasp training has no entry point here.

## Memory protection and stopping

The launcher shares `logs/right_arm_control.lock` with the scripted robot controllers. It refuses concurrent controllers. Based on measured startup cost, it requires **10 GB available host RAM and 4 GiB free GPU memory** before launch. This is stricter than the original controller's 5,000,000 Linux kB startup minimum. Close other large applications before starting it.

- Below 3,000,000 kB available RAM (3.072 GB) or 1.5 GiB free VRAM: request a checkpoint and graceful stop.
- Below 2,000,000 kB available RAM (2.048 GB) or 1 GiB free VRAM: terminate the child process group.
- Repeated GPU-monitoring failure or a shutdown timeout also stops the child.
- A 30-second checkpoint interval preserves progress before resource exhaustion. Only the latest checkpoint is retained per run.

Close the terminal run with Ctrl+C to terminate the simulation. To request a graceful checkpoint stop instead, create `checkpoint_and_stop.request` inside that run's output folder. A reserve/interruption stop is recorded as incomplete; it is not a passed stability test. Do not run a full-kitchen viewer concurrently.

## Evidence and limitations

Each output directory contains `simulation.log`, `resources.jsonl`, `memory_report.json`, configuration/hashes, progress, a checkpoint, and either `result.json` or `failure.json`. Camera runs additionally save a sample RGB image, raw depth and camera checks. Isaac Sim can exit with code zero after a Python exception, so the guard requires an explicit passed result before returning success.

The robot, parked arm, original knife geometry, board and countertop remain in the scene. The knife begins over the board centre and is moved directly only at explicit episode resets. Hand/blade collision uses separate convex hulls on the same free rigid body. This establishes resource feasibility for the stated workload, not grasp quality, learned perception, whole-board reachability, self-collision readiness or physical deployment.

Self-collision remains disabled in this resource probe and must be addressed in Phase 3. Provisional simulation drives are not measured hardware limits. The environment's package consistency issues are recorded in `docs/rl/dependency_check.txt`; do not perform blind upgrades to make the check disappear.

The complete staged scope remains in `RL_VISION_KNIFE_PICKUP_PLAN.md`. The user subsequently authorized dependency repair, native integration and Phase 3 continuation. Full training remains prohibited. Read `docs/rl/NATIVE_INTEGRATION_AND_PHASE3.md` and `phase3_summary.json` for the current partial Phase 3 status.

## Native and Phase 3 checks

These bounded modes use the project-local `.venv-native` overlay, preserve the original environment, and use the same watchdog and controller lock. They have no optimizer or training runner. Every output directory must be new.

```bash
bash /home/omen/teamwork_projects/tomato_cutting_right_arm/run_rl_benchmark.sh \
  --native --output /home/omen/teamwork_projects/tomato_cutting_right_arm/runs/rl/manual_native_check \
  --seconds 15

bash /home/omen/teamwork_projects/tomato_cutting_right_arm/run_rl_benchmark.sh \
  --phase3 --hand-cycle --output /home/omen/teamwork_projects/tomato_cutting_right_arm/runs/rl/manual_empty_hand_check \
  --seconds 30

bash /home/omen/teamwork_projects/tomato_cutting_right_arm/run_rl_benchmark.sh \
  --phase3-fixtures --output /home/omen/teamwork_projects/tomato_cutting_right_arm/runs/rl/manual_knife_settling \
  --seconds 30
```

The hand cycle closes an empty hand; the fixtures deactivate the robot to isolate knife/board dynamics. Neither is a successful knife pickup. Native physical modes do not use a camera and do not accept learner resume arguments. Early-stop files save validation progress rather than learner state.

Dependency runtime checks: run `.venv-native/bin/python rl/dependencies/verify_runtime.py` from this project. The overlay inherits `isaaclab_6`; do not remove or upgrade that base blindly. `overlay-requirements.txt`, `effective-freeze.txt`, `check_after.txt` and the installation log describe the local repair. Six known metadata conflicts remain because Isaac Lab deliberately overrides older Sim dependency pins; the verifier checks their exact set and exercises the used libraries.

## Central pickup diagnostics (currently failing)

`docs/rl/CENTRAL_GRASP_RESULTS.md` records the physical central-pickup attempts. They did not establish a firm wrapped pickup. To reproduce the current bounded pad-directed diagnostic, use a new output folder:

```bash
bash /home/omen/teamwork_projects/tomato_cutting_right_arm/run_rl_benchmark.sh \
  --phase3-grasp --grasp-plan pad-aware --candidate 1 \
  --output /home/omen/teamwork_projects/tomato_cutting_right_arm/runs/rl/manual_central_pickup \
  --seconds 180
```

This runs a scripted physical diagnostic, not a trained policy. Initial temporary pinch contact is permitted, but the final palm/three-finger wrap, 5 cm lift and 3 second unsupported hold remain mandatory. Force, blade, board and self-contact stops reject the run. Failed acquisition is not reported as successful because the arm completed a motion. Native rendering/vision training is not enabled by this mode. Individual runs retain actual trajectories and code/configuration snapshots.

## Contact-only in-place tilt diagnostics

Add `--in-place-tilt pitch`, `roll-positive`, or `roll-negative` to a `--phase3-grasp` command. These are **experimental, unvalidated pickup paths**. They command only the hand: a 3 mm hand-clearance motion, then up to an 8° supported pitch arc with optional ±12° roll. The latest path transitions to an early wrap once measured handle rise reaches 10 mm, and limits the subsequent seating descent to 3 mm. The knife remains a free body and can move only through physics after reset. The latest controller uses a lighter provisional preload (2 N finger / 3 N thumb target) during this supported phase; original drive effort limits remain unchanged.

Small contact moves preserve the arm’s existing load-holding command offset instead of resetting targets to sagged measured joints; a measured position offset above 2 cm rejects the move. A regression test verifies that zero relative motion preserves the prior command.

The measured full knife footprint must stay at least 5 mm inside the board, its centre must remain within 3 cm of the settled position, and its orientation must remain within 20° of the settled pose. Existing blade, board, self-contact, speed, joint and memory stops still apply. Hand motion alone does not count as knife clearance: at least 8 mm measured handle rise is required before seating, and the unchanged final wrap/lift/hold oracle is still required for a pass. These diagnostics do not enable a camera or learner.

For example, append `--in-place-tilt pitch` to the central pickup command above and choose a fresh output folder. Results and stop reasons are recorded in `docs/rl/in_place_tilt_results.json` and `IN_PLACE_TILT_RESULTS.md`.

## Supported palm seating continuation

`docs/rl/PALM_SEATING_RESULTS.md` records the current failures and the improved supported clearance. `--seating-mode adaptive` uses measured object-pose feedback to attain more clearance, followed by coordinated seating. `coordinated` retains the simpler diagnostic for comparison. `mesh-guided` follows the near-contact endpoint in `docs/rl/refined_supported_wrap.json`; its tested transition also failed. These modes require `--phase3-grasp --in-place-tilt`; none starts a learner. All modes remain experimental, and no firm wrapped pickup has passed.

```bash
bash /home/omen/teamwork_projects/tomato_cutting_right_arm/run_rl_benchmark.sh \
  --phase3-grasp --grasp-plan pad-aware --candidate 1 --in-place-tilt pitch \
  --seating-mode adaptive --seconds 240 \
  --output /home/omen/teamwork_projects/tomato_cutting_right_arm/runs/rl/manual_palm_seating
```

Choose a fresh output folder. The knife is moved directly only during the initial reset. The controller repeats the physical approach and clearance before seating; a validation checkpoint does not restore ongoing contact state. New modes stop on persistent pinch loss and include a conservative thumb-posture check; these are provisional software guards, not verified hardware limits. Final acceptance, existing force/contact stops, memory reserves and the single-controller lock remain mandatory.


## Contact preserving seating diagnostic

`--seating-mode contact-path` uses `docs/rl/contact_seating_plan.json` and requires `--phase3-grasp --in-place-tilt pitch`. It remains a scripted feasibility check. The active seven-waypoint plan only covers a limited intermediate movement; completing that path does not certify seating or lifting. The worker snapshots the loaded plan, synchronizes wrist/finger interpolation and stops above 3 mm tracked-point error or 2 mm additional lateral knife-centre drift. It records a bounded physics-step trace. The unchanged palm/three-finger contact gate refuses lift when support is inadequate.

Latest result and limitations: `docs/rl/CONTACT_SEATING_RESULTS.md`. To reproduce, use the guarded launcher with a fresh output folder:

```bash
bash /home/omen/teamwork_projects/tomato_cutting_right_arm/run_rl_benchmark.sh \
  --phase3-grasp --grasp-plan pad-aware --candidate 1 --in-place-tilt pitch \
  --seating-mode contact-path --seconds 240 \
  --output /home/omen/teamwork_projects/tomato_cutting_right_arm/runs/rl/manual_contact_seating
```

No full training is enabled by this command. Offline planners are geometry proposals, not acceptance tests, trained policies or physical attachments.


## Contact transfer continuation

See `docs/rl/CONTACT_TRANSFER_RESULTS.md` for the latest failed transfer diagnostics. The active contact-path configuration now uses the experimental rolling controller with the original contact model. It refreshes measured contact references between bounded increments while retaining the fixed global knife-centre drift limit. It has not achieved a stable handoff, power grasp, or lift. The earlier seven-waypoint configuration is preserved in the source snapshot for `runs/rl/phase3/contact_seating_04`.

Material sensitivities are separate files. `contact_transfer_plan_patch2mm.json` did not improve the tested motion; `contact_transfer_plan_patch_min1mm.json` remains unexecuted because the memory reserve refused startup. These are uncalibrated contact assumptions. The active configuration uses neither override. All runs must use the guarded launcher and a fresh output folder. No full training is authorized or enabled.

## Offline grasp checks after Astra review

Read `docs/rl/OFFLINE_GRASP_CHECK_RESULTS.md` before another physical test. The offline tools inspect the composed USD, existing candidates and stored trajectories; they never launch Isaac Sim or modify the active controller, assets, criteria or guard. Convex envelopes of decomposed shapes are not cooked colliders, and contact proximity is not loaded contact.

Reproduce the offline analysis with one numerical thread:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /home/omen/teamwork_projects/tomato_cutting_right_arm/.venv-native/bin/python \
  /home/omen/teamwork_projects/tomato_cutting_right_arm/rl/offline_grasp_audit.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /home/omen/teamwork_projects/tomato_cutting_right_arm/.venv-native/bin/python \
  /home/omen/teamwork_projects/tomato_cutting_right_arm/rl/offline_controller_replay.py
```

These commands regenerate only their analysis JSON files in `docs/rl/`. Physical tests still require the guarded launcher and sufficient startup memory. Current authorization requires reporting the offline findings before physical testing; no full training is enabled.

## Inner surface refinement and bounded diagnostics

The subsequent offline proposals and evidence are in `runs/offline/grasp_refinement_01/`; read `docs/rl/INNER_WRAP_REFINEMENT_RESULTS.md`. Neither proposal is active or physically validated. `refine_inner_wrap.py`, `polish_inner_wrap.py` and `validate_inner_wrap.py` contain the bounded geometry workflow; their current paths refer to that work directory. Preserve its archived results when preparing any further experiment.

During a future guarded contact-path run, `central_grasp.py` saves `command_diagnostics.json` with at most 96 command records and `seating_substeps.json` with at most 96 physics records. Each raw frame caps normal/friction point lists at 96 and pair summaries at 64; indices refer to accompanying name tables, and truncation/calibration flags must be inspected. The command record separates intermediate projected displacement from final desired/applied targets. Contact shape/feature IDs are unavailable through the current backend API. The original oracle contact filtering and final criteria are unchanged.

This instrumentation compiles and passes offline regression checks but has not been run in Isaac Sim. Validate timing, direction/separation conventions and logging overhead on simple known contacts before interpreting a new hold-versus-motion test. Full training remains paused.

## Offline load support audit

See `docs/rl/LOAD_SUPPORT_RESULTS.md` and `runs/offline/load_support_01/`. The independent mass check and finite contact solver are in `knife_mass_audit.py` and `contact_load_model.py`; surface, layout and orientation analyses are in `multipoint_load_audit.py`, `refine_load_support.py`, `optimize_load_layout.py`, `validate_oriented_support.py` and `assess_support_sensitivity.py`. These tools do not launch Isaac Sim or write USD assets. Preserve the archived evidence before reusing their fixed result paths.

`docs/rl/load_support_candidate.json` is an inactive mathematical terminal proposal. Its 90-degree axial roll gives conditional load support and preserves the outward blade axis, but exceeds the existing 20-degree in-place diagnostic bound. It is not consumed by the active controller. Do not replace the active contact plan or bypass that motion check to test it. Positive contact gaps, cooked geometry, terminal retention and the route from a flat reset remain open; full training remains paused.
