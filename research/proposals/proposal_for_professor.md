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

$$\mathbf{M}_d \ddot{\tilde{\mathbf{x}}} + \mathbf{D}_d^{(q)} \dot{\tilde{\mathbf{x}}} + \mathbf{K}_d^{(q)} \tilde{\mathbf{x}} = \mathbf{F}_{ext}$$

where $q \in \{1, 2, 3, 4\}$ denotes the active phase, and $\tilde{\mathbf{x}} = \mathbf{x} - \mathbf{x}_d$ represents deviation from the planned path.

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
| **IEEE RA-L / IROS 2028** | Submit Mar 2028 | Full system design, on-tool sensing, phase-aware control, and experimental benchmark. |
| **ICRA 2029** (Follow-up) | Submit Sep 2028 | Extended multi-food manipulation, generalization analysis, and demonstration-guided trajectory tuning. |

### Conference Fit

This work sits at the intersection of contact-rich manipulation, tactile and force sensing, and compliant robot control, all of which are core topics at IROS and ICRA. Combining an explicit physical mechanics formulation with embedded hardware implementation and practical food robotics benchmarks provides a balanced, publishable submission.

---

## 7. Timeline

| Period | Milestone |
|:-------|:---------|
| **Oct to Nov 2026** | Literature review, sensor selection, and mechanical adapter design. |
| **Dec 2026** | Rapid proof-of-concept prototype for initial signal acquisition. |
| **Jan 2027** | Embedded firmware development for signal filtering and phase transition detection. |
| **Feb 2027** | Integration with lab manipulator arm and ROS 2 environment for preliminary cutting trials. |
| **Mar to Apr 2027** | Controller refinement, tuning passivity layer, and transition timing. |
| **May 2027** | Integration with visual perception for automated cut placement. |
| **Jun to Jul 2027** | Refined hardware revision with custom electronics and durable casing. |
| **Aug to Oct 2027** | Full experimental trials and cross-food generalization testing. |
| **Nov 2027 to Jan 2028** | Experimental data analysis and manuscript preparation. |
| **Feb to Mar 2028** | Submission to RA-L / IROS 2028. |
| **Apr to Jun 2028** | Master's thesis completion and defense. |

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

---

I would welcome the opportunity to discuss this direction further and refine the plan according to your suggestions.

---

**[Your Name]**
[Your Email]
DEX-ROB Lab, Tianjin University
