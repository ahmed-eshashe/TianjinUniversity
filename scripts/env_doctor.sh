#!/usr/bin/env bash
# ==============================================================================
# Research Lab Environment Doctor & System Diagnostics
# DEX-ROB Lab, Tianjin University | Bimanual Deformable Slicing RL
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}==============================================================================${NC}"
echo -e "${BLUE}     DEX-ROB Lab (Tianjin University) - AI Multi-Agent Environment Doctor     ${NC}"
echo -e "${BLUE}==============================================================================${NC}"

# 1. GPU & CUDA
echo -e "\n${YELLOW}[1/6] Checking GPU & CUDA Driver...${NC}"
if command -v nvidia-smi &> /dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)
    GPU_MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader | head -n 1)
    DRIVER=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -n 1)
    echo -e "${GREEN}✓ GPU Detected:${NC} $GPU_NAME ($GPU_MEM), Driver: $DRIVER"
else
    echo -e "${RED}✗ No NVIDIA GPU / nvidia-smi detected!${NC}"
fi

# 2. Python & Conda Environment
echo -e "\n${YELLOW}[2/6] Checking Robotics Python Environment...${NC}"
CONDA_ENV="/home/omen/miniforge3/envs/tianjin-robotics"
if [ -d "$CONDA_ENV" ]; then
    PY_VER=$("$CONDA_ENV/bin/python" --version)
    echo -e "${GREEN}✓ Conda env found:${NC} $CONDA_ENV ($PY_VER)"
else
    echo -e "${RED}✗ Conda env 'tianjin-robotics' not found at $CONDA_ENV${NC}"
fi

# 3. Isaac Sim Installation
echo -e "\n${YELLOW}[3/6] Checking NVIDIA Isaac Sim...${NC}"
ISAAC_SIM_PATH="/home/omen/isaac-sim"
if [ -d "$ISAAC_SIM_PATH" ] && [ -f "$ISAAC_SIM_PATH/isaac-sim.sh" ]; then
    echo -e "${GREEN}✓ NVIDIA Isaac Sim found:${NC} $ISAAC_SIM_PATH (isaac-sim.sh)"
else
    echo -e "${YELLOW}! Isaac Sim not at default path $ISAAC_SIM_PATH${NC}"
fi

# 4. Isaac Lab Installation
echo -e "\n${YELLOW}[4/6] Checking NVIDIA Isaac Lab...${NC}"
ISAAC_LAB_PATH="/home/omen/IsaacLab"
if [ -d "$ISAAC_LAB_PATH" ] && [ -f "$ISAAC_LAB_PATH/isaaclab.sh" ]; then
    echo -e "${GREEN}✓ NVIDIA Isaac Lab found:${NC} $ISAAC_LAB_PATH"
else
    echo -e "${YELLOW}! Isaac Lab not found at $ISAAC_LAB_PATH${NC}"
fi

# 5. ROS 2 Installation
echo -e "\n${YELLOW}[5/6] Checking ROS 2 Installation...${NC}"
if [ -f "/opt/ros/jazzy/setup.bash" ]; then
    echo -e "${GREEN}✓ ROS 2 Jazzy detected at /opt/ros/jazzy${NC}"
elif command -v ros2 &> /dev/null; then
    echo -e "${GREEN}✓ ROS 2 binary detected:${NC} $(which ros2)"
else
    echo -e "${YELLOW}! ROS 2 not sourced or detected in standard path${NC}"
fi

# 6. Python Packages for Research State & Analysis
echo -e "\n${YELLOW}[6/6] Checking Python Analysis & State Packages...${NC}"
if [ -f "$CONDA_ENV/bin/python" ]; then
    "$CONDA_ENV/bin/python" -c "
import sys
packages = ['torch', 'gymnasium', 'skrl', 'stable_baselines3', 'pydantic', 'yaml', 'pandas', 'scipy', 'rich', 'tabulate', 'matplotlib']
missing = []
for p in packages:
    try:
        __import__(p)
    except ImportError:
        missing.append(p)
if missing:
    print(f'\033[0;31m✗ Missing packages: {missing}\033[0m')
    sys.exit(1)
else:
    print('\033[0;32m✓ All required Python packages are installed!\033[0m')
" || true
fi

echo -e "\n${BLUE}==============================================================================${NC}"
echo -e "${GREEN}System diagnostic completed.${NC}"
