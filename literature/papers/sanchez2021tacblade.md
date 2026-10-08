---
title: "Robotic Slicing of Deformable Objects with Force/Tactile Feedback"
authors: ["J. Sanchez", "J. A. Corrales", "B. C. Bouzgarrou", "Y. Mezouar"]
year: 2021
venue: "IEEE RA-L"
doi: "10.1109/LRA.2021.3062331"
robot_platform: "Unspecified standard arm"
object_type: "Deformable food/objects"
sensors: ["6-axis F/T", "Tactile"]
control_paradigm: "Tactile-Reactive Control"
claimed_contribution: "Demonstrates that reactive control utilizing high-frequency tactile and force feedback significantly improves cutting stability on non-homogeneous deformable objects compared to open-loop kinematics."
limitations: "Primarily analytical control rather than data-driven/RL."
relevance_to_project: "Provides a traditional control baseline (e.g., admittance/impedance) for our RL policies and establishes the necessity of force/tactile feedback."
---

# Summary
This paper investigates the use of force and tactile feedback to actively control the slicing of deformable objects. By closing the loop on contact forces, the robot can adapt its cutting speed and applied pressure to avoid excessively deforming or crushing the object before the cut is achieved.

## Key Takeaways for our Bimanual Tomato Slicing
- Confirms Hypothesis 1: Force/tactile feedback is crucial to prevent object rolling/crushing during cutting.
- Provides a strong baseline methodology against which our RL-based approach should be benchmarked.
