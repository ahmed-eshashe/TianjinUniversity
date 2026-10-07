# Core Research Question & Scope Definition

## 1. Primary Research Question

> **"How can a hierarchical residual reinforcement learning framework fusing multi-modal vision and high-rate tactile impedance regulation achieve robust, zero-shot sim-to-real transfer for bimanual slicing of highly deformable, non-linear food objects (tomatoes) under severe mechanical and contact uncertainty?"**

---

## 2. Key Sub-Questions

1. **Sub-Question 1 (Contact Fracture Dynamics)**:  
   Can tactile feedback at the blade and gripper detect the micro-slip and elastic-to-fracture transition phases of a tomato skin in real-time ($>500\text{ Hz}$), preventing crushing before rupture?
2. **Sub-Question 2 (Hierarchical Policy Decoupling)**:  
   Does decoupling macro-trajectory kinematic generation ($30\text{ Hz}$) from residual impedance adaptation ($500\text{ Hz} - 1\text{ kHz}$) prevent catastrophic policy oscillations and improve sample efficiency compared to monolithic end-to-end joint torque RL?
3. **Sub-Question 3 (Sim-to-Real Domain Randomization)**:  
   What minimal set of PhysX 5 FEM material parameter randomizations (Young's modulus $E$, Poisson's ratio $\nu$, friction $\mu$, rupture stress $\sigma_c$) is sufficient to bridge the sim-to-real gap to physical commercial tomatoes without real-world policy updates?

---

## 3. Embodiment & Target Setup

- **Robotic Platform**: Dual ARX AR5-L6 arms (7 degrees of freedom per arm, direct CAN bus interface).
  - Left Arm: Holding / Fixturing arm equipped with LinkerHand O6 (5-finger dexterous hand with tactile skin/arrays).
  - Right Arm: Slicing arm equipped with custom instrumented culinary blade (load cell / 6-axis F/T or optical tactile sensor).
- **Simulation Platform**: NVIDIA Isaac Sim 6.1.0 + Isaac Lab + PhysX 5 GPU-accelerated Finite Element Method (FEM) deformable mesh solver.
- **Physical Test Objects**: Standard beefsteak and Roma tomatoes across 3 distinct ripeness stages (Firm/Unripe, Optimal/Ripe, Overripe/Soft).

---

## 4. Target Venues & Deadlines

- **Primary Target**: IEEE International Conference on Robotics and Automation (**IEEE ICRA 2028**), Submission Deadline: **Mid-September 2027**.
- **Secondary Target**: IEEE Robotics and Automation Letters (**RA-L**) / IEEE Transactions on Robotics (**T-RO**).

---

## 5. Quantitative Success Criteria

1. **Slicing Success Rate**: $\ge 90\%$ clean through-cut completion without object ejection or tool jamming across all 3 ripeness categories.
2. **Deformation / Burst Suppression**: Maximum volumetric crush deformation $< 15\%$ of initial undeformed tomato radius prior to skin puncture.
3. **Slice Uniformity**: Thickness variation $< \pm 1.5\text{ mm}$ across the sliced cross-section.
4. **Sample Efficiency**: Policy convergence in Isaac Lab within $< 10\text{M}$ environment steps ($< 3\text{ hours}$ wall-clock time on RTX 5060 GPU).
5. **Zero-Shot Real-World Transfer**: $\ge 80\%$ success rate on real physical setup using uncalibrated tomatoes directly from local markets.
