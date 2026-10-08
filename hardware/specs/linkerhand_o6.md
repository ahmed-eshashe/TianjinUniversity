# LinkerHand O6 5-Finger Dexterous Hand Specification

## 1. System Overview
* **Manufacturer**: Linker Robotics (灵巧智能)
* **Model**: LinkerHand O6 (5-Finger Anthropomorphic Dexterous Hand)
* **Hardware Role**: Adaptive holding, soft-body grasp stabilization, non-destructive deformation control.
* **Mechanical Architecture**:
  * **Total Degrees of Freedom**: 11 Revolute Joints across 5 fingers.
  * **Actuation Principle**: 6 Active Motors + 5 Mechanically Coupled Tendon Joints.
  * **Fingertip Sensors**: Multi-element tactile sensing arrays on fingertip distal pads and palm.

---

## 2. Joint & Kinematic Breakdown

| Finger | Joint Name | Role / Actuation | Motion Range (rad) | Mechanical Coupling Ratio |
| :--- | :--- | :--- | :--- | :--- |
| **Thumb** | `lh_thumb_cmc_yaw` | Active Motor (Abduction/Adduction) | 0.0 to 1.57 rad | Independent motor |
| | `lh_thumb_cmc_pitch` | Active Motor (Flexion/Extension) | 0.0 to 1.57 rad | Independent motor |
| | `lh_thumb_dip` | Passive Tendon-Coupled Joint | 0.0 to 1.92 rad | Coupled to CMC Pitch: $\theta_{dip} = 1.2265 \cdot \theta_{cmc\_pitch}$ |
| **Index** | `lh_index_mcp_pitch` | Active Motor (Flexion) | 0.0 to 1.57 rad | Independent motor |
| | `lh_index_dip` | Passive Tendon-Coupled Joint | 0.0 to 1.77 rad | Coupled to MCP Pitch: $\theta_{dip} = 1.1257 \cdot \theta_{mcp\_pitch}$ |
| **Middle** | `lh_middle_mcp_pitch` | Active Motor (Flexion) | 0.0 to 1.57 rad | Independent motor |
| | `lh_middle_dip` | Passive Tendon-Coupled Joint | 0.0 to 1.77 rad | Coupled to MCP Pitch: $\theta_{dip} = 1.1257 \cdot \theta_{mcp\_pitch}$ |
| **Ring** | `lh_ring_mcp_pitch` | Active Motor (Flexion) | 0.0 to 1.57 rad | Independent motor |
| | `lh_ring_dip` | Passive Tendon-Coupled Joint | 0.0 to 1.77 rad | Coupled to MCP Pitch: $\theta_{dip} = 1.1257 \cdot \theta_{mcp\_pitch}$ |
| **Pinky** | `lh_pinky_mcp_pitch` | Active Motor (Flexion) | 0.0 to 1.57 rad | Independent motor |
| | `lh_pinky_dip` | Passive Tendon-Coupled Joint | 0.0 to 1.77 rad | Coupled to MCP Pitch: $\theta_{dip} = 1.1257 \cdot \theta_{mcp\_pitch}$ |

---

## 3. Communication & Electrical Interface
* **Interface**: CAN 2.0B / CAN-FD / RS-485
* **Default SocketCAN Bitrate**: 1,000,000 bps (1 Mbps)
* **CAN IDs & Packet Structure**:
  * Broadcast cycle: 100 Hz to 1 kHz
  * Command frame: Per-axis target angle setpoints, velocity limits, torque cutoffs.
  * Feedback frame: Joint positions, motor currents, fault codes, tactile sensor arrays.
* **Flange Adapter**: `lh_rk_adapter` mounted to arm TCP flange (`AR5_5_07L_W4C4A2_tcp`).

---

## 4. Software Drivers & Repositories in Lab Database
* **Syswonder Robonix LinkerHand O6 Assembly**: `hardware/repos/hand/robot-linkerbot-linker_hand_o6/`
  * Complete assembly manifest (`robonix_manifest.yaml`), `soma.yaml`, and standalone URDF.
* **Cleaned LinkerHand O6 CAN Driver**: `hardware/repos/hand/primitive-linkerbot-linker_hand_o6/`
  * Contains pure Python SocketCAN driver (`linkerhand_o6/vendor/linker_hand_o6_can.py` and `can_iface.py`).
  * Fixes the upstream plaintext password leak and dynamic `sys.path` injection bugs.
* **Unitree Linker Hand Service**: `hardware/repos/hand/linker_hand_service/`
  * C++ service bridging LinkerHand CAN/Serial packets into ROS / DDS.
* **Official LinkerHand C++ SDK**: `hardware/repos/hand/linkerhand-cpp-sdk/`
  * Official manufacturer C++ library supporting O6, L6, L7, CAN, CAN-FD, and Modbus.
* **Official LinkerHand Python SDK**: `hardware/repos/hand/linkerhand-python-sdk/`
  * Official Python APIs, example scripts, and dynamic grasping utilities.
