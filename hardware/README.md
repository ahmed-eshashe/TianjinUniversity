# DEX-ROB Lab Hardware Database & Driver Repository
## Bimanual Soft-Body Slicing Platform (Tianjin University)

Welcome to the **Hardware Section of the Shared Multi-Agent Database**. This directory serves as the centralized repository and single source of truth for all physical robotic manipulators, dexterous end-effectors, CAN bus drivers, and integration SDKs used across the project.

---

## 1. Hardware Architecture Overview

| Subsystem | Hardware Model | Manufacturer | DoF & Actuation | Primary Responsibility | Assigned Agent |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Holding Manipulator** | **ARX AR5-L6** (`07L`) | ARX Robotics (松延动力) | 7-DoF Revolute | Tomato fixturing, Cartesian positioning, impedance holding | `ros_agent` |
| **Slicing Manipulator** | **ARX AR5-L6** (`07R`) | ARX Robotics (松延动力) | 7-DoF Revolute | High-frequency sawing, fracture penetration, normal force regulation | `ros_agent` |
| **Dexterous Fixture** | **LinkerHand O6** | Linker Robotics (灵巧智能) | 11 DoF (6 Active + 5 Coupled) | Non-destructive soft deformation grasping, tactile feedback | `ros_agent` |
| **Active Slicing Tool** | **TacBlade** | DEX-ROB Custom | Rigid culinary knife mount | Knife blade with strain gauge bridge & force sensing | `ros_agent` |

---

## 2. Directory Layout & Cloned Repositories

```
hardware/
├── README.md                            # This Master Hardware Database index
├── specs/                               # Detailed technical datasheets & protocols
│   ├── ar5_l6_manipulator.md            # ARX AR5-L6 joint limits, torques, kinematics
│   ├── linkerhand_o6.md                 # LinkerHand O6 tendon ratios, tactile skin, contracts
│   └── can_bus_topology_and_wiring.md   # CAN 2.0B / SocketCAN 1 kHz RT loop setup
├── scripts/
│   └── clone_hardware_repos.sh          # Automated synchronization script
└── repos/                               # Cloned driver repositories
    ├── arm/
    │   ├── arx5-sdk/                    # Stanford REAL ARX5 C++ & Python SDK
    │   └── ARX_CAN/                     # Official ARX CAN driver & diagnostic doctor
    └── hand/
        ├── robot-linkerbot-linker_hand_o6/      # Syswonder LinkerHand O6 deployment & URDF
        ├── primitive-linkerbot-linker_hand_o6/  # Cleaned LinkerHand O6 Python CAN backend
        ├── linker_hand_service/                # Unitree Linker Hand DDS/ROS service
        ├── linkerhand-cpp-sdk/                 # Official LinkerHand C++ SDK (CAN / CAN-FD)
        └── linkerhand-python-sdk/              # Official LinkerHand Python SDK & API
```

---

## 3. Cloned Repositories Registry

### A. Robot Arm Repositories (`hardware/repos/arm/`)
1. **[Stanford REAL ARX5 SDK](https://github.com/real-stanford/arx5-sdk)** (`arx5-sdk/`)
   * **Source**: `https://github.com/real-stanford/arx5-sdk.git`
   * **Role**: Primary C++ and Python SDK for ARX 6/7-DoF arms. Provides joint-space and Cartesian-space impedance control, teleoperation, and teach-and-replay.
2. **[ARX Robotics Official CAN Driver](https://github.com/ARXroboticsX/ARX_CAN)** (`ARX_CAN/`)
   * **Source**: `https://github.com/ARXroboticsX/ARX_CAN.git`
   * **Role**: Official low-level CAN communication library and diagnostic utility (`ARX_CAN_doctor`) for bus health monitoring.

### B. Dexterous Hand Repositories (`hardware/repos/hand/`)
1. **[Syswonder LinkerHand O6 Assembly](https://github.com/syswonder/robot-linkerbot-linker_hand_o6)** (`robot-linkerbot-linker_hand_o6/`)
   * **Source**: `https://github.com/syswonder/robot-linkerbot-linker_hand_o6.git`
   * **Role**: Complete deployment manifest (`robonix_manifest.yaml`), `soma.yaml`, and standalone URDF specifically tailored for the 6-axis LinkerHand O6.
2. **[Syswonder Cleaned O6 CAN Driver](https://github.com/syswonder/primitive-linkerbot-linker_hand_o6-hand-rbnx)** (`primitive-linkerbot-linker_hand_o6/`)
   * **Source**: `https://github.com/syswonder/primitive-linkerbot-linker_hand_o6-hand-rbnx.git`
   * **Role**: Cleaned, standalone Python SocketCAN driver (`linker_hand_o6_can.py`) with environment-based sudo handling and zero `sys.path` side-effects.
3. **[Unitree Linker Hand Service](https://github.com/unitreerobotics/linker_hand_service)** (`linker_hand_service/`)
   * **Source**: `https://github.com/unitreerobotics/linker_hand_service.git`
   * **Role**: Production C++ service bridging LinkerHand CAN/Serial frames into ROS/DDS communication networks.
4. **[Linker Robotics Official C++ SDK](https://github.com/linker-bot/linkerhand-cpp-sdk)** (`linkerhand-cpp-sdk/`)
   * **Source**: `https://github.com/linker-bot/linkerhand-cpp-sdk.git`
   * **Role**: Official multi-model C++ SDK supporting O6, L6, L7 with CAN, CAN-FD, and Modbus interfaces.
5. **[Linker Robotics Official Python SDK](https://github.com/linker-bot/linkerhand-python-sdk)** (`linkerhand-python-sdk/`)
   * **Source**: `https://github.com/linker-bot/linkerhand-python-sdk.git`
   * **Role**: Official Python control APIs, tactile data readers, and example grasping policies.

---

## 4. Shared Agent Access
* **`ros_agent`**: Uses driver packages in `hardware/repos/` to formulate real-time ROS 2 Jazzy hardware interfaces and 1 kHz CAN loops.
* **`simulation_agent`**: Verifies physical URDF, inertia tensors, and joint limits in `hardware/specs/` against PhysX 5 USD models.
* **`rl_agent`**: Reads torque limits and maximum velocities to enforce realistic action spaces and clipping bounds during policy training.
