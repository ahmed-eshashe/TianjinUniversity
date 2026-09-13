# Isaac Lab vs MuJoCo + Isaac Sim

**Project:** DOM — Dual Robot Arms for Tomato Cutting  
**Question:** Which simulation platform to use for robot learning?

---

## Architecture Overview

### 🟩 Isaac Lab — Unified Robot Learning Framework (NVIDIA)

A single integrated platform where physics (PhysX 5), photorealistic rendering (RTX), and RL training APIs all run together on the GPU.

```
┌──────────────────────────────────────┐
│            Isaac Lab                 │
│  ┌──────────┐  ┌──────────┐  ┌────┐ │
│  │ PhysX 5  │  │ RTX Rend │  │ RL │ │
│  │(Physics) │  │(Visuals) │  │APIs│ │
│  └──────────┘  └──────────┘  └────┘ │
│        All on GPU — one process      │
└──────────────────────────────────────┘
```

### 🔵 MuJoCo + Isaac Sim — Best-of-Breed Hybrid (DeepMind + NVIDIA)

Two separate best-in-class engines bridged together.

```
┌─────────────────────┐        ┌─────────────────────┐
│       MuJoCo        │  sync  │     Isaac Sim        │
│  (Physics Engine)   │ ──────→│   (Rendering)        │
│  CPU / MJX-GPU      │ state  │   RTX ray-tracing    │
└─────────────────────┘        └─────────────────────┘
         ↑                               ↑
  RL / IL training              VLA / vision model
  (physics fidelity)             training data
```

---

## Detailed Comparison

| Dimension | 🟩 Isaac Lab | 🔵 MuJoCo + Isaac Sim |
|---|---|---|
| **Physics Engine** | PhysX 5 (NVIDIA, GPU) | MuJoCo (DeepMind) — gold standard for manipulation |
| **Rendering** | RTX ray-tracing (native) | Isaac Sim RTX (separate process) |
| **RL Training Speed** | ⭐ Very fast — thousands of parallel GPU envs | ⚠️ Moderate — MuJoCo CPU-based; MJX catching up |
| **Contact / Cutting Physics** | Good for rigid bodies | ⭐ Best-in-class for dexterous, contact-rich tasks |
| **Setup Complexity** | ✅ Lower — one stack, pre-built assets | ❌ Higher — two systems to sync and maintain |
| **IL / VLA Support** | Growing (GROOT, tutorials) | ⭐ Strong — ACT, Diffusion Policy, ALOHA all use MuJoCo |
| **Domain Randomization** | ⭐ Native built-in | Manual implementation in each engine |
| **Sim-to-Real Gap (dynamics)** | ⚠️ Moderate (PhysX) | ⭐ Smaller — MuJoCo physics closer to real manipulation |
| **Sim-to-Real Gap (visual)** | ✅ RTX closes visual gap | ✅ Isaac Sim RTX closes visual gap |
| **Hardware Requirement** | NVIDIA GPU required | MuJoCo runs on CPU; Isaac Sim needs GPU |
| **Research Community** | Growing, NVIDIA-backed (newer) | ⭐ Massive — DeepMind, Stanford, CMU, Berkeley, thousands of papers |
| **Deformable Objects (tomatoes)** | ⚠️ Limited PhysX FEM support | ⚠️ Limited — both approximate soft-body deformation |
| **RL Framework Integration** | RSL-RL, SkRL, SB3 (plug-and-play) | Gymnasium, MJX, any Python RL library |

---

## When to Use Each

### 🟩 Choose Isaac Lab when…
- You need **large-scale RL training fast** (parallel GPU environments, millions of steps overnight)
- Your team is already in the NVIDIA ecosystem
- You want **physics + rendering + RL in one unified tool**
- You prioritize development speed over physics accuracy
- Task is primarily **rigid-body manipulation** (grasping, pick-and-place)
- You need built-in domain randomization for Sim-to-Real transfer

### 🔵 Choose MuJoCo + Isaac Sim when…
- You need **accurate contact physics** for cutting or dexterous manipulation
- You are training **IL or VLA models** (ACT, Diffusion Policy, π0)
- Your research references or extends papers that use MuJoCo (most manipulation literature)
- You need **maximum physics fidelity** for Sim-to-Real transfer
- You want fine-grained independent control over each simulation component
- Your team already has MuJoCo expertise

---

## The Fundamental Limitation Both Share

> **Neither simulator handles tomato deformation accurately.**
>
> Both platforms treat the tomato as approximately rigid. The real cutting dynamics — squish under knife pressure, juice release, skin tension, fracture propagation — are not faithfully modelled by either PhysX or MuJoCo in their default configurations. This is an active research gap in food manipulation simulation.

---

## DOM Verdict

### Short-term: MuJoCo + Isaac Sim (current setup) ✅

The current hybrid approach is the **correct choice for a research context**:
- Better contact physics for knife-on-tomato interaction
- Directly compatible with ACT / Diffusion Policy literature
- Isaac Sim renders photorealistic images for VLA training
- More defensible in a publication — aligned with mainstream manipulation research

### Long-term: Consider Isaac Lab for scale-up

If the project moves to **large-scale RL training** (10M+ parallel rollouts for policy optimization), Isaac Lab's GPU-parallel environments will offer a significant speed advantage. This is a natural Phase 2 migration once the core pipeline is validated.

### DOM Quick Scorecard

| Criterion | Winner |
|---|---|
| Contact physics accuracy | 🔵 MuJoCo + Isaac Sim |
| RL training speed | 🟩 Isaac Lab |
| IL / VLA model training | 🔵 MuJoCo + Isaac Sim |
| Setup simplicity | 🟩 Isaac Lab |
| Research community & reproducibility | 🔵 MuJoCo + Isaac Sim |
| Domain randomization | 🟩 Isaac Lab |
| Deformable object support | Tie ⚠️ (both approximate) |

---

## References

- Isaac Lab: https://isaac-sim.github.io/IsaacLab/
- MuJoCo: https://mujoco.org/
- ALOHA (bimanual IL with MuJoCo): Zhao et al., 2023 — *Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware*
- ACT: Zhao et al., 2023 — *Action Chunking with Transformers*
- Diffusion Policy: Chi et al., 2023 — *Diffusion Policy: Visuomotor Policy Learning via Action Diffusion*
