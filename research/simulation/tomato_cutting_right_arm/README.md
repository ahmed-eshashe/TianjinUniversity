> **7 November update:** See [snapshot status and limitations](REPOSITORY_SNAPSHOT.md) and [learning checklist](docs/progress/learning-roadmap.html). The scripted cut remains incomplete; the material and robot tests below are historical unless explicitly dated.

# Tomato cutting — clean simulation workspace

## Vision based RL development

The current project direction is camera-based learned knife pickup. The user has authorized Phase 1 auditing and Phase 2 bounded resource testing; full grasp training has not started. The scripted grip sections below are preserved historical baselines.

- [Complete plan for Sol](RL_VISION_KNIFE_PICKUP_PLAN.md)
- [Phase 1 software and robot interface audit](docs/rl/PHASE1_AUDIT.md)
- [Current phase status](docs/rl/PHASE_STATUS.md)
- [Phase 2 resource results](docs/rl/PHASE2_RESULTS.md)
- [Bounded benchmark commands and memory protection](rl/README.md)


## Current nearer-grip experiments

The previous accepted launcher below is preserved while the new arrangement is being tested. `run_closer_grasp_experiment.sh` is experimental: it aligns the original board with the countertop, deactivates the original spare knife in the session, and moves the board/knife together to an accessible counter edge. These scene edits have been verified, but the nearer physical grasp has **not** passed the complete wrapped-grip validation. Do not interpret the small clearance pickup as an accepted grip-and-lift result. No attachment or commanded knife motion is used after physics begins.

The experiment doubles planned arm travel speed from 6 to 12 degrees/second and finger closure from 6 to 10 degrees/second. Settling now renders once per eight physics steps instead of every step; the physics rate stays 240 Hz. Actual wall-clock speed still depends on rendering and contact computation. The unchanged memory watchdog and contact/IK stops remain active. Larger shifts toward the blade have either contacted the blade/board or held the handle diagonally without the required finger enclosure, so they remain rejected. The previous accepted configuration and reports remain available below.

## Previous accepted right-hand cutting grip

From a desktop terminal, run:

```bash
/home/omen/teamwork_projects/tomato_cutting_right_arm/run_kitchen_grasp.sh --gui --interactive --close-camera
```

No environment activation is needed. The fingers start closing while the thumb stays open. After two fingers support the handle above 0.1 N for 0.15 seconds, the thumb closes and the hand completes its squeeze. The index starts one second after the other fingers to reduce uneven seating. Incidental contact with the stationary thumb is recorded separately; this does not claim all four fingers fully clamp before any thumb touch. The knife lifts about 6 cm, then the wrist turns so the blade exits the thumb/index side, points away from the robot, and presents its cutting edge toward the board. The final camera shows the blade and hand. Close the window to stop; omit `--interactive` for a finite test that closes automatically.

This is programmed arm motion with contact-force feedback, using the simulator's handle pose. It has no vision detection or RL training. The object is the original `/Indoor/RZ/SM_kitchen_knife_02` inside the kitchen asset: no duplicate knife or grasp attachment. The existing knife and board are reoriented in the session before physics (knife yaw 120 degrees, other blade face downward); the robot base is adjusted to a screened stance. After physics starts, the free knife is moved only by contact. Source assets and the hand linkage remain unchanged.

Two finite tests passed the unchanged wrapped-grasp checks and the new orientation/closure-order checks. At least three fingers curl around and contact the handle, with palm/opposed-thumb support and at least two contacts on proximal links or pads at least 15 mm from their tips throughout all 24 samples of a three-second hold. Headless trial18 lifted **57.53 mm** with **1.75 mm** relative slip; index/middle inner contact persisted throughout. Visible trial19 lifted **59.22 mm** with **0.07 mm** relative slip; index/middle/ring inner contact persisted throughout. Knife–board force was zero throughout both holds. Blade direction, edge-down orientation and fingers-first closure passed in both runs. New inspected captures are `logs/cooking_trial19_pose.png`, `cooking_trial19_end.png` and `cooking_trial19_fingers_seated.png`.

Validation reports are `logs/kitchen_grasp_validation_report.json` and `logs/kitchen_grasp_gui_validation_report.json`, with matching `*_validation_memory.json` files. Exact configuration and evidence hashes are in `work/validated_grasp_configuration.json` and `work/validated_cooking_grasp_evidence.json`. Prior wrapped settings/results are preserved under `run_kitchen_wrapped_pre_photo.sh`, `work/validated_wrapped_pre_photo_configuration.json` and `logs/kitchen_wrapped_pre_photo_*`; that older grip had the wrong blade direction for cutting. The original fingertip demonstration remains `run_kitchen_pinch.sh`.

The unchanged memory watchdog permits only one controller, requires 5 GB available RAM to start, and stops below 2 GB. Both accepted runs exited normally without a crash. Peak resident memory was 8.146 GB headless and 8.212 GB visible; minimum available RAM was 3.878 GB and 3.930 GB respectively. Finger torque stays capped at 0.3 Nm and thumb torque at 1 Nm. Finger and thumb distal-pad pressure targets are 4 N, with a separate thumb-opposition force cap of 20 N and the existing global contact stops. Friction/compliance remain provisional and uncalibrated; robot self-collision remains disabled. A 60-sample parked-arm/torso screen passed, with runtime kitchen contact and reachability guards. These finite tests validate the stated arrangement and three-second hold, not extended holding, arbitrary positions or cutting under load. Interactive mode continues monitoring wrap, lift, cutting orientation and memory.

## Historical position tests — previous grip orientation

The results below belong to the previous grip preserved in `run_kitchen_wrapped_pre_photo.sh`; they do not validate the new cutting orientation at other positions. The finite test runner checks the original location and four 5 cm translations in world X/Y. The robot base, ready pose, hand orientation, gains and wrap acceptance criteria stay fixed. Only the original kitchen knife and its supporting board are translated before physics starts; the board keeps its validated handle overhang. The controller reads the settled handle pose from the simulator and solves the arm path again. This tests local translation handling, not learned perception, rotated handles, flat-counter pickup or arbitrary kitchen locations.

Results from one finite trial per position on 2026-10-18:

| World XY offset (cm) | Wrapped grip and lift | Lift | Relative slip |
| --- | --- | --- | --- |
| (0, 0) | Pass | 27.29 mm | 2.78 mm |
| (+5, 0) | Fail: inner wrapped contact not retained throughout hold | 30.78 mm | 10.06 mm |
| (-5, 0) | Controlled stop: descent waypoint unreachable | — | — |
| (0, +5) | Pass | 30.18 mm | 8.58 mm |
| (0, -5) | Pass | 28.74 mm | 1.67 mm |

Three of five placements passed all unchanged wrap/lift criteria, including a three-second hold. This is a limited translation test, not an estimate of repeatability or arbitrary-location performance. All five attempts ended normally at the process level; acceptance failures stopped deliberately. Peak RSS ranged up to 8.221 GB and available RAM stayed at or above 3.517 GB. Actual settled offsets matched requested offsets within 0.2 mm, and the saved configurations confirmed identical controller settings except placement. Evidence: `logs/position_tests_20261018/summary.json`, `placement_audit.json`, and per-case reports/logs in that folder. These saved results used the previous grip configuration. A separate visible repeat at (0, -5 cm) also passed: 27.36 mm lift, 2.71 mm slip, three-second wrapped hold. Its side/end images were inspected and are saved under `logs/position_tests_20261018/visual_repeat_y_minus_5cm/`. The visible repeat peaked at 8.242 GB RSS and retained at least 3.808 GB available RAM.

```bash
/usr/bin/python3 /home/omen/teamwork_projects/tomato_cutting_right_arm/scripts/test_grasp_positions.py
```

New runs of this command use the current cutting-grip launcher. Use a new output folder for this profile; do not combine it with historical results. Each trial starts a fresh simulator through the same memory watchdog, one at a time. Reports and logs are saved after each attempt in a timestamped `logs/position_tests_*` folder. A launch refusal or memory stop ends the batch. A normal grip/reach failure is recorded and the next position is tested. The batch returns a nonzero result if any acceptance check fails; this does not mean the simulator crashed. Use `--output /absolute/path/to/existing/position_tests_folder` to resume and skip recorded cases, or `--case x_plus_5cm` to select one case in a new output folder.

To watch one position directly:

```bash
/home/omen/teamwork_projects/tomato_cutting_right_arm/run_kitchen_grasp.sh --test-offset-xy .05 0 --gui --interactive --close-camera
```

Offsets are metres in the scene's world X/Y axes and limited to 15 cm from the baseline. Zero offset retains the default grip demo. Placement edits stay in the disposable session layer; the knife is never attached or repositioned during the grasp or lift.

## Launch the full scene

From a normal desktop terminal:

```bash
/home/omen/teamwork_projects/tomato_cutting_right_arm/run_scene.sh
```

This uses the Python interpreter in `isaaclab_6` explicitly. No environment activation is required. It opens a paused preview through Isaac Lab's AppLauncher. Close the window to exit. The original assets are composed as a sublayer into a disposable stage, so the kitchen and knife are included alongside the robot. The script does not save changes to the source USD.

Optional bounded preview: `./run_scene.sh --steps 300`.
Full-kitchen physics remains unverified and previously exhausted RAM. Use the robot-only controller below for physics tests.
This is not a controller or an RL training environment. Existing scene velocities, drive settings, and hand coupling have not yet been corrected.

## Files

- `scripts/load_scene.py`: complete scene preview and optional physics launch.
- `scripts/scene_stage.py`: shared USD composition and GPU-independent inspection.
- `logs/scene_preflight.json`: last composition inspection.
- `assets/`: preserved assets and scene files.
- `ros2_ws/src/ar5_o6_right_description/`: preserved robot descriptions and referenced geometry/USD files. Kept at the original paths deliberately.
- `archive/code_restart_20261017_181810/`: archived scripts, tasks, package metadata, logs, MoveIt configuration, and ROS build/install outputs. `manifest.json` records original relative paths and SHA-256 hashes. Restore individual items to their recorded paths if required; do not overwrite the new scripts folder wholesale.

## Environment findings

Two desktop shortcuts are named Isaac Sim. `IsaacSim.desktop` launches the installation in `isaaclab_6` directly. `isaac-sim.desktop` launches `/home/omen/run_isaac.sh`, which activates `isaaclab_6` after sourcing ROS 2 Jazzy and calls `isaacsim`. Installed Isaac Sim package: 6.1.0.0. Isaac Lab is editable at `/home/omen/IsaacLab`; its VERSION file says 3.0.0, while installed package metadata reports 19.0.0. This checkout uses `--visualizer kit`, not the older `--headless` CLI flag.

## Verification and outstanding issues

USD preflight confirmed 3,682 composed prims, the robot articulation root, 36 robot revolute joints, the kitchen, and the dynamic knife path. Run it without starting the simulator:

```bash
/home/omen/miniconda3/envs/isaaclab_6/bin/python /home/omen/teamwork_projects/tomato_cutting_right_arm/scripts/scene_stage.py
```

One pre-existing composition error remains: the external kitchen references a missing `UnitsAdjust-238947e75d6c04db8e8a7b24e401cb90.metricsAssembler` layer. Its contents are unknown, so it has not been fabricated or removed. The kitchen still depends on `/home/omen/Aperdata-SimReady-Kitchen-01`; keep that folder.

The full scene was subsequently rendered successfully. Kernel logs confirmed out-of-memory kills during full-scene runs. The paused preview now disables accessible collision shapes in its disposable layer; do not use it for physics validation.

Next milestone: validate the scene visually and then establish deterministic reset and right arm/hand control before designing the RL reaching task.

## Right-arm physics and manual control

Launch the lightweight robot-only scene with a seven-slider control panel:

```bash
/home/omen/teamwork_projects/tomato_cutting_right_arm/run_right_arm.sh --gui --interactive
```

For a finite physics test without a window, run the same launcher without arguments. Every launch tests the seven right-arm joints before enabling manual controls. The arm starts at the simulator's zero-joint pose, not the saved kitchen pose. Each slider uses degrees, is restricted to +/-10 degrees about the starting pose and the authored joint limits, and commands at no more than 5 degrees/second. The return button restores the starting targets. Left-arm and finger targets remain fixed.

The authored hand collision group included the entire stage and filtered contacts within it. The test restricts that group to its explicit hand members in the disposable stage.

The test uses CPU PhysX at 120 Hz with gravity, a fixed robot base, 44 convex-hull mesh colliders, and a ground plane. A falling block checks gravity and ground contact. Self-collision is disabled. Kitchen collisions, grasping, finger coupling, knife contact, deformable cutting, hardware-rated torque limits, and sim-to-real behavior are not validated. Motor gains are provisional simulation settings.

Only the robot prim is referenced from the existing scene. All overrides are in memory; source USD assets are not saved. A single-instance launcher requires at least 5 GB available host RAM and stops the process if available RAM falls below 2 GB. This reduces memory risk but cannot guarantee against every crash. Close any other Isaac Sim window before launching.

Results: `logs/right_arm_physics_report.json`, `logs/right_arm_memory_report.json` (written on exit), and `logs/right_arm_gui.log` for the current session. The first bounded run peaked at approximately 6.84 GB process RSS and exited normally.

## Kitchen knife approach

Launch the restored kitchen with a tested open-hand approach:

```bash
/home/omen/teamwork_projects/tomato_cutting_right_arm/run_kitchen_reach.sh --gui --interactive
```

The target is the **existing kitchen knife** `/Indoor/RZ/SM_kitchen_knife_02`. Its composition includes `/Root/RZ/SM_kitchen_knife_02` in the original `Indoor.usd`; the script does not spawn or copy another knife. The kitchen also contains knife_01, which is not the target. The target knife starts at its authored elevated position, then falls onto the original cutting board under gravity. Its handle target is calculated from Section2 of the original knife mesh after settling.

The left arm is initialized in its zero-joint pose to clear the approach. The right arm initializes at a raised ready pose with an open hand; it does not traverse from the previous saved kitchen pose. Joint-drive motion then takes the palm to 12 cm above the settled handle. The panel provides Return to raised ready pose and Reach above knife handle. No grasp, knife lifting, or cutting is performed.

`work/kitchen_reach.usda` references the original robot and kitchen. Simple materials replace kitchen textures/MDL only in this derived scene. Twelve nearby kitchen meshes have collision enabled; static meshes use triangle collisions, the dynamic knife and robot meshes use convex hulls. Distant objects remain visual. Cabinet joints are disabled, and the hand collision collection is restricted to its explicit members. Runtime changes use an unsaved session layer. Original assets remain untouched.

`reach_kinematics.py` derives FK/IK from USD joint frames. Forty Cartesian waypoints use bounded joint solutions; joint targets are limited to 6 degrees/second. The controller verifies actual hand pose, checks distal-link height over the worktop, monitors right-arm contact force, tracking error, finite state, and unexpected knife displacement. A separate 41-waypoint convex-hull screen checks the right arm against the left arm and torso (excluding the proximal shoulder attachment) and rejects overlaps larger than 2 mm. See `logs/kitchen_reach_clearance.json`. Self-collision remains disabled; this is not a complete collision-aware motion planner. Gains and inertial/contact settings remain provisional.

First finite validation: palm target error 0.24 mm; palm clearance 119.76 mm; no detected right-arm contact; left-joint drift 0.035 degrees; peak process RSS 8.16 GB with at least 4.12 GB host RAM available. See `logs/kitchen_reach_report.json` and `logs/kitchen_reach_status.json` for the latest results. Watchdog protection and single-instance locking are the same as the robot-only controller; no guarantee against every crash.

Implementation: `scripts/prepare_kitchen_reach.py`, `scripts/reach_kinematics.py`, `scripts/kitchen_reach.py`, `scripts/guarded_reach.py`, and `work/reach_seed.json`. Preparation uses the isaaclab_6 Python interpreter without starting the simulator. Close the running simulator before regenerating the derived scene.

## Scripted fingertip pinch and lift (baseline)

Launch the preserved baseline pinch-and-lift demo:

```bash
/home/omen/teamwork_projects/tomato_cutting_right_arm/run_kitchen_pinch.sh --gui --interactive --close-camera
```

The right hand approaches with shaped fingers, pinches the kitchen's existing knife handle between finger pads, then lifts it. This baseline is a fingertip pinch, not a human-like power grasp. The knife remains a free rigid body: no attachment, duplicate knife, or commanded knife motion is used. The visible scene holds the grip after the test passes. Closing the window stops the simulation.

This setup moves the robot base about 14.5 cm closer and shifts the existing cutting board about 14 cm toward the blade, leaving the handle overhanging. The grip sits nearer the blade end of the handle to reduce its turning load. The left arm stays parked. All placement, collision and material changes are in an unsaved session layer; original robot and kitchen assets remain unchanged.

The pinch-and-lift stability checks passed; they did not validate an enveloping grasp: **29.61 mm knife lift**, **0.385 mm relative slip in the hand frame**, three-second stable hold (0.402 mm height range), and **zero knife–board contact throughout the hold**. Thumb, index and ring contacts remained active. Peak process RSS was **8.132 GB**, with at least **4.518 GB RAM available**. The single-instance lock and 2 GB available-RAM watchdog remain active. Evidence: `logs/kitchen_pinch_validation_report.json`, `logs/kitchen_pinch_validation_memory.json`, and `logs/grasp_trial53.log`. The latest visible run writes `logs/kitchen_grasp_report.json` and phase/configuration information in `logs/kitchen_grasp_status.json`.

Fingertips use a provisional compliant contact model: stiffness 15,000 N/m, damping 60 N s/m, torsional patch radius 6 mm, static/dynamic friction 1.2/1.0. The knife is rigid, with mass 0.25 kg and separate blade/handle convex hulls on the same existing body. Finger joint torque is capped at 0.6 N m and thumb torque at 3 N m; mimic followers remain passive with DIP/MCP ratio 0.89 and thumb IP/CMC ratio 1.86. These simulation values are not hardware calibration.

Physics runs at 240 Hz on the CPU. Motion uses joint drives and bounded IK. Guards stop on non-finite state, unexpected velocity, arm tracking error, arm or parked-body contact above 5 N, hand–board contact above 5 N, or hand contact above 60 N. Interactive holding also detects a dropped knife. `scripts/check_grasp_clearance.py` samples the arm route against the left arm and torso. Robot self-collision remains disabled, kitchen materials/collisions are simplified, and this is a validated grasp for this arranged scene rather than a general grasp planner.

The preserved pinch configuration is `work/validated_pinch_configuration.json`; `run_kitchen_pinch.sh` supplies those settings. Experimental geometry searches and test modes remain available in the scripts for further development.

## Learning versus scripted motion

No reinforcement learning has been run for this grasp. There is no trained policy, reward optimization, or learned grasp controller in the launcher. The controller reads the knife handle pose directly from the simulator after it settles, solves inverse kinematics for a programmed approach, and sends programmed finger and lift targets to simulated motors. Contact forces and slip are measured for validation. It is tailored to this arranged scene; recognizing a moved knife or generalizing to new placements has not been validated.

The wrapped-grip launcher enables `--require-wrap`. `--require-wrap` additionally requires palm and thumb contact, three fingers that curl past the handle centre with handle contact, contact at least 15 mm away from the fingertips on at least two fingers (or proximal finger contact), and a handle position near the palm. A lift alone cannot pass this mode. `scripts/search_wrap_grasp.py` screens geometry before physics. Only the configuration saved in `work/validated_grasp_configuration.json` is the current tested wrapped-grip setup; other experimental poses are not validated launch configurations. The single-instance and RAM safeguards remain enabled for every physics trial.
