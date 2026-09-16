# Research Proposal: Vision-Tactile Fusion for Adaptive Cutting of Deformable Foods

**Proposed by:** [Your Name]
**Advisor:** Prof. Shan An (安山)
**Lab:** DEX-ROB Lab, School of Electrical and Automation Engineering, Tianjin University
**Program:** M.S. in Control Science and Engineering
**Date:** September 2026

---

## 1. Motivation

Cutting deformable foods like slicing tomatoes, dicing onions, or portioning soft proteins is one of the last unsolved manipulation primitives in food service automation. While our lab and the broader community have made remarkable progress in dexterous grasping (DexCatch, CoRL 2024), teleoperation (Open TeleDex), and high-speed manipulation (Astribot S1), no existing system can reliably cut a tomato.

The reason is a fundamental sensing and control problem. Cutting involves a fracture event, which is the instant the knife punctures the food's skin. At this moment:

- The cutting force drops by 50% to 80% within approximately 5 milliseconds.
- If the robot does not react, the knife plunges into the soft interior, crushing the food.
- Vision cannot help directly during contact: the blade occludes the contact zone, and cameras at 30 Hz are too slow to catch a 5 ms event.
- Wrist-mounted F/T sensors are delayed by 15 to 25 ms due to tool inertia and structural compliance.

This explains why advanced cooking robots can stir-fry, flip, and pour, but still struggle to cut cleanly. Addressing this problem will help unlock fully autonomous food preparation.

---

## 2. Research Questions

1. **Can on-tool force and vibration sensing detect cutting phase transitions (skin puncture, contact transitions, board contact) with sub-millisecond latency?**

2. **Does phase-aware switching of impedance parameters improve cutting quality over constant-impedance or vision-only control, and can we guarantee stability across the fracture discontinuity?**

3. **How much does on-tool sensing outperform wrist-mounted F/T sensing for dynamic cutting tasks?**

---

## 3. Proposed Approach

### 3.1 System Architecture

The system combines two complementary sensing modalities in a hierarchical architecture:

**Vision Layer (30 Hz)**, focusing on spatial planning:
- Food segmentation and localization, leveraging the lab's existing perception models.
- Slice position planning from measured object geometry.
- Post-cut quality verification.

**On-Tool Force Layer (1 kHz)**, focusing on real-time cutting control:
- A compact sensorized tool adapter ("TacBlade") mounted at the knife-handle interface, combining strain gauges for quasi-static force measurement with piezoelectric elements for high-frequency fracture vibration detection.
- On-board microcontroller running analytical phase detection using a threshold-based state machine, requiring no neural network training.
- Real-time impedance parameters transmitted to the robot's joint controller at 1 kHz.

Vision tells the robot where to cut. On-tool sensing regulates interaction forces during the cut and catches the fracture event that vision cannot observe directly.

### 3.2 Cutting Phase Model

The cutting process can be modeled as a hybrid dynamical system with four discrete phases:

| Phase | Physical Process | Control Objective |
|:------|:----------------|:------------------|
| 1. Skin deformation | Elastic membrane stretches under knife | Push through resistance with controlled stiffness |
| 2. Puncture | Fracture with force dropping 50% to 80% in ~5 ms | Rapidly compliant and heavily damped to arrest forward slam |
| 3. Interior cutting | Soft tissue yielding with low, variable force | Maintain steady slicing motion |
| 4. Exit / board contact | Second skin contact followed by rigid stop | Decelerate smoothly before impacting the cutting surface |

Phase transitions are detected using on-tool signals: the force derivative captures the sudden force drop, while piezoelectric burst energy tracks acoustic emissions during skin fracture.

### 3.3 Adaptive Impedance Control with Stability Guarantees

The control system follows the vision-planned trajectory with phase-dependent compliance:

    M_d · ẍ_tilde + D_d(q) · ẋ_tilde + K_d(q) · x_tilde = F_ext

where q in {1, 2, 3, 4} denotes the active phase, and x_tilde = x - x_d represents deviation from the planned path.

*Note: Phase-shifting and variable impedance switching across discrete contact fractures is an active area of research.* Discontinuous adjustments to stiffness and damping risk injecting artificial energy into the loop. To address this, a virtual energy tank framework will be investigated to guarantee passivity: an auxiliary energy state tracks accumulated dissipation and gates parameter transitions, ensuring formal stability under measurement noise and unmodeled disturbances.

### 3.4 Experimental Evaluation

The evaluation will focus on benchmarking cutting performance across varying tomato ripeness levels and blade conditions:

- Comparing position-based baselines, vision-only compliance, wrist-mounted force feedback, and the proposed on-tool sensing approach.
- Evaluating the impact of rapid puncture detection on preventing crushing and force overshoot.
- Testing generalization across other food categories (cucumbers, kiwis, bread, and tofu) to observe behavior on materials with differing skin toughness and interior mechanics.

---

## 4. Fit with DEX-ROB Lab

This research directly aligns with and extends the lab's core directions:

| Lab Strength | How This Work Connects |
|:------------|:----------------------|
| **Open TeleDex** | Human cutting demonstrations can be recorded to extract benchmark force profiles and inform reference trajectory generation. |
| **DexCatch** | Fast contact event handling and impedance regulation complement dynamic manipulation and impact management studies. |
| **6D Pose Estimation** | The vision module for food localization and cut planning builds on the lab's existing vision pipelines. |
| **HyperGraph ROS** | The on-tool sensor interface integrates smoothly with the lab's distributed middleware setup. |
| **Cooking Robot Focus** | Clean slicing provides a missing building block toward end-to-end autonomous cooking and meal preparation. |
| **Industry Connections (Meishanshi / 美膳狮)** | Practical tool-level force sensing is directly relevant to commercial automated cooking platforms. |

The lab has established strength in visual perception and manipulation learning. This project introduces a contact-level sensing and high-rate control module, expanding the lab's reach into delicate culinary tasks like slicing, peeling, and carving.

---

## 5. Expected Contributions

1. **On-tool sensing module (TacBlade)**: A sensorized tool interface specifically tailored for knife-based robotic cutting, provided with open hardware design files and firmware.
2. **Phase-adaptive impedance control**: A control strategy addressing impact and fracture transitions with formal passivity and stability considerations.
3. **Deformable cutting experimental dataset**: A systematic evaluation of food slicing dynamics across varying sharpness, ripeness, and food textures.
4. **Hierarchical vision-tactile integration**: A modular framework combining slower visual planning with fast, on-tool contact regulation.

---

## 6. Publication Plan

| Target | Timeline | Focus |
|:-------|:---------|:------|
| **IEEE RA-L / IROS 2028** | Submit Early 2028 (Year 2) | Core system design, on-tool sensing, phase-aware control, and preliminary benchmarks. |
| **IEEE ICRA / T-RO 2029** | Submit Late 2028 / Early 2029 (Year 3) | Advanced multi-food generalization, vision-tactile integration, stability proofs, and comprehensive experimental dataset. |

### Conference Fit

This work sits at the intersection of contact-rich manipulation, tactile and force sensing, and compliant robot control, all of which are core topics at IROS and ICRA. Combining an explicit physical mechanics formulation with embedded hardware implementation and practical food robotics benchmarks provides a balanced, publishable submission.

---

## 7. Timeline (3-Year Program)

### Year 1: Coursework, Fundamentals & Early Prototyping (2026 to 2027)
- **Fall 2026**: Complete Master's core coursework; in-depth literature review on cutting dynamics, impedance control, and contact mechanics; initial sensor bench testing.
- **Spring 2027**: Complete remaining coursework; mechanical design of tool interface; rapid breadboard/Nucleo prototype for preliminary force and vibration signal acquisition.
- **Summer 2027**: Transition to full-time lab research; initial data collection of blade-food contact signatures; define baseline experimental protocols.

### Year 2: System Development, Integration & First Publication (2027 to 2028)
- **Fall 2027**: Custom hardware revision with embedded sensing; firmware development for on-board filtering and phase transition detection; preliminary robot integration.
- **Winter 2027 to 2028**: Implement phase-switching impedance control and virtual energy tank passivity architecture; conduct primary cutting trials on tomatoes.
- **Spring 2028**: Prepare and submit initial manuscript to **IEEE RA-L / IROS 2028**; integrate visual perception for automated cut trajectory generation.
- **Summer 2028**: Refine controller based on initial review feedback; expand vision-force handoff testing.

### Year 3: Scaling, Multi-Food Generalization & Thesis Defense (2028 to 2029)
- **Fall 2028**: Large-scale multi-food generalization campaign across varying food textures, skin toughness, and blade sharpness levels; long-term durability testing.
- **Winter 2028 to 2029**: Manuscript preparation and submission for second milestone paper (**IEEE ICRA / T-RO 2029**).
- **Spring 2029**: Final system polish, packaging open-source hardware/software releases, and writing Master's thesis.
- **May to June 2029**: Master's thesis defense and graduation.

---

## 8. Long-Term Vision

### 8.1 Expanding Autonomous Cooking Capabilities

In the short to medium term, this project fills an important operational gap in robotic food preparation. Equipping a robot to slice, dice, and carve alongside existing capabilities like stirring, tossing, and plating brings systems closer to complete meal automation.

### 8.2 Autonomous Food Experience Booths

Beyond laboratory research, there is clear practical potential in compact automated food kiosks. Autonomous preparation units could be deployed in public spaces, transit hubs, or commercial food courts:

- **Fresh fruit platters**: Automated slicing and serving of fresh fruit to order.
- **Salad and bowl bars**: Precise, on-demand dicing and portioning of ingredients.
- **Slicing stations**: Delicate culinary prep operating reliably as an engaging customer experience.

Such kiosks provide an engaging visual experience while maintaining high consistency and operational efficiency, running autonomously with minimal on-site staffing requirements. The sensor integration, control techniques, and food-handling methods developed in this research serve as the core technical foundation for such applications.

### 8.3 Future Work: Toward Foundation Models & A Unified Manipulation Skill Library

Looking beyond specialized cutting controllers, this research establishes the foundational sensory and motor primitives for culinary tool use that can be integrated into broader **Embodied AI Foundation Models**:

- **Pre-Trained Skill Libraries (ADEPT Paradigm)**: Drawing from recent breakthroughs in dexterous pre-training such as **ADEPT** (Lee et al., CoRL 2026), our cutting dynamics and impedance controllers can be encapsulated as reusable motor priors. Instead of training food preparation behaviors from scratch, downstream applications can post-train on top of these verified contact-rich skills.
- **Open-Source Model Integration**: Experimental cutting trajectories and multi-modal contact data will be structured to interface with open-source foundation platforms—including **Hugging Face LeRobot**, **Octo (Open X-Embodiment)**, and **OpenVLA**. This connects specialized cutting mechanics to generalized language-conditioned manipulation (*"slice the tomato into 5mm rings"*).
- **Unified Robot Operating Infrastructure**: In synergy with the laboratory's ongoing work on hardware-agnostic teleoperation (*Open TeleDex*) and emerging unified OS initiatives (e.g., *OpenMind OM1* and *NVIDIA Isaac Lab*), these manipulation skills can be retargeted seamlessly across diverse robotic embodiments, from tabletop single-arm manipulators to dual-arm humanoid platforms (DexCatch).

---

I would welcome the opportunity to discuss this direction further and refine the plan according to your suggestions.

---

**[Your Name]**
[Your Email]
DEX-ROB Lab, Tianjin University
