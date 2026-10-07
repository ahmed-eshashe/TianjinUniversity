# Open Research Questions & Active Bottlenecks

This document tracks unresolved scientific, mechanical, and implementation challenges being actively investigated by the multi-agent team.

---

## 1. Physical Modeling & Simulation

### [OQ-001] Real-Time Volumetric Mesh Cutting in PhysX 5
- **Problem**: Slicing requires topological mesh separation (splitting tetrahedra along the cutting plane). In standard real-time PhysX 5, dynamic remeshing can introduce GPU memory allocation spikes or frame rate drops during parallel vectorization.
- **Assigned Agents**: `simulation_agent`, `rl_agent`
- **Candidate Solutions**:
  1. *Virtual cutting plane with constraint deactivation*: Pre-split the mesh along slicing planes with breakable bilateral spring constraints that detach when normal/shear stress exceeds critical threshold $\sigma_c$.
  2. *Extended Position-Based Dynamics (XPBD) or Material Point Method (MPM)*: Higher fidelity, but potentially slower than standard PhysX 5 FEM.
  3. *Kinematic proxy with force response*: Train tactile impedance policy against continuous resistance, triggering visual slice separation at cut termination.

---

## 2. Perception & Tactile Sensing

### [OQ-002] Multi-Rate Fusion (30 Hz RGB-D vs 1 kHz Tactile)
- **Problem**: Vision cameras provide global tomato pose and surface deformation at 30 Hz with ~33 ms latency. Tactile sensors and joint torque observers operate at 500 Hz - 1 kHz. Feeding both directly into an MLP policy causes latency mismatch.
- **Assigned Agents**: `rl_agent`, `ros_agent`
- **Candidate Solutions**:
  - Asynchronous dual-rate actor: High-level visual planner updates target contact plane at 10 Hz; low-level tactile policy modulates impedance at 500 Hz.
  - History buffer with Temporal Convolutional Network (TCN) or GRU over high-frequency tactile differentials $(\Delta F, \dot{F})$.

---

## 3. Hardware & Real-World Safety

### [OQ-003] AR5-L6 Low-Level Impedance Mode via CAN Bus
- **Problem**: The ARX AR5-L6 arm driver operates via CAN bus. We need to verify whether the embedded joint controller supports direct motor current / feedforward torque commands $\tau_{cmd}$ at 1 kHz with deterministic PREEMPT_RT timing, or if commands must pass via position/velocity setpoints.
- **Assigned Agents**: `ros_agent`
- **Action Item**: Inspect ARX CAN communication protocol in lab SDK and test round-trip latency.
