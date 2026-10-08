#!/usr/bin/env bash
# ==============================================================================
# Hardware Repositories Setup & Sync Script
# DEX-ROB Lab | Tianjin University
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARDWARE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPOS_DIR="${HARDWARE_DIR}/repos"

mkdir -p "${REPOS_DIR}/arm"
mkdir -p "${REPOS_DIR}/hand"

echo "=============================================================================="
echo " Synchronizing DEX-ROB Hardware Repositories (ARX AR5 + LinkerHand O6)"
echo " Destination: ${REPOS_DIR}"
echo "=============================================================================="

# --- 1. Manipulator (Arm) Repositories ---
echo "[1/2] Syncing Robot Arm Repositories..."

# Stanford REAL ARX5 SDK
if [ ! -d "${REPOS_DIR}/arm/arx5-sdk" ]; then
    echo "  -> Cloning real-stanford/arx5-sdk..."
    git clone --depth 1 https://github.com/real-stanford/arx5-sdk.git "${REPOS_DIR}/arm/arx5-sdk"
else
    echo "  -> arx5-sdk already present."
fi

# Official ARX Robotics CAN Driver & Diagnostic Doctor
if [ ! -d "${REPOS_DIR}/arm/ARX_CAN" ]; then
    echo "  -> Cloning ARXroboticsX/ARX_CAN..."
    git clone --depth 1 https://github.com/ARXroboticsX/ARX_CAN.git "${REPOS_DIR}/arm/ARX_CAN"
else
    echo "  -> ARX_CAN already present."
fi

# --- 2. Dexterous Hand (LinkerHand O6) Repositories ---
echo "[2/2] Syncing Dexterous Hand Repositories..."

# Syswonder LinkerHand O6 Assembly & URDF
if [ ! -d "${REPOS_DIR}/hand/robot-linkerbot-linker_hand_o6" ]; then
    echo "  -> Cloning syswonder/robot-linkerbot-linker_hand_o6..."
    git clone --depth 1 https://github.com/syswonder/robot-linkerbot-linker_hand_o6.git "${REPOS_DIR}/hand/robot-linkerbot-linker_hand_o6"
else
    echo "  -> robot-linkerbot-linker_hand_o6 already present."
fi

# Syswonder LinkerHand O6 Cleaned CAN Primitive & Vendored Backend
if [ ! -d "${REPOS_DIR}/hand/primitive-linkerbot-linker_hand_o6" ]; then
    echo "  -> Cloning syswonder/primitive-linkerbot-linker_hand_o6-hand-rbnx..."
    git clone --depth 1 https://github.com/syswonder/primitive-linkerbot-linker_hand_o6-hand-rbnx.git "${REPOS_DIR}/hand/primitive-linkerbot-linker_hand_o6"
else
    echo "  -> primitive-linkerbot-linker_hand_o6 already present."
fi

# Unitree Robotics Linker Hand Service
if [ ! -d "${REPOS_DIR}/hand/linker_hand_service" ]; then
    echo "  -> Cloning unitreerobotics/linker_hand_service..."
    git clone --depth 1 https://github.com/unitreerobotics/linker_hand_service.git "${REPOS_DIR}/hand/linker_hand_service"
else
    echo "  -> linker_hand_service already present."
fi

# Official LinkerHand C++ SDK
if [ ! -d "${REPOS_DIR}/hand/linkerhand-cpp-sdk" ]; then
    echo "  -> Cloning linker-bot/linkerhand-cpp-sdk..."
    git clone --depth 1 https://github.com/linker-bot/linkerhand-cpp-sdk.git "${REPOS_DIR}/hand/linkerhand-cpp-sdk"
else
    echo "  -> linkerhand-cpp-sdk already present."
fi

# Official LinkerHand Python SDK
if [ ! -d "${REPOS_DIR}/hand/linkerhand-python-sdk" ]; then
    echo "  -> Cloning linker-bot/linkerhand-python-sdk..."
    git clone --depth 1 https://github.com/linker-bot/linkerhand-python-sdk.git "${REPOS_DIR}/hand/linkerhand-python-sdk"
else
    echo "  -> linkerhand-python-sdk already present."
fi

echo "=============================================================================="
echo " All hardware repositories synchronized successfully."
echo "=============================================================================="
