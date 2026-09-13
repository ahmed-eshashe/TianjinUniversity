# Training Approach Comparison for DOM

**Project:** DOM — Dual Robot Arms for Tomato Cutting  
**Constraint:** Tight time budget  
**Question:** Imitation Learning vs Vision-Based RL vs Traditional Control?

---

## Summary Table

| Criterion | Imitation Learning | Vision-Based RL | Traditional Control |
|---|---|---|---|
| **Time to Deploy** | ✅ Fast (weeks) | ❌ Very slow (months) | ⚠️ Medium |
| **Data Needed** | 50–200 teleoperation demos | Millions of sim steps | None (hand-engineered) |
| **Tomato Variance** | Good | Excellent | Poor |
| **Setup Complexity** | Low–Medium | Very High | High (modelling burden) |
| **Dual Arm Coordination** | Natural (encoded in demos) | Hard to reward-shape | Must be manually specified |
| **Iterability** | Add demos → retrain | Retrain from scratch (slow) | Tune parameters |
| **Expertise Needed** | Moderate ML | Deep RL + Sim expertise | Robotics + Control theory |
| **Debuggability** | Opaque (learned) | Opaque (learned) | ✅ Fully step-through |
| **Best For** | Tight deadlines, structured tasks | Long-term, max robustness | Fixed, known environments |

---

## 1. Imitation Learning (IL)

Learn directly from human demonstrations via teleoperation.  
**Key algorithms:** ACT (Action Chunking with Transformers), Diffusion Policy, BC-Z.

### Pros
- Fast iteration cycle — collect demos → train overnight → deploy
- Naturally captures bimanual coordination (no explicit reward shaping)
- Works directly on real robot — no simulator or sim-to-real gap needed
- Handles soft/deformable objects better than RL (learned from real physics)
- ACT and Diffusion Policy are validated on bimanual tasks (ALOHA, UMI)

### Cons
- Limited to demonstrated distribution — fails on unseen configurations
- Requires quality teleoperation rig for dual arms (non-trivial to build/buy)
- Needs a skilled operator for consistent demos (bad demos poison the policy)
- Debugging failures is opaque — no step-through logic
- High-dimensional joint action space (2 arms × 6–7 DOF) with thin coverage at 100–200 demos

### Realistic Timeline
| Phase | Duration |
|---|---|
| Teleop rig setup + camera calibration | 1–2 weeks |
| Demo collection (100–200 cuts) | 1–2 weeks |
| Training + hyperparameter tuning | 3–5 days |
| Debugging + iteration | 1–2 weeks |
| **Total to first working policy** | **~4–6 weeks** |

---

## 2. Vision-Based Reinforcement Learning

Agent learns by trial-and-error from visual observations + reward signal in simulation.  
**Key algorithms:** PPO, SAC, DrQ-v2, TD-MPC2. **Foundation models:** RT-2, OpenVLA.

### Pros
- Can exceed human-level performance given enough training time
- Generalizes to unseen tomato positions, sizes, lighting conditions
- Self-improves without new human demonstrations

### Cons
- Requires weeks–months of simulation training before any real-robot deployment
- **Sim-to-real gap is severe for deformable objects** — tomatoes squish, MuJoCo/PhysX approximate this poorly
- Reward shaping for a clean tomato cut is non-trivial
- Bimanual coordination reward is difficult to define without dense supervision
- Very high compute requirement (GPU cluster for parallel rollouts)

> **DOM verdict:** Not recommended as a primary approach. Reserve for Phase 2 robustness hardening once a traditional/IL baseline exists. The deformable food cutting sim-to-real gap is an open research problem.

---

## 3. Traditional Control Methods

Classical motion planning + force/impedance control + computer vision for detection.  
**Tools:** MoveIt!, PID, impedance control, YOLO/SAM for detection.

### Pros
- Deterministic and fully interpretable — debuggable step by step
- No training data required
- Fast to prototype for a fixed, known workspace
- Force-torque sensing provides safe cutting with explicit limits

### Cons
- Brittle to tomato size, shape, position, and lighting variation
- Requires precise, frequent recalibration
- Bimanual synchronization must be manually specified
- Knife contact/force modelling for cutting is complex
- Any calibration drift causes complete failure with no graceful recovery

### Realistic Timeline (fixed workspace, uniform tomatoes)
- 1–2 weeks to a working but fragile demo

---

## Recommended Strategy for DOM (Staged Hybrid)

Given the existing simulator infrastructure and research context, the optimal approach is a **staged pipeline**:

```
Stage 1 — Week 1–2: Traditional Control Baseline
  ├── YOLO/SAM for tomato detection & pose estimation
  ├── MoveIt! for pre-grasp arm trajectories
  ├── Scripted knife trajectory (fixed cut plane)
  └── Force-torque safety layer
  → Goal: something cutting tomatoes, even if brittle. Demo fallback.

Stage 2 — Week 2–5: Imitation Learning on Execution
  ├── Collect 100–200 bimanual teleoperation demos
  ├── Train ACT or Diffusion Policy on bimanual execution segment only
  ├── Traditional control handles deterministic sub-tasks
  └── IL handles grasp variation and cut alignment
  → Goal: robustness to tomato variation

Stage 3 — If time permits: RL in MuJoCo
  ├── Harden policy against tomato size/orientation variation
  ├── Use domain randomization in Isaac Sim for visual robustness
  └── Fine-tune sim policy on real robot data
  → Goal: publication-grade generalization results
```

### Key decision variable
> **How variable are your tomatoes and how fixed is the workspace?**
> - Uniform tomatoes, fixed surface → Traditional Control → working in **1–2 weeks**
> - Varied tomatoes, some clutter, research-demo quality → IL on top of traditional baseline → **4–6 weeks**
> - Wild variation, unstructured, production-grade → RL/VLA → **3+ months**

---

## Recommended Stack

```
Overhead camera + wrist cameras (both arms)
        ↓
YOLO / SAM  →  tomato detection & pose
        ↓
ACT or Diffusion Policy  ←  bimanual teleoperation demos
        ↓
ROS2 / robot controller
        ↓
Force-torque sensing  →  contact-safe cutting phase
```
