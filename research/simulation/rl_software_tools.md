# Software Tools for RL-Based Dual Arm Tomato Cutting (DOM)

**Paper scope:** Traditional RL in simulation → Sim-to-Real transfer → Dual arm cutting robot  
**Simulator:** Isaac Lab (recommended for RL at scale)  
**Date:** September 2026

---

## Overview: The Full Software Stack

The RL pipeline for DOM spans seven layers. Each tool below is categorized by its layer, role, and how it connects to the next.

```
┌─────────────────────────────────────────────────────┐
│  Layer 7: Monitoring & Experiment Management        │  WandB, TensorBoard, Hydra
├─────────────────────────────────────────────────────┤
│  Layer 6: RL Training Framework                     │  SkRL, RSL-RL, CleanRL, SB3
├─────────────────────────────────────────────────────┤
│  Layer 5: Deep Learning & Policy Network            │  PyTorch, CUDA
├─────────────────────────────────────────────────────┤
│  Layer 4: Perception / Vision                       │  YOLO, OpenCV, RealSense SDK
├─────────────────────────────────────────────────────┤
│  Layer 3: Simulation Environment                    │  Isaac Lab, Isaac Sim, MuJoCo
├─────────────────────────────────────────────────────┤
│  Layer 2: Robot Middleware & Control                │  ROS2, MoveIt2, ros2_control
├─────────────────────────────────────────────────────┤
│  Layer 1: System & Development                      │  Python, CUDA, Docker, Git
└─────────────────────────────────────────────────────┘
```

---

## Layer 1: System & Development Foundation

### Python 3.10+
- **Role:** Primary language for the entire pipeline
- **Why this version:** Isaac Lab and most RL libraries require Python ≥ 3.10; type hinting and `match` statements help with policy code readability
- **Install:** Via Conda (recommended to isolate Isaac Lab dependencies)

### CUDA 12.x
- **Role:** GPU acceleration for physics (PhysX), rendering (RTX), and neural network training
- **Why it matters:** Isaac Lab is GPU-only. Without CUDA, you cannot run parallel environments
- **Install:** NVIDIA CUDA Toolkit — must match your driver version
- **Check:** `nvidia-smi` → confirm GPU + driver; `nvcc --version` → confirm CUDA compiler

### Conda / Mamba
- **Role:** Environment management — isolates Isaac Lab, ROS2, and RL library dependencies which often conflict
- **Recommended layout:**
  ```
  conda env: isaaclab    ← Isaac Lab + SkRL + PyTorch + WandB
  conda env: ros2        ← ROS2 Jazzy + MoveIt2 + robot drivers
  ```
- **Mamba** is a drop-in Conda replacement that resolves dependencies 10× faster

### Git + GitHub
- **Role:** Version control for all code, reward functions, configs, and experiment logs
- **Remote:** Already configured at `github.com/ahmed-eshashe/TianjinUniversity`
- **Branching strategy:** `main` (stable) → `dev/rl-training` (experiments) → `feature/reward-shaping`

### Docker (optional but recommended)
- **Role:** Containerize the Isaac Lab environment for reproducibility and cluster deployment
- **NVIDIA Container Toolkit** enables GPU passthrough inside Docker containers
- **Use case:** Submit RL training jobs to a university HPC cluster without environment conflicts

---

## Layer 2: Robot Middleware & Control

### ROS2 (Jazzy Jalisco — LTS)
- **Role:** The communication backbone between all real-robot components
- **What it handles:**
  - Joint state publishing from robot arms
  - Camera image streams (RGB, depth)
  - Force-torque sensor data
  - Action command dispatch to controllers
- **Key packages:**
  - `robot_state_publisher` — publishes TF tree from URDF
  - `ros2_control` — hardware abstraction layer for joint controllers
  - `sensor_msgs`, `geometry_msgs`, `trajectory_msgs` — standard message types
- **Note:** ROS2 is used at **real-robot deployment time**, not during RL training in Isaac Lab

### MoveIt2
- **Role:** High-level motion planning — computes collision-free joint trajectories
- **DOM use cases:**
  - Pre-grasp approach trajectories (move arm to above tomato)
  - Knife retraction after cut
  - Safe home position recovery
- **Works with:** OMPL (sampling-based planning), STOMP, PILZ industrial planner
- **Integration:** Receives goal poses from the RL policy output → plans joint trajectory → sends to `ros2_control`

### ros2_control
- **Role:** Real-time joint-level controller interface between ROS2 and physical robot hardware
- **Provides:** Position, velocity, and effort controllers per joint
- **For DOM:** Impedance controller plugin for force-compliant cutting motion

### Robot-Specific Driver
- **Depends on your arm brand:**
  | Robot | Driver Package |
  |---|---|
  | Universal Robots (UR5e/UR10e) | `ur_robot_driver` |
  | Franka Panda | `franka_ros2` |
  | JACO / Kinova | `kinova_ros2` |
  | Custom arm | Custom `ros2_control` hardware interface |
- **Role:** Translates ROS2 joint commands into the arm's proprietary protocol

---

## Layer 3: Simulation Environment

### Isaac Lab ⭐ (Primary — recommended for RL)
- **Website:** https://isaac-sim.github.io/IsaacLab/
- **Role:** Unified robot learning framework — wraps Isaac Sim with RL-ready APIs
- **What it gives you:**
  - Gymnasium-compatible environment interface (`gym.Env`)
  - GPU-parallel environment manager (run 2048+ envs simultaneously)
  - Built-in domain randomization (randomize tomato mass, friction, lighting per episode)
  - Pre-built robot assets (UR5, Franka, etc.) with USD format
  - Action and observation space definitions
  - Reward composition utilities
- **Key classes you will implement:**
  - `DirectRLEnv` or `ManagerBasedRLEnv` — your custom cutting environment
  - `RewardManager` — define cutting success reward, force penalty, coordination reward
  - `ObservationManager` — define what the policy sees (joint states, ee pose, tomato pose)
  - `EventManager` — randomize tomato position, size, friction at episode reset

### Isaac Sim (underlies Isaac Lab)
- **Role:** Photorealistic rendering engine + PhysX 5 physics
- **What it provides to Isaac Lab:**
  - RTX ray-traced camera observations (if using vision-based RL)
  - USD scene management (load robot + tomato + table assets)
  - Contact force sensors
  - RigidPrim / GeometryPrim APIs for object manipulation
- **When you interact with it directly:** When building custom sensors, importing robot USD models, or debugging scene setup visually

### MuJoCo (supplementary)
- **Role:** Alternative physics backend for prototyping reward functions before moving to Isaac Lab
- **When to use:** Quick algorithmic tests on a simple single-arm cutting task before scaling to dual-arm Isaac Lab
- **Python API:** `import mujoco` — direct Python bindings from DeepMind
- **MJX:** MuJoCo on JAX for GPU-accelerated physics (experimental, catching up to Isaac Lab)
- **Gymnasium wrapper:** `gymnasium-robotics` provides MuJoCo-based manipulation envs as reference

### USD Composer / Isaac Sim GUI
- **Role:** Visual scene editor for building and validating your simulation environment
- **Use:** Load robot URDF → convert to USD → place tomato mesh → verify collision geometry → export to Isaac Lab training script

---

## Layer 4: Perception & Vision

### YOLO v11 / YOLO-World
- **Role:** Real-time tomato detection and bounding box estimation from RGB camera
- **Framework:** Ultralytics (`pip install ultralytics`)
- **DOM use:** At deployment on real robot — detect tomato position in camera frame, pass to RL policy as observation or to MoveIt2 as goal pose
- **Training data:** Fine-tune on a small tomato dataset; Isaac Sim can generate synthetic labeled training images to augment real data

### Intel RealSense SDK / SDK2
- **Role:** Driver and API for RealSense depth cameras (D435, D455) mounted on robot wrists and overhead
- **Outputs:** Aligned RGB + depth frames, point clouds
- **ROS2 package:** `realsense2_camera` — publishes camera topics automatically

### OpenCV
- **Role:** Image preprocessing, coordinate transforms, HSV-based tomato segmentation (as backup to YOLO), ArUco marker tracking for workspace calibration
- **Python:** `pip install opencv-python`

### Open3D (optional)
- **Role:** Point cloud processing — reconstruct 3D tomato pose from depth image for more accurate RL observation
- **Use:** Convert depth frame → point cloud → fit bounding volume → extract centroid + orientation

---

## Layer 5: Deep Learning & Policy Network

### PyTorch
- **Role:** Neural network framework for the RL policy (actor) and value function (critic)
- **Why PyTorch over TensorFlow:** Isaac Lab, SkRL, and most modern RL libraries are PyTorch-native
- **Key components for DOM:**
  - `torch.nn.MLP` — standard feedforward policy for state-based RL
  - `torch.nn.LSTM` / Transformer — if policy needs memory (e.g., multi-step cutting state)
  - `torch.distributions` — action sampling for stochastic policies

### Policy Network Architecture (recommended starting point)

```
Observation vector (joint positions × 2 arms, ee poses, tomato pose, F/T readings)
        ↓
MLP: [512 → 256 → 128]  with ELU activations
        ↓
Actor head → mean + log_std → Gaussian action distribution → joint deltas
Critic head → scalar value estimate
```

For vision-based observation extension: prepend a CNN or ViT encoder before the MLP.

### torchrl (optional)
- **Role:** PyTorch-native RL data structures (TensorDict, ReplayBuffer, rollout collectors)
- **Advantage:** Tight integration with PyTorch autograd; cleaner than manual buffer management

---

## Layer 6: RL Training Framework

### SkRL ⭐ (Recommended)
- **Website:** https://skrl.readthedocs.io/
- **Role:** Clean, modular RL library built natively for Isaac Lab
- **Algorithms available:** PPO, SAC, TD3, DDPG, TRPO, RPO
- **Why SkRL for DOM:**
  - Official Isaac Lab integration (drop-in trainer)
  - Handles multi-agent / multi-arm setups
  - Supports both state-based and vision-based observation spaces
  - Clean separation of agent, memory, and trainer components
- **DOM algorithm:** Start with **PPO** (stable, well-understood) → graduate to **SAC** (sample efficient, off-policy)

### RSL-RL
- **Role:** Lightweight, fast RL trainer originally developed for legged robot locomotion (ETH Zurich)
- **Algorithms:** PPO only
- **When to use:** Maximum training speed for large-scale parallel PPO experiments
- **Limitation:** Less flexible than SkRL for custom reward structures

### Stable-Baselines3 (SB3)
- **Role:** Reliable reference implementations of PPO, SAC, TD3
- **When to use:** Prototyping on non-Isaac-Lab environments (e.g., quick MuJoCo tests)
- **Limitation:** Not optimized for GPU-parallel Isaac Lab environments

### CleanRL
- **Role:** Single-file RL algorithm implementations, very readable
- **When to use:** Understanding exactly what PPO/SAC is doing; educational reference when debugging training instability
- **Website:** https://cleanrl.dev

---

## Layer 7: Monitoring, Config & Experiment Management

### Weights & Biases (WandB) ⭐
- **Role:** Experiment tracking — logs reward curves, episode lengths, loss values, video rollouts, hyperparameters
- **Why essential:** RL training produces hundreds of metrics; you need to compare reward curves across different reward function designs
- **DOM use:** Log per-episode cutting success rate, mean force applied, bimanual sync error
- **Integration:** `import wandb; wandb.log({"reward": r, "cut_success": s})`

### TensorBoard
- **Role:** Alternative to WandB, local-only, no account needed
- **Use:** Quick local monitoring during development; WandB for final experiment comparisons

### Hydra (by Meta)
- **Role:** Configuration management — define all hyperparameters in YAML, override from CLI
- **Why critical for RL:** Reward weights, learning rates, network architecture, domain randomization ranges all need to be versioned and swept
- **Example:**
  ```bash
  python train.py rl.lr=3e-4 reward.cut_weight=1.0 reward.force_penalty=0.1
  ```
- **Hydra Optuna Sweeper:** Automatic hyperparameter search (learning rate, reward weights)

### Optuna
- **Role:** Hyperparameter optimization — automatically find the best reward weights, learning rate, network size
- **Integration:** Pairs with Hydra for systematic sweeps
- **DOM use:** Sweep over `cut_success_weight`, `bimanual_sync_penalty`, `force_regularization` to find the optimal reward function

---

## Summary: Tool Decisions at a Glance

| Decision | Chosen Tool | Reason |
|---|---|---|
| Simulation platform | **Isaac Lab** | GPU-parallel RL, 100× faster than MuJoCo+Isaac Sim for RL |
| RL algorithm (start) | **PPO** via SkRL | Stable, well-understood, good for continuous control |
| RL algorithm (later) | **SAC** via SkRL | Sample-efficient, better for complex manipulation |
| Policy network | **MLP in PyTorch** | State-based RL; add CNN if switching to vision obs |
| Robot middleware | **ROS2 Jazzy** | Standard, LTS, works with all major robot arms |
| Motion planning | **MoveIt2** | Collision-free pre-grasp trajectories |
| Object detection | **YOLOv11** | Real-time tomato detection for real robot deployment |
| Experiment tracking | **WandB** | Reward curve comparison across reward function variants |
| Config management | **Hydra** | Version all hyperparameters; enable CLI sweeps |
| Environment management | **Conda** | Isolate Isaac Lab / ROS2 dependency conflicts |
| Version control | **Git + GitHub** | Already set up at `ahmed-eshashe/TianjinUniversity` |

---

## Installation Order (Recommended)

```bash
# 1. CUDA + NVIDIA drivers (system level)
#    → verify: nvidia-smi

# 2. Conda / Mamba
conda create -n isaaclab python=3.10
conda activate isaaclab

# 3. Isaac Lab (pulls Isaac Sim, PhysX, PyTorch)
git clone https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab && ./isaaclab.sh --install

# 4. RL Framework
pip install skrl["torch"]

# 5. Experiment tracking
pip install wandb hydra-core optuna

# 6. Vision tools
pip install ultralytics opencv-python open3d

# 7. ROS2 (separate environment — Ubuntu only)
# → Follow: https://docs.ros.org/en/jazzy/Installation.html
# → Then: sudo apt install ros-jazzy-moveit
```

> **Note:** Isaac Lab currently requires **Ubuntu 22.04** for full support. On Windows, use WSL2 (Ubuntu 22.04) for the simulation stack. ROS2 also runs best on native Ubuntu or WSL2.

---

## Key Papers to Read (Algorithms & Tools)

| Paper | Relevance |
|---|---|
| Schulman et al. (2017) — *Proximal Policy Optimization* | PPO algorithm used for training |
| Haarnoja et al. (2018) — *Soft Actor-Critic* | SAC algorithm for sample efficiency |
| Andrychowicz et al. (2020) — *Learning Dexterous In-Hand Manipulation* | Domain randomization at scale (OpenAI) |
| Rudin et al. (2022) — *Learning to Walk in Minutes* | RSL-RL + Isaac Lab philosophy |
| Tobin et al. (2017) — *Domain Randomization for Transferring Deep Neural Networks* | Sim-to-Real technique |
