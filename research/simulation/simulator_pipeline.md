# Simulator Pipeline: MuJoCo + Isaac Sim

**Project:** DOM — Dual Robot Arms for Tomato Cutting  
**Pipeline:** MuJoCo (physics) + Isaac Sim (rendering) hybrid

---

## Overview

The DOM simulator uses two best-in-class engines together:

| Engine | Role | Provided by |
|---|---|---|
| **MuJoCo** | Physics simulation | DeepMind / Google |
| **Isaac Sim** | Photorealistic rendering | NVIDIA |

> **Why two engines?** MuJoCo alone produces cartoon-like images — vision models trained on it fail on real cameras. Isaac Sim alone is too slow to run the millions of physics steps RL requires. Together they provide *accurate physics + photorealistic visuals*.

---

## 1. The Two Engines

### MuJoCo — Physics Engine

Simulates the physical laws of the world: forces, contacts, joint dynamics, collisions, and friction.

- Best-in-class contact physics for dexterous manipulation (industry standard for manipulation research)
- Models robot joints, knife-tomato contact, end-effector forces
- RL algorithms use MuJoCo state to compute rewards
- Runs thousands of physics steps per second (headless, no rendering overhead)
- **Analogy:** MuJoCo is the *laws of physics* — it decides what happens when the knife touches the tomato

### Isaac Sim — Rendering / Perception Engine

Generates photorealistic visual observations that look like real camera feeds.

- RTX ray-tracing: realistic shadows, reflections, material shading
- Randomizes lighting, textures, tomato colors (domain randomization)
- Generates synthetic training images for vision-based models (VLA, YOLO fine-tuning)
- Outputs RGB, depth, and segmentation data
- **Analogy:** Isaac Sim is the *camera and lighting crew* — it makes the simulation look real enough to fool a vision model

---

## 2. Real-to-Sim and Sim-to-Real

These are the two directions of the bridge between reality and simulation.

```
 REAL WORLD  ←─────────────────────→  SIMULATOR
              Sim-to-Real  (deploy)
              Real-to-Sim  (model)
```

### Real-to-Sim (R2S) — Bringing the real world into the simulator

You replicate the real environment in simulation so the sim closely matches your actual lab setup.

**DOM applications:**
- 3D scan real tomatoes → import mesh into MuJoCo with material properties
- Match real robot URDF/mass/inertia parameters in sim
- Calibrate sim camera to match real wrist camera intrinsics/extrinsics
- Validate policies in sim before running on physical robot arms (safe testing)

### Sim-to-Real (S2R) — Deploying simulator-trained policies to the real robot

Train models in simulation (cheap, fast, safe), then transfer learned weights to the physical robot.

**DOM applications:**
- Train RL policy for 10M+ sim steps overnight (no hardware wear)
- Apply domain randomization (tomato sizes, knife friction, lighting) to bridge the gap
- Deploy trained policy weights directly to dual arms
- Fine-tune with real robot data if the gap causes failures

### The Sim-to-Real Gap — Key Challenge for DOM

> Tomatoes are **deformable, soft objects**. Simulators struggle to model how they squish and deform under knife pressure. This is currently an open research problem.

Both MuJoCo (contact mechanics) and Isaac Sim (photorealistic appearance) work together to minimize the gap:
- Isaac Sim closes the **visual gap** (images look real)
- MuJoCo closes the **dynamics gap** (physics behaves realistically)

---

## 3. Data Collection: Real Robot + Simulation

Training data can be collected from both sources and combined:

| Source | What you collect | Cost | Fidelity |
|---|---|---|---|
| 🔴 **Real Robot** | Teleoperated demos, sensor readings, real camera RGB/depth | Slow & expensive | Ground truth ✅ |
| 🟦 **Simulator** | Millions of RL rollouts, synthetic images, auto-labeled data | Fast & free | Approximation ⚠️ |
| 🔀 **Mixed** | Pre-train on sim data, fine-tune on real robot demos | Balanced | Best of both ⭐ |

**Best practice for DOM:** Pre-train vision models on large-scale Isaac Sim rendered data, then fine-tune on real wrist camera images from teleoperation sessions.

---

## 4. Training Models: RL vs VLA

### Reinforcement Learning (RL)

The robot learns by trial-and-error in MuJoCo, getting a reward signal for successful cuts.

- **Reward signal:** Did the knife pass cleanly through the tomato? Was grip force within bounds?
- **Penalties:** Collisions, dropped tomato, excessive cutting force, arm singularities
- **Algorithms:** PPO, SAC, TD-MPC2
- **Requirement:** Accurate simulator + carefully designed reward function

**DOM use case:** Train arm motion planning policies in MuJoCo; render observations via Isaac Sim for vision-conditioned RL.

### Vision-Language-Action (VLA) Models

Large pre-trained foundation models (RT-2, OpenVLA, π0) that take *camera images + language instructions* and output robot actions.

- **Input:** `"Cut the tomato in half"` + camera image frame
- **Output:** Joint angles or end-effector trajectory deltas
- **Training:** Fine-tune on your combined sim + real demonstration data
- **Strength:** Generalizes to new tomato types, positions, and language-described tasks

**DOM use case:** Isaac Sim generates photorealistic images → feed into VLA fine-tuning pipeline → VLA drives dual arms in real world. Particularly suited for handling tomato variation without explicit reprogramming.

---

## 5. End-to-End Pipeline for DOM

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Real-to-Sim — Build the Environment                │
│  • Scan tomatoes → MuJoCo mesh                              │
│  • Calibrate robot URDF                                     │
│  • Match kitchen layout in Isaac Sim                        │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Data Collection — Sim + Real                       │
│  • RL rollouts in MuJoCo (millions of episodes)             │
│  • Teleoperation demos on real dual arms (100–200)          │
│  • Isaac Sim renders photorealistic images for both         │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Training — RL and/or VLA                           │
│  • RL policy: trained on MuJoCo state data                  │
│  • VLA: fine-tuned on Isaac Sim renders + real demos        │
│  • Models learn cutting motion + bimanual coordination      │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Sim-to-Real — Deploy to Dual Arms                  │
│  • Transfer policy weights to real robot                    │
│  • Fine-tune with additional real demos if gap persists     │
│  • Iterate: failure → collect more demos → retrain          │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Evaluate on Real Tomatoes 🍅                       │
│  • Test varied sizes, positions, lighting                   │
│  • Failure cases → add demos → close the loop              │
└─────────────────────────────────────────────────────────────┘
```

**Key insight:** The MuJoCo + Isaac Sim hybrid creates a *scalable data flywheel*. The simulator generates unlimited training scenarios; Isaac Sim makes them visually realistic enough for vision models. You are not bottlenecked by how many physical tomatoes can be cut in the lab.
