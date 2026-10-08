# ARX AR5-L6 7-DoF Manipulator Specification

## 1. System Overview
* **Manufacturer**: ARX Robotics (松延动力 / ARX)
* **Model**: AR5-L6 (7-DoF Anthropomorphic Manipulator)
* **Hardware Designations in DEX-ROB Lab**:
  * **Left Arm (Holding/Fixturing)**: `AR5_5_07L_W4C4A2` (equipped with LinkerHand O6)
  * **Right Arm (Active Slicing)**: `AR5_5_07R_W4C4A2` (equipped with sensorized culinary knife)
* **Degrees of Freedom**: 7 Revolute Joints per arm
* **Target Payload**: 3.0 kg nominal (5.0 kg peak)
* **Reach**: ~650 mm

---

## 2. Joint Limits & Dynamic Parameters

| Joint Name | Type | Lower Limit (rad) | Upper Limit (rad) | Max Vel (rad/s) | Peak Torque (N·m) | Nominal Effort (N·m) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `joint_1` (Base Yaw) | Revolute | -3.1067 (-178°) | +3.1067 (+178°) | 3.05 | 108.0 | 50.0 |
| `joint_2` (Shoulder Pitch) | Revolute | -0.1000 (-5.7°) | +3.6652 (+210°) | 3.05 | 108.0 | 50.0 |
| `joint_3` (Shoulder Roll) | Revolute | -3.1067 (-178°) | +3.1067 (+178°) | 3.05 | 108.0 | 50.0 |
| `joint_4` (Elbow Pitch) | Revolute | -0.1000 (-5.7°) | +3.1067 (+178°) | 3.05 | 108.0 | 50.0 |
| `joint_5` (Wrist Yaw) | Revolute | -3.1067 (-178°) | +3.1067 (+178°) | 4.19 | 19.0 | 15.0 |
| `joint_6` (Wrist Pitch) | Revolute | -1.0472 (-60°) | +1.0472 (+60°) | 4.19 | 19.0 | 15.0 |
| `joint_7` (Wrist Roll / Flange) | Revolute | -3.1067 (-178°) | +3.1067 (+178°) | 4.19 | 19.0 | 15.0 |

---

## 3. Communication & Actuation Architecture
* **Bus Interface**: CAN 2.0B / CAN-FD via SocketCAN (e.g., `can0` or USB-CAN adapter)
* **Bitrate**: 1,000,000 bps (1 Mbps)
* **Control Modes**:
  1. **Joint Position Mode**: PD setpoints interpolated at 500 Hz–1 kHz.
  2. **Joint Velocity Mode**: Direct velocity feedforward for Cartesian trajectory tracking.
  3. **Joint Effort / Torque Mode**: Direct current/torque feedforward for active compliance and impedance control.
* **Controller Frequency**: 1 kHz deterministic control loop under PREEMPT_RT Linux.

---

## 4. Software Drivers & Repositories
* **Stanford REAL ARX5 SDK**: Located at `hardware/repos/arm/arx5-sdk/`
  * C++ controller and Python bindings (`import arx5_interface`).
  * Cartesian trajectory execution, teach-and-replay, and joystick teleoperation.
* **ARX Robotics Official CAN Driver**: Located at `hardware/repos/arm/ARX_CAN/`
  * Low-level SocketCAN communication diagnostic tool: `ARX_CAN_doctor`.
  * Real-time packet parsing and bus health monitoring.
