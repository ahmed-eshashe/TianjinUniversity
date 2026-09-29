# 12-Month Research & Engineering Master Plan (Sep 2026 – Sep 2027)

**Project:** Autonomous Bimanual Soft-Body Slicing via Proprioceptive Adaptive Impedance & RL  
**Target Publication:** IEEE RA-L / IROS / ICRA (Submission: September 2027)  
**Authors / Research Team:**  
- **Ahmed:** Lead Holding Arm, Proprioceptive Compliance & Real-Time Robot Control  
- **Shahd:** Lead Slicing Arm, Fracture Physics (FEM) & Trajectory Coordination  
**Laboratory:** DEX-ROB Lab, School of Electrical & Automation Engineering, Tianjin University  
**Advisor:** Prof. Shan An (安山)  

---

## 1. Executive Strategy: High-Rate Proprioceptive Sensing on Standard Embodiments

Per confirmation with Prof. Shan An, **no custom tactile sensors will be fabricated**. Instead, the system leverages the robot's **native built-in 1 kHz joint torque sensing stack**, making the research cleaner, immediately reproducible by any robotics lab worldwide, and completely free of custom hardware turnaround delays:

1. **The Native Proprioceptive Sensing Pipeline:**
   - **Franka Emika Panda 1 kHz Joint Torques ($\boldsymbol{\tau}_{ext} \in \mathbb{R}^7$):** Internal strain-gauge torque sensors in all 7 joints measure external interaction torques by subtracting gravity, Coriolis, and link inertia models at 1,000 Hz.
   - **Cartesian Contact Wrench Reconstruction:** Contact forces at the fingertips are computed analytically via the manipulator Jacobian transpose pseudo-inverse:
     $$\mathbf{F}_{ext} = \left(\mathbf{J}^T(\mathbf{q})\right)^\dagger \boldsymbol{\tau}_{ext} \in \mathbb{R}^3$$
     This provides clean 3-axis force feedback ($F_x, F_y, F_z$) with $< 0.2\text{ N}$ sensitivity without adding external sensors or wiring.
   - **Gripper Current Feedback:** Motor current monitoring on the Franka Hand provides direct clamp force estimation ($F_{grip} \propto K_t \cdot I_{motor}$).
   - **Vision (30 Hz):** Overhead Intel RealSense D435i camera provides global 6D tomato pose, cut positioning, and macro deformation tracking.

2. **The Hardware Engineer's Advantage in Proprioceptive Robot Control:**
   Your background in embedded systems, motor drivers, and current loops translates directly into low-level robot control:
   - Understanding torque constants ($K_t$), motor driver current loops, and bandwidth limits is essential for tuning stable 1 kHz impedance controllers.
   - Setting up real-time Linux kernels (`PREEMPT_RT`) and low-latency C++ control loops (`libfranka`) to avoid packet drops or jitter.
   - The mechanical spring-damper equation is mathematically identical to an analog RLC filter:
     $$\underbrace{M_d \ddot{\tilde{x}}}_{\text{Inertia } (L)} + \underbrace{D_d \dot{\tilde{x}}}_{\text{Damping } (R)} + \underbrace{K_d \tilde{x}}_{\text{Stiffness } (1/C)} = F_{ext}$$

---

## 2. Team Division of Labor (Decoupled Parallel Architecture)

To ensure neither researcher ever blocks the other, development follows **Option A (Horizontal Subsystem Split)** from `research/simulation/two_person_parallel_workflow.md`:

```
                       DECOUPLED 2-PERSON PARALLEL ARCHITECTURE
┌─────────────────────────────────────────────────────────┐  ┌─────────────────────────────────────────────────────────┐
│         SHAHD: SLICING ARM & FRACTURE LEAD              │  │        AHMED (YOU): HOLDING ARM & CONTROL LEAD          │
├─────────────────────────────────────────────────────────┤  ├─────────────────────────────────────────────────────────┤
│ • Physics: Gmsh volumetric TetMesh & PhysX 5 FEM tearing│  │ • Control: 1 kHz joint torque force estimator (F_ext)   │
│ • Slicing Arm: Knife URDF, feed delta Δv_z, sawing v_x  │  │ • Compliance: Grasp force regulation (1.5N < F < 5.0N) │
│ • Slicing Reward: R_pen, R_slicing, P_crush, P_slam     │  │ • Slip Prevention: Tangential friction compensation Δx  │
│ • Controller: Phase-adaptive knife Z-impedance          │  │ • Holding Reward: P_sync, P_bruise, P_slip              │
│ • Macro Planning: MoveIt 2 pre-contact approach & sync  │  │ • Real-Time Systems: PREEMPT_RT Linux & libfranka C++   │
│ • Perception: RealSense 6D tomato pose & localization   │  │ • Observation Space: 33D state packing (`state_mgr.py`) │
│                                                         │  │                                                         │
│ [Unit Test A: Knife slices a rigidly clamped tomato]    │  │ [Unit Test B: Gripper stabilizes tomato vs disturbances]│
└────────────────────────────┬────────────────────────────┘  └────────────────────────────┬────────────────────────────┘
                             │                                                            │
                             └─────────────────────────────┬──────────────────────────────┘
                                                           │
                                                PHASE 2: BIMANUAL MERGER
                                                           ▼
                                      Dual Franka Arms: Hold + Slice concurrently
```

---

## 3. High-Level 12-Month Gantt Roadmap

| Phase | Timeframe | Primary Focus | Ahmed's Deliverables (Holding Arm & Control) | Shahd's Deliverables (Slicing Arm & Physics) |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1** | **M1–M3** (Oct–Dec 2026) | Foundations & Decoupled Single-Arm Sim | Gripper holding unit test under disturbance; 33D state manager; `libfranka` 1 kHz torque interface | Clamped tomato slicing unit test in Isaac Lab; Gmsh TetMesh; MoveIt 2 setup |
| **Phase 2** | **M4–M6** (Jan–Mar 2027) | Bimanual Sim Integration & Core RL Sweeps | Grasp compliance & slip prevention RL; `PREEMPT_RT` workstation setup; baseline comparisons | Merged bimanual env (`BimanualTomatoCuttingEnv`); knife impedance law; WandB sweeps |
| **Phase 3** | **M7–M9** (Apr–Jun 2027) | Domain Randomization & Physical Lab Experiments | Physical robot real-time 1 kHz grasp loop; holding slip & deformation logs; safety watchdogs | Sim domain randomization; RealSense 6D tomato pose; **30-Tomato Physical Benchmark Matrix** |
| **Phase 4** | **M10–M12** (Jul–Sep 2027) | Manuscript Drafting, Figures & IEEE Submission | Sections II & IV; holding stability & slip plots; control architecture block diagram | Sections III & V; cutting force plots; FEM stress contours; IEEE paper submission |

---

## 4. Month-by-Month Detailed Engineering Roadmap

### Phase 1: Foundations, Tooling & Decoupled Unit Tests (Months 1–3: Oct – Dec 2026)

#### Month 1: October 2026 — Ramp-up, Toolchain Setup & Math Bridges
* **Goal:** Transition hardware skills to robotics primitives and establish isolated development environments.
* **Ahmed (You — Holding Arm & Real-Time Control Lead):**
  - **Robotics Primitives:** Master ROS 2 TF2 coordinate transforms, gripper URDF models, and joint torque interfaces ($\boldsymbol{\tau} = \mathbf{J}^T \mathbf{F}$).
  - **Simulation Tooling:** Install NVIDIA Isaac Lab and SkRL on the RTX workstation. Run Franka gripper grasp tutorials.
  - **State Architecture:** Build `src/observations/state_manager.py` to assemble the 33D observation vector using dummy PyTorch tensors.
  - **Curriculum Study:** Read the beginner-friendly CS285 Master Guides in `research/simulation/scripts/` (focusing on Lecture 4: Policy Gradients & Lecture 5: Actor-Critic).
  - **Milestone 1.1:** Spawn Franka arm with parallel gripper in Isaac Sim and command closing force/position.
* **Shahd (Slicing Arm & Fracture Lead):**
  - **Physics & Meshing:** Learn Gmsh scripting to turn 3D tomato `.obj` surface scans into solid tetrahedral meshes (`tomato.msh`).
  - **Knife CAD & Kinematics:** Attach kitchen knife CAD to Franka arm flange in Isaac Sim. Verify tool center point (TCP).
  - **Trajectory Planning:** Configure MoveIt 2 in ROS 2 for collision-free Cartesian trajectory generation.
* **Joint Checkpoint (End of Month 1):** Shared interface definitions locked (33D observation, 4D slicing action, 2D holding action).

#### Month 2: November 2026 — Asset Pipeline & Independent Unit Tests
* **Goal:** Build the two decoupled simulation worlds so both researchers can train RL without waiting for each other.
* **Ahmed (You):**
  - **Holding Scene (`src/envs/components/holding_arm.py`):** Model a Franka arm equipped with a compliant gripper holding an upright deformable tomato.
  - **Disturbance Generator:** Inject synthetic oscillating forces ($\pm 4\text{ N}$ lateral sawing shear, $2–8\text{ N}$ downward penetration) into the tomato body to simulate the knife's cutting actions.
  - **Proprioceptive Force Sensor Modeling:** Reconstruct contact wrench from simulated joint torque sensors in Isaac Lab.
* **Shahd:**
  - **Clamped Slicing Scene (`src/envs/components/cutting_arm.py`):** Model a Franka arm holding a knife above a tomato clamped in a rigid jig on a cutting board.
  - **PhysX FEM Tearing:** Configure PhysX 5 FEM deformable body elasticity ($E = 1.2\text{ MPa}, \nu = 0.4$) and topological element separation under blade contact.
  - **Feed Kinematics:** Implement combined downward penetration ($\Delta v_z$) and longitudinal sawing feed ($v_{slice, x}$) to reduce cutting friction.
* **Joint Checkpoint (End of Month 2):** Both single-arm environments run headlessly at >100 FPS in Isaac Lab.

#### Month 3: December 2026 — Single-Arm RL Benchmarks & Real-Time Driver Verification
* **Goal:** Prove both arms work in isolation and verify the physical robot driver interface in DEX-ROB Lab.
* **Ahmed (You):**
  - **Holding RL Training:** Train PPO on the holding gripper to maintain normal force within the safe non-bruising window:
    $$1.5\text{ N} < F_{hold} < 5.0\text{ N} \quad (\text{slip prevention without bruising})$$
  - **Real-Time Linux Test:** Configure a lab PC with Ubuntu 22.04 + `PREEMPT_RT` kernel. Compile `libfranka` and run `echo_robot_state` to verify 1 kHz joint torque readouts with $< 50\,\mu\text{s}$ jitter.
* **Shahd:**
  - **Slicing RL Training:** Train PPO on the clamped tomato. Reward function:
    $$R_{slice} = w_{pen}\Delta z + w_{saw}|v_x|\mathbb{I}(F_z > 0.5) - w_{crush}\max(0, F_z - 8.0)^2 - w_{slam}\max(0, \ddot{z})$$
  - Verify knife cuts completely through the clamped tomato without triggering the crushing penalty.
* **Deliverable Gate 1 (End of Month 3):**
  1. Ahmed's gripper keeps the tomato stable against 8 N disturbance forces without crushing.
  2. Shahd's knife slices the clamped tomato cleanly in Isaac Lab.
  3. `libfranka` 1 kHz torque communication verified on the physical lab arm.

---

### Phase 2: Bimanual Integration & Core RL Benchmarking (Months 4–6: Jan – Mar 2027)

#### Month 4: January 2027 — The Bimanual Merger & Impedance Law
* **Goal:** Integrate both arms into a unified scene and implement the dual-arm impedance control law.
* **Joint:**
  - Merge `cutting_arm.py` and `holding_arm.py` into `src/envs/bimanual_cutting_env.py`.
  - Validate collision meshes between the two Franka arms in Isaac Lab.
* **Ahmed (You):**
  - **Grasp Compliance Law (`src/controllers/holding_compliance.py`):** Implement adaptive grasp compliance with tangential friction compensation:
    $$\Delta x_{hold} = -k_{slip} \cdot v_{tomato, x}, \quad F_{hold} = \text{clamp}(F_{target}, 1.5\text{ N}, 5.0\text{ N})$$
  - **State Wiring:** Connect reconstructed joint-torque contact forces into `state_manager.py`.
* **Shahd:**
  - **Slicing Impedance (`src/controllers/slicing_impedance.py`):** Implement variable Z-impedance controller ($K_z, D_z$) with virtual energy tank to arrest blade slam post-puncture.
  - **Macro-to-Micro Handoff:** Code supervisory state machine: MoveIt brings both arms to pre-contact clearance $\to$ triggers contact threshold ($F_z > 0.5\text{ N}$) $\to$ activates RL policy.
* **Milestone 2.1:** Dual-arm Isaac Lab environment runs synchronously with zero NaN errors or joint physics explosions.

#### Month 5: February 2027 — Co-Training & Real-Time C++ Controller
* **Goal:** Achieve autonomous bimanual slicing in sim and complete the real-time C++ control node.
* **Ahmed (You):**
  - **C++ Controller Node:** Implement the real-time 1 kHz joint torque controller in C++ using `libfranka` / `ros2_control`. Map Cartesian impedance directly into joint torques:
    $$\boldsymbol{\tau}_{cmd} = \mathbf{J}^T \left( \mathbf{K}_d \tilde{\mathbf{x}} + \mathbf{D}_d \dot{\tilde{\mathbf{x}}} \right) + \mathbf{g}(\mathbf{q})$$
  - Add software safety limits (joint velocity caps, max force limits).
* **Shahd:**
  - **Bimanual Training Sweeps:** Run SkRL PPO across 128 parallel environments in Isaac Lab.
  - **WandB Tracking:** Log episode return, tomato slip distance, peak crushing force, and cut completion %.
* **Milestone 2.2:** Policy achieves >85% clean cuts in simulation without dropping or squishing the fruit.

#### Month 6: March 2027 — Simulation Baselines & Benchmark Comparison
* **Goal:** Complete all simulation baseline evaluations.
* **Ahmed (You):**
  - **Holding Stability Analysis:** Benchmark grip stability with adaptive torque compliance vs rigid fixed-width grasping.
* **Shahd:**
  - **Sim Baseline Comparisons:** Run comparative benchmarks:
    1. Baseline 1: Pure Position Control (rigid trajectory replay).
    2. Baseline 2: Fixed Impedance Control (constant $K_z, D_z$).
    3. Baseline 3: Vision-Only RL (no force/torque compliance).
    4. Proposed Method: Bimanual Proprioceptive Adaptive Impedance RL.
* **Deliverable Gate 2 (End of Month 6):**
  1. Simulation results show proposed bimanual method reduces slip by >80% and peak crushing force by >60% compared to baselines.
  2. Real-time C++ controller running stably at 1 kHz with $< 50\,\mu\text{s}$ latency.

---

### Phase 3: Domain Randomization, Sim-to-Real & Lab Trials (Months 7–9: Apr – Jun 2027)

#### Month 7: April 2027 — Domain Randomization & Physical Lab Setup
* **Goal:** Close the reality gap in simulation and configure the physical dual-arm workspace in DEX-ROB Lab.
* **Ahmed (You):**
  - **Physical Safety Watchdogs:** Configure real-time E-stop logic ($F_{hold} > 10\text{ N}$ abort, workspace bounding boxes).
  - Calibrate gripper finger friction on real food samples.
* **Shahd:**
  - **Domain Randomization in Sim:** Randomize tomato elasticity ($E \in [0.8, 1.8]\text{ MPa}$), skin toughness, knife friction, and control latency ($1–15\text{ ms}$). Retrain bimanual policy.
  - **Perception Setup:** Mount Intel RealSense D435i overhead camera. Configure YOLOv11-seg for 6D tomato bounding box and pose estimation.
* **Milestone 3.1:** Policy converges under domain randomization in Isaac Lab. Physical Franka dual-arm testbed ready.

#### Month 8: May 2027 — Zero-Shot / Fine-Tuned Real Robot Deployment
* **Goal:** Achieve the first autonomous physical bimanual tomato slice without crushing or fruit drop.
* **Ahmed (You):**
  - Deploy 1 kHz grasp compliance loop on physical Franka holding arm. Verify real-time force tracking during contact.
* **Shahd:**
  - Deploy slicing arm trajectory control. Coordinate MoveIt approach with vision tracking.
* **Joint Milestone 3.2:** **FIRST SUCCESSFUL PHYSICAL BIMANUAL CUT.** Holding arm stabilizes tomato without bruising; slicing arm cuts cleanly into 8 mm disks without juice spray!

#### Month 9: June 2027 — Comprehensive Physical Benchmark Trials (The 30-Tomato Matrix)
* **Goal:** Execute the full physical experimental matrix to build irrefutable, publication-grade empirical proof.
* **Joint Experimental Protocol:**
  - Test **30 fresh market tomatoes** across 3 ripeness tiers:
    1. Tier A (Unripe / Green-Firm): High skin toughness, stiff pulp.
    2. Tier B (Ripe / Table-Ready): Standard elastic skin, moderate pulp yielding.
    3. Tier C (Overripe / Soft): Fragile pre-stressed skin, fluid-rich interior (extreme crushing/bruising hazard).
  - Benchmark across 4 conditions: (1) Rigid Position Control, (2) Constant Compliance, (3) Vision-Only RL, (4) **Our Proposed Proprioceptive Bimanual System**.
* **Ahmed (You):**
  - Measure holding arm slip displacement, fruit deformation, and juice loss mass.
  - Record 1 kHz joint torque profiles ($\boldsymbol{\tau}_{ext}$) and reconstructed contact forces ($\mathbf{F}_{ext}$).
* **Shahd:**
  - Record knife penetration force profiles ($F_z, F_x$) and blade slam deceleration.
  - Measure slice thickness uniformity and surface roughness using optical depth scans.
* **Deliverable Gate 3 (End of Month 9):**
  1. Complete physical experimental dataset collected and logged.
  2. Proven 0% crushing and 0% slip failure on overripe tomatoes using proprioceptive compliance vs >70% failure on baselines.

---

### Phase 4: Manuscript Drafting, Polishing & IEEE Submission (Months 10–12: Jul – Sep 2027)

#### Month 10: July 2027 — Manuscript Drafting & Figure Generation
* **Goal:** Draft the complete 6-page IEEE format manuscript following the 50/50 division.
* **Ahmed (You) — Primary Sections:**
  - **Section II (Related Work):** Proprioceptive force control, compliant grasping, food manipulation robotics.
  - **Section IV (System Architecture & Proprioceptive Control):** Joint-torque force reconstruction ($\mathbf{F}_{ext} = (\mathbf{J}^T)^\dagger \boldsymbol{\tau}_{ext}$), 1 kHz grasp compliance law, slip prevention mechanics.
  - **Section VI-B (Holding Stability & Baselines):** Grasp force regulation plots, slip arrest metrics, baseline comparison tables.
  - **Figures:** Generate Fig. 1 (System block diagram), Fig. 3 (Proprioceptive grasp loop), Fig. 4B (Grip force & slip plots).
* **Shahd — Primary Sections:**
  - **Section III (Deformable Mechanics & Tearing Physics):** 4-phase cutting dynamics, PhysX FEM simulation parameters, fracture criteria ($K_I \ge K_{Ic}$).
  - **Section V (MDP Problem Formulation & Coordination):** Dual-arm state/action spaces, reward formulation, macro-to-micro handoff state machine.
  - **Section VI-A (Slicing Performance & Ablations):** Knife force profiles, slice thickness uniformity, juice loss analysis.
  - **Figures:** Generate Fig. 2 (4-Phase cutting force curve & FEM stress fields) and Fig. 4A (Physical slice photos & cross-sections).
* **Milestone 4.1:** Complete Draft 1 assembled in LaTeX (Overleaf IEEE template).

#### Month 11: August 2027 — Video Production & Advisor Feedback Iteration
* **Goal:** Polish paper with Prof. Shan An and produce the compulsory IEEE supplementary video.
* **Joint:**
  - **Supplementary Video (3 Minutes):**
    - 0:00–0:45: Problem motivation (why soft foods slip or get crushed; the bimanual coordination challenge).
    - 0:45–1:30: Isaac Lab GPU simulation setup & proprioceptive torque sensing pipeline.
    - 1:30–2:15: Side-by-side slow-motion physical cutting comparisons (Baseline dropped/crushed tomato vs Our clean slice).
    - 2:15–3:00: Quantitative plots, force curves, and summary of contributions.
  - **Advisor Review:** Submit Draft 1 and video to Prof. Shan An. Revise introduction narrative, abstract punchiness, and formal notation.
* **Milestone 4.2:** Draft 2 approved by Prof. Shan An.

#### Month 12: September 2027 — Final Polish & Submission to IEEE RA-L / IROS
* **Goal:** Final proofreading, formatting compliance, and official submission.
* **Week 1 (Sep 1–7):** Final mathematical check; ensure every variable in equations is defined. Run IEEE PDF eXpress to ensure compliance.
* **Week 2 (Sep 8–14):** Polish high-resolution vector figures (300 DPI, CMYK color space). Verify video audio and subtitles.
* **Week 3 (Sep 15–21):** Upload final manuscript, supplementary video, and open-source GitHub repository link to IEEE PaperPlaza / submission portal.
* **Week 4 (Sep 22–30):** Celebrate milestone submission! Prepare code for lab archival and transition to Paper 2 (ADEPT scaling).

---

## 5. Weekly Rhythm & Sync Protocol

To maintain steady progress without burnout or miscommunication:
1. **Monday Morning Sync (30 min):**
   - Review previous week's git commits.
   - Align on the single primary deliverable for the week.
   - Identify any shared interface changes (`state_manager.py`, action bounds).
2. **Wednesday Mid-Week Check-in (15 min):**
   - Quick blocker resolution (e.g., Isaac Lab physics divergence, real-time driver latency).
3. **Friday Afternoon Demo & Lab Log (45 min):**
   - Live demo of simulation progress or physical robot test.
   - Commit and push all code to `TianjinUniversity` repository.
   - Update weekly log in `research/reports/`.
4. **Monthly Advisor Meeting with Prof. Shan An:**
   - Present slide deck with video recordings, force plots, and upcoming milestone forecast.

---

## 6. Proactive Risk Management & Contingency Plan

| Potential Failure Point | Likelihood | Impact | Built-in Countermeasure / Fallback |
| :--- | :--- | :--- | :--- |
| **FEM tearing in Isaac Lab is unstable or slow** | Medium | High | Shahd can use **clamped surface boundary method** with dynamic topological element deletion, or benchmark on continuous contact with non-linear compliance before full fracture splitting. |
| **Joint torque force estimation has noise** | Low | Low | Apply an on-line 1st-order low-pass Butterworth filter ($f_c \approx 50\text{ Hz}$) or Kalman filter on $\boldsymbol{\tau}_{ext}$ in C++. |
| **Physical robot access is limited in lab** | Low | High | Decoupled sim architecture allows 90% of RL reward tuning and impedance parameter sweeps to be completed in Isaac Lab prior to physical hardware access. |
| **Tomato slip occurs under high sawing speeds** | Low | Medium | Ahmed's holding arm policy incorporates active tangential friction compensation ($\Delta x_{hold}$) counter-acting knife longitudinal travel $v_{slice, x}$. |
| **Paper deadline pressure in August** | Medium | Medium | Figures, tables, and experimental methodology are written continuously during Months 6–9 rather than saved for Month 10. |

---

## 7. Recommended Immediate Action Items (Next 14 Days)

1. **Lock Git Branches:**
   - `git checkout -b dev/holding-arm` (Ahmed)
   - `git checkout -b dev/cutting-arm` (Shahd)
2. **Isaac Lab Environment Smoke Test:**
   - Run Isaac Lab headless Franka gripper tutorial to confirm GPU acceleration and contact physics are operational.
3. **Physical Robot Driver Verification (DEX-ROB Lab):**
   - Build `libfranka` on the lab workstation and run `echo_robot_state` to observe native 1 kHz joint torque readouts.
4. **Read Selected CS285 Masterclass Guides:**
   - Review Lecture 4 (Policy Gradients) and Lecture 5 (Actor-Critic) in `research/simulation/scripts/` to connect physical grasp compliance actions to PPO policy outputs.
