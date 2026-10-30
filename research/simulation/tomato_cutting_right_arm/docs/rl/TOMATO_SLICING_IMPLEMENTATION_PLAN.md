# Tomato slicing implementation plan

Prepared 19 October 2026 for Sol. Status: planning only. Knife-grasp experiments are paused until the RAM upgrade. This document authorizes no simulator run, training, dependency installation or controller change. Later implementation and physical experiments require a subsequent user instruction.

The research objective is robot learning and control for slicing. Begin with the cheapest mechanically meaningful model that supports deformation, blade-dependent damage and independent slice separation. Compare it against coarse FEM before investing in detailed tomato anatomy. Keep execution local to the laptop and retain the same arms and hands.

## 1 Scope and decisions

The first robot milestone is one slice of specified thickness, with a known knife grasp and an explicitly disclosed fixture holding the remaining tomato. Use a nominal 10 mm slice as a proposed benchmark setting, pending user agreement. The fixture is an experimental aid; success does not demonstrate left-hand stabilization or knife pickup.

Before the robot milestone, isolate tomato mechanics using a prescribed knife trajectory. A kinematically driven test blade in this mechanics-only experiment does not demonstrate the hand supporting cutting loads. Robot integration must subsequently use the existing knife, actual grasp dynamics and unchanged grasp criteria. A rigid tool mount may be considered only as a separately labelled control experiment; it must never be reported as a successful hand grasp.

Later milestones add left-hand stabilization, camera localization, repeated slices and the learned knife-pickup skill. A successful scripted pickup is not automatically a prerequisite for all cutting research, but any simplification of the grasp must be disclosed.

## 2 Offline capability audit

These are source-inspection findings, not new runtime validation. The installed checkout is under `/home/omen/IsaacLab`; the project runtime entry is `.venv-native/bin/python`. No Isaac, Torch or simulator imports were executed for this audit.

| Capability | Evidence inspected | Finding and next gate |
| --- | --- | --- |
| Current robot physics | `rl/native_env.py`, `rl/native_probe.py` | CPU PhysX, one environment, 1/240 s physics timestep and decimation 12. Preserve this existing task; create a separate experimental slicing configuration later. |
| FEM deformation | Installed `source/isaaclab_physx/isaaclab_physx/assets/deformable_object/deformable_object.py` | FEM asset interface, nodal state and simulation/collision mesh access exist. The implementation describes the API as experimental. Presence does not establish working knife contact or cutting. |
| Deformable backend | Installed PhysX deformable test uses `cuda:0`; NVIDIA PhysX documentation describes GPU-only deformables | The current CPU configuration cannot simply be assumed to support native FEM. Verify backend/version compatibility and robot interaction in a separate GPU experiment before adopting it. |
| Fracture and separation | Inspected the core and PhysX deformable asset directories for fracture, tearing, cutting and topology interfaces | No ready-made cutting operation was identified in these interfaces. This is a bounded search, not proof that every installed component lacks cutting. A damage/separation implementation and backend compatibility remain open. |
| Wrist measurements | Installed `sensors/joint_wrench/base_joint_wrench_sensor_data.py`, `joint_wrench_sensor_cfg.py` and PhysX implementation | The simulated joint reaction sensor exposes force in N and torque in N m, expressed in the incoming child-side joint frame at its anchor. It includes gravity/inertial reactions; it is not automatically the external blade contact wrench. |
| Camera | Installed `sensors/camera/camera.py` | RGB and depth interfaces exist. Their presence does not validate deformable rendering, cut-surface appearance, latency or robot visibility. Defer rendering until mechanics passes. |
| Dependencies | `docs/rl/native_dependency_smoke.json` | Earlier smoke checks passed, with explicitly recorded package metadata overrides. Record the exact runtime again before later implementation; do not treat that report as a slicing validation. The checkout's `isaaclab/pyproject.toml` declares 19.0.0; installed distribution identity still needs capture without importing the simulator. |

Offline work for Sol after implementation authorization: record resolved package metadata and checkout revision, identify supported material/mesh APIs, inspect collision updates and independent-piece creation, and map the physical wrist mount to the simulated sensor frame. Prove that the selected backend can exchange equal-and-opposite robot/blade/tomato contact reactions. If using two solvers, specify synchronization, units and force transfer before integration; visual coexistence is insufficient.

**Gate A:** an evidence table distinguishes source presence, earlier runtime evidence and untested features. No claim of native cutting support until separation is demonstrated. If separation needs unsupported topology changes, choose a supported predefined-interface method or reconsider the solver rather than assuming remeshing is available.

## 3 Tomato geometry and provisional mechanics

No CAD is required to start. Generate a parameterized rounded ellipsoid with adjustable width, height, flattening and mild shape asymmetry. Use a proposed nominal 65 mm width and 55 mm height solely as synthetic test dimensions; replace distributions with measured tomatoes. Specify slice thickness in metres, relative to the exposed tomato end and a defined board coordinate frame.

Maintain three representations derived from one parameter set:

- **Visual:** smooth tomato surface, colour variation and cut faces. Keep detail out of collision and mechanical meshes. Add skin texture and internal appearance only when testing perception.
- **Collision:** simplified closed exterior with correctly oriented faces and explicit blade/board contact. Newly exposed cut surfaces must acquire appropriate collision behaviour. Avoid one convex hull spanning a separated slice and remaining tomato.
- **Mechanical:** coarse nodes/elements or reduced deformable cells, with distinct effective flesh and skin-failure response. For FEM, use quality tetrahedra and refine locally near the intended cut only when needed. Do not begin with a costly explicitly thin volumetric skin.

Initial simplifications omit individual seeds, liquid flow and detailed cavities. Record them as model limitations and revisit if force/deformation measurements show systematic errors. Do not infer mechanical material values from the CAD appearance.

Provisional parameter registry: density/mass, elastic or hyperelastic response, damping/rate dependence, compressibility, skin rupture, flesh fracture energy, knife friction, board friction and fixture compliance. Give every parameter a unit, source, uncertainty, model version and calibration status. Do not assign literature values from another food as validated tomato values. Check nearly incompressible material behaviour for locking and timestep sensitivity.

**Gate B:** units and dimensions are explicit; surface is watertight and nonintersecting; element volumes are positive; mass and inertia are consistent; the fixture and intended interface are visible in metadata. Mesh quality limits must be defined for the selected solver before generation.

## 4 Model comparison and recommendation

| Model | Useful scope | Cost and limitations | Decision |
| --- | --- | --- | --- |
| Rigid pieces with a timed release | Rendering and scene layout only | No deformation or trustworthy rupture; easy for a policy to exploit | Exclude from cutting acceptance and training claims. |
| Reduced deformable model with cohesive bonds across a predefined interface | Initial single slice at a configured plane | Small state, controllable cost; restricted fracture paths and approximate local mechanics | Preferred first candidate, conditional on compatible contacts and stable separation. |
| Coarse FEM with a predefined cohesive interface | Deformation and force comparison for the same restricted task | More expensive; FEM alone does not provide fracture; interface and cut-face contact still need implementation | Comparison candidate and possible reference model. |
| Arbitrary evolving fracture or remeshing | Choosing arbitrary cut paths and more general slicing | Highest integration, numerical and resource risk | Defer until the restricted model and research need justify it. |

For the preferred candidate, predefine possible bonds between the future slice and remaining body. Damage must depend on local blade contact and a stated traction/work or fracture-energy law. A blade merely reaching a depth or a clock advancing cannot remove bonds. Damage is irreversible during an episode; its dissipation and mass accounting must be logged. Only damaged regions should separate, with no persistent collision barrier spanning the cut and no premature gap through intact material.

The fixture must support the remaining body without fastening the slice or artificially forcing it to detach. Record fixture geometry, constrained degrees of freedom and reaction loads separately from blade loads.

A predefined plane can support controlled fixed-plane slicing research. It cannot establish arbitrary slice placement. Vary target planes by constructing compatible interfaces at reset for the restricted task, explicitly report that reset-time knowledge, and test off-plane motion: it must not cause magical fracture along an untouched interface. A general perception-guided slicing claim eventually requires placement tolerance validated against the interface discretization or a more general fracture model.

**Gate C:** choose by contact fidelity, independent separation, controllability, numerical robustness and measured local cost. Do not choose by appearance alone. If neither candidate meets these gates, report the missing capability before starting RL.

## 5 First bounded experiment after the RAM upgrade

This is a future experiment specification, not an executable command. The existing guard has no tomato worker mode; a future dedicated worker and guarded integration must be reviewed and implemented before launch. Never pass a new workload through an unrelated mode just to obtain a process.

Start with one headless environment: flat board, one coarse tomato, disclosed fixture and prescribed blade. No robot, kitchen, camera, optimizer or policy. First check resting stability and a nonfracturing indentation; then run one slow prescribed draw-and-down cut at the target plane, followed by a small blade withdrawal and slice-release observation. Limit the worker to **60 seconds wall time**, with stage deadlines; an unfinished cut is inconclusive, not a pass. The existing watchdog's bounded startup/termination allowance must also be recorded.

Use a separately authored blade contact representation that preserves the existing knife dimensions and cutting edge. Initial prescribed motion is diagnostic only. Start with one coarse mesh; compare a finer mesh and half timestep only after the first run passes. Keep all workloads serial and output bounded logs, summaries and a few diagnostic frames only if later enabled.

Preserve `rl/guard_benchmark.py`: startup at least **10,000,000,000 bytes available RAM and 4 GiB free VRAM**; runtime warning/checkpoint thresholds 3,000,000 KiB RAM and 1.5 GiB VRAM, hard thresholds 2,000,000 KiB RAM and 1 GiB VRAM. Keep the common lock, monitor-error handling and termination behaviour. These are minimum gates, not proof a new FEM workload fits. Increase required reserve if justified by measurement; never lower existing floors to permit a run.

Record baseline and peak process-tree RSS, system minimum available RAM, swap activity, baseline/peak total GPU memory, available VRAM, sampling interval, startup/cooking time, simulated duration, physics steps/s, real-time factor, median/p95 step time and solver iterations. Distinguish process and machine-wide memory. Record exit reason, guard warnings and incomplete stages. A zero exit code is insufficient.

**Gate D:** no guard warning, no invalid states, no runaway deformation, and successful physical/model separation checks below. Set a proposed training-throughput target of at least real time for the reduced single-environment model; slower FEM may remain useful for reference tests. Measure sample cost and estimate local training duration before approving any training budget. A failed memory gate stops the experiment without bypassing it.

## 6 Sensor contract and conventional controller

Treat wrist torque feedback as provisional. Confirm sensor manufacturer/model, measured axes, mount, sampling rate, delay, saturation, overload limits, filtering and calibration. Distinguish dedicated wrist measurements from estimated motor torques. Torque-only feedback cannot generally recover the full cutting force because multiple force/contact distributions can produce the same moment.

For a six-axis sensor, calibrate sign and frame using known loads and moment arms. Compensate hand/tool gravity, bias and inertial contributions; account for shifting the wrench reference point. Verify timing against the physics step and command application. For torque-only hardware, mask unavailable simulated force channels and use a torque-limited controller; do not label it force control. Keep a separate six-axis experimental branch only if hardware confirmation supports it.

The baseline is a bounded Cartesian draw-and-down trajectory with joint-limit, velocity, acceleration and effort constraints. Adapt or pause downward/drawing speed using confirmed measured channels. Use admittance or hybrid motion/force control only after sensing, bandwidth and stability are established. Robot integration must confirm a grasp that withstands cutting loads, including lateral forces and moments; supporting knife weight alone is insufficient.

**Gate E:** repeatable single cuts on a small geometry/firmness matrix, with no limit violations and an interpretable load/progress trace. Compare pure downward motion and drawing motion under the same conditions. Establish the baseline before attributing improvements to RL.

## 7 RL specification and curriculum

Use a residual policy around the bounded baseline before considering full motion generation. Proposed actions are small changes to downward speed, drawing speed and permitted blade orientation. A fixed lower-level controller enforces limits; the policy cannot change damage thresholds, teleport geometry, detach bonds or alter safeguards. Start at 20 Hz as a compatibility proposal, not a validated control bandwidth; sensor and mechanics tests determine the eventual rate.

| Observation or signal | Initial development | Physical deployment rule |
| --- | --- | --- |
| Joint positions/velocities and prior action | Actor and critic | Confirm actual encoders and latency. |
| Knife pose/velocity | From robot kinematics for debugging | Include grasp uncertainty; add visual tracking if slip matters. |
| Wrist torque | Actor with calibrated noise/delay model | Only verified measured axes. |
| Wrist force | Optional separate branch | Excluded until six-axis hardware is confirmed. |
| Tomato pose and target plane | Exact state in explicitly labelled initial experiments | Replace with camera estimates for vision-based claims. |
| Damage, nodal strain, true slice connectivity, exact material values and contact identities | Evaluator or privileged critic | Never feed these hidden quantities to the deployment actor. |

Use short observation histories for delayed/noisy feedback. An asymmetric critic is optional. Reward validated separation and thickness, controlled progress and smoothness; penalize excessive measured loads, tomato displacement, grasp slip and failure. Hidden simulator state may support training rewards and evaluation, but it must not become an undeclared actor input. Penalize hacking the interface, pushing the whole tomato away or completing via crushing. Safety remains an independent termination rule, not merely a reward term.

Curriculum and exit gates:

1. **Known state and fixture:** one plane, one geometry, baseline established; bounded learning only after separate user authorization.
2. **Mechanics variation:** held-out size, firmness, friction, skin strength and blade sharpness ranges. Randomize within justified ranges and report provisional values.
3. **Camera localization:** one modest-resolution camera; validate intrinsic/extrinsic calibration, occlusion and pose/slice-plane error. Train with estimated state and sensor dropout/latency. Do not report exact-state results as vision-based.
4. **Left-hand stabilization:** remove the fixture explicitly. Add limited compliant holding, tomato deformation checks and blade clearance. Evaluate fixture and hand-held conditions separately.
5. **Repeated slices:** update remaining geometry, mass and exposed faces; let loose slices settle; prevent the controller from using the original uncut shape indefinitely.
6. **Pickup integration:** connect the separately evaluated pickup skill and test grasp retention under cutting loads. Preserve all frozen grasp criteria.

Use a small bounded PPO baseline only if measured local sample cost permits it; algorithm selection remains provisional. Keep policies small, seeds and checkpoints reproducible, and compare against the conventional controller. No full training follows automatically from passing a mechanics benchmark.

## 8 Success checks and evaluation

The following numerical values are proposed simulation research thresholds, to be frozen in a separate slicing contract before implementation. They are not calibrated hardware safety limits and do not modify existing grasp criteria.

| Check | Measurement and proposed acceptance |
| --- | --- |
| Separation | No intact mechanical bonds connecting the intended slice to the remainder; a gentle release/probe confirms independent motion for at least 1 s. Fixture or blade must not be the only reason pieces appear apart. Depth alone never passes. |
| Thickness | Nominal target 10 mm, proposed tolerance ±2 mm on the released slice. Measure in the defined cut-normal direction at multiple interior locations after a stated settling period; report variation/taper and deformation rather than only blade-plane distance. |
| Tomato movement | Proposed remainder translation ≤5 mm and rotation ≤5 degrees relative to the board, using bulk material tracking that distinguishes deformation from rigid motion. Log fixture reaction and crushing separately. |
| Knife slip | Proposed hand-relative drift ≤2 mm and ≤3 degrees during the cut; continue enforcing unchanged grasp acceptance and failure rules. Not applicable to the prescribed-blade mechanics fixture, which makes no grasp claim. |
| Loads | Peak/RMS/impulse and duration above warning thresholds in available sensor axes; no saturation or approved limit violation. Numerical force/torque limits remain blocking inputs for robot/real cutting until actuator, hand, sensor and lab limits are confirmed. |
| Hand and blade | No blade contact with either hand. Proposed simulation minimum distance 20 mm from the blade to left-hand skin, with model/pose uncertainty included; verify reachable geometry before freezing. Right-hand intentional handle contact is allowed, blade contact is not. Physical margins require lab review. |
| Numerical validity | Finite state, no inverted invalid elements, no unbounded energy or mass loss, no unexplained fracture away from blade loading. Proposed mass-accounting error <1%; define energy accounting for damage and driven blade work. |
| Resolution sensitivity | Proposed change <10% in peak load/cutting work and <1 mm in thickness when halving timestep or refining mesh; otherwise refine or narrow claims. |

First mechanics checks use positive and negative controls: no blade contact causes no damage; an off-plane pass causes no untouched-interface separation; incomplete cuts retain connections; complete cuts release; rest and repeated resets remain stable. Include interrupted motions and blade withdrawal. These tests catch timer/depth triggers and hidden constraints.

For later policy evaluation, freeze disjoint training and held-out instances, use at least three training seeds if resources permit, and evaluate baseline and policy on the same 30 or more held-out cases initially. Report counts, uncertainty, every failure category, time, thickness, loads and compute cost. Proposed advancement target is ≥90% complete successful slices with zero observed hard-limit/hand–blade violations; the sample size does not certify physical safety. Test generalization to new target thicknesses only where the model actually supports them.

## 9 Real measurements and open decisions

Acquire tomato dimensions, mass, variety, ripeness and temperature; board/skin friction; compression response; cutting load or available torque versus blade displacement/speed; skin breakthrough; final thickness and deformation video. Record knife edge condition, dimensions and surface material. Separate calibration tomatoes from held-out validation tomatoes. If only wrist torque is available, fit observable torque response and state what parameters remain unidentifiable; do not claim force calibration.

Outstanding decisions:

- Confirm nominal slice thickness and whether the first slice is an end slice or an interior slice.
- Identify the actual wrist sensor and physical controller interfaces.
- Confirm access to tomato samples and measurement tools; full force calibration may need additional instrumentation.
- Verify a supported separation/contact path in the installed backend.
- Establish material parameters, robot load limits, fixture design and camera placement.
- Measure available resources after the upgrade; RAM capacity alone does not establish FEM throughput or VRAM capacity.

## 10 Implementation handoff and stop points

After a subsequent implementation instruction, Sol should first produce an offline capability record and provisional slicing contract, then geometry/model design, then a minimal guarded benchmark worker. Suggested future outputs are `tomato_capability_audit.json`, `tomato_parameter_schema.json`, `slicing_criteria.json`, benchmark summaries and a baseline report under the existing documentation/run conventions. These are proposed outputs, not files created by this planning task.

Report each gate before increasing scope. A failed fracture/contact gate leads to model revision; a resource refusal leads to stopping; insufficient sensor information blocks force-control claims. Keep knife experiments paused, all frozen grasp criteria unchanged, and full training separately authorized. The first future physical simulation is the one-environment 60-second mechanics benchmark in Section 5, after the upgrade and guard check.

## References and evidence scope

- Local source paths in Section 2 were inspected as text on 19 October 2026; APIs were not imported or run. Hardware sensor identity remains unknown.
- [NVIDIA PhysX deformable overview](https://nvidia-omniverse.github.io/PhysX/physx/5.7.0/docs/DeformableBodyOverview.html): FEM and GPU requirements; SDK documentation is context, not verification of this installed runtime.
- [DiSECt research project](https://diff-cutting-sim.github.io/): FEM with a separate damage mechanism and calibration against cutting measurements. It is a reference approach, not an installed or validated Isaac Lab integration.
- Existing project references: `rl/guard_benchmark.py`, `rl/native_env.py`, `docs/rl/native_dependency_smoke.json`, `docs/rl/phase3_grasp_criteria.json`, `rl/grasp_metrics.py`. This document does not supersede their safeguards or acceptance criteria.
