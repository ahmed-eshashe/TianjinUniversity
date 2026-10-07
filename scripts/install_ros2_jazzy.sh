#!/usr/bin/env bash
# ==============================================================================
# Installation Script for ROS 2 Jazzy Jalisco (LTS) on Ubuntu 24.04 (Noble)
# Optimized with High-Speed Domestic Mirror (Tsinghua TUNA) & Ubuntu Keyserver
# Designed for DEX-ROB Lab & NVIDIA Isaac Sim 6.1 / Isaac Lab Integration
# ==============================================================================

set -e

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}    ROS 2 Jazzy Jalisco (LTS) Automated Installer     ${NC}"
echo -e "${BLUE}    Target: Ubuntu 24.04 LTS (Noble) & Isaac Sim 6.1  ${NC}"
echo -e "${BLUE}======================================================${NC}"

# Check for root/sudo
if [ "$EUID" -ne 0 ]; then
  echo -e "${YELLOW}[!] This script requires root privileges to configure apt and install packages.${NC}"
  echo -e "${YELLOW}[!] Re-running with sudo...${NC}"
  exec sudo bash "$0" "$@"
fi

# 1. Verify OS Distribution
echo -e "\n${GREEN}[1/7] Verifying Ubuntu version...${NC}"
UBUNTU_CODENAME=$(lsb_release -cs 2>/dev/null || grep -oP '(?<=VERSION_CODENAME=).*' /etc/os-release)
if [ "$UBUNTU_CODENAME" != "noble" ]; then
  echo -e "${RED}[ERROR] Detected Ubuntu codename: '$UBUNTU_CODENAME'.${NC}"
  echo -e "${RED}ROS 2 Jazzy Jalisco is officially targeted for Ubuntu 24.04 (noble).${NC}"
  exit 1
fi
echo -e "OS verified: Ubuntu 24.04 LTS (noble)."

# 2. Locale Configuration
echo -e "\n${GREEN}[2/7] Configuring UTF-8 locale...${NC}"
apt-get update -y
apt-get install -y locales software-properties-common curl gnupg lsb-release
locale-gen en_US en_US.UTF-8
update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# 3. Enable Ubuntu Universe Repository
echo -e "\n${GREEN}[3/7] Ensuring Universe repository is enabled...${NC}"
add-apt-repository -y universe

# 4. Add ROS 2 GPG Key (Using Ubuntu Keyserver to bypass raw.githubusercontent.com connection reset)
echo -e "\n${GREEN}[4/7] Adding official ROS 2 GPG key (via Ubuntu Keyserver & Mirrors)...${NC}"
install -d -m 0755 /usr/share/keyrings
KEYRING_PATH="/usr/share/keyrings/ros-archive-keyring.gpg"

KEY_SUCCESS=0

# Method A: Ubuntu Keyserver (hkp://keyserver.ubuntu.com:80)
if [ $KEY_SUCCESS -eq 0 ]; then
  echo "Attempting to receive key from Ubuntu Keyserver (keyserver.ubuntu.com)..."
  if gpg --no-default-keyring --keyring "$KEYRING_PATH" --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-keys C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654 2>/dev/null; then
    echo "Successfully fetched key from keyserver.ubuntu.com."
    KEY_SUCCESS=1
  fi
fi

# Method B: Fast mirror proxy
if [ $KEY_SUCCESS -eq 0 ]; then
  echo "Attempting mirror proxy for ros.key..."
  if curl -sSL --connect-timeout 10 https://mirror.ghproxy.com/https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o "$KEYRING_PATH" 2>/dev/null; then
    echo "Successfully fetched key via mirror proxy."
    KEY_SUCCESS=1
  fi
fi

# Method C: Direct curl fallback
if [ $KEY_SUCCESS -eq 0 ]; then
  echo "Attempting direct fetch from raw.githubusercontent.com..."
  if curl -sSL --connect-timeout 10 https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o "$KEYRING_PATH" 2>/dev/null; then
    echo "Successfully fetched key from raw.githubusercontent.com."
    KEY_SUCCESS=1
  fi
fi

if [ $KEY_SUCCESS -eq 0 ]; then
  echo -e "${RED}[ERROR] Failed to obtain the ROS 2 GPG key. Please check network connectivity.${NC}"
  exit 1
fi
chmod 0644 "$KEYRING_PATH"

# 5. Add ROS 2 APT Repository (Using High-Speed Tsinghua TUNA Mirror)
echo -e "\n${GREEN}[5/7] Adding ROS 2 apt repository (Tsinghua TUNA Mirror)...${NC}"
ARCH=$(dpkg --print-architecture)
# Use Tsinghua mirror for high speed and reliable connection in China
echo "deb [arch=${ARCH} signed-by=${KEYRING_PATH}] https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu noble main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null

# 6. Install ROS 2 Jazzy Desktop and Development Tools
echo -e "\n${GREEN}[6/7] Updating apt repositories and installing ros-jazzy-desktop & ros-dev-tools...${NC}"
apt-get update -y
apt-get install -y ros-jazzy-desktop ros-dev-tools

# 7. Initialize rosdep & Environment Sourcing
echo -e "\n${GREEN}[7/7] Setting up rosdep and bash environment...${NC}"
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
  rosdep init || true
fi

TARGET_USER="${SUDO_USER:-$USER}"
TARGET_HOME=$(getent passwd "$TARGET_USER" | cut -d: -f6)

if [ -n "$TARGET_USER" ] && [ "$TARGET_USER" != "root" ]; then
  echo -e "Updating rosdep for user: ${TARGET_USER}..."
  su - "$TARGET_USER" -c "rosdep update || true"
  
  # Add setup.bash to target user's .bashrc if not present
  if ! grep -q "/opt/ros/jazzy/setup.bash" "$TARGET_HOME/.bashrc" 2>/dev/null; then
    echo -e "\n# ROS 2 Jazzy Jalisco Environment" >> "$TARGET_HOME/.bashrc"
    echo "source /opt/ros/jazzy/setup.bash" >> "$TARGET_HOME/.bashrc"
    echo -e "Added 'source /opt/ros/jazzy/setup.bash' to ${TARGET_HOME}/.bashrc."
  else
    echo -e "ROS 2 Jazzy sourcing already present in ${TARGET_HOME}/.bashrc."
  fi
else
  rosdep update || true
fi

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN}  ROS 2 Jazzy Jalisco successfully installed!         ${NC}"
echo -e "${GREEN}  Location: /opt/ros/jazzy                             ${NC}"
echo -e "${GREEN}======================================================${NC}"
echo -e "To verify in your terminal, run:"
echo -e "  source /opt/ros/jazzy/setup.bash"
echo -e "  ros2 --help"
