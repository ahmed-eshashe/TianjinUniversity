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
