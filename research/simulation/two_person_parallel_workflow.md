# Two-Person Parallel Workflow: Subsystem Division (Paper 1 — Option A)

**Project:** Autonomous Bimanual Soft-Body Slicing (DOM — Dual Robot Arms)  
**Target Publication:** IEEE RA-L / IROS  
**Authors / Research Team:** Ahmed & Shahd (DEX-ROB Lab, Tianjin University)  
**Strategy:** Option A (Horizontal Subsystem Split: Active Slicing Arm vs. Compliant Holding Arm)  

---

## 1. Executive Summary & The Parallelism Principle

A major question when planning a robotics RL paper between two researchers is:  
> *"Don't we have to wait for the simulation to be finished before we can start training?"*

**The Answer: NO.** In professional robotics labs, researchers **never wait for the full simulation**. 

Waiting 3 to 4 weeks for a final photorealistic, FEM-tearing tomato scene before writing a single line of RL code is a classic trap: it wastes nearly a month, and when the simulation is finally handed over, you encounter dozens of simultaneous bugs across physics, controllers, tensor shapes, and reward scales without knowing which subsystem caused the failure.

Instead, this workflow uses **Subsystem Decoupling and Single-Arm Mocking**:
1. **The task is split into two independent mechanical halves:**
   - **Subsystem 1 (Person A):** The Active Slicing Arm & Fracture Mechanics.
   - **Subsystem 2 (Person B):** The Compliant Holding Arm, Perception & Macro Coordination.
2. **Each arm is developed and unit-tested in isolation during Weeks 1–4:**
   - Person A trains a cutting knife to slice a tomato clamped rigidly to a board (no holding arm needed).
   - Person B trains a gripper arm to stabilize a tomato subjected to simulated cutting disturbance forces (no cutting arm needed).
3. **The two subsystems merge in Week 5:** Because observation and action interfaces are standardized on Day 1, merging the two arms into a unified bimanual environment takes hours, not weeks.

```
                        OPTION A: BIMANUAL SUBSYSTEM DECOUPLING
┌──────────────────────────────────────────────────┐  ┌──────────────────────────────────────────────────┐
│       SHAHD: SLICING ARM & FRACTURE LEAD         │  │    AHMED: HOLDING ARM & PROPRIOCEPTIVE LEAD      │
├──────────────────────────────────────────────────┤  ├──────────────────────────────────────────────────┤
│ • Knife End-Effector & URDF attachment           │  │ • Stabilizing Gripper / Fingertip End-Effector   │
│ • Volumetric TetMesh & PhysX FEM tearing         │  │ • 1 kHz torque force reconstruction (F_ext)      │
│ • 4-Phase Cutting Force Math (Skin → Pulp → Board│  │ • Soft-body grasp compliance (prevent bruising)  │
│ • Slicing MDP: v_slice, Δv_z, Z-impedance        │  │ • Tangential slip prevention under blade sawing  │
│ • Slicing Reward: R_pen, R_slicing, P_slam       │  │ • Holding Sync MDP: Δx_hold, Δy_hold, F_hold      │
│ • Macro pre-contact planning (MoveIt 2)          │  │ • 1 kHz joint torque compliance & slip arrest    │
│                                                  │  │                                                  │
│ [Unit Test: Slices a tomato clamped to a table]  │  │ [Unit Test: Holds tomato under disturbance force]│
└────────────────────────┬─────────────────────────┘  └────────────────────────┬─────────────────────────┘
                         │                                                     │
                         └──────────────────────────┬──────────────────────────┘
                                                    │
                                         WEEKS 5–6: THE MERGER
                                                    │
                                                    ▼
                         Full Bimanual Coordination: Hold + Slice concurrently
```

---

## 2. Detailed Role Breakdown
 
### 2.1 Shahd: Active Slicing Arm & Fracture Mechanics Lead
 
* **Primary Engineering Mission:** Optimize the knife blade trajectory, downward feed rate, sawing action, and variable impedance to cut through deformable soft tissue cleanly without causing crushing or excessive downward force.
* **Daily Development Stack:** NVIDIA Isaac Sim / Isaac Lab, Gmsh / fTetWild, PhysX 5 FEM, PyTorch, SkRL, ROS 2 (MoveIt 2).
* **Key Theoretical & Mathematical Responsibilities:**
  1. **Volumetric TetMeshing:** Convert hollow tomato surface scans into solid tetrahedral meshes (`.msh` / `.usd`) using Delaunay tetrahedralization in Gmsh.
  2. **PhysX FEM Elasticity & Tearing:**
     - Configure continuum mechanics parameters: Young's modulus $E = 1.2\text{ MPa}$, Poisson ratio $\nu = 0.4$, mass density $\rho = 1050\text{ kg/m}^3$.
     - Implement topological element decoupling when localized principal stress reaches critical fracture toughness ($K_I \ge K_{Ic}^{skin} = 0.35\text{ MPa}\sqrt{\text{m}}$).
  3. **Cutting Action Control ($\mathcal{A}_{slice} \subset \mathbb{R}^4$):**
     - Downward penetration feed delta: $\Delta v_{des, z} \in [-5, +5]\text{ mm/s}$.
     - Longitudinal sawing velocity: $v_{slice, x} \in [0, 50]\text{ mm/s}$ (shear friction reduction).
     - Adaptive Z-stiffness modulation: $\Delta K_{d, z} \in [100, 2000]\text{ N/m}$.
     - Adaptive Z-damping modulation: $\Delta D_{d, z} \in [20, 300]\text{ Ns/m}$ (post-puncture slam arrest).
  4. **Slicing Reward Engineering:**
     - $R_{penetration} = w_{pen} \cdot \max(0, z_{target} - z_{blade})$
     - $R_{slicing} = w_{slice} \cdot |v_{blade, x}| \cdot \mathbb{I}(F_z > F_{contact})$
     - $P_{force\_crush} = -w_{crush} \cdot \max(0, F_z - 8.0\text{ N})^2$
     - $P_{slam} = -w_{slam} \cdot \max(0, \ddot{z}_{blade}) \cdot \mathbb{I}(\text{Phase} == 2)$
* **Independent Unit Test (Zero Waiting):**  
  Shahd builds an Isaac Lab environment with **one Franka/UR arm holding a knife** and a **tomato clamped in a rigid jig**. Shahd trains PPO/SAC to slice cleanly through the clamped tomato without needing the holding arm.
 
---
 
### 2.2 Ahmed: Compliant Holding Arm, Proprioceptive Compliance & Real-Time Control Lead
 
* **Primary Engineering Mission:** Stabilize the deformable tomato against the knife's lateral sawing friction and downward penetration forces, ensuring the fruit does not slip, roll, or suffer grasp bruising, using Franka's native 1 kHz joint torque sensing ($\boldsymbol{\tau}_{ext}$), task-space force reconstruction ($\mathbf{F}_{ext}$), and closed-loop grasp compliance.
* **Daily Development Stack:** NVIDIA Isaac Lab, PyTorch, SkRL, WandB, ROS 2 (Jazzy), `libfranka` (C++), `PREEMPT_RT` Linux.
* **Key Theoretical & Mathematical Responsibilities:**
  1. **Proprioceptive Contact Force Reconstruction & Grasp Compliance:**
     - Reconstruct task-space contact wrench from Franka's native joint torque sensors: $\mathbf{F}_{ext} = (\mathbf{J}^T)^\dagger \boldsymbol{\tau}_{ext} \in \mathbb{R}^3$.
     - Regulate holding normal force $F_{hold}$ strictly within the non-bruising, non-slip operating window:
       $$F_{slip} < F_{hold} < F_{bruise} \quad (1.5\text{ N} < F_{hold} < 5.0\text{ N})$$
     - Counteract lateral blade drag force $F_x$ via tangential friction modeling ($\mu_{contact} \approx 0.45$) and active micro-adjustments ($\Delta x_{hold}$).
  2. **Observation Space Assembly ($\mathcal{S} \subset \mathbb{R}^{33}$):**
     - Dual-arm kinematics: $[\mathbf{q}_{dual}, \dot{\mathbf{q}}_{dual}] \in \mathbb{R}^{14}$.
     - Tool state: $[\mathbf{p}_{knife}, \mathbf{v}_{knife}, \boldsymbol{\omega}_{knife}] \in \mathbb{R}^9$.
     - Tomato state: $[\mathbf{p}_{tomato}, \mathbf{R}_{tomato}] \in \mathbb{R}^7$.
     - Proprioceptive force feedback: 3D reconstructed contact wrench $\mathbf{F}_{ext} \in \mathbb{R}^3$.
  3. **Holding Action Control ($\mathcal{A}_{hold} \subset \mathbb{R}^2$):**
     - Planar holding position adjustments: $\Delta x_{hold}, \Delta y_{hold} \in [-2, +2]\text{ mm}$.
  4. **Holding & Coordination Rewards:**
     - $P_{sync} = -w_{sync} \cdot \|\mathbf{p}_{hold} - \mathbf{p}_{tomato}\|^2$
     - $P_{bruise} = -w_{bruise} \cdot \max(0, F_{hold} - 5.0\text{ N})^2$
     - $P_{slip} = -w_{slip} \cdot |v_{tomato, x}|$
* **Independent Unit Test (Zero Waiting):**  
  Ahmed builds an Isaac Lab environment with **one Franka/UR arm with a gripper holding a tomato**. A simulated oscillating disturbance force ($\pm 4\text{ N}$ lateral, $2–8\text{ N}$ downward) is applied to the tomato to simulate the knife's actions. Ahmed trains the holding policy to keep the tomato stable and upright without bruising.

---

## 3. 8-Week Roadmap & Integration Schedule

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ WEEKS 1–2: SINGLE-ARM INDEPENDENT PROTOTYPES                                          │
│   • Shahd: Clamped tomato + knife arm + FEM mesh + downward sawing physics.           │
│   • Ahmed: Gripper arm + held tomato + disturbance forces + tactile/state manager.     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ WEEKS 3–4: SINGLE-ARM RL BENCHMARKS                                                   │
│   • Shahd: Trains PPO on slicing arm to minimize cutting force and stop slam.          │
│   • Ahmed: Trains PPO on holding arm to maintain stable grip under disturbances.       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ WEEKS 5–6: THE BIMANUAL MERGER                                                        │
│   • Combine into a dual-arm Isaac Lab scene (`BimanualTomatoCuttingEnv`).              │
│   • Run joint training: Arm 1 cuts while Arm 2 dynamically stabilizes.                 │
│   • Run baseline comparisons: Our Method vs Fixed Impedance vs Rigid Position Control. │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ WEEKS 7–8: EXPERIMENTAL FIGURES & MANUSCRIPT DRAFTING                                  │
│   • Shahd writes physics, tearing, and cutting performance sections.                   │
│   • Ahmed writes holding stability, tactile hardware, and coordination sections.       │
│   • Final review with Prof. Shan An for IEEE RA-L / IROS submission.                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Modular Codebase Architecture

To prevent Git merge conflicts, code is structured into decoupled components:

```
src/
├── envs/
│   ├── components/
│   │   ├── cutting_arm.py          # Shahd: Knife kinematics, downward/sawing feed
│   │   ├── holding_arm.py          # Ahmed: Gripper kinematics, grasp regulation
│   │   └── tomato_fem.py           # Shahd: PhysX FEM TetMesh asset & tearing schema
│   ├── bimanual_cutting_env.py     # Week 5 Integration: Assembles cutting + holding
│   └── bimanual_cutting_cfg.py     # Joint scene configuration (dual arms, board, sensors)
├── controllers/
│   ├── slicing_impedance.py        # Shahd: 1 kHz variable Z-impedance (K_z, D_z)
│   └── holding_compliance.py       # Ahmed: Grasp compliance & slip prevention
├── rewards/
│   ├── slicing_rewards.py          # Shahd: R_pen, R_slicing, P_crush, P_slam
│   └── holding_rewards.py          # Ahmed: P_sync, P_bruise, P_slip
├── observations/
│   └── state_manager.py            # Ahmed: Assembles 33D observation vector
└── train_bimanual.py               # Combined SkRL PPO execution script with WandB
```

---

## 5. IEEE RA-L / IROS Manuscript Ownership

Every section of the final publication has a primary owner, ensuring equal 50/50 academic contribution:

| Section | Manuscript Heading | Primary Writer | Supporting Reviewer | Key Figures / Tables Contributed |
| :---: | :--- | :---: | :---: | :--- |
| **I** | **Introduction** | **Both** | Advisor (Prof. Shan An) | Fig. 1: Bimanual DOM System Architecture |
| **II** | **Related Work** | **Ahmed** | Shahd | Comparative taxonomy table (DOM & Food Robotics) |
| **III** | **Deformable Mechanics & Tearing** | **Shahd** | Ahmed | Fig. 2: 4-Phase cutting force curve & FEM stress fields |
| **IV** | **System Architecture & Control** | **Ahmed** | Shahd | Fig. 3: Control handoff & proprioceptive grasp loop |
| **V** | **MDP Problem Formulation** | **Both** | Advisor | Formal State ($\mathbb{R}^{33}$), Action ($\mathbb{R}^6$), and Reward tables |
| **VI** | **Experiments & Ablations** | **Both** | Advisor | Fig. 4: WandB PPO convergence curves, cut cross-sections, crush-rate vs. baseline table |
| **VII**| **Conclusion & Future Work** | **Both** | Advisor | Final summary & Sim-to-Real transition |

---

## 6. Day 1 Immediate Action Checklist

### Shahd (Slicing Arm & Fracture Lead)
1. Initialize local Git branch: `git checkout -b dev/cutting-arm`.
2. Install 3D meshing libraries: `pip install gmsh trimesh`.
3. Obtain a high-resolution 3D surface mesh of a tomato (`.obj` or `.stl`).
4. Write a standalone Python script using Gmsh to generate the volumetric solid tetrahedral mesh (`tomato.msh`).
5. Open Isaac Sim and mount the knife CAD model onto the robot flange to verify tool center point (TCP) transforms.

### Ahmed (Holding Arm, Tactile Hardware & Coordination Lead)
1. Initialize local Git branch: `git checkout -b dev/holding-arm`.
2. Install RL and experiment logging libraries: `pip install skrl["torch"] wandb hydra-core`.
3. Set up a free account on [wandb.ai](https://wandb.ai) and run `wandb login`.
4. Run the Franka benchmark training script to verify GPU acceleration and logging:
   ```bash
   ./isaaclab.sh -p source/standalone/workflows/skrl/train.py --task Isaac-Reach-Franka-v0 --headless --num_envs 64
   ```
5. Create `src/observations/state_manager.py` and implement the 33-dimensional tensor observation packing logic using dummy NumPy/PyTorch arrays.
