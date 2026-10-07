# Master Roadmap: Autonomous Bimanual Soft-Body Slicing (Paper 1)
## Calibrated 49-Week Research & Engineering Blueprint: Beginner to IEEE Submission
### DEX-ROB Lab | School of Electrical & Automation Engineering, Tianjin University

**Project:** Autonomous Bimanual Soft-Body Slicing via Proprioceptive Adaptive Impedance & Residual RL  
**Target Publication:** **IEEE ICRA 2028** (First Publication Deadline: **September 15, 2027**)  
**Embodiment:** Dual ARX AR5-L6 (7-DoF Manipulators) + LinkerHand O6 (5-Finger Dexterous Hand) + Culinary Knife  
**Research Team:**
- **Ahmed (Lead Holding Arm & Real-Time Control):** Left ARX AR5-L6 + LinkerHand O6, 1 kHz Proprioceptive Contact Wrench Observer $\mathbf{F}_{ext} = (\mathbf{J}^T)^\dagger \boldsymbol{\tau}_{ext}$, Grasp Stability & Anti-Crush Barrier RL, Linux PREEMPT_RT & CAN Bus Driver.
- **Shahd (Lead Slicing Arm & Fracture Mechanics):** Right ARX AR5-L6 + Culinary Knife, Gmsh Solid Tetrahedral Meshing, PhysX 5 FEM Fracture Dynamics, MoveIt 2 Cartesian Sawing Trajectory.
- **Advisor:** Prof. Shan An (安山) — Embodied Intelligence & Dexterous Manipulation.

---

## 1. The Hardware Engineer's Mental Model: Translating Your Knowledge

Coming from a hardware and embedded engineering background, you already possess intuition that pure computer science graduates lack. Robotics and Reinforcement Learning (RL) are not black magic; they are continuous control loops wrapped in numerical optimization.

| Hardware / Embedded Concept | Robotics Primitives | Reinforcement Learning Equivalents |
| :--- | :--- | :--- |
| **Microcontroller Main Loop** (`while(1)`) | Real-time 1 kHz control loop (`PREEMPT_RT`) | Environment Step (`env.step(action)`) |
| **ADC Readings & Sensor Conditioning** | Joint encoders ($\mathbf{q}, \dot{\mathbf{q}}$), Motor current ($I_{motor}$) | Observation Vector ($\mathbf{o}_t \in \mathbb{R}^{33}$) |
| **PWM & H-Bridge / Inverter Gates** | Motor torque commands ($\boldsymbol{\tau} \propto K_t \cdot I_q$) | Action Vector ($\mathbf{a}_t$) or Impedance Target |
| **RLC Analog Filter Circuit** | Spring-Mass-Damper Mechanical System | Impedance Model: $M_d \ddot{\tilde{x}} + D_d \dot{\tilde{x}} + K_d \tilde{x} = F_{ext}$ |
| **Feedback PID Loop Tuning** | Computed Torque / Task-Space Impedance Control | RL Policy Network ($\pi_\theta(\mathbf{a}_t \mid \mathbf{o}_t)$) adjusting $K_p, K_d, \mathbf{x}_{ref}$ |
| **Signal Noise & Component Tolerances** | Sensor jitter, gear backlash, link compliance | Domain Randomization ($\pm 20\%$ mass, friction, delay) |

---

## 2. Resource Acceleration: How AI & Assets Save 12 Weeks

| Resource / Tool | Standard Lab Approach | Our Accelerated Pipeline | Time Saved |
| :--- | :--- | :--- | :--- |
| **Aperdata SimReady Kitchen Assets** | Model countertops, plates, cutting boards in Blender/USD (~4 weeks). | Load pre-validated OpenUSD physics assets from `/home/omen/isaac-sim-assests/` directly into Isaac Lab. | **3–4 Weeks** |
| **DrEureka / LLM Reward Synthesis** | Hand-tune 8 reward penalty weights ($\lambda_{crush}, \lambda_{slip}$) through dozens of trial-and-error runs (~5 weeks). | Use LLM reflection loops on TensorBoard telemetry (`metrics/crush_rate`, `metrics/slip_dist`) to iteratively propose Pareto-optimal reward bounds. | **4–5 Weeks** |
| **Isaac Lab GPU Vectorization** | Train single-instance PyBullet / MuJoCo at 60 FPS (requires 48+ hours per run). | Run 512 to 1,024 parallel environments on RTX 5060 GPU with SkRL 2.1.0 PPO (converges in 2.5M steps / 2.5 hours). | **3 Weeks** |
| **Proprioceptive Torque Observer** | Design, manufacture, calibrate, and wire custom silicone tactile sensor arrays (~8–10 weeks). | Exploit native 1 kHz joint torque sensing $\mathbf{F}_{ext} = (\mathbf{J}^T)^\dagger \boldsymbol{\tau}_{ext}$ (confirmed with Prof. An). Zero hardware manufacturing delay. | **8–10 Weeks** |

---

## 3. The 49-Week Calendar Overview (Oct 7, 2026 – Sep 15, 2027)

```
                                     2026 - 2027 RESEARCH CALENDAR
 2026                                                  2027
 OCT     NOV     DEC     JAN           FEB     MAR     APR           MAY     JUN     JUL     AUG     SEP
 ├─── Sprint 1 ──┤ ├─── Sprint 2 ──┤ ├─── S3 ──┤ ├─── Sprint 4 ──┤ ├─── Sprint 5 ──┤ ├─── Sprint 6 ──┤ ├─ S7 ┤
  Kinematics &    Decoupled Hold    Winter GPU    Bimanual Sim &  Hardware Testbed   Sim-to-Real &   Paper &
  USD Tooling     RL & Saw Dist.    Break (CNY)   EXP-001..006    CAN & MoveIt 2    Physical Bench  Sub (ICRA)
                                                    ▲                                               ▲
                                              INTERNAL MID-TERM                             FIRST PAPER DEADLINE
                                              LAB CHECKPOINT                                (IEEE ICRA 2028)
                                              (Mar 31, 2027)                                (Sep 15, 2027)
```

- **Internal Mid-Term Checkpoint (March 31, 2027 / Week 25):** Complete Isaac Lab bimanual cutting simulation, validate baselines EXP-001 to EXP-006, and lock the simulation manuscript draft. This is an internal laboratory quality milestone for Prof. Shan An's review.
- **First Publication Deadline (September 15, 2027 / Week 49):** Complete physical sim-to-real transfer on dual AR5-L6 arms, 30-tomato physical cutting benchmark trials across 3 ripeness categories, statistical significance tests, 3-minute narrated video, and flagship **IEEE ICRA 2028** submission.

---

## 4. Sprint-by-Sprint Technical Execution Plan

### Sprint 1: Kinematic Tooling & Proprioceptive Observer (Weeks 1–6: Oct 7 – Nov 17, 2026)
*Goal: Move from robot asset import to real-time Cartesian Jacobian contact wrench estimation.*

#### Week 1 (Oct 7 – Oct 13): Asset Stabilization & Verification (COMPLETED)
- [x] Converted ARX AR5-L6 + LinkerHand O6 URDF to OpenUSD (`ar5_o6_left_combined.usda`).
- [x] Fixed 6,000:1 mass ratio instability via motor rotor armature conditioning (`armature=0.05` arm, `0.005` hand).
- [x] Verified active teleoperation via `control_ar5_teleop.py`.

#### Week 2 (Oct 14 – Oct 20): Standalone Kinematics & Manipulator Jacobian
- [ ] Implement `research/simulation/src/kinematics/ar5_kinematics.py` using PyTorch / Pinocchio:
  - Compute Forward Kinematics $\mathbf{x}_{tcp} = f(\mathbf{q})$ and Jacobian $\mathbf{J}(\mathbf{q}) \in \mathbb{R}^{6 \times 7}$.
  - Compute pseudo-inverse $\mathbf{J}^\dagger = \mathbf{J}^T (\mathbf{J} \mathbf{J}^T)^{-1}$ with damping $\lambda = 10^{-4}$ for singularity robustness.
- [ ] Unit test: verify analytical Jacobian against numerical finite differences ($err < 10^{-5}$).

#### Week 3 (Oct 21 – Oct 27): 1 kHz Proprioceptive Contact Wrench Observer
- [ ] Implement `research/simulation/src/control/wrench_estimator.py`:
  $$\mathbf{F}_{ext} = \left(\mathbf{J}^T(\mathbf{q})\right)^\dagger \left(\boldsymbol{\tau}_{measured} - \boldsymbol{\tau}_{gravity}(\mathbf{q}) - \boldsymbol{\tau}_{coriolis}(\mathbf{q}, \dot{\mathbf{q}})\right)$$
- [ ] Add 1st-order low-pass Butterworth filter ($f_c = 50\text{ Hz}$) to reject motor PWM current ripple.
- [ ] Unit test in Isaac Sim: press virtual fingertip against a rigid wall, verify estimated normal force matches PhysX ground-truth contact sensor within 5%.

#### Week 4 (Oct 28 – Nov 3): LinkerHand O6 Actuator Mapping
- [ ] Configure active actuators for the 6 motors: `lh_thumb_cmc_yaw`, `lh_thumb_cmc_pitch`, `lh_index_mcp_pitch`, `lh_middle_mcp_pitch`, `lh_ring_mcp_pitch`, `lh_pinky_mcp_pitch`.
- [ ] Enforce kinematic coupling for the 5 passive DIP joints: $\theta_{DIP} = 1.126 \cdot \theta_{MCP}$.
- [ ] Ensure mimic joints have zero conflicting PD controllers to prevent infinite torque fighting.

#### Week 5 (Nov 4 – Nov 10): Aperdata Scene Composition & Props
- [ ] Import `/home/omen/isaac-sim-assests/0_Kitchen_Indoor/Indoor.usd` into Isaac Sim.
- [ ] Spawn `dining_plate.usd` and custom cutting board prop at origin $(0, 0, 0.75)$.
- [ ] Position Left AR5 arm at $x = -0.35\text{ m}$ in default holding ready stance.

#### Week 6 (Nov 11 – Nov 17): Sprint 1 Review & Integration Test
- [ ] Run end-to-end integration test: script commands arm to approach tomato, close fingers in compliant grasp, and report reconstructed contact wrench.
- [ ] Output verification artifact: `experiments/results/sprint1_kinematic_validation.json`.

---

### Sprint 2: Decoupled Single-Arm Holding RL (Weeks 7–14: Nov 18, 2026 – Jan 12, 2027)
*Goal: Train RL holding policy to stabilize tomato against synthetic cutting disturbances.*

#### Week 7 (Nov 18 – Nov 24): Gym Environment Scaffolding (`HoldingTomatoEnvCfg`)
- [ ] Create `research/simulation/src/envs/holding_tomato_env.py` inheriting from Isaac Lab `ManagerBasedRLEnv`.
- [ ] Assemble 33D observation space $\mathbf{o}_t$:
  - Arm joint positions & velocities $\mathbf{q}_{1..7}, \dot{\mathbf{q}}_{1..7}$ (14D)
  - Hand active & passive joint positions $\mathbf{q}_{hand, 1..11}$ (11D)
  - Reconstructed fingertip contact forces $\mathbf{F}_{ext} \in \mathbb{R}^3$ (3D)
  - Estimated tomato displacement $\mathbf{p}_{tomato} - \mathbf{p}_0$ (3D)
  - Estimated tomato linear velocity $\mathbf{v}_{tomato, xy}$ (2D)

#### Week 8 (Nov 25 – Dec 1): Synthetic Slicing Disturbance Generator
- [ ] Build standalone disturbance generator applying realistic knife contact forces to the tomato:
  $$F_z(t) = 3.5 + 1.5 \sin(2\pi \cdot 2.0 \cdot t)\text{ N}, \quad F_x(t) = \pm 4.0\text{ N (sawing shear)}$$
- [ ] Verify that an open-loop or loose grip causes the tomato to slip or roll off the cutting board within 2 seconds.

#### Week 9 (Dec 2 – Dec 8): Multi-Objective Reward Formulation (`holding_rewards.py`)
- [ ] Implement barrier reward function:
  $$R_{hold} = R_{stability} - \lambda_1 P_{slip} - \lambda_2 P_{crush} - \lambda_3 P_{torque}$$
  - $R_{stability} = \exp(-\|\mathbf{p}_{tomato} - \mathbf{p}_0\|^2 / \sigma_p^2)$
  - $P_{slip} = \|\mathbf{v}_{rel, tomato-fingers}\|^2$ (penalizes micro-slip)
  - $P_{crush} = \max(0, F_n - 5.0\text{ N})^2$ (quadratic penalty above 5 N crushing barrier)
  - $P_{torque} = \|\boldsymbol{\tau}\|^2$ (regularizes excessive control effort)

#### Week 10 (Dec 9 – Dec 15): First SkRL Vectorized Training Run
- [ ] Launch 512 parallel Isaac Lab environments on RTX 5060 GPU:
  ```bash
  /home/omen/isaac-sim/python.sh experiments/scripts/train_holding_ppo.py --num_envs 512 --headless
  ```
- [ ] Stream metrics to WandB / TensorBoard: log `reward/total`, `metrics/crush_rate`, `metrics/slip_dist`.

#### Week 11 (Dec 16 – Dec 22): Reward Debugging & Eureka Automated Tuning
- [ ] Implement LLM reflection script inspecting reward logs to dynamically adjust penalty weights $\lambda_1, \lambda_2$.
- [ ] Eliminate failure modes: frozen grip (refusal to squeeze) vs death clamp (instant crushing).

#### Week 12 (Dec 23 – Dec 29): Fall Semester Exam Buffer / Policy Evaluation
- [ ] Evaluate trained policy across varying disturbance frequencies ($1\text{ Hz} \le f \le 5\text{ Hz}$).
- [ ] Log slip distance ($\Delta d_{slip}$) and peak normal force ($F_{max}$).

#### Week 13 (Dec 30 – Jan 5): Shahd's Subsystem Sync (Slicing Arm Progress)
- [ ] Sync with Shahd: inspect Gmsh tetrahedral tomato mesh (`tomato.msh`) and PhysX 5 FEM fracture parameters.
- [ ] Verify coordinate frame alignment: Left Arm palm facing $+x$, Right Arm knife approach from $+z$.

#### Week 14 (Jan 6 – Jan 12): Single-Arm Holding Checkpoint Lock
- [ ] Lock checkpoint `experiments/runs/holding_policy_v1.pt`.
- [ ] Verify against Hypothesis H1: normal force suppressed below 5.0 N in $\ge 95\%$ of synthetic sawing rollouts.

---

### Sprint 3: Winter Break GPU Simulation & Automated Training (Weeks 15–18: Jan 13 – Feb 16, 2027)
*Goal: Heavy headless simulation, policy optimization, and literature curation during university winter recess.*

#### Week 15 (Jan 13 – Jan 19): SkRL PPO Hyperparameter Sweep
- [ ] Execute multi-seed training runs (seeds 42, 100, 2026, 777, 999) on laptop GPU.
- [ ] Sweep learning rate ($1\times 10^{-4}$ to $5\times 10^{-4}$), GAE-$\lambda$ ($0.90$ to $0.98$), clip range ($\epsilon = 0.2$).

#### Week 16 (Jan 20 – Jan 26): Residual Action Space Implementation (ADR-004)
- [ ] Implement nominal Cartesian sawing trajectory generator for the right arm:
  $$v_{x,nom}(t) = A \omega \cos(\omega t), \quad v_{z,nom} = -v_{feed}$$
- [ ] Define policy residual action: $\mathbf{a}_t = [\Delta v_x, \Delta v_y, \Delta v_z, \Delta K_x, \Delta K_y, \Delta K_z]^T \in \mathbb{R}^6$.
- [ ] Verify that residual policy achieves smooth contact modulation without trajectory divergence.

#### Week 17 (Jan 27 – Feb 2 / Chinese New Year): Literature Deep Dive & Section II Drafting
- [ ] Populate `literature/papers/` with latest 2026/2027 publications on robotic food cutting and tactile impedance.
- [ ] Draft `paper/sections/02_related_work.tex` in IEEEtran format.

#### Week 18 (Feb 3 – Feb 16): Automated Domain Randomization (DrEureka Bounds)
- [ ] Configure PhysX 5 FEM parameter randomization:
  - Tomato Young's Modulus $E \in [30\text{ kPa}, 120\text{ kPa}]$
  - Poisson's ratio $\nu \in [0.40, 0.49]$
  - Friction coefficient $\mu \in [0.25, 0.75]$
  - Knife sharpness cutting threshold $\sigma_c \pm 30\%$
- [ ] Pre-train policies for Sprint 4 bimanual integration.

---

### Sprint 4: Bimanual Merger & Baseline Sweep (Weeks 19–26: Feb 17 – Apr 13, 2027)
*Goal: Combine holding and cutting arms, execute EXP-001 through EXP-006, reach Gate 1 Milestone.*

#### Week 19 (Feb 17 – Feb 23): Bimanual Scene Assembly (`BimanualTomatoCuttingEnv`)
- [ ] Mount both ARX AR5-L6 arms in Isaac Lab stage: Left arm at $x = -0.35\text{ m}$, Right arm at $x = +0.35\text{ m}$.
- [ ] Integrate PhysX 5 FEM deformable tomato mesh between hand and blade.

#### Week 20 (Feb 24 – Mar 2): Slicing & Holding Co-Simulation
- [ ] Test closed-loop interaction: Left hand establishes 3.0 N holding grasp; Right arm executes sawing cut.
- [ ] Verify collision geometries and solver stability at 120 Hz physics substepping.

#### Week 21 (Mar 3 – Mar 9): Execution of Baseline 1 (EXP-001) & Baseline 2 (EXP-002)
- [ ] Run EXP-001: Pure kinematic sawing (fixed position trajectory). Measure crush rate on soft tomatoes.
- [ ] Run EXP-002: Fixed-gain task-space impedance control. Measure stall rate on firm tomatoes.
- [ ] Log 5 seeds per baseline into `experiments/runs/`.

#### Week 22 (Mar 10 – Mar 16): Execution of Proposed Method (EXP-003)
- [ ] Run EXP-003: Tactile-conditioned residual RL policy.
- [ ] Measure slice completion rate, max deformation, and pulp burst rate.

#### Week 23 (Mar 17 – Mar 23): Execution of Ablations (EXP-004, EXP-005, EXP-006)
- [ ] Run EXP-004: End-to-end 14-DoF joint position RL.
- [ ] Run EXP-005: End-to-end Cartesian velocity RL without nominal primitive.
- [ ] Run EXP-006: Residual over kinematic primitive RL.
- [ ] Measure sample efficiency steps to convergence across all three configurations.

#### Week 24 (Mar 24 – Mar 30): Statistical Hypothesis Testing (H1 & H2 Validation)
- [ ] Run Mann-Whitney U test and Welch's t-test via `analysis/statistical_tests.py`.
- [ ] Validate Claims CLAIM-01, CLAIM-02, CLAIM-03 in `research_state/paper_claims.yaml`.

#### Week 25 (Mar 31 – Apr 6): ★ GATE 1 MILESTONE REVIEW (M7 - RA-L / Workshop Ready)
- [ ] Compile simulation experimental results table and convergence curves (`analysis/plots/`).
- [ ] Draft simulation manuscript and submit for Prof. Shan An's mid-term evaluation.

#### Week 26 (Apr 7 – Apr 13): Mid-Term Architecture Debrief & Hardware Preparation
- [ ] Resolve any outstanding simulation issues; freeze simulation code.
- [ ] Order physical experiment consumables (specimen mounts, standardized test tomatoes, calibration weights).

---

### Sprint 5: Real Hardware Testbed & Low-Level Drivers (Weeks 27–34: Apr 14 – Jun 8, 2027)
*Goal: Commission physical dual AR5-L6 arms, PREEMPT_RT Linux, 1 kHz CAN bus, and safety interlocks.*

#### Week 27 (Apr 14 – Apr 20): Control PC Setup & PREEMPT_RT Linux Kernel
- [ ] Install Ubuntu 22.04 LTS with PREEMPT_RT patch on laboratory control workstation.
- [ ] Run `cyclictest`: verify latency jitter $< 50\ \mu\text{s}$ over 1 hour under CPU load.

#### Week 28 (Apr 21 – Apr 27): CAN Bus Hardware Interface (`can0`, `can1`)
- [ ] Configure dual CAN-FD / SocketCAN interfaces at 1 Mbps.
- [ ] Verify deterministic 1 kHz send/receive loop with ARX AR5-L6 motor drivers.

#### Week 29 (Apr 28 – May 4): Gravity & Friction Model Calibration
- [ ] Measure and calibrate dynamic parameters (link mass, center of mass, joint friction) for both AR5 arms.
- [ ] Ensure zero-gravity manual lead-through mode works smoothly without drift.

#### Week 30 (May 5 – May 11): 1 kHz External Wrench Calibration on Physical Arm
- [ ] Mount digital 6-axis load cell / force gauge to the LinkerHand O6 palm.
- [ ] Apply known forces ($1\text{ N}, 2\text{ N}, 5\text{ N}, 10\text{ N}$) and calibrate torque-to-wrench mapping $\mathbf{F}_{ext} = (\mathbf{J}^T)^\dagger \boldsymbol{\tau}_{ext}$.
- [ ] Confirm measurement error $< 0.3\text{ N}$ in the $1.5\text{ N} - 5.0\text{ N}$ operating window.

#### Week 31 (May 12 – May 18): LinkerHand O6 Physical Driver & Tendon Sync
- [ ] Interface LinkerHand O6 6 active motors via USB/CAN.
- [ ] Calibrate finger joint limits and verify gentle compliant tomato grasping without motor overheating.

#### Week 32 (May 19 – May 25): Hardware Safety Watchdog System
- [ ] Implement hardware E-stop interlocks:
  - Over-torque cutoff: trigger safe disable if $|\tau_i| > 25\text{ N}\cdot\text{m}$.
  - Cartesian workspace bounding box ($30\times 30\times 30\text{ cm}$ safety cube around cutting board).
  - Velocity limit clamping ($v_{cart} \le 0.15\text{ m/s}$).

#### Week 33 (May 26 – Jun 1): MoveIt 2 Cartesian Sawing Trajectory Integration
- [ ] Configure MoveIt 2 servo node for Right AR5 arm.
- [ ] Verify smooth, jitter-free sinusoidal sawing motion with culinary blade in free air.

#### Week 34 (Jun 2 – Jun 8): Bimanual Physical Teleop & Dry Runs
- [ ] Execute coordinated dry run: Left arm grasps rigid 3D-printed dummy tomato; Right arm executes sawing strokes above it.
- [ ] Confirm zero collision between knife flange and robot fingers.

---

### Sprint 6: Sim-to-Real Transfer & Physical Cutting Trials (Weeks 35–43: Jun 9 – Aug 10, 2027)
*Goal: Full-scale physical benchmarking with 30 commercial tomatoes across 3 ripeness categories.*

#### Week 35 (Jun 9 – Jun 15): Sim-to-Real Policy Export & ONNX / TensorRT Deployment
- [ ] Export trained PyTorch policy weights from Isaac Lab to ONNX format.
- [ ] Build C++ / Python real-time inference node evaluating policy at 100 Hz inside the 1 kHz RT control loop.

#### Week 36 (Jun 16 – Jun 22): Overhead Vision Sensor Calibration (Intel RealSense D435i)
- [ ] Mount RealSense D435i camera overhead; calibrate eye-to-hand extrinsics via AprilTag board.
- [ ] Configure point cloud segmentation to measure tomato height and deformation $\Delta h(t)$ in real-time.

#### Week 37 (Jun 23 – Jun 29): Physical Cutting Trials (Firm Tomatoes)
- [ ] Conduct first 10 physical cutting trials on Firm/Unripe tomatoes.
- [ ] Verify skin puncture detection and sawing feed without knife stalling.

#### Week 38 (Jun 30 – Jul 6): Physical Cutting Trials (Ripe/Optimal Tomatoes)
- [ ] Conduct 10 physical cutting trials on Standard Ripe tomatoes.
- [ ] Test proposed adaptive compliance vs fixed rigid grip (demonstrate crush prevention).

#### Week 39 (Jul 7 – Jul 13): Physical Cutting Trials (Soft/Overripe Tomatoes)
- [ ] Conduct 10 physical cutting trials on Soft/Overripe tomatoes.
- [ ] Record extreme contact deformations and verify zero pulp bursting.

#### Week 40 (Jul 14 – Jul 20): Sim-to-Real Domain Randomization Benchmark (EXP-007 vs EXP-008)
- [ ] Test policy trained without DR (EXP-007) vs policy trained with PhysX 5 FEM DR (EXP-008) on physical hardware.
- [ ] Validate Hypothesis H3 and Claim CLAIM-04 (zero-shot transfer $\ge 80\%$).

#### Week 41 (Jul 21 – Jul 27): Quantitative Metrics Extraction & Cross-Section Imaging
- [ ] Measure cut surface roughness, slice thickness uniformity ($\pm 1.5\text{ mm}$)$, and juice leakage weight.
- [ ] Photograph high-resolution cross-sections for publication figures.

#### Week 42 (Jul 28 – Aug 3): High-Speed Video & Failure Mode Recording
- [ ] Capture 120 FPS slow-motion footage of knife-skin puncture event.
- [ ] Document all failure modes (slip, stall, crush) across baselines for honest discussion section.

#### Week 43 (Aug 4 – Aug 10): Physical Data Archival & Script Finalization
- [ ] Archive all 1 kHz CSV telemetry logs to `experiments/results/physical_trials/`.
- [ ] Run `python scripts/research_cli.py verify-claims` to ensure 100% data backing.

---

### Sprint 7: IEEE Manuscript Authorship & ICRA Submission (Weeks 44–49: Aug 11 – Sep 15, 2027)
*Goal: Camera-ready IEEEtran paper, professional figures, 3-minute video, and conference submission.*

#### Week 44 (Aug 11 – Aug 17): Figure & Visualization Production
- [ ] Fig 1: End-to-end Bimanual System Architecture block diagram (Vector PDF).
- [ ] Fig 2: FEM vs Physical 4-phase contact force curves ($F_z, F_x$ during puncture).
- [ ] Fig 3: Training convergence curves (EXP-004 vs 005 vs 006, 5 seeds with shaded std-error).
- [ ] Fig 4: Photo montage of 30 physical cutting trials and slice cross-sections.

#### Week 45 (Aug 18 – Aug 24): Drafting Core Technical Sections
- [ ] Section III: Problem Formulation, 1 kHz Wrench Observer & Hybrid Dynamics.
- [ ] Section IV: Tactile-Conditioned Residual RL Policy & Barrier Rewards.
- [ ] Section V: Experimental Setup, Baselines & Simulation Benchmarks.

#### Week 46 (Aug 25 – Aug 31): Drafting Results, Discussion & Tables
- [ ] Section VI: Results & Ablations (Table I: Quantitative baseline comparison, Table II: Sim-to-Real metrics).
- [ ] Abstract & Section I: Introduction framing the soft-body manipulation challenge.
- [ ] Section VII: Conclusion & Future Work (connecting to ADEPT foundation dexterity).

#### Week 47 (Sep 1 – Sep 7): 3-Minute IEEE Supplementary Video Production
- [ ] Script, record, and voice-over 3-minute video: problem statement, sim training, physical experiments, slow-motion cuts.

#### Week 48 (Sep 8 – Sep 12): Advisor Review & Polish with Prof. Shan An
- [ ] Conduct formal paper review with Prof. An; incorporate revision suggestions.
- [ ] Check IEEEtran formatting, references, and margin compliance.

#### Week 49 (Sep 13 – Sep 15): Final Submission to IEEE ICRA 2028 Portal
- [ ] Upload PDF manuscript, supplementary video, and metadata before the mid-September deadline.
- [ ] Celebrate completion of Paper 1!
