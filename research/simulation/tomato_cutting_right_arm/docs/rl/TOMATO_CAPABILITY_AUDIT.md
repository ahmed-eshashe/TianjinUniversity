# Tomato slicing offline capability audit

Date: 19 October 2026. Scope: source and distribution-metadata inspection only. No simulator modules were imported, no simulator or training was launched, and no dependencies or runtime configuration were changed.

## Recommendation

The simplest source-supported candidate is a small reduced particle and spring solid with a predefined cutting interface, using the already installed Newton building blocks in a separate mechanics experiment. It needs custom blade-dependent damage, cut-contact handling and validation. There is no demonstrated turnkey slicing feature in the inspected stack.

Do not migrate the robot to Newton's simple solver on the strength of this finding. That solver explicitly lacks mimic/equality constraints and enforcement of certain actuator limits; the existing hand relies on coupled joints. Keep the current PhysX robot task intact. Robot integration remains a separate decision requiring verified joint behaviour and two-way contact. Coarse FEM with a cohesive interface is the comparison option, rather than a prerequisite for learning experiments.

This recommendation describes the smallest identified implementation route, not a runtime-tested model or a measured performance advantage. Neither the reduced model nor FEM cutting is ready to train.

## Installed software identity

Distribution metadata was read as text from `/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages`. No package was imported to retrieve a version.

| Distribution | Metadata version | Relevant scope |
| --- | --- | --- |
| isaaclab | 19.0.0 | Editable checkout at `/home/omen/IsaacLab/source/isaaclab` |
| isaaclab_physx | 7.0.1 | Editable checkout at `/home/omen/IsaacLab/source/isaaclab_physx` |
| isaacsim-core | 6.1.0.0 | Distribution identity, not a fresh runtime test |
| newton | 1.6.0 | Installed particle, spring, FEM and solver source |
| warp-lang | 1.17.0 | Installed numerical runtime metadata |
| torch | 2.12.0+cu130 | Installed distribution identity |

The project `.venv-native` inherits this environment through its `pyvenv.cfg` and interpreter link. The Lab checkout HEAD is `75e9c8ce12b27ecc5dc17a3de822e39cc6506d80`; an existing tracked modification in `scripts/reinforcement_learning/train.py` was observed and left untouched. Source hashes in `tomato_capability_audit.json` identify the actual inspected files rather than assuming HEAD describes the whole working tree. Earlier dependency smoke results are historical evidence, not proof of cutting compatibility.

## Confirmed source capabilities

### Existing PhysX robot and deformation

[The current task](/home/omen/teamwork_projects/tomato_cutting_right_arm/rl/native_env.py:22) specifies one CPU environment, a 1/240 s timestep and decimation 12. Its arm and hand remain the intended robot models.

[The PhysX deformable asset](/home/omen/IsaacLab/source/isaaclab_physx/isaaclab_physx/assets/deformable_object/deformable_object.py:45) describes an experimental FEM interface, nodal positions/velocities, simulation/collision mesh sizes, material views and volume kinematic targets. Its installed test defaults to CUDA. Kinematic targets are position constraints, not a general cohesive-force or fracture interface. No high-level nodal external-force setter or cut/remesh operation was identified in the inspected asset class.

Therefore PhysX can remain a deformation candidate, but custom interface forces and independent cut pieces are unresolved. GPU deformables would require a separate configuration rather than assuming the current CPU task will work unchanged. Source inspection does not validate collision quality, cutting or GPU resource requirements.

### Newton reduced and FEM building blocks

[ModelBuilder.add_spring](/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/sim/builder.py:9566) builds particle pairs with rest length, elastic stiffness and damping. `add_soft_grid` and `add_soft_mesh` also exist. The installed Lab contrib deformable bridge calls `add_soft_mesh` for volumes and `add_cloth_mesh` for surfaces. This demonstrates builder plumbing, not cutting support.

[The spring kernel](/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/solvers/semi_implicit/kernels_particle.py:20) reads model stiffness/damping arrays and adds opposite forces to the paired particles. Source structure therefore offers a plausible route to damageable finite-length bonds without runtime remeshing: pre-separate node indices across a possible cut and weaken only the interface coupling. A future damage implementation must update every relevant stiffness and damping contribution and verify broken bonds transmit no cohesive load.

Important geometry constraint: the kernel computes inverse particle separation without a zero-length guard. Connecting coincident duplicate cut nodes by ordinary springs is unsafe. Use finite-length interface bonds, or design a regularized cohesive element. Axial springs alone also do not automatically provide adequate volume, shear or skin mechanics; network design and convergence remain required.

[The contact kernel](/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/solvers/semi_implicit/kernels_contact.py:255) accumulates particle forces and dynamic body force/moment. A rigid–soft contact example is installed. These are source-level evidence for reciprocal contact accumulation, not proof of correct knife reaction measurements, edge resolution, momentum balance or stable co-simulation. A prescribed blade needs explicit reaction logging even though its trajectory is externally enforced.

[The simple solver's documented limitations](/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/solvers/semi_implicit/solver_semi_implicit.py:43) include absent mimic/equality support and unenforced effort/velocity options. Its small-timestep stability requirements may offset the reduced state's computational savings. This is why the recommendation is limited to a separate mechanics experiment. Other installed solver and coupled examples are leads for later investigation, not a validated robot solution.

### Sensors and cameras

[JointWrenchSensor configuration](/home/omen/IsaacLab/source/isaaclab/isaaclab/sensors/joint_wrench/joint_wrench_sensor_cfg.py:19) defines a child-side incoming-joint frame at the joint anchor. The PhysX implementation calls `get_link_incoming_joint_force` and separates force and torque buffers. This is a joint reaction, with gravity and inertial effects, not a direct isolated blade force measurement.

Hardware identity and measured axes are unknown. Keep actor force inputs disabled under the provisional torque-only assumption. Define sign, axis mapping, bias, gravity/inertia compensation, timing, saturation and wrench reference-point changes before interpreting cutting feedback. Numerical sensor access does not establish equivalent hardware sensing.

The installed camera class contains RGB/depth interfaces. Cut-surface rendering, occlusion and pose accuracy remain untested; they are not needed for the initial mechanics experiment.

## Assumptions and missing features

The initial proposal assumes a single end slice, nominally 10 mm thick, on a synthetic 65 by 65 by 55 mm tomato. These are research settings awaiting confirmation, not measured tomato dimensions. A fixture constrains only the remaining body; its geometry, constrained degrees of freedom and loads must be disclosed.

Required custom work, after separate authorization:

1. A volume-supporting mechanical discretization with acceptable compression/shear behaviour and consistent visual/collision geometry.
2. Irreversible damage driven by local blade interaction and an explicit traction/work law, with patch-area-based fracture-energy accounting.
3. Separate node/element sets across the intended cut. No unnoticed spring, tetrahedron, skin element or attachment may continue to connect released pieces.
4. Contact on exposed cut faces without either an invisible cross-cut wall or premature leakage. No blanket collision disabling that lets the blade or pieces pass through intact material.
5. Reset of damage, collision and fixture state, plus independent-component and energy checks.
6. Calibrated or clearly provisional material values, and model-specific numerical bounds before execution.
7. A dedicated guarded benchmark entry and a later robot-integration design that preserves hand coupling and limits.

The scoped searches covered Lab core/PhysX deformable interfaces, asset/simulation schema directories, the contrib Newton bridge, and Newton simulation/solver Python source with selected examples. No complete blade/cohesive cutting API was identified there. Generic rigid-joint break attributes do not supply soft-body cutting. This does not establish absence of functionality in every optional package or compiled SDK.

## Draft specifications

- [tomato_parameter_schema.json](/home/omen/teamwork_projects/tomato_cutting_right_arm/docs/rl/tomato_parameter_schema.json) defines geometry, three representations, material registry, interface rules and sensor assumptions. It is a structured parameter specification, not a formal JSON Schema or runnable configuration. Uncalibrated quantities are null; null is not zero and cannot silently select solver defaults.
- [slicing_criteria.json](/home/omen/teamwork_projects/tomato_cutting_right_arm/docs/rl/slicing_criteria.json) defines proposed separation, thickness, movement, slip, loads, clearance, numerical and resource checks. It is draft, not frozen or connected to a controller. Missing required measurements block acceptance; they never count as passing.
- [tomato_capability_audit.json](/home/omen/teamwork_projects/tomato_cutting_right_arm/docs/rl/tomato_capability_audit.json) records evidence paths/hashes, source-confirmed findings and remaining gates.

Thickness requires multiple measurements on the released slice, not just blade-plane placement. Separation requires loss of all cross-cut mechanical coupling and an independent-motion observation. A probe must not finish breaking a partially cut tomato and falsely count that as blade success. Stopped-blade controls distinguish timer-driven damage from any explicitly modelled stored-energy fracture.

## Next bounded experiment and stop point

After the RAM upgrade and later implementation authorization, first validate a minimal contact and interface unit scene, then the plan's one-environment, headless tomato–knife–board experiment with a prescribed blade and 60-second worker budget. It contains no robot, camera or learner. If startup/cooking consumes the budget or stages remain incomplete, report an inconclusive run.

Retain the existing common lock and RAM/VRAM thresholds. The present guard has no tomato worker route; no experiment can be launched by pretending to be an existing mode. Record resource peaks, step times, reaction loads and guard outcome. Compare finer mesh and half timestep only after a stable first experiment.

Before any robot cutting, resolve sensor identity, actuator/hand/load limits, grasp retention under lateral loads, and the backend coupling path. Before learning, freeze the separate slicing contract and establish a conventional controller baseline. This audit stops at the recommendation and draft specifications; implementation, simulation and training remain unstarted.
