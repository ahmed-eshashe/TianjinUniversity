# Beginner's Guide: Robotics RL Setup & Workflow (Paper 1)

**Target Audience:** Robotics Beginners & DEX-ROB Lab Master's Students  
**Focus:** Minimal 4-Tool Stack, Intuitive Mental Model, and Step-by-Step Setup  
**Target Project:** Adaptive Tomato Slicing via Traditional RL (PPO / SkRL in Isaac Lab)

---

## 1. The Mental Model: How Robotics RL Actually Works

If you come from computer science or machine learning, robotics can feel overwhelming because of the jargon (URDF, kinematics, torques, impedance, ROS). **Strip that away — robotics RL works just like training an AI bot in a video game:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE ROBOTICS RL LEARNING LOOP                       │
│                                                                             │
│   1. The Game World (Simulator: Isaac Lab / Isaac Sim)                      │
│      A virtual 3D room running on your GPU where physics, knife-blade       │
│      contacts, and squashy tomatoes exist.                                  │
│      It asks: "Where is the blade? What force is pressing on it?"           │
│                             │                                               │
│                             ▼ (Observation Vector S_t ∈ ℝ^33)               │
│   2. The Brain (Policy Network: SkRL / PPO in PyTorch)                      │
│      A simple neural network. It reads the sensory numbers and says:        │
│      "Push down 2 mm and slice forward 10 mm."                              │
│                             │                                               │
│                             ▼ (Action Vector A_t ∈ ℝ^6)                     │
│   3. The Safety Spring (Impedance Controller)                               │
│      Turns the brain's decision into safe motor behavior. If the tomato     │
│      skin pops suddenly, it softens the push so the tomato is not crushed.  │
│                             │                                               │
│                             ▼ (Feedback / Score)                            │
│   4. The Scoreboard (Reward Function R_t)                                   │
│      Clean cut without squishing? +10 points. Crushed into juice? -50.      │
│      Repeat 500,000 times in parallel until the policy masters it.          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Minimal Tool Checklist (Only 4 Things!)

Do **not** install 20 different packages. For Paper 1, you only need four core tools:

| # | Tool | Plain-English Role | Why It's Essential |
|---|---|---|---|
| **1** | **Ubuntu 22.04 (via WSL2)** | The Operating System layer | 95% of modern robotics simulators and drivers run natively and stably on Linux. |
| **2** | **NVIDIA Isaac Lab** | The Physics Simulator | Simulates 512–1024 robot arms cutting tomatoes at the same time directly on your RTX GPU. |
| **3** | **PyTorch + SkRL** | The Learning Library (PPO) | Pre-written, bug-free Python code that trains the neural network policy. |
| **4** | **Weights & Biases (WandB)** | The Live Scoreboard Dashboard | A free website where you watch live graphs of your robot's score going up as it learns. |

> **What about ROS 2?**  
> ROS 2 connects code to *physical metal robot arms* in DEX-ROB Lab. You do **not** need it on Day 1. In robotics RL, 95% of your time is spent in simulation first!

---

## 3. Step-by-Step Setup Guide on Windows 11 (Laptop)

**Hardware Specs:** Intel Core i7-14650HX, NVIDIA GeForce RTX 5060 Laptop GPU (8GB VRAM), 16GB RAM.

### Step 1: Install WSL2 (Ubuntu 22.04 LTS)
Open **PowerShell as Administrator** on Windows and run:
```powershell
wsl --install -d Ubuntu-22.04
```
* Restart your laptop if prompted.
* When Ubuntu opens, set your Linux username and password.

### Step 2: Configure WSL2 Memory Limit
WSL2 can consume all 16 GB of RAM if unrestricted. Create or edit `C:\Users\<YourUser>\.wslconfig` in Windows:
```ini
[wsl2]
memory=12GB
processors=12
swap=8GB
```
*This reserves 12 GB for simulation and 4 GB for Windows, preventing crashes.*

### Step 3: Install Miniconda inside Ubuntu
Open your Ubuntu terminal and run:
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda
eval "$($HOME/miniconda/bin/conda shell.bash hook)"
conda init
source ~/.bashrc
```

Create an isolated environment:
```bash
conda create -n isaaclab python=3.10 -y
conda activate isaaclab
```

### Step 4: Install Isaac Sim & Isaac Lab
NVIDIA provides a complete setup script:
```bash
# Clone the repository
git clone https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab

# Run the automated installer
./isaaclab.sh --install
```

### Step 5: Install SkRL and Experiment Tracking
In the same `isaaclab` conda environment:
```bash
pip install skrl["torch"] wandb hydra-core
```

---

## 4. Verification: Your First Robot Simulation Test

To verify everything is working properly on your GPU, run these two quick tests:

### Test 1: Verify Simulation Engine
```bash
./isaaclab.sh -p source/standalone/tutorials/00_sim/create_empty.py
```
*If a 3D window opens with a ground plane and lighting, your physics engine is working.*

### Test 2: Run a Franka Arm Reach Policy
```bash
./isaaclab.sh -p source/standalone/workflows/skrl/train.py --task Isaac-Reach-Franka-v0 --headless
```
*This verifies that PyTorch, GPU CUDA, PhysX 5, and SkRL PPO are learning together.*

---

## 5. 3-Stage Beginner Learning Roadmap

| Stage | Focus | Practical Action |
|---|---|---|
| **Stage 1 (Week 1)** | **Familiarization** | Run pre-built tutorial scripts. Learn how an Isaac Lab script loads an asset (`RigidObjectCfg`). |
| **Stage 2 (Weeks 2–3)** | **The Tomato Scene** | Spawn a table, import the tomato 3D mesh, attach the knife to the robot wrist, and test moving it downward. |
| **Stage 3 (Weeks 4–6)** | **RL Training** | Hook up the reward function ($R_{pen}, P_{crush}, P_{slam}$) and let PPO train for 2–4 hours until it slices cleanly. |
