# Master Roadmap: Autonomous Bimanual Soft-Body Slicing (Paper 1)
## From Zero-Experience Beginner to IEEE Conference Submission (Oct 2026 – Sep 2027)

**Target Publication:** IEEE Transactions on Robotics (T-RO) / IEEE RA-L / ICRA / IROS  
**Embodiement:** Dual AR5_L6 (7-DoF Manipulators) + LinkerHand O6 (5-Finger Dexterous Hand)  
**Research Team:**
- **Ahmed (You):** Lead Holding Arm, Proprioceptive Compliance, Real-Time Low-Level Control & Sim-to-Real Stack
- **Shahd:** Lead Slicing Arm, Fracture Mechanics (FEM / PhysX 5), Knife Feed Kinematics & Trajectory Coordination
**Laboratory:** DEX-ROB Lab, School of Electrical & Automation Engineering, Tianjin University  
**Advisor:** Prof. Shan An (安山)

---

## 1. The Hardware Engineer's Mental Model: Translating Your Bachelor's Knowledge

Coming from a hardware/embedded engineering background, you already possess intuition that pure computer science graduates lack. Robotics and Reinforcement Learning (RL) are not black magic; they are continuous control loops wrapped in numerical optimization.

| Hardware / Embedded Concept | Robotics Primitives | Reinforcement Learning Equivalents |
| :--- | :--- | :--- |
| **Microcontroller Main Loop** (`while(1)`) | Real-time 1 kHz control loop (`PREEMPT_RT`) | Environment Step (`env.step(action)`) |
| **ADC Readings & Sensor Conditioning** | Joint encoders ($\mathbf{q}, \dot{\mathbf{q}}$), Motor current ($I_{motor}$) | Observation Vector ($\mathbf{o}_t \in \mathbb{R}^{33}$) |
| **PWM & H-Bridge / Inverter Gates** | Motor torque commands ($\boldsymbol{\tau} \propto K_t \cdot I_q$) | Action Vector ($\mathbf{a}_t$) or Impedance Target |
| **RLC Analog Filter Circuit** | Spring-Mass-Damper Mechanical System | Impedance Model: $M_d \ddot{\tilde{x}} + D_d \dot{\tilde{x}} + K_d \tilde{x} = F_{ext}$ |
| **Feedback PID Loop Tuning** | Computed Torque / Task-Space Impedance Control | RL Policy Network ($\pi_\theta(\mathbf{a}_t \mid \mathbf{o}_t)$) adjusting $K_p, K_d, \mathbf{x}_{ref}$ |
| **Signal Noise & Component Tolerances** | Sensor jitter, gear backlash, link compliance | Domain Randomization ($\pm 20\%$ mass, friction, delay) |

---

## 2. The Software Toolchain Demystified

Understanding what each tool does and why we use it prevents tool fatigue:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE NVIDIA ISAAC ECOSYSTEM                                  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. NVIDIA Omniverse Kit & USD:                                                              │
│    • Universal Scene Description (.usd / .usda): Open standard 3D scene description.        │
│    • PhysX 5 Engine: Runs GPU-accelerated rigid-body dynamics, contact solver, and FEM.     │
│                                                                                             │
│ 2. NVIDIA Isaac Sim:                                                                        │
│    • The graphical simulator GUI. Renders photorealistic cameras, sensors, and lighting.    │
│    • Houses robot USD stages, meshes, and coordinate frames.                                │
│                                                                                             │
│ 3. NVIDIA Isaac Lab (formerly Orbit):                                                       │
│    • The Reinforcement Learning framework built ON TOP of Isaac Sim.                        │
│    • Runs 1,000 to 4,096 robot instances IN PARALLEL on a single RTX 5060 GPU!              │
│    • Replaces standard Gym with vectorized PyTorch tensors (zero CPU-GPU transfer bottle-   │
│      necks).                                                                                │
│                                                                                             │
│ 4. RL Libraries (SkRL / RSL-RL / Stable-Baselines3):                                         │
│    • Houses the Actor-Critic Neural Networks and PPO / SAC optimization algorithms.         │
│    • Takes batched observations from Isaac Lab, computes loss, and updates policy weights.  │
│                                                                                             │
│ 5. Real-Time Hardware Control Stack (PREEMPT_RT Linux + C++ SDK):                           │
│    • Deploys the trained policy weights onto the physical AR5_L6 robot in the laboratory.   │
│    • Communicates over CAN bus / EtherCAT at deterministic 1 kHz (1 millisecond cycle).     │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The Core Scientific Problem of Paper 1

### Why is Soft-Body Slicing a Top-Tier IEEE Paper Topic?
Cutting rigid objects (wood, metal) is well-understood. Cutting **soft, deformable, viscoplastic bodies** (like tomatoes, meat, or human tissue in robotic surgery) is an unsolved robotic challenge because:
1. **The Crushing vs. Slicing Dilemma:** Pressing downward with a knife compresses and bruises the soft flesh before it fractures. To cut cleanly, the slicing arm must saw horizontally ($v_x$) while feeding downward ($v_z$), reducing normal penetration resistance.
2. **The Holding Arm's Dual Dilemma (Your Responsibility):**
   - **Under-grasping:** The lateral sawing shear forces push the tomato out of the hand $\to$ Slip and task failure.
   - **Over-grasping:** Clamping too tightly crushes the interior pulp $\to$ Permanent bruising and damage.
3. **The Solution in Paper 1:** **Proprioceptive Adaptive Impedance Control**.  
   The holding hand uses its built-in 1 kHz joint torque sensing ($\boldsymbol{\tau}_{ext}$) to reconstruct external wrenches:
   $$\mathbf{F}_{ext} = \left(\mathbf{J}^T(\mathbf{q})\right)^\dagger \boldsymbol{\tau}_{ext}$$
   A learned neural policy adjusts finger compliance ($K_p$) in real-time: compliant enough to absorb knife vibrations, but stiff enough to resist slippage.

---

## 4. Phase-by-Phase Devil-in-the-Details Roadmap

```
2026                                                          2027
OCT     NOV     DEC     JAN     FEB     MAR     APR     MAY     JUN     JUL     AUG     SEP
├─── Phase 1 ───┤ ├─── Phase 2 ───┤ ├─ Phase 3 ─┤ ├─── Phase 4 ───┤ ├─── Phase 5 ───┤ ├── Phase 6 ──┤
 Foundations &     Decoupled RL     Bimanual Sim   Sim-to-Real &     Lab Experiments   Manuscript &
 Setup             Training         Integration    Domain Rand.      & Physical Bench  Submission
```

---

### Phase 1: Foundations, Tooling & Robot Kinematics (Months 1–2: Oct – Nov 2026)
*Target: From zero familiarity to fluent simulation and kinematic control.*

#### Week 1–2: Isaac Sim & Isaac Lab Hands-On
- [ ] **Run the Spawn Verification Script:**
  Run the newly integrated AR5_L6 verification script:
  `/home/omen/isaac-sim/python.sh /media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/scripts/test_spawn_ar5.py --robot combined`
- [ ] **Understand Isaac Lab Architecture:**
  - `InteractiveSceneCfg`: How ground, lights, and robots are assembled into a USD stage.
  - `ArticulationCfg`: How joints, stiffness ($k_p$), damping ($k_d$), and limits are configured.
  - Explore the generated USD stage in Isaac Sim GUI: inspect coordinate frames (`prim_path`) of the AR5 base, flange, and finger links.

#### Week 3–4: Coordinate Frames, Forward Kinematics & Jacobians
- [ ] **TF2 Coordinate Frames:** Learn the transformation tree from world origin $\to$ robot base $\to$ wrist link 7 $\to$ LinkerHand palm $\to$ fingertips.
- [ ] **Forward Kinematics (FK):**
  Given joint angles $\mathbf{q} \in \mathbb{R}^7$, compute end-effector Cartesian pose $\mathbf{x} = f(\mathbf{q}) \in \mathrm{SE}(3)$.
- [ ] **The Manipulator Jacobian ($\mathbf{J}(\mathbf{q}) \in \mathbb{R}^{6 \times 7}$):**
  Relates joint velocities to end-effector linear/angular velocities: $\dot{\mathbf{x}} = \mathbf{J} \dot{\mathbf{q}}$.  
  Relates Cartesian contact forces to joint torques: $\boldsymbol{\tau} = \mathbf{J}^T \mathbf{F}$.
- [ ] **Code Implementation:** Write a standalone Python utility `robot_kinematics.py` using PyTorch or Pinocchio to compute $\mathbf{J}(\mathbf{q})$ and inverse wrench mapping.

---

### Phase 2: Decoupled Holding Environment & First RL Policy (Months 3–4: Dec 2026 – Jan 2027)
*Target: Train an RL policy that stabilizes a deformable tomato against synthetic cutting disturbances.*

#### Week 5–6: Environment Building (`HoldingTomatoEnvCfg`)
- [ ] **Deformable Tomato in Sim:** Spawn a soft deformable mesh (or spring-damper proxy) resting on a cutting surface.
- [ ] **Disturbance Generator:** Since Shahd is working on the slicing arm in parallel, build a **Synthetic Cutting Disturbance Module**:
  - Injects downward pulsating normal forces: $F_z(t) = 3.0 + 1.5 \sin(2\pi f t)\text{ N}$ ($f \approx 2\text{ Hz}$).
  - Injects lateral sawing shear forces: $F_x(t) = \pm 4.0\text{ N}$ oscillating across the cutting axis.
- [ ] **Observation Pipeline ($\mathbf{o}_t \in \mathbb{R}^{33}$):**
  - Arm joint positions & velocities ($\mathbf{q}_{1..7}, \dot{\mathbf{q}}_{1..7}$): 14D
  - Hand joint positions ($\mathbf{q}_{hand, 1..11}$): 11D
  - Reconstructed fingertip contact forces ($F_x, F_y, F_z$): 3D
  - Target object displacement & velocity estimate: 5D

#### Week 7–8: Reward Function & First PPO Training Run
- [ ] **Reward Engineering (`reward_functions.py`):**
  $$R_{hold} = R_{stability} - \lambda_1 P_{slip} - \lambda_2 P_{crush} - \lambda_3 P_{torque}$$
  - $R_{stability}$: Keeps tomato center at target $(x_0, y_0, z_0)$.
  - $P_{slip} = \|\mathbf{v}_{rel}\|^2$: Penalizes relative movement between fingers and tomato skin.
  - $P_{crush} = \max(0, F_n - F_{max})^2$: Penalizes normal clamp force exceeding 5.0 N (crush threshold).
  - $P_{torque} = \|\boldsymbol{\tau}\|^2$: Penalizes wasteful joint energy.
- [ ] **Launch Vectorized Training in Isaac Lab:**
  - Launch 512 or 1,024 parallel environments on your RTX 5060 Laptop GPU.
  - Connect TensorBoard: monitor `reward/total`, `losses/value_loss`, and `metrics/crush_rate`.
  - Achieve stable convergence where the fingers dynamically clamp tighter during sawing strokes and relax during pauses.

---

### Phase 3: Bimanual Merger & Co-Simulation (Months 5–6: Feb – Mar 2027)
*Target: Combine the Holding Arm and Slicing Arm into a unified bimanual cutting cell.*

#### Week 9–10: Scene Assembly (`BimanualTomatoCuttingEnv`)
- [ ] **Dual-Robot Placement:**
  - Mount Left AR5_L6 + LinkerHand O6 at $x = -0.35\text{ m}$ (Holding).
  - Mount Right AR5_L6 + Custom Knife Flange at $x = +0.35\text{ m}$ (Slicing).
  - Center cutting board at origin $(0, 0, 0)$.
- [ ] **FEM Fracture Integration (with Shahd):**
  - Replace synthetic disturbance with Shahd's PhysX 5 FEM cutting model.
  - Slicing arm performs kinematic trajectory: approach $\to$ penetrate $\to$ sawing oscillation $\to$ severance.

#### Week 11–12: Benchmark Comparisons (The Heart of Your Paper's Results)
Every top robotics paper requires rigorous baseline comparisons. You will benchmark:
1. **Baseline 1 (Rigid Grip / Position Control):** Standard industrial gripper with fixed position setpoint. (Demonstrates catastrophic crushing of soft flesh).
2. **Baseline 2 (Pure Classical Impedance / Constant $K_p$):** Fixed spring-damper compliance without RL adaptation. (Demonstrates either slipping or excessive bruising).
3. **Proposed Method (Adaptive Proprioceptive RL Impedance):** Dynamically modulates grasp force according to 1 kHz torque feedback.

---

### Phase 4: Sim-to-Real Domain Randomization & Low-Level Driver (Months 7–8: Apr – May 2027)
*Target: Ensure the policy trained in Isaac Lab transfers to the physical robot without crashing.*

#### Week 13–14: Domain Randomization in Isaac Lab
In simulation, physics are clean. In the physical lab, motor friction varies, fruit skin varies, and communications have latency.
- [ ] Randomize tomato elasticity: $E \in [0.8, 1.8]\text{ MPa}$
- [ ] Randomize tomato skin friction: $\mu \in [0.3, 0.8]$
- [ ] Randomize knife sharpness / cutting resistance: $\pm 30\%$
- [ ] Randomize actuator damping and torque noise: Gaussian $\mathcal{N}(0, \sigma^2)$
- [ ] Randomize observation latency: 1 to 3 simulation steps delay

#### Week 15–16: Real-Time Workstation & AR5_L6 Low-Level Interface
- [ ] **Linux PREEMPT_RT Setup:** Ensure control computer runs low-latency kernel ($< 50\ \mu\text{s}$ jitter).
- [ ] **AR5_L6 Joint Torque Interface:** Connect via manufacturer C++/Python SDK.
- [ ] **Safety Watchdogs:**
  - Maximum torque limiters (e.g., cut power if $|\tau_i| > 25\text{ N}\cdot\text{m}$).
  - Workspace bounding box (robot halts if Cartesian position leaves safety bounding cube).
  - Emergency hardware stop button tested and accessible.

---

### Phase 5: Physical Lab Experiments & Benchmark Matrix (Months 9–10: Jun – Jul 2027)
*Target: Collect the experimental data, quantitative tables, and high-speed video clips for the paper.*

#### Week 17–18: Physical Experimental Setup
- [ ] Calibrate physical camera (Intel RealSense D435i) overhead using AprilTags.
- [ ] Set up tomato holding fixture and knife tool on the physical AR5 arms.
- [ ] Verify 1 kHz torque reading vs external digital scale for calibration.

#### Week 19–20: The 30-Tomato Physical Benchmark Trial
Run 30 physical cutting trials across 3 variations:
- 10x Firm Tomatoes (High elasticity, high rupture force)
- 10x Ripe/Soft Tomatoes (Low elasticity, high risk of crushing)
- 10x Irregularly Shaped / Deformed Tomatoes
Record quantitative metrics:
- **Crush Deformation ($\Delta h_{max}$ in mm):** Measured by overhead RealSense point cloud.
- **Slip Distance ($\Delta d_{slip}$ in mm):** Measured by fiducial markers on tomato skin.
- **Cut Completion Rate (%):** Clean through-cut vs stalled vs smashed.
- **Average Interaction Force ($F_{contact}$ in N):** Logged at 1 kHz from joint torques.

---

### Phase 6: Paper Writing, Figure Production & Submission (Months 11–12: Aug – Sep 2027)
*Target: Polish manuscript into camera-ready IEEE format and submit.*

#### Week 21–22: Drafting the Sections
- [ ] **Section I: Introduction:** The soft-body bimanual manipulation challenge; limitations of visual-only or rigid-grip approaches; list of 3 key contributions.
- [ ] **Section II: Related Work:** Bimanual manipulation, robotic cutting & food processing, proprioceptive impedance control.
- [ ] **Section III: System Formulation & Dynamics:** Robot kinematics, 1 kHz contact wrench reconstruction via $\mathbf{F}_{ext} = (\mathbf{J}^T)^\dagger \boldsymbol{\tau}_{ext}$, PhysX 5 FEM modeling.
- [ ] **Section IV: Learning Adaptive Proprioceptive Compliance (Your Section):** MDP formulation, 33D observation space, multi-objective reward formulation, PPO training setup in Isaac Lab.
- [ ] **Section V: Experimental Results & Ablations:**
  - Simulation vs. Real transfer curves.
  - Baseline comparison table (Rigid vs Classical Impedance vs Proposed).
  - Force trajectory tracking plots ($F_z, F_x$ during cutting).
- [ ] **Section VI: Conclusion & Future Work.**

#### Week 23–24: IEEE Figures & Supplementary Video
- [ ] **System Architecture Block Diagram:** Full-page vector graphic showing hardware $\to$ 1 kHz observer $\to$ RL policy $\to$ low-level torque commands.
- [ ] **Photo Strip of Physical Trial:** 5 keyframes showing approach, grasp, sawing, through-cut, release.
- [ ] **3-Minute IEEE Video:** Narrated overview with slow-motion footage of soft tomato slicing.
- [ ] **Final Proofreading & PDF Compilation:** Submit to IEEE conference portal (ICRA / IROS / RA-L).

---

## 5. Daily Beginner's Survival Guide & Golden Rules

1. **Rule 1: Always verify kinematics in simulation before running on hardware.**  
   Never send an unconstrained torque command to the physical robot. Test trajectory and force bounds in Isaac Sim first.
2. **Rule 2: Don't train RL blindly.**  
   If an RL policy fails to learn after 500,000 steps, do NOT just let it run overnight. 90% of failures are due to:
   - A bug in the reward function (e.g., reward hacking or one term completely dominating the gradient).
   - An unnormalized observation vector (all inputs to neural networks should be normalized to roughly $[-1.0, 1.0]$).
   - Unrealistic actuator torque limits.
3. **Rule 3: Decouple your development from your teammate.**  
   Always maintain your single-arm holding unit test with the synthetic disturbance generator. If Shahd's FEM meshing has a bug on a given week, your holding control work continues uninterrupted.
4. **Rule 4: Keep Isaac Sim and Isaac Lab asset paths clean.**  
   Always keep the robot USD models in the registered `isaaclab_assets` directory so that standard Isaac Lab scripts can import them directly without broken path references.
