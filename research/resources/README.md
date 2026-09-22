# Research Resources, Papers & Open-Source Repositories

This directory contains external reference papers, foundational open-source repositories, and technical resources supporting research at **DEX-ROB Lab (Tianjin University)**.

---

## 1. Downloaded Papers & Key Literature (`resources/papers/`)

| File / Citation | Venue | Description | Local Link |
| :--- | :--- | :--- | :--- |
| **ADEPT (Lee et al., 2026)** | **CoRL 2026** | *ADEPT: Accelerating Dexterity via Pre-Training and Post-Training using Reinforcement Learning* (NVIDIA Research & Univ. of Michigan). Foundational reposing pre-training, stable post-training (BC + critic warm-up + low-LR PPO), Cspace geometric fabrics, and visuo-tactile student distillation. | [`papers/ADEPT_CoRL2026.pdf`](papers/ADEPT_CoRL2026.pdf) |
| **Open TeleDex (Chi et al., 2025)** | arXiv:2510.14771 | *Open TeleDex: A Hardware-Agnostic Teleoperation System for Imitation Learning based Dexterous Manipulation* (DEX-ROB Lab, Tianjin University). Low-latency retargeting and cross-embodiment data collection. | [arXiv:2510.14771](https://arxiv.org/abs/2510.14771) |
| **Geometric Fabrics (Van Wyk et al., 2024)** | IEEE ICRA 2024 | *Geometric Fabrics: A Safe Guiding Medium for Policy Learning*. Second-order dynamical system enforcing collision avoidance and joint-limit constraints. | [arXiv:2008.02399](https://arxiv.org/abs/2008.02399) |
| **DexPBT (Petrenko et al., 2023)** | arXiv:2305.12127 | *DexPBT: Scaling up Dexterous Manipulation for Hand-Arm Systems with Population Based Training*. Massive parallel hyperparameter search on GPU clusters. | [arXiv:2305.12127](https://arxiv.org/abs/2305.12127) |

---

## 2. Core Open-Source Repositories & Toolchains

### 2.1 Tools for Paper 1: Traditional Reinforcement Learning & Simulation

These tools form the core operational stack for Paper 1 (Dual-Arm Tomato Slicing with PPO/SAC):

#### 1. [NVIDIA Isaac Lab](https://github.com/isaac-sim/IsaacLab)
* **GitHub:** `https://github.com/isaac-sim/IsaacLab`
* **Documentation:** `https://isaac-sim.github.io/IsaacLab/`
* **Role:** Primary simulation platform. Unified modular framework for GPU-accelerated robot learning in Isaac Sim, running 512–1024 parallel environments on PhysX 5.

#### 2. [SkRL (Reinforcement Learning Library)](https://github.com/Toni-SM/skrl)
* **GitHub:** `https://github.com/Toni-SM/skrl`
* **Documentation:** `https://skrl.readthedocs.io/`
* **Role:** Modular RL library with native Isaac Lab integration. Implements GPU-parallel PPO and SAC trainers, MLP policy architectures, and WandB experiment logging.

#### 3. Essential Traditional RL Reference Sites:
* **[OpenAI Spinning Up in Deep RL](https://spinningup.openai.com/):** Gold-standard theory, equations, and code implementations for PPO, SAC, and continuous action spaces.
* **[Gymnasium Documentation](https://gymnasium.farama.org/):** Standard API for environment interactions (`step()`, `reset()`, spaces).
* **[Weights & Biases (WandB)](https://wandb.ai/):** Real-time monitoring and logging of reward curves and policy convergence.
* **[Hydra Configuration Framework](https://hydra.cc/):** YAML-based hyperparameter configuration and CLI experiment sweeps.

---

### 2.2 Tools for Paper 2: Foundation Models & Generalist Dexterity

These frameworks represent the *"Android for Robots"* and generalist foundation model paradigm for Year 3 scaling:

#### 1. [Hugging Face LeRobot](https://github.com/huggingface/lerobot)
* **GitHub:** `https://github.com/huggingface/lerobot`
* **Role:** Standardized PyTorch implementations of state-of-the-art imitation learning (ACT, Diffusion Policy) and shared real-world datasets.

#### 2. [Octo (Open X-Embodiment)](https://github.com/octo-models/octo)
* **GitHub:** `https://github.com/octo-models/octo`
* **Project Page:** `https://octo-models.github.io/`
* **Role:** Generalist 93M-parameter diffusion policy pre-trained across 800k+ trajectories.

#### 3. [OpenVLA](https://github.com/openvla/openvla)
* **GitHub:** `https://github.com/openvla/openvla`
* **Project Page:** `https://openvla.github.io/`
* **Role:** 7-billion parameter open-source Vision-Language-Action (VLA) foundation model.

#### 4. [OpenMind OM1](https://github.com/OpenMind/OM1)
* **GitHub:** `https://github.com/OpenMind/OM1`
* **Website:** `https://openmind.com`
* **Role:** Open-source, hardware-agnostic AI operating system and Hardware Abstraction Layer (HAL).

---

## 3. Two-Paper Master's Thesis Strategy

Our research program directly bridges classical contact mechanics with modern pre-trained foundation models:

1. **Paper 1 (Year 2 — IEEE RA-L / IROS 2028)**:  
   * **Topic:** *Adaptive Slicing of Deformable Foods via On-Tool Visuo-Tactile Sensing and Traditional RL/Impedance Control*.  
   * **Focus:** Establishing the foundational physical dynamics: sensorized blade (TacBlade), fracture transition mechanics, 1 kHz impedance regulation, and baseline RL/imitation policies tested on soft foods (tomatoes).
2. **Paper 2 (Year 3 — IEEE ICRA / T-RO 2029)**:  
   * **Topic:** *Scaling Deformable Culinary Manipulation via Pre-Trained Foundation Dexterity and Structured Post-Training (The ADEPT Approach)*.  
   * **Focus:** Moving beyond single-object controllers. Pre-training manipulation priors in simulation, utilizing ADEPT’s stable post-training (BC actor distillation + critic warm-up + conservative PPO) and full joint geometric fabrics to generalize cutting across dozens of heterogeneous deformable foods, distilled into onboard visuo-tactile students.
