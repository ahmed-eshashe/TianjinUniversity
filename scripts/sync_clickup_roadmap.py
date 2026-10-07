#!/usr/bin/env python3
"""
ClickUp Master Roadmap Synchronization Script
DEX-ROB Lab | School of Electrical & Automation Engineering, Tianjin University
Author: Ahmed (Holding Arm & Sim-to-Real Control) | Research Lead Agent

Synchronizes all 49 weeks of the calibrated IEEE ICRA 2028 master roadmap
directly to ClickUp under Space: Tianjin University -> Folder: Research -> List: Tasks.
All tasks assigned to Ahmed Sameh (ID: 176612914) with:
- Exact calendar start and due dates (Oct 7, 2026 to Sep 15, 2027)
- Priorities (Urgent, High, Normal)
- Time estimates (15-25 hours/week)
- Tags (Sprint, Domain, ICRA 2028)
- Comprehensive Markdown descriptions with file paths, CLI commands, and checklist items.
"""

import urllib.request
import urllib.error
import json
import time
from datetime import datetime, timezone, timedelta

CLICKUP_TOKEN = 'pk_176612914_8AX37HX8WU54TI6HLUK2C2YVR5A5L3JB'
LIST_ID = '901222387244'  # Space: Tianjin University -> Folder: Research -> List: Tasks
USER_ID = 176612914       # Ahmed Sameh

HEADERS = {
    'Authorization': CLICKUP_TOKEN,
    'Content-Type': 'application/json'
}

def to_millis(dt: datetime) -> int:
    return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)

def hours_to_millis(h: float) -> int:
    return int(h * 3600 * 1000)

# Base date: Wednesday, October 7, 2026
START_DATE = datetime(2026, 10, 7, 9, 0, 0)

TASKS_DEF = [
    # =========================================================================
    # SPRINT 1: Kinematic Tooling & Proprioceptive Observer (Weeks 1–6)
    # =========================================================================
    {
        "week": 1,
        "sprint": "Sprint 1",
        "name": "[Sprint 1: W1] Robot Asset Stabilization & Teleop Verification",
        "priority": 1, # Urgent
        "status": "in progress",
        "hours": 15,
        "tags": ["Sprint 1", "Simulation", "USD", "AR5-L6", "ICRA 2028"],
        "description": """### Week 1 Objective: Asset Stabilization & Verification
Start your MSc thesis research by mastering the ARX AR5-L6 and LinkerHand O6 USD assets.

#### Action Checklist:
- [ ] Inspect converted OpenUSD stage in `research/simulation/assets/robots/ar5_l6/usd_clean/ar5_o6_left_combined/ar5_o6_left_combined.usda`.
- [ ] Understand why rotor armature conditioning (`armature=0.05` arm, `0.005` hand) solves the 6,000:1 mass ratio ill-conditioning.
- [ ] Run the active teleoperation script and test keyboard controls:
  ```bash
  /home/omen/isaac-sim/python.sh /media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/scripts/control_ar5_teleop.py
  ```
- [ ] Verify stance approach, finger opening, and compliant grasp closure without numerical explosions.

#### Deliverable:
Confirmed stable robot physics in NVIDIA Isaac Sim without NaNs.
"""
    },
    {
        "week": 2,
        "sprint": "Sprint 1",
        "name": "[Sprint 1: W2] Standalone Forward Kinematics & Manipulator Jacobian",
        "priority": 2, # High
        "status": "Open",
        "hours": 18,
        "tags": ["Sprint 1", "Kinematics", "Jacobian", "PyTorch", "ICRA 2028"],
        "description": """### Week 2 Objective: Analytical Kinematics & Manipulator Jacobian
Implement and master the kinematics engine that translates joint angles into end-effector Cartesian motions.

#### Action Checklist:
- [ ] Review `research/simulation/src/kinematics/ar5_kinematics.py`.
- [ ] Study the 7-DoF joint origins and rotation axes (revolute Z, Y, Z, Y, Z, Y, X).
- [ ] Verify analytical Jacobian J(q) in R^{6x7} against PyTorch autograd:
  ```bash
  /home/omen/miniforge3/envs/tianjin-robotics/bin/python research/simulation/src/kinematics/ar5_kinematics.py
  ```
- [ ] Confirm error between analytical Jacobian and autograd is < 1e-5.
- [ ] Implement damped least-squares pseudo-inverse J^\dagger = J^T (J J^T + lambda^2 I)^{-1}.

#### Deliverable:
Validated kinematics engine ready for high-rate contact force estimation.
"""
    },
    {
        "week": 3,
        "sprint": "Sprint 1",
        "name": "[Sprint 1: W3] 1 kHz Proprioceptive Contact Wrench Observer",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 1", "Control", "Wrench-Observer", "Proprioception", "ICRA 2028"],
        "description": """### Week 3 Objective: 1 kHz Contact Wrench Observer
Build the core sensing innovation confirmed with Prof. Shan An: estimating contact forces directly from joint torques without custom sensors.

#### Action Checklist:
- [ ] Review `research/simulation/src/control/wrench_estimator.py`.
- [ ] Implement equation: F_ext = (J^T(q))^\dagger * tau_ext.
- [ ] Tune 1st-order bilinear Butterworth low-pass filter (fc = 50 Hz at 1 kHz sample rate) to reject motor current ripple.
- [ ] Test regime classification:
  - UNDER_GRASP_SLIP (< 1.5 N)
  - NOMINAL_SAFE_HOLD (1.5 N to 5.0 N)
  - CRUSH_BARRIER_VIOLATION (> 5.0 N)
  - EMERGENCY_OVERLOAD (> 15.0 N)
- [ ] Execute self-test script:
  ```bash
  /home/omen/miniforge3/envs/tianjin-robotics/bin/python research/simulation/src/control/wrench_estimator.py
  ```

#### Deliverable:
Reconstructs external forces with < 1e-3 N error and attenuates 200 Hz noise by > 75%.
"""
    },
    {
        "week": 4,
        "sprint": "Sprint 1",
        "name": "[Sprint 1: W4] LinkerHand O6 Actuator Mapping & Tendon Coupling",
        "priority": 2, # High
        "status": "Open",
        "hours": 16,
        "tags": ["Sprint 1", "LinkerHand", "Dexterous-Hand", "IsaacLab", "ICRA 2028"],
        "description": """### Week 4 Objective: LinkerHand O6 Actuator Mapping
Configure the 6 active motors and 5 passive tendon-coupled DIP joints in Isaac Lab.

#### Action Checklist:
- [ ] Map 6 active joints: thumb_yaw, thumb_pitch, index_mcp, middle_mcp, ring_mcp, pinky_mcp.
- [ ] Enforce mechanical tendon pulley ratio for 5 DIP joints: theta_dip = 1.126 * theta_mcp.
- [ ] Ensure mimic joints do NOT have independent active PD controllers to prevent infinite torque fighting.
- [ ] Set actuator gains: stiffness = 30.0, damping = 3.0, armature = 0.005.

#### Deliverable:
Smooth, natural five-finger compliant closure in simulation.
"""
    },
    {
        "week": 5,
        "sprint": "Sprint 1",
        "name": "[Sprint 1: W5] Aperdata Kitchen Scene Composition & Cutting Props",
        "priority": 3, # Normal
        "status": "Open",
        "hours": 15,
        "tags": ["Sprint 1", "Aperdata", "USD", "Scene-Setup", "ICRA 2028"],
        "description": """### Week 5 Objective: Aperdata Scene Assembly
Compose the kitchen tabletop simulation using verified Aperdata SimReady assets.

#### Action Checklist:
- [ ] Import `/home/omen/isaac-sim-assests/0_Kitchen_Indoor/Indoor.usd`.
- [ ] Place cutting board and plate at origin (0, 0, 0.75).
- [ ] Place Left AR5-L6 holding arm at x = -0.35 m, facing origin.
- [ ] Test camera perspectives and lighting for publication figures.

#### Deliverable:
Clean OpenUSD kitchen workstation stage ready for tomato spawning.
"""
    },
    {
        "week": 6,
        "sprint": "Sprint 1",
        "name": "[Sprint 1: W6] Sprint 1 Review & End-to-End Integration Test",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 1", "Milestone", "Integration-Test", "ICRA 2028"],
        "description": """### Week 6 Objective: Sprint 1 Milestone Review (M2)
Validate the complete single-arm holding pipeline before starting RL training.

#### Action Checklist:
- [ ] Run end-to-end holding test: arm approaches tomato, forms compliant grasp, and logs estimated wrench.
- [ ] Verify zero NaN values, zero joint limit violations, and stable contact physics.
- [ ] Generate output artifact: `experiments/results/sprint1_kinematic_validation.json`.
- [ ] Update `research_state/project_status.yaml` progress to 100% for Milestone M2.

#### Deliverable:
Fully validated single-arm kinematic and wrench observer testbed.
"""
    },

    # =========================================================================
    # SPRINT 2: Decoupled Single-Arm Holding RL (Weeks 7–14)
    # =========================================================================
    {
        "week": 7,
        "sprint": "Sprint 2",
        "name": "[Sprint 2: W7] Gym Environment Scaffolding (HoldingTomatoEnvCfg)",
        "priority": 2, # High
        "status": "Open",
        "hours": 18,
        "tags": ["Sprint 2", "IsaacLab", "Gym-Env", "Observation-Space", "ICRA 2028"],
        "description": """### Week 7 Objective: Isaac Lab Gym Environment Construction
Implement `HoldingTomatoEnvCfg` inheriting from Isaac Lab's `ManagerBasedRLEnv`.

#### Action Checklist:
- [ ] Create `research/simulation/src/envs/holding_tomato_env.py`.
- [ ] Assemble 33D observation vector:
  - Arm joint pos & vel (14D)
  - Hand joint pos (11D)
  - Reconstructed contact forces (3D)
  - Tomato displacement & velocity (5D)
- [ ] Verify tensor shapes and GPU batch vectorization on RTX 5060.
"""
    },
    {
        "week": 8,
        "sprint": "Sprint 2",
        "name": "[Sprint 2: W8] Synthetic Slicing Disturbance Generator",
        "priority": 2, # High
        "status": "Open",
        "hours": 16,
        "tags": ["Sprint 2", "Disturbance", "Decoupling", "Simulation", "ICRA 2028"],
        "description": """### Week 8 Objective: Synthetic Sawing Disturbance Module
Decouple holding arm development from Shahd's cutting arm via synthetic contact forces.

#### Action Checklist:
- [ ] Build disturbance module injecting downward pulsating force: Fz = 3.5 + 1.5*sin(4*pi*t) N.
- [ ] Inject lateral sawing shear force: Fx = +/- 4.0 N at 2 Hz.
- [ ] Confirm open-loop or loose grasps drop or roll the tomato within 2 seconds.
"""
    },
    {
        "week": 9,
        "sprint": "Sprint 2",
        "name": "[Sprint 2: W9] Multi-Objective Barrier Reward Formulation",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 2", "Reward-Design", "Barrier-Function", "RL", "ICRA 2028"],
        "description": """### Week 9 Objective: Holding Reward Engineering
Implement the anti-crushing barrier reward: R_hold = R_stability - lambda1*P_slip - lambda2*P_crush - lambda3*P_torque.

#### Action Checklist:
- [ ] Implement P_crush = max(0, Fn - 5.0 N)^2 (quadratic penalty above 5 N threshold).
- [ ] Implement P_slip = ||v_rel||^2 (relative finger-skin velocity).
- [ ] Test reward normalization across 1,000 random rollouts.
"""
    },
    {
        "week": 10,
        "sprint": "Sprint 2",
        "name": "[Sprint 2: W10] First SkRL Vectorized PPO Training Run (512 Envs)",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 2", "SkRL", "PPO", "Training", "WandB", "ICRA 2028"],
        "description": """### Week 10 Objective: First GPU Vectorized Training
Launch headless training in Isaac Lab with SkRL 2.1.0 on RTX 5060 Laptop GPU.

#### Action Checklist:
- [ ] Run:
  ```bash
  /home/omen/isaac-sim/python.sh experiments/scripts/train_holding_ppo.py --num_envs 512 --headless
  ```
- [ ] Connect WandB / TensorBoard: log `reward/total`, `metrics/crush_rate`, `metrics/slip_dist`.
- [ ] Monitor VRAM usage (target: < 6.5 GB out of 8 GB).
"""
    },
    {
        "week": 11,
        "sprint": "Sprint 2",
        "name": "[Sprint 2: W11] Reward Debugging & Eureka Automated Tuning",
        "priority": 2, # High
        "status": "Open",
        "hours": 16,
        "tags": ["Sprint 2", "Eureka", "LLM-Tuning", "Reward", "ICRA 2028"],
        "description": """### Week 11 Objective: Automated Reward Reflection (Eureka Paradigm)
Use LLM prompts to analyze training curves and optimize reward coefficients.

#### Action Checklist:
- [ ] Detect failure modes: frozen grip (refusal to squeeze) vs death clamp (instant crushing).
- [ ] Refine penalty scales lambda1, lambda2 until grasp stabilizes without bruising.
"""
    },
    {
        "week": 12,
        "sprint": "Sprint 2",
        "name": "[Sprint 2: W12] Disturbance Frequency Sweep & Exam Buffer",
        "priority": 3, # Normal
        "status": "Open",
        "hours": 15,
        "tags": ["Sprint 2", "Robustness", "Evaluation", "ICRA 2028"],
        "description": """### Week 12 Objective: Frequency Robustness Evaluation
Test holding policy robustness across sawing frequencies f in [1.0, 5.0] Hz.

#### Action Checklist:
- [ ] Log slip distance Delta_d_slip and peak contact force Fn_max.
- [ ] Allocate buffer time for Fall semester university exams.
"""
    },
    {
        "week": 13,
        "sprint": "Sprint 2",
        "name": "[Sprint 2: W13] Shahd's Slicing Arm Sync & Coordinate Alignment",
        "priority": 2, # High
        "status": "Open",
        "hours": 16,
        "tags": ["Sprint 2", "Team-Sync", "FEM", "Bimanual", "ICRA 2028"],
        "description": """### Week 13 Objective: Slicing Subsystem Synchronization
Collaborate with Shahd to align the slicing arm and holding arm coordinate systems.

#### Action Checklist:
- [ ] Review Shahd's Gmsh tetrahedral tomato mesh (`tomato.msh`).
- [ ] Inspect PhysX 5 FEM fracture toughness and Young's modulus settings.
- [ ] Verify coordinate agreement: Left arm palm facing +x, Right arm knife feeding from +z.
"""
    },
    {
        "week": 14,
        "sprint": "Sprint 2",
        "name": "[Sprint 2: W14] Single-Arm Holding Checkpoint Lock (Milestone M3)",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 2", "Milestone", "Model-Checkpoint", "H1", "ICRA 2028"],
        "description": """### Week 14 Objective: Lock Holding Policy Checkpoint
Lock `experiments/runs/holding_policy_v1.pt`.

#### Action Checklist:
- [ ] Validate against Hypothesis H1: normal force suppressed < 5.0 N in >= 95% of disturbance rollouts.
- [ ] Update `research_state/project_status.yaml` for Milestone M3.
"""
    },

    # =========================================================================
    # SPRINT 3: Winter Break GPU Simulation Sprint (Weeks 15–18)
    # =========================================================================
    {
        "week": 15,
        "sprint": "Sprint 3",
        "name": "[Sprint 3: W15] Headless Multi-Seed PPO Hyperparameter Sweep",
        "priority": 2, # High
        "status": "Open",
        "hours": 18,
        "tags": ["Sprint 3", "Winter-Break", "PPO", "Hyperparameters", "ICRA 2028"],
        "description": """### Week 15 Objective: Multi-Seed PPO Training
Run multi-seed sweeps (seeds: 42, 100, 2026, 777, 999) headless on laptop GPU during winter break.

#### Action Checklist:
- [ ] Sweep learning rates: 1e-4, 3e-4, 5e-4.
- [ ] Sweep GAE-lambda: 0.90, 0.95, 0.98.
- [ ] Log convergence variance across seeds.
"""
    },
    {
        "week": 16,
        "sprint": "Sprint 3",
        "name": "[Sprint 3: W16] Residual Action Space Implementation (ADR-004)",
        "priority": 2, # High
        "status": "Open",
        "hours": 18,
        "tags": ["Sprint 3", "Residual-RL", "Sawing-Primitive", "ADR-004", "ICRA 2028"],
        "description": """### Week 16 Objective: Residual Policy over Kinematic Primitive
Implement ADR-004 residual action space for the cutting arm: a_t in R^6.

#### Action Checklist:
- [ ] Superimpose residual policy on nominal sinusoidal sawing motion:
  vx,nom(t) = A*omega*cos(omega*t), vz,nom = -v_feed.
- [ ] Verify that residual exploration stays within safe contact manifolds.
"""
    },
    {
        "week": 17,
        "sprint": "Sprint 3",
        "name": "[Sprint 3: W17] Literature Deep Dive & Section II Drafting (CNY)",
        "priority": 3, # Normal
        "status": "Open",
        "hours": 15,
        "tags": ["Sprint 3", "Literature", "LaTeX", "Paper-Drafting", "ICRA 2028"],
        "description": """### Week 17 Objective: Related Work Authorship (Chinese New Year)
Index latest 2026/2027 literature and draft Section II.

#### Action Checklist:
- [ ] Update `literature/papers/` and verified BibTeX in `paper/references.bib`.
- [ ] Draft `paper/sections/02_related_work.tex` in IEEEtran format.
"""
    },
    {
        "week": 18,
        "sprint": "Sprint 3",
        "name": "[Sprint 3: W18] Automated Domain Randomization (DrEureka Bounds)",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 3", "DrEureka", "Domain-Randomization", "PhysX5", "ICRA 2028"],
        "description": """### Week 18 Objective: PhysX 5 FEM Domain Randomization
Formulate physics parameter distributions for zero-shot sim-to-real transfer.

#### Action Checklist:
- [ ] Randomize tomato Young's modulus E in [30, 120] kPa.
- [ ] Randomize friction mu in [0.25, 0.75].
- [ ] Randomize fracture threshold sigma_c +/- 30%.
- [ ] Complete Milestone M4 in `project_status.yaml`.
"""
    },

    # =========================================================================
    # SPRINT 4: Bimanual Simulation & Baselines (Weeks 19–26)
    # =========================================================================
    {
        "week": 19,
        "sprint": "Sprint 4",
        "name": "[Sprint 4: W19] Bimanual Scene Assembly (BimanualTomatoCuttingEnv)",
        "priority": 2, # High
        "status": "Open",
        "hours": 18,
        "tags": ["Sprint 4", "Bimanual", "IsaacLab", "Scene-Composition", "ICRA 2028"],
        "description": """### Week 19 Objective: Assemble Dual-Arm Cell in Isaac Lab
Mount both AR5-L6 arms (Left at x=-0.35m, Right at x=+0.35m) with cutting board and FEM tomato.
"""
    },
    {
        "week": 20,
        "sprint": "Sprint 4",
        "name": "[Sprint 4: W20] Slicing & Holding Co-Simulation Verification",
        "priority": 2, # High
        "status": "Open",
        "hours": 18,
        "tags": ["Sprint 4", "Co-Simulation", "Physics-Stability", "ICRA 2028"],
        "description": """### Week 20 Objective: Closed-Loop Slicing Dynamics
Verify closed-loop interaction: Left arm holds tomato while Right arm executes sawing cut at 120 Hz solver substepping.
"""
    },
    {
        "week": 21,
        "sprint": "Sprint 4",
        "name": "[Sprint 4: W21] Baseline Execution: Pure Kinematic (EXP-001) & Fixed Impedance (EXP-002)",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 4", "Baselines", "EXP-001", "EXP-002", "H1", "ICRA 2028"],
        "description": """### Week 21 Objective: Run Mandatory Baselines 1 & 2
Run EXP-001 (Pure Kinematic Sawing) and EXP-002 (Fixed Impedance Control) across 5 seeds. Log crush and stall rates.
"""
    },
    {
        "week": 22,
        "sprint": "Sprint 4",
        "name": "[Sprint 4: W22] Proposed Method Execution: Tactile Residual RL (EXP-003)",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 22,
        "tags": ["Sprint 4", "Proposed-Method", "EXP-003", "H1", "ICRA 2028"],
        "description": """### Week 22 Objective: Run Proposed Method (EXP-003)
Execute EXP-003 across 5 seeds. Verify slice completion rate >= 90% and crush reduction >= 40% against EXP-001.
"""
    },
    {
        "week": 23,
        "sprint": "Sprint 4",
        "name": "[Sprint 4: W23] Ablation Suite Execution: EXP-004, EXP-005, EXP-006",
        "priority": 2, # High
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 4", "Ablations", "EXP-004", "EXP-005", "EXP-006", "H2", "ICRA 2028"],
        "description": """### Week 23 Objective: Run Architectural Ablations
Run EXP-004 (E2E Joint RL), EXP-005 (E2E Cartesian RL), and EXP-006 (Residual over Primitive). Prove 5x sample speedup.
"""
    },
    {
        "week": 24,
        "sprint": "Sprint 4",
        "name": "[Sprint 4: W24] Statistical Hypothesis Testing (H1 & H2 Validation)",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 18,
        "tags": ["Sprint 4", "Statistics", "Mann-Whitney", "Paper-Claims", "ICRA 2028"],
        "description": """### Week 24 Objective: Statistical Significance Tests
Run Mann-Whitney U test and Welch's t-test via `analysis/statistical_tests.py`. Verify CLAIM-01, CLAIM-02, CLAIM-03.
"""
    },
    {
        "week": 25,
        "sprint": "Sprint 4",
        "name": "[Sprint 4: W25] ★ INTERNAL MID-TERM CHECKPOINT (Simulation Manuscript Locked)",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 25,
        "tags": ["Sprint 4", "Milestone-M5", "Internal-Checkpoint", "ICRA 2028"],
        "description": """### Week 25 Objective: Internal Mid-Term Laboratory Review (Milestone M5)
Lock simulation manuscript draft with full baseline comparison tables and convergence plots for Prof. Shan An's review.
"""
    },
    {
        "week": 26,
        "sprint": "Sprint 4",
        "name": "[Sprint 4: W26] Mid-Term Architecture Debrief & Consumables Procurement",
        "priority": 3, # Normal
        "status": "Open",
        "hours": 15,
        "tags": ["Sprint 4", "Review", "Hardware-Prep", "ICRA 2028"],
        "description": """### Week 26 Objective: Transition to Physical Lab Phase
Debrief with Prof. Shan An. Procure physical testbed fixtures, calibration gauges, and test tomatoes.
"""
    },

    # =========================================================================
    # SPRINT 5: Real Hardware Testbed & Low-Level Drivers (Weeks 27–34)
    # =========================================================================
    {
        "week": 27,
        "sprint": "Sprint 5",
        "name": "[Sprint 5: W27] Control Workstation & PREEMPT_RT Linux Kernel Setup",
        "priority": 2, # High
        "status": "Open",
        "hours": 18,
        "tags": ["Sprint 5", "Hardware", "Linux-RT", "PREEMPT_RT", "ICRA 2028"],
        "description": """### Week 27 Objective: Real-Time Kernel Setup
Install Ubuntu 22.04 LTS + PREEMPT_RT patch. Run `cyclictest` and confirm latency jitter < 50 us over 1 hour.
"""
    },
    {
        "week": 28,
        "sprint": "Sprint 5",
        "name": "[Sprint 5: W28] Dual CAN Bus Interface (can0, can1) 1 kHz RT Loop",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 5", "Hardware", "CAN-Bus", "1kHz-Loop", "ICRA 2028"],
        "description": """### Week 28 Objective: 1 kHz Deterministic CAN Communication
Configure dual SocketCAN interfaces at 1 Mbps. Verify zero packet drops with AR5-L6 motor drivers.
"""
    },
    {
        "week": 29,
        "sprint": "Sprint 5",
        "name": "[Sprint 5: W29] Gravity & Friction Dynamics Model Calibration",
        "priority": 2, # High
        "status": "Open",
        "hours": 16,
        "tags": ["Sprint 5", "Hardware", "Calibration", "Dynamics", "ICRA 2028"],
        "description": """### Week 29 Objective: Physical Arm Dynamic Parameter Tuning
Calibrate link masses, centers of mass, and friction compensation. Verify smooth zero-gravity lead-through mode.
"""
    },
    {
        "week": 30,
        "sprint": "Sprint 5",
        "name": "[Sprint 5: W30] 1 kHz External Wrench Calibration on Physical Arm",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 5", "Hardware", "Wrench-Calibration", "Force-Gauge", "ICRA 2028"],
        "description": """### Week 30 Objective: Physical Force Calibration
Apply known forces (1N, 2N, 5N) using digital force gauge. Confirm torque-to-force observer error < 0.3 N.
"""
    },
    {
        "week": 31,
        "sprint": "Sprint 5",
        "name": "[Sprint 5: W31] LinkerHand O6 Physical Driver & Tendon Calibration",
        "priority": 2, # High
        "status": "Open",
        "hours": 18,
        "tags": ["Sprint 5", "Hardware", "LinkerHand", "Physical-Grasp", "ICRA 2028"],
        "description": """### Week 31 Objective: LinkerHand O6 Hardware Commissioning
Connect 6 active motors via USB/CAN. Test compliant grasping on soft fruit proxies without overheating.
"""
    },
    {
        "week": 32,
        "sprint": "Sprint 5",
        "name": "[Sprint 5: W32] Hardware Safety Watchdog System (Torque, Cube, E-stop)",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 5", "Safety", "Watchdog", "E-Stop", "ICRA 2028"],
        "description": """### Week 32 Objective: Multi-Tiered Safety Interlocks
Implement over-torque cutoff (|tau_i| > 25 Nm), 30x30x30 cm Cartesian bounding cube, and physical E-stop switch.
"""
    },
    {
        "week": 33,
        "sprint": "Sprint 5",
        "name": "[Sprint 5: W33] MoveIt 2 Cartesian Sawing Trajectory Integration",
        "priority": 2, # High
        "status": "Open",
        "hours": 18,
        "tags": ["Sprint 5", "ROS2", "MoveIt2", "Trajectory", "ICRA 2028"],
        "description": """### Week 33 Objective: MoveIt 2 Cartesian Sawing Node
Configure MoveIt 2 servo node for Right AR5 arm. Test smooth sinusoidal sawing motion in free air.
"""
    },
    {
        "week": 34,
        "sprint": "Sprint 5",
        "name": "[Sprint 5: W34] Bimanual Physical Teleoperation & Dry-Run Slicing (Milestone M6)",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 22,
        "tags": ["Sprint 5", "Milestone-M6", "Dry-Run", "Bimanual", "ICRA 2028"],
        "description": """### Week 34 Objective: Coordinated Physical Dry Runs (Milestone M6)
Execute coordinated dry runs with 3D-printed dummy tomato. Confirm zero tool-hand collisions. Lock Milestone M6.
"""
    },

    # =========================================================================
    # SPRINT 6: Sim-to-Real Transfer & Physical Cutting Trials (Weeks 35–43)
    # =========================================================================
    {
        "week": 35,
        "sprint": "Sprint 6",
        "name": "[Sprint 6: W35] Policy Export to ONNX / TensorRT & Real-Time C++ Node",
        "priority": 2, # High
        "status": "Open",
        "hours": 18,
        "tags": ["Sprint 6", "ONNX", "TensorRT", "Inference", "ICRA 2028"],
        "description": """### Week 35 Objective: Policy Deployment Runtime
Export trained PyTorch policy to ONNX format. Build real-time C++ inference node evaluating at 100 Hz inside 1 kHz loop.
"""
    },
    {
        "week": 36,
        "sprint": "Sprint 6",
        "name": "[Sprint 6: W36] Overhead RealSense D435i Camera Extrinsics & AprilTag Calibration",
        "priority": 2, # High
        "status": "Open",
        "hours": 16,
        "tags": ["Sprint 6", "RealSense", "Vision", "Extrinsics", "ICRA 2028"],
        "description": """### Week 36 Objective: Overhead Vision & Deformation Measurement
Calibrate RealSense D435i camera extrinsics via AprilTag. Configure real-time tomato height deformation tracking Delta_h(t).
"""
    },
    {
        "week": 37,
        "sprint": "Sprint 6",
        "name": "[Sprint 6: W37] Physical Cutting Trials: 10x Firm Tomatoes",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 6", "Physical-Trials", "Firm-Tomatoes", "ICRA 2028"],
        "description": """### Week 37 Objective: Physical Benchmark Batch 1 (Firm)
Conduct 10 physical cutting trials on Firm/Unripe tomatoes. Record skin puncture forces and sawing feed rates.
"""
    },
    {
        "week": 38,
        "sprint": "Sprint 6",
        "name": "[Sprint 6: W38] Physical Cutting Trials: 10x Ripe Tomatoes (Adaptive vs Rigid)",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 6", "Physical-Trials", "Ripe-Tomatoes", "Baselines", "ICRA 2028"],
        "description": """### Week 38 Objective: Physical Benchmark Batch 2 (Ripe)
Conduct 10 physical cutting trials on Standard Ripe tomatoes. Compare proposed adaptive compliance vs fixed rigid grip.
"""
    },
    {
        "week": 39,
        "sprint": "Sprint 6",
        "name": "[Sprint 6: W39] Physical Cutting Trials: 10x Soft Tomatoes (Anti-Crush Verification)",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 6", "Physical-Trials", "Soft-Tomatoes", "Anti-Crush", "ICRA 2028"],
        "description": """### Week 39 Objective: Physical Benchmark Batch 3 (Soft/Overripe)
Conduct 10 physical cutting trials on Soft/Overripe tomatoes. Prove zero pulp bursting and crush deformation < 15%.
"""
    },
    {
        "week": 40,
        "sprint": "Sprint 6",
        "name": "[Sprint 6: W40] Sim-to-Real Domain Randomization Benchmark (EXP-007 vs EXP-008)",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 22,
        "tags": ["Sprint 6", "Sim-to-Real", "EXP-007", "EXP-008", "H3", "ICRA 2028"],
        "description": """### Week 40 Objective: Domain Randomization Validation
Benchmark policy trained without DR (EXP-007) vs policy with PhysX 5 FEM DR (EXP-008). Validate CLAIM-04 (>= 80% success).
"""
    },
    {
        "week": 41,
        "sprint": "Sprint 6",
        "name": "[Sprint 6: W41] Slice Uniformity, Leakage Weight & Cross-Section Macro Photography",
        "priority": 2, # High
        "status": "Open",
        "hours": 18,
        "tags": ["Sprint 6", "Metrics", "Photography", "Uniformity", "ICRA 2028"],
        "description": """### Week 41 Objective: Quantitative Metrics Collection
Measure slice thickness variation (+/- 1.5 mm), juice leakage weight, and photograph cross-sections for paper figures.
"""
    },
    {
        "week": 42,
        "sprint": "Sprint 6",
        "name": "[Sprint 6: W42] 120 FPS High-Speed Video Capture & Failure Mode Taxonomy",
        "priority": 2, # High
        "status": "Open",
        "hours": 18,
        "tags": ["Sprint 6", "High-Speed-Video", "Failure-Modes", "ICRA 2028"],
        "description": """### Week 42 Objective: High-Speed Footage & Failure Analysis
Record 120 FPS slow-motion clips of skin puncture. Document failure modes across baselines for honest discussion section.
"""
    },
    {
        "week": 43,
        "sprint": "Sprint 6",
        "name": "[Sprint 6: W43] Physical Data Archival & `research_cli.py verify-claims` (Milestone M7)",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 6", "Milestone-M7", "Data-Archival", "Claim-Verify", "ICRA 2028"],
        "description": """### Week 43 Objective: Lock Physical Experimental Results (Milestone M7)
Archive all 1 kHz CSV telemetry to `experiments/results/physical_trials/`. Run `python scripts/research_cli.py verify-claims`. Lock Milestone M7.
"""
    },

    # =========================================================================
    # SPRINT 7: IEEE Manuscript Authorship & ICRA Submission (Weeks 44–49)
    # =========================================================================
    {
        "week": 44,
        "sprint": "Sprint 7",
        "name": "[Sprint 7: W44] Publication Vector Figures (Fig 1 Architecture, Fig 2 Force Curves, Fig 3 Training Curves)",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 7", "Paper", "Figures", "Vector-Graphics", "ICRA 2028"],
        "description": """### Week 44 Objective: Publication-Quality Figures
Generate Fig 1 (System Architecture), Fig 2 (4-phase force curves), Fig 3 (convergence curves with shaded error), Fig 4 (photo strip).
"""
    },
    {
        "week": 45,
        "sprint": "Sprint 7",
        "name": "[Sprint 7: W45] Draft Section III (System Formulation), IV (Residual RL), V (Experimental Setup)",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 22,
        "tags": ["Sprint 7", "Paper", "LaTeX", "Methods", "ICRA 2028"],
        "description": """### Week 45 Objective: Draft Core Methodology Sections
Write Section III (Problem Formulation & 1 kHz Wrench Observer), Section IV (Residual RL Policy), Section V (Experimental Setup).
"""
    },
    {
        "week": 46,
        "sprint": "Sprint 7",
        "name": "[Sprint 7: W46] Draft Section VI (Results & Ablation Tables I & II), I (Introduction), VII (Conclusion)",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 24,
        "tags": ["Sprint 7", "Paper", "LaTeX", "Results", "ICRA 2028"],
        "description": """### Week 46 Objective: Draft Results, Tables & Framing
Write Section VI (Results & Ablation Tables I and II), Section I (Introduction & Contributions), Section VII (Conclusion).
"""
    },
    {
        "week": 47,
        "sprint": "Sprint 7",
        "name": "[Sprint 7: W47] 3-Minute Narrated Supplementary Video Production",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 7", "Video", "Supplementary", "Voiceover", "ICRA 2028"],
        "description": """### Week 47 Objective: 3-Minute Supplementary Video
Script, record, and voice-over 3-minute video: problem statement, sim training, physical experiments, slow-motion cuts.
"""
    },
    {
        "week": 48,
        "sprint": "Sprint 7",
        "name": "[Sprint 7: W48] Formal Paper Review & IEEEtran Compliance Polish with Prof. Shan An",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 25,
        "tags": ["Sprint 7", "Advisor-Review", "Proofreading", "IEEEtran", "ICRA 2028"],
        "description": """### Week 48 Objective: Supervisor Sign-off
Conduct rigorous review session with Prof. Shan An. Verify mathematical notation, IEEEtran margins, and claims evidence.
"""
    },
    {
        "week": 49,
        "sprint": "Sprint 7",
        "name": "[Sprint 7: W49] ★ FIRST PUBLICATION DEADLINE: Submit to IEEE ICRA 2028 Portal",
        "priority": 1, # Urgent
        "status": "Open",
        "hours": 20,
        "tags": ["Sprint 7", "Submission", "ICRA 2028", "Milestone-M8"],
        "description": """### Week 49 Objective: Official Paper Submission (September 15, 2027)
Upload PDF manuscript, supplementary video, and metadata before the mid-September deadline to IEEE ICRA 2028. Celebrate!
"""
    }
]

def create_task(task_def: dict, index: int) -> dict:
    week_num = task_def["week"]
    # Calculate start and due dates
    start_dt = START_DATE + timedelta(weeks=week_num - 1)
    due_dt = start_dt + timedelta(days=6, hours=14) # Due Tuesday evening of that week

    payload = {
        "name": task_def["name"],
        "description": task_def["description"],
        "assignees": [USER_ID],
        "tags": task_def.get("tags", []),
        "status": task_def.get("status", "Open"),
        "priority": task_def["priority"],
        "start_date": to_millis(start_dt),
        "due_date": to_millis(due_dt),
        "time_estimate": hours_to_millis(task_def["hours"])
    }

    req = urllib.request.Request(
        f'https://api.clickup.com/api/v2/list/{LIST_ID}/task',
        data=json.dumps(payload).encode('utf-8'),
        headers=HEADERS,
        method='POST'
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8')
        print(f"Error creating task W{week_num}: {e.code} - {err_msg}")
        raise e

def main():
    print(f"Starting ClickUp synchronization for {len(TASKS_DEF)} tasks...")
    print(f"Target: Space 'Tianjin University' -> Folder 'Research' -> List 'Tasks' (ID: {LIST_ID})")
    print(f"Assignee: Ahmed Sameh (ID: {USER_ID})")
    print("=" * 60)

    success_count = 0
    for i, t in enumerate(TASKS_DEF):
        try:
            res = create_task(t, i)
            task_id = res.get("id")
            task_name = res.get("name")
            print(f"[{i+1}/{len(TASKS_DEF)}] Created: {task_name} (ID: {task_id})")
            success_count += 1
            # Respect rate limit (ClickUp allows 100 req/min)
            time.sleep(0.6)
        except Exception as e:
            print(f"Failed at task {t['name']}: {e}")
            break

    print("=" * 60)
    print(f"Synchronization complete! {success_count}/{len(TASKS_DEF)} tasks created successfully.")

if __name__ == "__main__":
    main()
