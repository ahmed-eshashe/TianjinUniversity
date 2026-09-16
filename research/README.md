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

### 6. Resources & Papers (`research/resources/`)
- [`README.md`](resources/README.md): Master resource index containing downloaded literature, open-source repositories, and the two-paper thesis strategy.
- [`papers/ADEPT_CoRL2026.pdf`](resources/papers/ADEPT_CoRL2026.pdf): Full local PDF of the seminal CoRL 2026 paper on foundational dexterity pre-training and post-training.

