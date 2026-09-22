# Simulation & Training Methodology

This folder documents the simulation infrastructure, training approach decisions, and simulator comparisons for the DOM (dual-arm tomato cutting) project.

## Contents

| File | Description |
|---|---|
| [`training_approach_comparison.md`](training_approach_comparison.md) | Comparison of Imitation Learning vs Vision-Based RL vs Traditional Control, with DOM-specific verdict |
| [`simulator_pipeline.md`](simulator_pipeline.md) | Explanation of the MuJoCo + Isaac Sim hybrid architecture, Real-to-Sim, Sim-to-Real, data collection, and RL vs VLA training |
| [`isaac_lab_vs_mujoco_isaac_sim.md`](isaac_lab_vs_mujoco_isaac_sim.md) | Detailed comparison between Isaac Lab (unified) and MuJoCo + Isaac Sim (hybrid) platforms |
| [`rl_software_tools.md`](rl_software_tools.md) | Full 7-layer software stack for traditional RL-based DOM: simulation, RL framework, perception, middleware, monitoring, and install order |
| [`rl_data_sources_and_mdp_formulation.md`](rl_data_sources_and_mdp_formulation.md) | Comprehensive MDP mathematical formulation (State, Action, Reward), cutting force models, TacBlade sensing parameters, and SkRL PPO hyperparameters |
| [`beginner_robotics_rl_setup_guide.md`](beginner_robotics_rl_setup_guide.md) | Practical onboarding guide for robotics beginners: mental model, minimal 4-tool stack, step-by-step WSL2/Isaac Lab setup on laptop, and verification tests |
