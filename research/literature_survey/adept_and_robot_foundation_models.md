# Literature Survey & Future Work: Pre-Trained Foundation Dexterity and the Unified Robotic OS ("Android for Robots")

**Author:** Master's Student, Control Science and Engineering  
**Affiliation:** DEX-ROB Lab, School of Electrical and Automation Engineering, Tianjin University  
**Date:** September 2026  
**Related Project:** Vision-Tactile Fusion for Adaptive Cutting of Deformable Foods  

---

## 1. Executive Summary & Research Motivation

In modern artificial intelligence, the paradigm has shifted decisively from training single-task models from scratch to **pre-training foundational representations** (e.g., LLMs, vision transformers) and **post-training/fine-tuning them for downstream tasks**. 

Historically, physical robotics has lagged behind this paradigm. In both academic labs and industry, when an engineer trains a robot to perform a new manipulation task (such as peg insertion, cloth folding, or culinary slicing), the control policy is almost invariably trained **completely from scratch**. Consequently, millions of compute cycles and weeks of engineering time are wasted rediscovering basic motor coordination—such as reaching toward an object, coordinating multi-joint trajectories without self-collision, and stabilizing contact grasp forces.

This document synthesizes:
1. **The ADEPT Framework (NVIDIA & UMich, CoRL 2026)**: The seminal demonstration of pre-training foundational motor dexterity on generic reposing and post-training specialists for contact-rich downstream manipulation without policy collapse.
2. **The Open-Source Foundation Model & "Robot OS" Ecosystem**: An analysis of current open-source initiatives (Hugging Face LeRobot, Octo, OpenVLA, OpenMind OM1, and NVIDIA Isaac Lab) striving toward an *"Android for Robotics"*.
3. **Strategic Integration as Future Work for DEX-ROB Lab**: How the concepts of foundational motor priors, geometric fabrics, and visuo-tactile distillation can be incorporated into future stages of the Master's research on autonomous culinary cutting and dexterous manipulation.

---

## 2. Core Paper Breakdown: ADEPT (CoRL 2026)

* **Full Title:** *ADEPT: Accelerating Dexterity via Pre-Training and Post-Training using Reinforcement Learning*
* **Authors:** Jayjun Lee, Jessica Yin, Asif Rana, Nicholas Blauch, Sam Mady, Mohak Bhardwaj, Nima Fazeli, Nathan Ratliff, Karl Van Wyk, Ankur Handa
* **Affiliations:** NVIDIA Research & University of Michigan (Michigan Robotics)
* **Venue:** Conference on Robot Learning (CoRL) 2026
* **Paper / ArXiv:** [arXiv:2608.19182](https://arxiv.org/abs/2608.19182)
* **Project Page:** [https://adept-dexterity.github.io/](https://adept-dexterity.github.io/)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Stage 1: Pre-Training in Simulation (Isaac Gym)                         │
│ Generic Object Reposing (16 primitives) → Foundational Motor Prior      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Stage 2: Structured RL Post-Training                                    │
│ 1. BC Actor Distillation  ──►  2. Critic Warm-up  ──►  3. Conservative   │
│ (transfer observation space)   (calibrate value fn)    PPO (100x low LR)│
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Stage 3: Full Joint Configuration Space Geometric Fabric                │
│ Second-order dynamical safety layer (collision & joint-limit repulsion) │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Stage 4: Two-Stage Teacher-Student Distillation                         │
│ Stage 1: ResNet + 8-Keypoint Pose Loss ──► Stage 2: Downstream BC       │
│ Zero-shot deployment with Stereo RGB + 5x Fingertip Tactile Maps        │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.1 The Core Problem Solved
When researchers attempt to take a pre-trained reinforcement learning policy and fine-tune it on a contact-rich downstream task, the policy exhibits **catastrophic policy collapse**—dropping to 0% success within a few gradient updates. The authors trace this failure to:
1. **Reward Mismatch**: Transitioning from a generic reposing reward to a task-specific objective.
2. **Observation Shift**: Introduction of downstream-specific signals (e.g., receptacle pose and contact forces).
3. **Critic Desynchronization**: An uncalibrated critic feeds wildly inaccurate advantage estimates to PPO, causing large, destructive policy updates.

### 2.2 The ADEPT 3-Step Post-Training Recipe
ADEPT stabilizes transfer without requiring complex explicit KL or EWC regularization penalties:
1. **Behavior-Cloning (BC) Actor Distillation (40k iterations)**: Distills the pre-trained actor into a new downstream actor that natively accepts the expanded observation space.
2. **Critic Warm-Up (20 epochs, ~1M steps per GPU)**: Freezes the actor and trains only the new critic against the downstream reward, ensuring accurate value estimates before any policy gradients are applied.
3. **Conservative PPO Updates**: Unfreezes both networks and executes joint PPO updates with a **substantially reduced learning rate** ($1 \times 10^{-3} \to 1 \times 10^{-5}$) and tightened clipping ($\epsilon = 0.05$).

### 2.3 Joint Configuration Space Geometric Fabrics
To prevent motor limit violations and self-collisions while retaining the complete dexterity of high-DoF systems, ADEPT introduces a full Cspace **Geometric Fabric**:
$$\mathbf{M}_{f}(\mathbf{q}_{f},\dot{\mathbf{q}}_{f})\,\ddot{\mathbf{q}}_{f}+\mathbf{f}_{f}(\mathbf{q}_{f},\dot{\mathbf{q}}_{f})+\mathbf{f}_{\pi}(\mathbf{a})=\mathbf{0}$$
* Unlike prior works that artificially compress hand movement into a 5D PCA grasp subspace, this fabric operates across **all 23 to 29 joints independently**.
* Provides mathematical collision avoidance and joint-limit repulsion while exposing 100% of the kinematic degree-of-freedom space to the RL policy.
* The identical fabric runs in simulation and on physical hardware at 1 kHz via an admittance controller, closing the controller reality gap.

### 2.4 Visuo-Tactile Student Distillation
* **Teacher**: Runs with privileged simulation state (ground truth 3D meshes, contact forces).
* **Student**: Runs on physical hardware using only two 320×240 RGB camera feeds and five vision-based fingertip tactile depth maps (**TacMap** + **SaTA FiLM** spatial anchoring).
* **Two-Stage Distillation**: Stage 1 isolates perception by supervising an auxiliary 8-keypoint 3D bounding-box pose loss; Stage 2 fine-tunes policy actions on top of the pre-trained encoder.

### 2.5 Quantitative Benchmarks & Results
* **Hardware Embodiments**:
  * 23-DoF Kuka iiwa7 + Allegro 4-fingered hand (stereo RGB).
  * 29-DoF Flexiv Rizon + Sharpa 5-fingered hand (stereo RGB + 5x fingertip tactile sensors).
* **Sample Efficiency**: Pre-training takes 8B steps (amortized once); downstream post-training takes only **3B steps** (compared to 9B+ steps from scratch, which rarely succeeded).
* **Execution Speed**: Solves long-horizon pick, reorient, and insert tasks in **5–10 seconds** (a **2× to 14× speedup** over traditional parallel-jaw gripper baselines that require 20–70 seconds and external regrasp fixtures).
* **Impact of Touch**: On the asymmetric FMB square-and-round peg, tactile sensing increased real-world zero-shot success from **3/10 (vision only) to 8/10 (visuo-tactile)** by eliminating grasp hesitation and contact ambiguity.

---

## 3. Open-Source Ecosystem: Building Blocks of an "Android for Robots"

To realize a unified, scalable robotics platform where engineers build upon pre-trained foundation libraries rather than training from scratch, five primary open-source projects represent the current state of the art:

| Project | Organization / Creators | Primary Focus | Repository / Link |
| :--- | :--- | :--- | :--- |
| **LeRobot** | Hugging Face | Pre-trained imitation learning models (ACT, Diffusion Policy), standardized hardware interfaces, and shared datasets | [github.com/huggingface/lerobot](https://github.com/huggingface/lerobot) |
| **Octo** | Berkeley, Stanford, CMU, Google | Generalist 93M-parameter diffusion policy pre-trained on the Open X-Embodiment dataset (800k+ trajectories across 22 embodiments) | [github.com/octo-models/octo](https://github.com/octo-models/octo) |
| **OpenVLA** | Stanford, Berkeley | 7B open-source Vision-Language-Action (VLA) foundation model supporting parameter-efficient fine-tuning (LoRA) on consumer GPUs | [github.com/openvla/openvla](https://github.com/openvla/openvla) |
| **OpenMind OM1** | OpenMind AGI | Open-source, hardware-agnostic AI operating system ("Android for Robots") with modular runtime and hardware abstraction layer (HAL) | [github.com/OpenMind/OM1](https://github.com/OpenMind/OM1) |
| **Isaac Lab** | NVIDIA | Modular open-source framework for large-scale GPU-accelerated robot learning and sim-to-real reinforcement learning | [github.com/isaac-sim/IsaacLab](https://github.com/isaac-sim/IsaacLab) |

### 3.1 Hugging Face LeRobot
LeRobot is designed to democratize robot learning by creating the *"Hugging Face Hub for Physical Robotics"*. It standardizes:
* Data collection pipelines for low-cost arms (SO-100, SO-101) up to advanced humanoids (Unitree G1).
* Plug-and-play implementations of state-of-the-art behavioral cloning algorithms (Action Chunking with Transformers, Diffusion Policy).
* Direct community sharing of pre-trained skill weights.

### 3.2 Octo & OpenVLA (Embodied Foundation Models)
* **Octo**: Proved that a single transformer-based policy can be pre-trained across dozens of diverse robot morphologies (parallel-jaw grippers, multi-fingered hands, mobile bases) and fine-tuned downstream with minimal demonstration data.
* **OpenVLA**: Bridges multimodal language understanding with direct 7-DoF motor tokenization, enabling robots to interpret natural language instructions (*"slice the ripe tomato thinly"*) directly from camera feeds.

### 3.3 OpenMind OM1
OpenMind OM1 addresses the operating system layer:
* Decouples high-level multimodal reasoning (LLMs, vision models) from specific embedded motor drivers.
* Establishes a standard Hardware Abstraction Layer (HAL) so that applications written for one robot can deploy across different physical platforms.

---

## 4. Synthesis: Roadmap as Future Work for DEX-ROB Lab

Integrating the insights from ADEPT, LeRobot, and open foundation models directly enriches our laboratory's research trajectory in deformable object manipulation and culinary automation.

```
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 1: Near-Term Master's Research (Years 1-2)                       │
│ • Vision-Tactile Fusion for Deformable Food Cutting                    │
│ • 1 kHz Impedance Regulation & Phase Switching (TacBlade)              │
│ • Benchmarked on Franka Emika Panda / Kinova Gen3                     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 2: Skill Library Packaging (Year 2)                              │
│ • Package cutting, slicing, and peeling as modular skill primitives   │
│ • Export datasets & models in LeRobot / Open X-Embodiment formats      │
│ • Create standardized benchmark tasks for culinary tool interaction   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 3: Foundation Model Scaling & ADEPT Post-Training (Year 3)       │
│ • Pre-train culinary manipulation priors in Isaac Lab                  │
│ • Use ADEPT stable post-training (BC + Critic Warm-up + low-LR PPO)    │
│ • Distill into student policies operating from onboard RGB + tactile   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Phase 4: Cross-Platform Deployment & High-DoF Systems (Long-Term)      │
│ • Transfer skills to DEX-ROB Lab platforms (DexCatch dual-arm,        │
│   Astribot S1 high-speed manipulator, multi-fingered hands)            │
│ • Contribute to a unified, open-source dexterous manipulation OS       │
└────────────────────────────────────────────────────────────────────────┘
```

### Strategic Milestones:
1. **From Isolated Control to Modular Skills**: In addition to traditional hybrid impedance controllers, record and format knife-food interaction datasets according to the **LeRobot** and **Open X-Embodiment** schemas, allowing the broader research community to use our tactile cutting data.
2. **Adopting the ADEPT Adaptation Recipe**: When applying reinforcement learning to tool manipulation (such as slicing heterogeneous fruits with tough skins and soft pulps), utilize ADEPT’s **critic warm-up and conservative learning rate decay** to avoid policy collapse during sim-to-real transfer.
3. **Hardware-Agnostic Retargeting**: In alignment with Prof. Shan An's work on *Open TeleDex* (TripleAny teleoperation), leverage unified robot HAL concepts to ensure that cutting and manipulation policies trained on single-arm setups can transfer to the lab’s dual-arm humanoid platforms.

---

## 5. References & Bibliographic Citations

1. **ADEPT (CoRL 2026)**: J. Lee, J. Yin, A. Rana, N. Blauch, S. Mady, M. Bhardwaj, N. Fazeli, N. Ratliff, K. Van Wyk, and A. Handa. *"ADEPT: Accelerating Dexterity via Pre-Training and Post-Training using Reinforcement Learning."* 9th Conference on Robot Learning (CoRL), 2026. [arXiv:2608.19182](https://arxiv.org/abs/2608.19182).
2. **LeRobot**: Hugging Face Robotics Team. *"LeRobot: State-of-the-art Machine Learning for Real-World Robotics in PyTorch."* GitHub repository, 2024–2026. [github.com/huggingface/lerobot](https://github.com/huggingface/lerobot).
3. **Octo**: Octo Model Team, et al. *"Octo: An Open-Source Generalist Robot Policy."* Robotics: Science and Systems (RSS), 2024. [github.com/octo-models/octo](https://github.com/octo-models/octo).
4. **OpenVLA**: M. Kim, K. Pertsch, et al. *"OpenVLA: An Open-Source Vision-Language-Action Model."* arXiv preprint arXiv:2406.09246, 2024. [github.com/openvla/openvla](https://github.com/openvla/openvla).
5. **OpenMind OM1**: OpenMind AGI Team. *"OM1: An Open-Source Operating System for Intelligent Machines."* 2025–2026. [github.com/OpenMind/OM1](https://github.com/OpenMind/OM1).
6. **Isaac Lab**: NVIDIA Isaac Lab Team. *"Isaac Lab: Modular Framework for GPU-Accelerated Robot Learning."* GitHub repository, 2024–2026. [github.com/isaac-sim/IsaacLab](https://github.com/isaac-sim/IsaacLab).
7. **Geometric Fabrics**: K. Van Wyk, A. Handa, V. Makoviychuk, et al. *"Geometric Fabrics: A Safe Guiding Medium for Policy Learning."* IEEE ICRA, 2024.
8. **Open TeleDex**: X. Chi, C. Zhang, Y. Su, L. Dou, F. Yang, J. Zhao, H. Zhou, X. Jia, Y. Zhou, and S. An. *"Open TeleDex: A Hardware-Agnostic Teleoperation System for Imitation Learning based Dexterous Manipulation."* arXiv preprint arXiv:2510.14771, 2025.
