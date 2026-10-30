# Vision based reinforcement learning knife pickup plan for Sol

Prepared 19 October 2026. Owner: the user. Implementation agent: Sol.

## Status and execution boundary

This is a planning handoff. Creating this file does not authorize implementation, installation, simulation, training, or hardware operation. Wait for the user's instruction to begin. Once implementation is requested, follow the phases below in order and record their results. Physical robot trials require a separate explicit instruction and the hardware readiness checks in Phase 9.

The objective is a learned right-hand policy that uses robot-mounted vision to locate the kitchen knife, manipulate its handle if needed, form a physical wrapped grasp, and lift it from varied flat placements on the cutting board. The eventual physical robot will use the same arm and hand models as the simulation. Tactile sensing is unconfirmed.

## Agreed scope

- All development and training must run on the user's laptop. No cloud training.
- Start with one simulated RGB-D camera near the head or upper torso, viewing the board.
- Use the existing kitchen knife asset, including its handle and blade. The final kitchen demonstration must use the knife already in the kitchen asset, not a duplicate.
- Knife starts may be at the centre or elsewhere on the board, flat on the surface, with varied orientations. An initial edge placement must not be required.
- Learned nudging or rotation before grasping is allowed. Evaluate pickups completed away from the edge separately to detect an edge-only strategy.
- Train the right arm and hand first. Keep the left arm parked and represented as a collision obstacle.
- The final grasp must surround and retain the handle. A fingertip pinch may be an intermediate physical action, but is not the required final grasp.
- No attachment, hidden constraint, object teleportation, or commanded knife motion during an episode. Object placement is allowed only at reset.
- Preserve the preference for fingers establishing support before firm thumb opposition. Evaluate its feasibility and record the learned sequence; do not silently hard-code the old finger trajectory into the new policy.
- Blade outward and cutting edge downward are the eventual presentation goals, added after stable pickup is learned.
- Cutting, two-arm coordination, generalisation to arbitrary knife models, and unbounded kitchen search are outside the first task.

“Anywhere on the board” means the entire usable board must be assessed for reachability, visibility, and collision-free access. Identify inaccessible regions explicitly. Do not silently exclude difficult regions and claim whole-board performance. If necessary, propose a board/camera/base arrangement that makes the intended region accessible.

## Laptop constraints

Read-only inspection on 19 October 2026 found:

| Resource | Configuration |
| --- | --- |
| GPU | NVIDIA GeForce RTX 5060 Laptop GPU |
| VRAM | 8151 MiB, approximately 8 GB |
| CPU | Intel Core i7-14650HX, 16 cores and 24 threads |
| RAM | Approximately 16 GB installed; Linux reported 15 GiB |
| Project drive free space | Approximately 227 GiB at inspection |

Available memory and disk space change over time. Recheck before benchmarking. NVIDIA's published Isaac Sim 5.1 requirements list 32 GB RAM and 16 GB VRAM; this is a resource warning, not proof that the reduced task cannot run. Verify requirements and compatibility for the actual installed versions before selecting a configuration. Do not upgrade the simulator merely because a newer release exists.

The earlier full-kitchen scripted tests used roughly 8 GB of process RAM before adding RL training and vision learning. A reduced scene is therefore essential. Whether useful camera-based RL fits this laptop remains an open feasibility question.

## Existing project and preservation requirements

Working directory: `/home/omen/teamwork_projects/tomato_cutting_right_arm`.

Relevant existing files include `README.md`, `scripts/kitchen_grasp.py`, `scripts/guarded_grasp.py`, `run_kitchen_grasp.sh`, and `work/validated_grasp_configuration.json`. Inspect them before reuse. Their controller is scripted IK and joint-drive control, not a trained policy.

Previous accepted scripted demonstrations are baselines only. Recent closer-to-blade experiments did not establish a newly validated full grasp; do not use their labels or small clearance lifts as evidence of RL or successful wrapped pickup. Check report dates, configurations, controller hashes, and videos before relying on any result.

Preserve original robot and kitchen assets, accepted baseline launchers, and reports. Keep the RL task separate from the scripted demo. Treat synced project `sources/` as read-only. The project mirror and the actual robotics working directory are different locations.

## Proposed system architecture

Deployment flow:

RGB-D camera → compact perception model → handle pose and confidence → learned RL policy → bounded hand and finger commands → low-level robot controller.

Confirmed robot feedback, such as joint positions and velocities, also enters the policy. A small observation history may be used to handle occlusion and motion. Sensor timestamps and stale-image handling must be explicit.

Start with separate perception and manipulation models to limit simultaneous rendering and learning costs. This is vision-based RL control, with a learned perception front end; it is not a claim that one network learned everything end to end from raw pixels.

Use a state-based RL teacher first, then expose the control policy to camera-derived estimates and refine it. A compact PPO implementation supported by the installed Isaac Lab stack is the initial candidate, not a guaranteed best algorithm. Choose its rollout and network sizes from measurements.

The RL policy chooses bounded incremental hand translation/orientation and independent finger actuator targets. IK and joint drives may execute those choices. Mimic joints must retain their physical coupling. Do not give the policy impossible independent control of coupled joints. Keep actuator limits and command smoothing in a documented low-level controller.

### Information access contract

| Information | Training use | Deployed policy use |
| --- | --- | --- |
| RGB-D images or camera-derived features | Yes | Yes |
| Joint position and velocity | Yes | Only if physically available and verified |
| Motor current or torque estimates | Optional | Only after interface and meaning are confirmed |
| Fingertip or wrist force measurements | Optional | Only if real sensors are confirmed |
| Exact simulator knife pose | Teacher, reward, critic, evaluation | Never |
| Simulator contact forces and contact identities | Reward, critic, evaluation | Never unless replaced by a validated real equivalent |
| Simulator segmentation and handle labels | Perception training labels | Never as an externally supplied answer |

An asymmetric critic may use privileged simulator information while the actor uses deployable inputs. Record these input lists separately and test for information leakage.

## Phase 1 Hardware interface and software audit

Steps:

1. Record installed Isaac Sim, Isaac Lab, Python, PyTorch, CUDA, and driver versions and their compatibility. Preserve the working environment.
2. Inventory arm and hand joints, mimic relations, physical dimensions, actuator limits, and control modes.
3. Determine which physical signals the robot provides from manufacturer documentation or hardware interfaces. Tactile sensing remains unknown until verified.
4. Define policy observation and action schemas with units, frames, limits, update rates, and missing-sensor handling.
5. Separate motor-current estimates from actual contact-force measurements; they are not interchangeable without calibration.

Success checks:

- Every proposed deployment input has a confirmed source or is explicitly excluded.
- Every action maps to an available physical actuator/control interface.
- Unknown hardware details are listed as open items; simulator sensors are not assumed to exist physically.
- Existing scripted baselines remain recoverable.

Output: interface specification, version inventory, and unresolved hardware questions.

## Phase 2 Minimal scene and resource feasibility

Steps:

1. Compose a derived training scene with the robot, existing knife geometry, board, and necessary countertop. Omit decorative kitchen geometry and expensive materials.
2. Keep relevant collision geometry and the parked arm. Validate collision simplifications around fingers, handle, blade, and board.
3. Begin with one environment, without a visible viewport. First benchmark physics and a small policy update without cameras; then add one camera and perception inference.
4. Measure available system RAM, process memory, GPU memory, peak memory during updates, simulation throughput, and time spent rendering.
5. Increase environment count gradually only while maintaining measured headroom. Reduce environments, image size, rollout length, or network size if necessary.
6. Benchmark long enough to include repeated resets and policy updates, not just startup. Use a 30-minute initial stability test and record memory trends.

Safeguards:

- Preserve the existing single-instance simulator lock and host-memory watchdog. Its current startup minimum is 5 GB available RAM and stop threshold is 2 GB; do not weaken these to force a run.
- Add a warning/checkpoint threshold above the stop threshold, initially around 3 GB available RAM, and tune conservatively from measurement.
- Set a GPU headroom threshold from measured peak allocations, including rendering and training-update spikes. Avoid allocating to the device limit.
- Save periodic checkpoints while sufficient memory remains. Do not rely on saving only after memory is exhausted.
- Do not run perception training, RL training, and a full-kitchen viewer concurrently.
- Record disk growth; retain bounded checkpoints and sampled videos rather than every rendered frame.

Success checks:

- The minimal task completes the stability test with repeated resets and updates, no OOM, no sustained memory growth, and reserve memory intact.
- Save/restart/resume is demonstrated, including optimizer state, observation normalization, curriculum state, and random seeds where supported.
- A measured training configuration and throughput estimate exist.

If a single useful camera environment cannot fit, report that result before long training. Reduce scene/model costs or propose a separately validated local alternative. Do not silently change physics engines or claim feasibility from a simulator launch alone.

Output: resource benchmark, memory limits, resume demonstration, and a go/no-go decision for the next phase.

## Phase 3 Physical task and evaluation definitions

Steps:

1. Validate knife scale, mass, centre of mass, inertia, friction, and collision geometry. Inspect for interpenetration and unrealistic contact behaviour.
2. Validate hand geometry, actuator limits, passive coupling, and self-collision handling. An inherited disabled self-collision setting must be resolved or explicitly block physical deployment readiness.
3. Test whether the hand can form a wrapped handle grasp from representative flat placements. Include centre placements and allowed nudging/rotation.
4. Define reset distributions over board position and yaw. Let the knife settle physically before beginning an episode. Reject invalid resets with logged reasons.
5. Build success, failure, and timeout detectors independently of the reward.

Proposed episode success criteria, to freeze before training:

- Knife is at least 5 cm above its initial settled handle height and retained for 3 seconds.
- No board support during the measured hold.
- Palm support, opposing thumb support, and at least three fingers surrounding/contacting the handle, with at least two contacts meaningfully away from their tips.
- Relative slip during the hold is at most 10 mm, measured in the hand frame.
- No blade contact by the hand, no attachment, and no unacceptable collision, force, or joint-limit violation.
- Later presentation stage additionally requires blade outward and edge toward the board, using documented geometric tolerances.

These are proposed engineering targets, not achieved results. Use the actual handle surface and contact geometry to validate the wrap detector across orientations. Do not depend solely on a single fingertip coordinate threshold, and do not revise criteria after seeing a policy fail merely to label it successful.

Success checks:

- Detectors reject a fingertip-only final pinch, a knife resting on the board, a dropped knife, blade contact, and a knife merely pushed upward.
- Detectors accept physically verified representative wraps and are checked against visual evidence.
- Valid reset coverage includes centre placements; reachability exclusions are documented.

Output: task specification, reset sampler, independent metrics, and annotated success/failure examples.

## Phase 4 State based RL manipulation teacher

Steps:

1. Train a compact policy with privileged knife state and robot feedback to learn physical manipulation first.
2. Progress from nearby grasp-and-hold to approach-and-lift, then random positions, random rotations, and difficult flat placements.
3. Permit bounded nudging/rotation and recovery attempts. Penalise pushing the knife off the board.
4. Reward sustained successful pickup most strongly. Use smaller guidance rewards for approach to the handle, useful contact, and stable enclosure.
5. Penalise blade contact, excessive forces, unsafe motion, dropping, and unnecessary action. Prevent repeated rewards for cycling between contact and release or momentarily crossing a lift threshold.
6. Log actual physical success separately from return. Compare with random or untrained actions and, where applicable, the scripted baseline.
7. Record checkpoint identifiers, training steps, seeds, learning curves, action bounds, and all reward changes. Start a new experiment record when changing the task or reward materially.

Success checks:

- Policy parameters actually update and independent task success improves over the untrained policy.
- Saved policies reproduce performance in evaluation with learning disabled.
- Reward increases correspond to real grasps in sampled videos.
- A practical curriculum gate is at least 80% success over 100 held-out episodes at the current difficulty, with no observed blade/unsafe contact. Freeze or explicitly revise this target before the corresponding experiment.

Output: trained teacher checkpoints, learning curves, evaluation results, and documented failure modes. This phase alone is not vision-based pickup.

## Phase 5 Simulated camera and perception model

Steps:

1. Place one fixed RGB-D camera near the head/upper torso. Specify intrinsics, mounting transform, depth convention, clipping planes, update rate, and timestamps.
2. Verify full-board coverage and useful handle visibility. Start with a modest resolution such as 128 by 128 as a benchmark candidate; increase or crop based on measured localisation quality, not habit.
3. Generate synthetic images with knife/handle labels from varied board locations and rotations. Separate training, validation, and test scenes/seeds.
4. Train a compact model to estimate handle position, orientation, and confidence. Include absent/occluded targets and depth failures.
5. Save training data in bounded batches or generate it on demand. Train perception separately from large simulation jobs if memory requires it.

Success checks:

- Coordinate transformations are checked with known test points.
- Position and orientation errors are measured across the board, including occlusions.
- Acceptable errors are tied to experimentally measured grasp tolerances from Phase 4, not an arbitrary universal accuracy claim.
- Low-confidence or stale observations lead to bounded recovery or stopping, rather than an unrestricted reach.
- Memory limits remain satisfied with rendering and perception inference active.

Output: camera specification, perception checkpoint, held-out accuracy report, and latency/memory measurements.

## Phase 6 Camera driven RL control

Steps:

1. Transfer the teacher's useful behaviour into a policy consuming estimated handle state, confidence, and confirmed robot feedback.
2. Introduce measured perception errors, latency, dropouts, and occlusion during training. Use real perception outputs for final refinement and evaluation.
3. If distillation or demonstrations initialise the policy, label this accurately and then perform RL refinement. Distillation alone is not evidence of vision-conditioned RL training.
4. Keep exact object state and simulator contact labels restricted to rewards, critic, and evaluation code.
5. Audit the actor's input tensors and wrappers for information leakage. Test whether changing visible knife position changes the policy's target, and whether hiding the target produces the intended uncertainty response.

Success checks:

- A final evaluation run disables actor access to ground-truth knife pose and simulator-only contact feedback.
- The camera-driven policy succeeds on unseen positions/orientations, not just the original scripted location.
- Report the performance gap between privileged-state and camera-driven control.
- Action bounds, physical grip criteria, and memory protections remain active.

Output: deployable observation/action specification, vision-conditioned RL checkpoint, leakage audit, and comparative evaluation.

## Phase 7 Robustness and final simulated acceptance

Steps:

1. Add bounded variation in lighting, textures, camera calibration, depth noise, friction, knife mass, actuator strength, latency, and initial posture. Derive physical ranges from hardware measurements when available.
2. Add the blade-outward/edge-down presentation objective after stable pickup works. Record fingers/thumb timing and assess the preferred sequence explicitly.
3. Freeze the policy and evaluate on a separate test set. Include centre, edge, corner, multiple yaw ranges, and flat placements requiring repositioning.
4. Repeat training with at least three seeds when the measured local budget permits; report training-seed variability. At minimum, use multiple independent evaluation seeds and label any single-training-seed result as such.

Proposed final gate, to agree and freeze before the final test:

- At least 200 held-out episodes with at least 90% overall success.
- At least 80% success in each predeclared major placement/orientation group, with sample counts reported.
- No observed blade-contact or unsafe-collision events in the acceptance set; report them separately from ordinary failures. Zero observed events is not proof of zero risk.
- Report confidence intervals, slip, completion time, peak forces, intervention count, and memory use.
- Include a centre/away-from-edge subset where success is completed without depending on board-edge pickup.

Do not repeatedly tune against the final test set. Use validation episodes for tuning and reserve a fresh test set after material changes.

Output: frozen checkpoint, reproducible evaluation configuration, numerical report, and representative success/failure videos.

## Phase 8 Full kitchen validation

Steps:

1. Load the trained policy into the original kitchen using the existing knife. Keep the board parallel to the countertop and deactivate the spare knife that intersected it.
2. Run one environment under the same memory safeguards. Keep camera calibration and robot interfaces consistent with training.
3. Repeat a representative placement/orientation set. Diagnose changes in lighting, contacts, occlusion, and runtime separately.

Success checks:

- Actor still uses camera-derived observations without hidden object-state access.
- Original kitchen knife is moved by physical interaction only.
- Report success rates and the performance change from the reduced scene; do not claim transfer based on one successful video.
- Full-scene memory and latency are measured and remain within the tested budget.

Output: full-kitchen demonstration and transfer evaluation. Cutting remains outside scope.

## Phase 9 Preparation for the physical robot

Steps after separate authorization for hardware work:

1. Confirm real control interfaces, sensor availability, actuator limits, finger coupling, and robot geometry against the simulated model.
2. Calibrate the real camera and robot frames; measure observation/command latency and validate timestamp handling.
3. Match simulated dynamics to measured behaviour. Train with realistic uncertainty rather than compensating through implausible friction or motor strength.
4. Validate command limits, workspace boundaries, emergency stop, and loss-of-vision handling independently of the learned policy.
5. Start with perception-only checks, then empty-hand bounded movements, then a blunt knife-shaped training object, under supervision.
6. Review physical results before any sharp-tool test. Do not perform unrestricted RL exploration with a real knife.

Success checks:

- Every actor input is supplied by a real verified signal; missing tactile sensors do not break deployment.
- No commands exceed the physical limits or continue after a stop condition.
- Physical pickup and slip measurements are recorded separately from simulation results.
- Hardware testing uses a separately agreed protocol and explicit authorization; simulation acceptance is not hardware certification.

Output: calibrated deployment interface, hardware test records, and remaining transfer gaps.

## Proposed implementation organisation

Create this structure only after implementation is requested. Adapt it to existing project conventions rather than overwriting them.

| Area | Responsibility |
| --- | --- |
| `rl/scene/` | Minimal scene composition and original-asset references |
| `rl/task/` | Reset distributions, observations, actions, rewards, termination |
| `rl/control/` | Bounded low-level commands and hardware-compatible interfaces |
| `rl/vision/` | Camera configuration, data generation, perception model |
| `rl/train/` | Teacher, perception, and vision-policy training entry points |
| `rl/evaluate/` | Independent success detectors and held-out evaluation |
| `rl/configs/` | Versioned laptop configurations and experiment settings |
| `rl/deploy/` | Inference interface; hardware adapters remain gated |
| `runs/rl/` | Checkpoints, metrics, manifests, selected videos |
| `docs/rl/` | Phase results, decisions, hardware interface, limitations |

Each run manifest should identify code/configuration versions, asset provenance, random seeds, observation/action schemas, reward version, resource measurements, checkpoint path, and test-set identity. Record changes between experiments so results can be reproduced.

## Instructions for Sol at handoff

1. Read this plan and the existing project instructions before acting.
2. Wait for the user's instruction to implement; this file alone is planning authorization.
3. Begin with Phase 1, then the Phase 2 benchmark. Do not start a large training job or load the entire kitchen as the initial training environment.
4. Finish and record each phase's success checks before advancing. If a check fails, diagnose it and report the evidence rather than weakening the definition of success.
5. Keep updates concise: what passed, what failed, what changed, and what the next test will establish.
6. Separate confirmed results from proposed settings and estimates. Do not promise a training duration before measuring throughput and learning progress.
7. Stop safely and preserve progress on memory pressure or interruption. No automatic unbounded restart loop.

## Reference documentation

- [NVIDIA Isaac Sim 5.1 requirements](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/requirements.html): resource reference only; verify the actual installed release before implementation.
- [Isaac Lab camera documentation](https://isaac-sim.github.io/IsaacLab/v2.0.1/source/overview/sensors/camera.html): camera concepts and rendering-memory considerations; use API documentation matching the installed version.

## Current completion status

Execution update on 19 October 2026: the user authorized Phases 1 and 2. The model/software audit and scoped one-environment resource benchmark are complete; see [current phase status](docs/rl/PHASE_STATUS.md), [Phase 1 audit](docs/rl/PHASE1_AUDIT.md) and [Phase 2 results](docs/rl/PHASE2_RESULTS.md).

The 30-minute RGB-D resource probe passed with repeated resets and bounded surrogate PPO updates. This did not train knife pickup or perception.

Subsequent authorization covered dependency repair, native integration checks and continuation of Phase 3, with no full training. A local dependency overlay and native DirectRLEnv/PhysX/RSL adapter now pass targeted tests. The separate Phase 3 scene has self-collision enabled with fixed-assembly/adjacent-pair filtering and a corrected ready posture. Flat reset sampling, knife settling and independent grasp logic have been implemented and tested within their recorded scope. See [native integration and Phase 3 results](docs/rl/NATIVE_INTEGRATION_AND_PHASE3.md).

Phase 3 remains open: physical wrapped pickup from a flat central placement and positive detector/visual validation are not established. Full-board arbitrary poses are also limited by the current knife/board geometry. Physical interfaces remain unverified. Phases 4–9 and full training have not started.

Central-pickup continuation on 19 October 2026: bounded native physical attempts established initial opposed pinch contact but did not pass the firm central lift/hold criteria. Contact stops exposed remaining thumb/palm and board-clearance issues. The criteria and source assets were preserved; no full training was started. See [central grasp test results](docs/rl/CENTRAL_GRASP_RESULTS.md).
