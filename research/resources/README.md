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

## 2. Core Open-Source Repositories & Foundation Platforms

The following open-source frameworks represent the cutting edge of the *"Android for Robots"* and generalist foundation model paradigm:

### 1. [Hugging Face LeRobot](https://github.com/huggingface/lerobot)
* **GitHub:** `https://github.com/huggingface/lerobot`
* **Hugging Face Hub:** `https://huggingface.co/lerobot`
* **Role:** Standardized PyTorch implementations of state-of-the-art imitation learning (ACT, Diffusion Policy), hosted pre-trained weights, and shared real-world robotics datasets.

### 2. [Octo (Open X-Embodiment)](https://github.com/octo-models/octo)
* **GitHub:** `https://github.com/octo-models/octo`
* **Project Page:** `https://octo-models.github.io/`
* **Role:** Generalist 93M-parameter diffusion policy pre-trained across 800k+ trajectories and 22 robot types. Used to bootstrap new manipulation tasks without starting from scratch.

### 3. [OpenVLA](https://github.com/openvla/openvla)
* **GitHub:** `https://github.com/openvla/openvla`
* **Project Page:** `https://openvla.github.io/`
* **Role:** 7-billion parameter open-source Vision-Language-Action (VLA) foundation model. Connects natural language prompts (*"slice the tomato"*) to robot control, fine-tunable on consumer GPUs (LoRA).

### 4. [OpenMind OM1](https://github.com/OpenMind/OM1)
* **GitHub:** `https://github.com/OpenMind/OM1`
* **Website:** `https://openmind.com`
* **Role:** Open-source, hardware-agnostic AI operating system ("Android for Robots"). Modular runtime and Hardware Abstraction Layer (HAL) decoupling AI brains from physical robot hardware.

### 5. [NVIDIA Isaac Lab](https://github.com/isaac-sim/IsaacLab)
* **GitHub:** `https://github.com/isaac-sim/IsaacLab`
* **Documentation:** `https://isaac-sim.github.io/IsaacLab/`
* **Role:** Unified modular framework for GPU-accelerated robot learning and reinforcement learning in Isaac Sim, powering large-scale multi-environment simulation.

---

## 3. Two-Paper Master's Thesis Strategy

Our research program directly bridges classical contact mechanics with modern pre-trained foundation models:

1. **Paper 1 (Year 2 — IEEE RA-L / IROS 2028)**:  
   * **Topic:** *Adaptive Slicing of Deformable Foods via On-Tool Visuo-Tactile Sensing and Traditional RL/Impedance Control*.  
   * **Focus:** Establishing the foundational physical dynamics: sensorized blade (TacBlade), fracture transition mechanics, 1 kHz impedance regulation, and baseline RL/imitation policies tested on soft foods (tomatoes).
2. **Paper 2 (Year 3 — IEEE ICRA / T-RO 2029)**:  
   * **Topic:** *Scaling Deformable Culinary Manipulation via Pre-Trained Foundation Dexterity and Structured Post-Training (The ADEPT Approach)*.  
   * **Focus:** Moving beyond single-object controllers. Pre-training manipulation priors in simulation, utilizing ADEPT’s stable post-training (BC actor distillation + critic warm-up + conservative PPO) and full joint geometric fabrics to generalize cutting across dozens of heterogeneous deformable foods, distilled into onboard visuo-tactile students.
