# Research Progress & Documentation Index

This directory serves as the structured knowledge base for Master's research in Control Science and Engineering at DEX-ROB Lab (Tianjin University).

## Structure Overview

### 1. Proposals (`research/proposals/`)
- [`proposal_for_professor.md`](proposals/proposal_for_professor.md): Official proposal draft for Prof. Shan An detailing the *Vision-Tactile Fusion for Adaptive Cutting of Deformable Foods* project, experimental design, paper pipeline, resources, and long-term vision (autonomous experience kiosks).

### 2. Research Directions & Strategy (`research/directions/`)
- [`master_research_directions.md`](directions/master_research_directions.md): Initial comprehensive survey of 4 research directions (Variable Impedance, SNN Slip Reflex, Compliant Wrist, Whole-Finger Skin) bridging IROS/ICRA publication constraints with B2B hardware strategy.
- [`direction5_tacblade_cutting.md`](directions/direction5_tacblade_cutting.md): Deep-dive into TacBlade deformable food cutting dynamics, fracture mechanics formulation, and dynamic phase switching.

### 3. System Architectures (`research/architectures/`)
- [`vision_tactile_fusion_cutting.md`](architectures/vision_tactile_fusion_cutting.md): Hierarchical control architecture combining 30 Hz Vision Trajectory Generation with 1 kHz On-Tool Force-Driven Impedance Regulation.

### 4. Literature Survey (`research/literature_survey/`)
- [`adept_and_robot_foundation_models.md`](literature_survey/adept_and_robot_foundation_models.md): Comprehensive survey of the **ADEPT** pre-training/post-training framework (CoRL 2026), open-source foundation models (**LeRobot**, **Octo**, **OpenVLA**), the *"Android for Robots"* paradigm (**OpenMind OM1**, **Isaac Lab**), and strategic roadmap for DEX-ROB Lab.

### 5. Simulation & Training Methodology (`research/simulation/`)
- [`training_approach_comparison.md`](simulation/training_approach_comparison.md): Comparison of Imitation Learning vs Vision-Based RL vs Traditional Control for DOM, including a staged hybrid strategy and realistic timelines.
- [`simulator_pipeline.md`](simulation/simulator_pipeline.md): Explanation of the MuJoCo + Isaac Sim hybrid architecture — why two engines, Real-to-Sim, Sim-to-Real, data collection strategies, and RL vs VLA training models.
- [`isaac_lab_vs_mujoco_isaac_sim.md`](simulation/isaac_lab_vs_mujoco_isaac_sim.md): Head-to-head platform comparison between Isaac Lab (NVIDIA unified) and MuJoCo + Isaac Sim (hybrid), with DOM-specific verdict and scorecard.
- [`rl_software_tools.md`](simulation/rl_software_tools.md): Full 7-layer software stack for traditional RL-based DOM (Isaac Lab, SkRL, ROS 2, WandB, Hydra).
- [`rl_data_sources_and_mdp_formulation.md`](simulation/rl_data_sources_and_mdp_formulation.md): Comprehensive mathematical MDP formulation (33D state, 6D action, 7-part reward), piecewise fracture mechanics, and sensor integration.
- [`beginner_robotics_rl_setup_guide.md`](simulation/beginner_robotics_rl_setup_guide.md): Practical onboarding guide for beginners: intuitive mental model, minimal 4-tool stack, step-by-step WSL2/Isaac Lab setup on laptop, and verification tests.

### 6. Resources & Papers (`research/resources/`)
- [`README.md`](resources/README.md): Master resource index containing downloaded literature, open-source repositories, and the two-paper thesis strategy.
- [`papers/ADEPT_CoRL2026.pdf`](resources/papers/ADEPT_CoRL2026.pdf): Full local PDF of the seminal CoRL 2026 paper on foundational dexterity pre-training and post-training.

### 7. Reports & Milestones (`research/reports/`)
- [`bimanual_dom_pipeline_report.md`](reports/bimanual_dom_pipeline_report.md): **Primary Review Document (Markdown)**. Enhanced comprehensive technical report preserving 100% of pipeline mechanics, DRL formulations, and hardware benchmarking, featuring the embedded Figure 1 architecture diagram.
- [`report1_enhanced.docx`](reports/report1_enhanced.docx): **Enhanced Word Document** (475 KB). Features executive typography, styled callout boxes, striped spec tables, running headers/footers, and embedded Figure 1.
- [`figures/fig1_system_architecture.png`](reports/figures/fig1_system_architecture.png): End-to-end 5-stage Bimanual DOM system pipeline diagram.
- [`weekly_report_2026_09_19.md`](reports/weekly_report_2026_09_19.md) / [`.docx`](reports/weekly_report_2026_09_19.docx) / [`.pdf`](reports/weekly_report_2026_09_19.pdf): Previous weekly sprint report.


