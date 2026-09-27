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
| [`two_person_parallel_workflow.md`](two_person_parallel_workflow.md) | Two-person parallel work breakdown (Option A: Subsystem Split), single-arm mocking, 8-week timeline, modular code architecture, and IEEE RA-L co-authorship plan |

## UC Berkeley CS 285 (Deep RL) Priority 1 Study Guides

Comprehensive, beginner-friendly mathematical & robotics study guides for UC Berkeley CS 285 (Prof. Sergey Levine), enhanced with Joshua Achiam's *Spinning Up in Deep RL* frameworks and Goodfellow et al.'s *Deep Learning* book foundations. Tailored directly for the dual-arm tomato slicing project (Isaac Lab + SkRL):

| Guide PDF | Topic & Core Scope | Key Robotics & Code Trap Insights |
|---|---|---|
| [`CS285_Lecture1_Beginner_Guide.pdf`](CS285_Lecture1_Beginner_Guide.pdf) | **L01: Introduction & Imitation Learning** | Continuous control (T, P, E), compounding errors $\mathcal{O}(\epsilon T^2)$, DAgger loop, Wolpert's motor control thesis |
| [`CS285_Lecture4_Beginner_Guide.pdf`](CS285_Lecture4_Beginner_Guide.pdf) | **L04: Introduction to Reinforcement Learning** | Continuous MDPs, Bellman self-consistency operator, 4 value functions ($V, Q, A, V^*$), `[N]` vs `[N, 1]` broadcast bug |
| [`CS285_Lecture5_Beginner_Guide.pdf`](CS285_Lecture5_Beginner_Guide.pdf) | **L05: Policy Gradients** | Likelihood-ratio trick, EGLP Lemma, Achiam's 5 forms of $\Phi_t$, Gaussian continuous control, log-std clamping |
| [`CS285_Lecture6_Beginner_Guide.pdf`](CS285_Lecture6_Beginner_Guide.pdf) | **L06: Actor-Critic Algorithms** | Generalized Advantage Estimation (GAE-$\lambda$) telescoping sum, semi-gradient detaching, squashed Gaussian Jacobian correction |
| [`CS285_Lecture8_Beginner_Guide.pdf`](CS285_Lecture8_Beginner_Guide.pdf) | **L08: Value Function Methods & Max-Entropy RL** | Continuous Q-learning, SAC entropy temperature $\alpha$, target entropy $\bar{\mathcal{H}} = -\dim(\mathcal{A})$, Polyak decay half-life, replay buffer action trap |
| [`CS285_Lecture10_Beginner_Guide.pdf`](CS285_Lecture10_Beginner_Guide.pdf) | **L10: Advanced Policy Gradients (PPO)** | PPO-Clip vs PPO-Penalty, trust region constraints, KL early stopping rule ($\bar{D}_{\text{KL}} > 1.5 d_{\text{target}}$), value clipping, batch flattening trap |
| [`CS285_Priority1_Master_Robotics_Guide.pdf`](CS285_Priority1_Master_Robotics_Guide.pdf) | **Priority 1 Master Robotics Compendium** | Unified synthesis across all 6 lectures, complete algorithm selection matrix (PPO vs SAC for dual-arm slicing), TacBlade reward design |

### Guide Generation Scripts
The Python ReportLab generator scripts used to build these publication-grade PDFs are archived in [`scripts/`](scripts/):
- `generate_lecture1_guide.py`: Generates Lecture 1 guide
- `generate_lecture4_guide.py`: Generates Lecture 4 guide
- `generate_lecture5_guide.py`: Generates Lecture 5 guide
- `generate_lecture6_guide.py`: Generates Lecture 6 guide
- `generate_lecture8_guide.py`: Generates Lecture 8 guide
- `generate_lecture10_guide.py`: Generates Lecture 10 guide
- `generate_priority1_master_guide.py`: Generates Master Compendium guide

