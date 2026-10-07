---
name: ros2-robotics
description: "ROS 2 Jazzy node architecture, real-time CAN bus motor control, MoveIt 2 Cartesian planning, and safety interlocks for ARX AR5-L6."
---

# ROS 2 Robotics & Real-Time Hardware Skill

## When to Use
Use when:
- Designing or modifying ROS 2 Jazzy nodes and launch scripts.
- Interfacing with ARX AR5-L6 manipulators via SocketCAN / C++ SDK.
- Setting up 1 kHz deterministic control loops under PREEMPT_RT Linux.
- Implementing emergency stop interlocks and force threshold monitoring.

## Safety & Real-Time Rules
1. **Never Bypass E-Stop**: The hardware E-stop software daemon must listen continuously at $\ge 500\text{ Hz}$ on joint torque and F/T topics.
2. **Deterministic Loop**: Avoid dynamic memory allocations, file I/O, or blocking network calls inside the 1 kHz RT thread.
3. **Hardware Sanity Check**: Verify joint limits, self-collision zones, and workspace Cartesian bounding boxes before executing policy trajectories on physical hardware.
