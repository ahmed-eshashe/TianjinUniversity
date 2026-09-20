# Data Sources & Mathematical MDP Formulation for Traditional RL (Paper 1)

**Project:** Dual-Arm Robot Tomato Cutting (DOM) — Paper 1 Execution  
**Target Venue:** IEEE RA-L / IROS  
**Framework:** Traditional RL (PPO / SAC via SkRL in Isaac Lab)  
**Primary Focus:** Pulling and synthesizing all physical models, sensor parameters, system dynamics, and MDP formulations from the repo for RL environment construction.

---

## 1. Overview of Pulled Data Sources

This document consolidates key mathematical models, mechanical parameters, and system data from across the repository:
- `architectures/vision_tactile_fusion_cutting.md` (Hierarchical Vision-Force Control & Handoff)
- `directions/direction5_tacblade_cutting.md` (Fracture Mechanics & Piecewise Force Equations)
- `simulation/rl_software_tools.md` (7-Layer Software Stack & Isaac Lab / SkRL integration)

---

## 2. Complete MDP Formulation for Traditional RL

For Paper 1, the tomato cutting task is formulated as a Markov Decision Process (MDP) defined by the tuple $\mathcal{M} = (\mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma, \rho_0)$.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ISAAC LAB RL ENVIRONMENT                         │
│                                                                             │
│   Observation Vector S_t ∈ ℝ^33             Action Vector A_t ∈ ℝ^6        │
│  ┌───────────────────────────┐             ┌───────────────────────────┐    │
│  │ • Joint positions/vels   │             │ • Impedance deltas ΔK, ΔD │    │
│  │ • Knife EE pose & vels    │  ◄────────  │ • Feed rate delta Δv_des  │    │
│  │ • Tomato 3D pose          │   Policy    │ • Slicing velocity v_slice│    │
│  │ • TacBlade 6-axis F/T     │  π_θ(a|s)   │ • Holding arm target Δx   │    │
│  │ • Acoustic burst E_burst  │             └───────────────────────────┘    │
│  └─────────────┬─────────────┘                           │                  │
│                │                                         ▼                  │
│                └─────────────────────────► [Reward Computation R_t]         │
│                                            • Penetration progress           │
│                                            • Lateral sawing reward          │
│                                            • Puncture force penalty         │
│                                            • Bimanual sync penalty          │
└─────────────────────────────────────────────────────────────────────────┘
```

### A. State / Observation Space ($\mathcal{S} \subset \mathbb{R}^{33}$)

At each environment step $t$, the policy receives a continuous observation vector $\mathbf{s}_t$:

$$\mathbf{s}_t = \Big[ \mathbf{q}_{dual}, \, \dot{\mathbf{q}}_{dual}, \, \mathbf{p}_{knife}, \, \mathbf{v}_{knife}, \, \boldsymbol{\omega}_{knife}, \, \mathbf{p}_{tomato}, \, \mathbf{R}_{tomato}, \, \mathbf{F}_{TacBlade}, \, E_{burst} \Big]^T \in \mathbb{R}^{33}$$

| Component | Variable | Dimension | Physical Meaning |
|---|---|---|---|
| **Dual Arm Kinematics** | $\mathbf{q}_{dual}, \dot{\mathbf{q}}_{dual}$ | $\mathbb{R}^{14}$ | Joint positions and velocities of dual arms (7 DOF per arm) |
| **Knife EE State** | $\mathbf{p}_{knife}, \mathbf{v}_{knife}, \boldsymbol{\omega}_{knife}$ | $\mathbb{R}^9$ | 3D position, linear velocity, and angular velocity of the cutting blade |
| **Tomato Pose** | $\mathbf{p}_{tomato}, \mathbf{R}_{tomato}$ | $\mathbb{R}^7$ | 3D position and orientation quaternion of the target tomato |
| **TacBlade On-Tool Force** | $\mathbf{F}_{TacBlade} = [F_x, F_y, F_z, M_x, M_y, M_z]^T$ | $\mathbb{R}^6$ | 6-axis force/torque vector measured at blade root |
| **Acoustic Burst Energy** | $E_{burst}$ | $\mathbb{R}^1$ | Piezoelectric high-frequency vibration envelope ($100\text{ Hz} - 5\text{ kHz}$) |

---

### B. Action Space ($\mathcal{A} \subset \mathbb{R}^{6}$)

The policy outputs continuous impedance parameter deltas and trajectory modulations executed by Layer 1 (1 kHz Impedance Controller):

$$\mathbf{a}_t = \Big[ \Delta v_{des, z}, \, v_{slice, x}, \, \Delta K_{d, z}, \, \Delta D_{d, z}, \, \Delta x_{hold}, \, \Delta y_{hold} \Big]^T \in \mathbb{R}^6$$

| Component | Variable | Bounds | Role |
|---|---|---|---|
| **Downward Feed Delta** | $\Delta v_{des, z}$ | $[-5, \, +5] \text{ mm/s}$ | Modulates vertical penetration rate |
| **Lateral Slicing Velocity**| $v_{slice, x}$ | $[0, \, 50] \text{ mm/s}$ | Drives sawing action along blade edge ($F_x$ friction reduction) |
| **Z-Stiffness Modulation** | $\Delta K_{d, z}$ | $[100, \, 2000] \text{ N/m}$ | Modulates vertical compliance (soft during puncture, stiff during approach) |
| **Z-Damping Modulation** | $\Delta D_{d, z}$ | $[20, \, 300] \text{ Ns/m}$ | Modulates damping to arrest post-puncture forward slam |
| **Holding Arm Sync** | $\Delta x_{hold}, \Delta y_{hold}$ | $[-2, \, +2] \text{ mm}$ | Adjusts non-cutting hand grasping stabilization |

---

### C. Comprehensive Reward Function ($\mathcal{R}$)

The reward function $R_t$ balances penetration progress, lateral slicing, force regulation, and bimanual coordination:

$$R_t = R_{penetration} + R_{slicing} + P_{force\_crush} + P_{sync} + P_{action\_smooth} + R_{success}$$

#### 1. Penetration Progress Reward ($R_{penetration}$)
Encourages steady downward progress through the tomato height $H_{tomato}$:

$$R_{penetration} = w_{pen} \cdot \max\Big(0, \, z_{slice\_plane}(t) - z_{blade}(t)\Big)$$

#### 2. Lateral Slicing Reward ($R_{slicing}$)
Rewards sawing motion along the blade's longitudinal axis ($x$-axis), which reduces normal force $F_z$ via fracture mechanics shear coupling:

$$R_{slicing} = w_{slice} \cdot \left| v_{blade, x} \right| \cdot \mathbb{I}(F_z > F_{contact})$$

#### 3. Puncture & Crush Penalty ($P_{force\_crush}$)
Penalizes excessive normal force $F_z$ that causes elastic squishing or juice expulsion:

$$P_{force\_crush} = - w_{crush} \cdot \max\Big(0, \, F_z - F_{z, max}\Big)^2$$

*where $F_{z, max} = 8.0 \text{ N}$ (tomato skin puncture threshold).*

#### 4. Post-Puncture Slam Penalty ($P_{slam}$)
Penalizes high downward acceleration $\ddot{z}_{blade}$ immediately following puncture (detected when $\dot{F}_z < -\alpha$):

$$P_{slam} = - w_{slam} \cdot \max\Big(0, \, \ddot{z}_{blade}\Big) \cdot \mathbb{I}(\text{Phase} == 2)$$

#### 5. Bimanual Holding Sync Penalty ($P_{sync}$)
Ensures the holding arm maintains stable contact without slipping or excessive clamping force:

$$P_{sync} = - w_{sync} \cdot \|\mathbf{p}_{hold\_arm} - \mathbf{p}_{tomato}\|^2 - w_{hold\_force} \cdot \max\Big(0, \, F_{hold} - F_{hold, max}\Big)$$

#### 6. Action Smoothness Penalty ($P_{action\_smooth}$)
Prevents high-frequency chatter in impedance parameter updates:

$$P_{action\_smooth} = - w_{smooth} \cdot \|\mathbf{a}_t - \mathbf{a}_{t-1}\|^2$$

#### 7. Terminal Success Reward ($R_{success}$)
Awarded when the knife blade cleanly reaches the cutting board plane ($z_{board}$) without crushing the tomato structure:

$$R_{success} = \begin{cases} +100, & \text{if } z_{blade} \le z_{board} \text{ and } \text{Deformation} < 15\% \\ -50, & \text{if } \text{Tomato Crushed} (F_z > 25\text{ N}) \end{cases}$$

---

## 3. Physical Cutting Force Models (Fracture Mechanics Data)

The RL environment in Isaac Lab / MuJoCo simulates cutting using a four-phase piecewise force law pulled from `direction5_tacblade_cutting.md`:

```
               PIECEWISE CUTTING FORCE PROFILE
  Force (N)
   10 │             Phase 2: PUNCTURE
      │                (Fracture Discontinuity)
    8 │                  /╲
    6 │                 /  ╲  ← 50-80% Force drop in <5ms
    4 │   Phase 1:     /    ╰─────────────── Phase 3: VISCOPLASTIC
    2 │   ELASTIC     /                       INTERIOR
    0 └───SKIN───────/────────────────────────────────────────► Penetration (δ)
```

### Phase Equations & Parameters

#### Phase 1: Elastic Skin Deformation ($0 \le \delta < \delta_{punct}$)
$$\mathbf{F}_{cut}(\delta) = \frac{4}{3} E^* \sqrt{R_{blade}} \, \delta^{3/2} + \sigma_0 \cdot w \cdot \delta$$
- $E^* = 1.2 \text{ MPa}$ (Effective skin modulus)
- $R_{blade} = 25 \, \mu\text{m}$ (Blade edge radius)
- $\sigma_0 = 0.45 \text{ N/mm}$ (Biaxial skin pre-stress)
- $w = 20 \text{ mm}$ (Blade contact width)

#### Phase 2: Skin Puncture Fracture ($\delta = \delta_{punct}$)
Puncture occurs when stress intensity reaches critical fracture toughness $K_I \ge K_{Ic}^{skin} = 0.35 \text{ MPa}\sqrt{\text{m}}$.  
Discontinuous force drop:

$$\Delta F_{fracture} = (0.50 \text{ to } 0.80) \cdot F_{peak}$$

#### Phase 3: Viscoplastic Interior Cutting ($\delta_{punct} < \delta < \delta_{exit}$)
$$F_{cut}(\delta) = \tau_y \cdot A_{shear}(\delta) + G_c \cdot w + \eta \cdot \dot{\delta} \cdot A_{contact}(\delta)$$
- $\tau_y = 12 \text{ kPa}$ (Yield stress of interior pulp/gel)
- $G_c = 180 \text{ J/m}^2$ (Interior fracture toughness)
- $\eta = 0.08 \text{ Pa}\cdot\text{s}$ (Viscous drag coefficient)

#### Phase 4: Bottom Skin & Board Exit ($\delta \ge \delta_{exit}$)
Second skin puncture ($F_z \approx 4\text{ N}$) followed by rigid cutting board contact ($K_{board} = 10^5 \text{ N/m}$).

---

## 4. TacBlade On-Tool Sensing Integration

TacBlade sensor data integrated into the RL observation vector:

```
┌─────────────────────────────────────────────────────────────┐
│                 TacBlade 1 kHz Sensor Data                  │
│                                                             │
│  • Strain Gauges (2 kHz):  Fz (normal), Fx (slice), My (bend) │
│  • Piezo Elements (10 kHz): Burst energy E_burst (1-5 kHz)   │
│  • STM32 On-Chip Phase Detector: Phase ID q ∈ {1, 2, 3, 4}   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
            Passed into Policy Observation Vector s_t
```

---

## 5. Summary of Key Hyperparameters for SkRL (PPO)

| Hyperparameter | Value | Rationale |
|---|---|---|
| **Algorithm** | PPO (Proximal Policy Optimization) | Stable continuous control |
| **Policy Architecture** | MLP `[256, 256, 128]` | State-based vector input ($\mathbb{R}^{33}$) |
| **Activation Function** | ELU | Smooth gradient flow for impedance deltas |
| **Learning Rate** | $3 \times 10^{-4}$ (Linear decay) | Standard PPO convergence |
| **Discount Factor ($\gamma$)** | $0.99$ | Long-horizon cutting sequence |
| **GAE Parameter ($\lambda$)** | $0.95$ | Variance reduction |
| **Clip Range ($\epsilon$)** | $0.2$ | Policy update stability |
| **Number of Envs** | 512–1024 | Optimized for 8GB VRAM RTX 5060 |
| **Horizon Length ($T$)** | 240 steps | 4-second cutting episode @ 60 Hz control |
