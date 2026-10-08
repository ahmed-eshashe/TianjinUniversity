# Architectural & Scientific Decisions (ADR)
## DEX-ROB Lab | Master's Research Record

This log documents all immutable architectural and scientific decisions. Once ratified, decisions can only be revised by opening a new decision record with explicit rationale and human supervisor approval.

---

### [ADR-001] Single Antigravity Workspace Architecture with Git as Central Memory
- **Date**: 2026-10-05
- **Status**: **ACCEPTED**
- **Decision Makers**: Ahmed (Researcher), Antigravity AI Multi-Agent System
- **Context**: The project spans literature reviews, mathematical MDP formulations, Isaac Sim simulation, RL policy training, ROS 2 hardware drivers, and IEEE LaTeX manuscript drafting.
- **Decision**: All multi-agent operations will be hosted directly within `/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity`. Structured YAML/Markdown files under `research_state/` serve as the Single Source of Truth (SSOT).
- **Consequences**: No hidden private states between AI turns; complete reproducibility across Git commits; deterministic tracking of experiments.

---

### [ADR-002] Simulation Platform: NVIDIA Isaac Sim 6.1.0 + Isaac Lab with PhysX 5 FEM
- **Date**: 2026-10-05
- **Status**: **ACCEPTED**
- **Context**: Simulating cutting of deformable soft bodies (tomatoes) requires realistic continuous fracture or mesh topology modifications and high contact fidelity. Traditional rigid simulators (MuJoCo, PyBullet) lack native non-linear volumetric fracture solvers without extensive custom C++ plugins.
- **Decision**: Use Isaac Sim 6.1.0 with Isaac Lab on RTX 5060 GPU. Soft body dynamics are modeled using PhysX 5 GPU-accelerated deformable meshes with dynamic strain-energy fracture criteria.
- **Consequences**: Allows running hundreds of parallel simulated environments in GPU VRAM with zero CPU-GPU copy bottlenecks; direct integration with SkRL / Stable-Baselines3.

---

### [ADR-003] Embodiment Role Split: Bimanual Dexterous Fixturing & Slicing
- **Date**: 2026-10-05
- **Status**: **ACCEPTED**
- **Context**: Unconstrained food slicing leads to object slippage, unpredictable rolling, and unequal slice geometry.
- **Decision**:
  - **Left Manipulator (Holding Arm)**: ARX AR5-L6 fitted with LinkerHand O6 dexterous hand. Provides soft adaptive enveloping grasp with real-time slip detection.
  - **Right Manipulator (Slicing Arm)**: ARX AR5-L6 fitted with rigid knife blade and 6-axis F/T sensing. Executes sawing cutting trajectories with dynamic normal force regulation.
- **Consequences**: Separates the research work cleanly into two sub-problems (holding stability vs cutting dynamics) allowing parallel collaborative execution between researchers (Ahmed & Shahd).

---

### [ADR-004] Residual Action Space over Cartesian Kinematic Primitives
- **Date**: 2026-10-05
- **Status**: **ACCEPTED**
- **Context**: Pure end-to-end 14-DoF joint torque RL faces immense exploration search spaces, causing high sample complexity and erratic motions that would damage physical hardware.
- **Decision**: The action space $\mathbf{a}_t \in \mathbb{R}^6$ represents residual Cartesian velocity adjustments $(\Delta v_x, \Delta v_y, \Delta v_z)$ and active compliance gains $(\Delta K_x, \Delta K_y, \Delta K_z)$ superimposed onto a nominal sinusoidal sawing motion primitive.
- **Consequences**: Drastically narrows exploration to safe contact manifolds; guarantees baseline motion capability from step 0; ensures safe sim-to-real transfer.

---

### [ADR-005] Human Authority & Safety Gate Protocol
- **Date**: 2026-10-05
- **Status**: **ACCEPTED**
- **Decision**: No agent may dispatch commands to physical robot arms, modify core physics parameters silently, or report unverified scientific claims without human verification.
- **Protocol**: `AI proposes -> AI explains -> HUMAN APPROVES -> AI executes -> AI analyzes -> HUMAN ACCEPTS`.

---

### [ADR-006] Acceptance of Virtual Inertia (Armature) and Base PD Gains for PhysX 5 Stability
- **Date**: 2026-10-07
- **Status**: **ACCEPTED**
- **Decision Makers**: Research Lead Agent, Simulation Agent, User
- **Context**: The `simulation_agent` modified the AR5-L6 and LinkerHand O6 USD files by adding virtual inertia (`physxJoint:armature = 0.05` for arm, `0.005` for hand) and setting base position drive gains (`stiffness = 400.0`, `damping = 40.0`). The user questioned if these modifications are acceptable for upcoming RL training milestones (Milestone 3).
- **Decision**: These modifications are approved for use in Isaac Lab RL training. The base PD gains in the USD provide a stable default state, while the armature prevents PhysX 5 solver divergence (explosions) caused by the extreme mass ratio between the heavy arm links and light finger links. 
- **Consequences**: 
  1. **Sim-to-Real Gap Risk**: The added armature acts as a virtual low-pass filter on joint accelerations, meaning the simulated arm will dynamically respond differently (more sluggishly) than the physical AR5-L6 at high frequencies (1 kHz). 
  2. **Mitigation Requirement**: For M3 and M4, the `rl_agent` MUST implement Domain Randomization (DR) on the actuator parameters (e.g., introducing action latency and randomizing mass/inertia properties) to prevent the policy from overfitting to the artificially dampened simulation dynamics. 
  3. **Action Space Compatibility**: Since ADR-004 specifies an action space of residual active compliance gains ($\Delta K$), the hardcoded USD stiffness/damping values will simply serve as the nominal setpoints or be overridden by Isaac Lab's `ActuatorCfg` during training.

---

### [ADR-007] Dexterous Hand Control: FollowJointTrajectory over GripperCommand
- **Date**: 2026-10-08
- **Status**: **ACCEPTED**
- **Context**: The Setup Assistant classified the 6-DoF dexterous hand (LinkerHand O6) as a `GripperCommand`, which is strictly for 1-DoF parallel-jaw claws. This prevented MoveIt from loading the `hand_controller` action server.
- **Decision**: Rewrote `moveit_controllers.yaml` to classify the hand as a full `FollowJointTrajectory` controller.
- **Consequences**: Grants MoveIt independent mathematical control over all 6 active knuckles, enabling dexterous manipulation.

---

### [ADR-008] SRDF Self-Collision Exclusion for Dexterous Hand
- **Date**: 2026-10-08
- **Status**: **ACCEPTED**
- **Context**: Closing the fingers into a fist causes mathematically intersecting bounding boxes in the dense collision meshes of the hand. MoveIt's default safety system detected this as a crash (`Start state in collision`) and aborted planning.
- **Decision**: Generated an exhaustive collision-exclusion matrix, injecting `<disable_collisions>` tags for all 13 hand links into the SRDF.
- **Consequences**: Legally allows the fingers to touch each other, resolving the self-collision aborts.

---

### [ADR-009] Real-Time Mimic Joint Calculation via ros2_control.xacro
- **Date**: 2026-10-08
- **Status**: **ACCEPTED**
- **Context**: The LinkerHand O6 has powered knuckles (active) and unpowered tip joints linked via tendons (passive mimic joints). Using `mock_components/GenericSystem`, the unpowered tip angles were not broadcast to `/joint_states`, causing Isaac Sim to render them stiff.
- **Decision**: Injected mathematical mimic tags directly into `ros2_control.xacro`, permanently deleting passive joints from the SRDF planning group, and forcing fake hardware to calculate unpowered tip angles in real-time.
- **Consequences**: Isaac Sim correctly renders the full joint state of both active and passive joints without planning crashes.

---

### [ADR-010] Sequential Wiring of Isaac Sim Action Graph
- **Date**: 2026-10-08
- **Status**: **ACCEPTED**
- **Context**: Parallel execution wires in the Isaac Sim Action Graph triggered the Subscribe node and Controller simultaneously. The Controller fired before new ROS 2 data finished downloading, causing the physical robot in Isaac Sim to remain stationary despite MoveIt working.
- **Decision**: Rewired the graph sequentially: `Tick -> Subscribe (Exec Out) -> Controller (Exec In)`.
- **Consequences**: Eliminates race conditions, ensuring synchronization between MoveIt's command and Isaac Sim's physics execution.

---

### [ADR-011] Physical Hardware Repository Registry & Shared Hardware Database Integration
- **Date**: 2026-10-08
- **Status**: **ACCEPTED**
- **Context**: Bimanual physical deployment requires low-level SocketCAN communication drivers, diagnostic tools, and SDKs for both the ARX AR5-L6 7-DoF arm and the LinkerHand O6 dexterous hand. Agents must have shared, un-siloed access to physical hardware specifications and driver source trees.
- **Decision**: Established a centralized Hardware Database under `hardware/` (with a shared link `database/hardware`), containing cloned driver repositories for both the arm (`arx5-sdk`, `ARX_CAN`) and the hand (`robot-linkerbot-linker_hand_o6`, `primitive-linkerbot-linker_hand_o6`, `linker_hand_service`, `linkerhand-cpp-sdk`, `linkerhand-python-sdk`), along with complete datasheets and a machine-readable hardware state specification (`research_state/hardware.yaml`).
- **Consequences**: Enables `ros_agent`, `simulation_agent`, and `rl_agent` to share validated kinematic limits, CAN bus identifiers, and real-time SocketCAN drivers without duplicate or fragmented assumptions.

