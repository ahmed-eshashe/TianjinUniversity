---
title: "Residual Reinforcement Learning for Robot Control"
authors: ["Tobias Johannink", "Shikhar Bahl", "Ashvin Nair", "Jianlan Jian", "Eugen Solowjow", "Sergey Levine"]
year: 2019
venue: "IEEE ICRA"
doi: "10.1109/ICRA.2019.8794127"
robot_platform: "Franka Panda / UR5"
object_type: "Rigid objects (Block assembly, etc.)"
sensors: ["Proprioception", "Vision"]
control_paradigm: "Residual Reinforcement Learning"
claimed_contribution: "Introduced Residual RL, where a conventional feedback controller solves the bulk of a task, and an RL agent learns a residual action to overcome modeling errors or complex contact dynamics."
limitations: "Did not explore highly deformable fracture mechanics (cutting)."
relevance_to_project: "The foundational architecture for our RL approach. We use traditional Cartesian impedance for the macro slicing motion, and an RL agent to provide residual adjustments based on tactile feedback."
---

# Summary
This paper proposes combining standard analytical controllers (like PID or operational space control) with deep reinforcement learning. The analytical controller acts as a strong prior (the "base policy"), while the RL agent outputs a "residual" action added to the base action. This drastically improves sample efficiency and safety during contact-rich tasks like peg-in-hole.

## Key Takeaways for our Bimanual Tomato Slicing
- Forms the architectural basis of our control strategy.
- We apply this specifically to cutting: base policy executes a saw-like trajectory, residual policy adjusts depth, pressure, and bimanual holding force based on high-frequency haptics.
