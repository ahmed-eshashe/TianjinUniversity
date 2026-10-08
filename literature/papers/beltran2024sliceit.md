---
title: "SliceIt!: A Dual Simulator Framework for Learning Compliant Food Slicing"
authors: ["Cristian C. Beltran-Hernandez", "Nicolas Erbetti", "Masashi Hamaya"]
year: 2024
venue: "IEEE ICRA"
doi: "arXiv:2404.02569"
robot_platform: "Frank Emika Panda"
object_type: "Food items (cucumber, egg, etc.)"
sensors: ["6-axis F/T"]
control_paradigm: "Reinforcement Learning (Sim2Real)"
claimed_contribution: "Proposed a Real2Sim2Real framework with a dual simulator (DiSECt + Gazebo) for compliant food slicing to avoid real-world RL hazards."
limitations: "Limited to specific knife models; assumes homogenous properties along the slicing plane in some instances."
relevance_to_project: "Directly relates to our Sim2Real pipeline for RL-based tomato cutting, demonstrating how dual-simulation environments are used to bridge the dynamics gap."
---

# Summary
This paper introduces a Real2Sim2Real RL pipeline for compliant food slicing. By pairing a high-fidelity cutting simulator (DiSECt) with a standard robotic simulator (Gazebo), the authors learn a cutting policy that reduces contact forces and safely transfers to a physical robot without requiring expensive, messy, and dangerous real-world RL exploration.

## Key Takeaways for our Bimanual Tomato Slicing
- Validates the approach of using FEM-based simulation (like PhysX 5 / DiSECt) to pre-train RL policies.
- Emphasizes the need for compliant control during the slicing motion.
- Highlights that single simulators often struggle to couple high-fidelity robot kinematics with high-fidelity fracture mechanics.
