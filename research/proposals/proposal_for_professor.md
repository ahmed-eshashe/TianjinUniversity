# Research Proposal: Vision-Tactile Fusion for Adaptive Cutting of Deformable Foods

**Proposed by:** [Your Name]
**Advisor:** Prof. Shan An (安山)
**Lab:** DEX-ROB Lab, School of Electrical and Automation Engineering, Tianjin University
**Program:** M.S. in Control Science and Engineering
**Date:** September 2026

---

## 1. Motivation

Cutting deformable foods — slicing tomatoes, dicing onions, portioning soft proteins — is one of the last unsolved manipulation primitives in food service automation. While our lab and the broader community have made remarkable progress in dexterous grasping (DexCatch, CoRL 2024), teleoperation (Open TeleDex), and high-speed manipulation (Astribot S1), **no existing system can reliably cut a tomato**.

The reason is a fundamental sensing and control problem. Cutting involves a **fracture event** — the instant the knife punctures the food's skin. At this moment:

- The cutting force drops by 50–80% within ~5 milliseconds
- If the robot doesn't react, the knife plunges into the soft interior, crushing the food
- Vision cannot help: the blade occludes the contact zone, and cameras at 30 Hz are too slow to catch a 5 ms event
- Wrist-mounted F/T sensors are delayed 15–25 ms due to tool inertia and structural compliance

This is why the world's most advanced cooking robots can stir-fry, flip, and pour — but still cannot cut. Solving this would unlock the final missing capability for fully autonomous food preparation.

---

## 2. Research Questions

1. **Can on-tool force and vibration sensing detect cutting phase transitions (skin puncture, interior flow, board contact) with sub-millisecond latency?**

2. **Does phase-aware switching of impedance parameters improve cutting quality over constant-impedance or vision-only control, and can we guarantee stability across the fracture discontinuity?**

3. **How much does on-tool sensing outperform wrist-mounted F/T sensing for cutting tasks?**

---

## 3. Proposed Approach

### 3.1 System Architecture

The system combines two complementary sensing modalities in a hierarchical architecture:

**Vision Layer (30 Hz)** — spatial planning:
- Food segmentation and localization (leveraging the lab's existing perception models)
- Slice position planning from measured object geometry
- Post-cut quality verification

**On-Tool Force Layer (1 kHz)** — real-time cutting control:
- A compact sensorized tool adapter ("TacBlade") mounted at the knife-handle interface, combining strain gauges for quasi-static force measurement with piezoelectric elements for high-frequency fracture vibration detection
- On-board microcontroller running analytical phase detection (a threshold-based state machine — no neural network training required)
- Phase-switched impedance parameters transmitted to the robot's joint controller at 1 kHz

**The key insight:** Vision tells the robot *where* to cut. On-tool sensing controls *how hard* to cut — and critically, catches the fracture event that vision cannot see.

### 3.2 Cutting Phase Model

The cutting process is modeled as a hybrid dynamical system with four discrete phases:

| Phase | Physical Process | Impedance Strategy |
|:------|:----------------|:------------------|
| 1. Skin deformation | Elastic membrane stretches under knife | High stiffness — push through resistance |
| 2. Puncture | Fracture — force drops 50–80% in ~5 ms | **Low stiffness + high damping** — arrest forward slam |
| 3. Interior cutting | Viscoplastic flow — low, variable force | Low stiffness — gentle steady-state |
| 4. Exit / board contact | Second skin + rigid stop | Medium stiffness + high damping — decelerate |

Phase transitions are detected from on-tool signals: the force derivative $\dot{F}_z$ captures the force drop, while piezoelectric burst energy $E_{burst}$ captures the acoustic emission of skin fracture — providing a ~1 ms detection advantage over force alone.

### 3.3 Adaptive Impedance Control with Stability Guarantee

The impedance law follows the robot's vision-planned reference trajectory $\mathbf{x}_d(t)$ with phase-dependent compliance:

$$\mathbf{M}_d \ddot{\tilde{\mathbf{x}}} + \mathbf{D}_d^{(q)} \dot{\tilde{\mathbf{x}}} + \mathbf{K}_d^{(q)} \tilde{\mathbf{x}} = \mathbf{F}_{ext}$$

where $q \in \{1, 2, 3, 4\}$ is the detected cutting phase, and $\tilde{\mathbf{x}} = \mathbf{x} - \mathbf{x}_d$ is the deviation from the vision reference.

Switching impedance parameters at phase transitions risks injecting energy. A **virtual energy tank** framework guarantees passivity: an auxiliary state $s(t)$ accumulates dissipated damping energy during each phase, and "spends" it at transitions. If insufficient energy is stored, the transition is delayed — ensuring the system remains passive across all phase switches.

This yields a formal **Input-to-State Stability (ISS)** proof — a novel extension of energy tank methods to event-triggered phase switching driven by on-tool sensing, which constitutes the core control-theoretic contribution.

### 3.4 Experimental Design

**Primary experiment:** 750 tomato cuts (50 tomatoes × 5 ripeness levels × 3 knife sharpness conditions), comparing five conditions:

| Condition | Vision | Force Sensing | Controller |
|:----------|:------:|:------------:|:----------:|
| A. Position control | ✅ | ❌ | Fixed trajectory |
| B. Vision-only adaptive | ✅ | ❌ | Vision-estimated compliance |
| C. Wrist F/T + vision | ✅ | Wrist only | Adaptive (slow) |
| D. On-tool force only | ❌ | ✅ TacBlade | Phase-switched |
| E. **Vision + TacBlade** | ✅ | ✅ TacBlade | Phase-switched |

**Metrics:** Slice thickness consistency (σ), juice loss (% mass), post-puncture force overshoot, and human-rated visual quality.

**Generalization:** 10 additional food types (cucumber, kiwi, bread, cheese, tofu, etc.) to validate cross-food transfer without re-tuning.

> The 750-cut scale would be the most rigorous quantitative robotic cutting evaluation in the literature. Most existing food cutting papers present 5–10 qualitative examples.

---

## 4. Fit with DEX-ROB Lab

This research is designed to extend the lab's existing capabilities into a new physical domain:

| Lab Strength | How This Work Extends It |
|:------------|:------------------------|
| **Open TeleDex** | Human chef cutting demonstrations can be recorded to provide reference force profiles for comparison — and in future work, for learning impedance trajectories from expert demonstrations |
| **DexCatch** | The phase-switching impedance framework generalizes to other dynamic contact tasks in the lab's pipeline: catching, flipping, stirring, tool handovers |
| **6D Pose Estimation** | The vision pipeline for food localization and slice planning directly builds on the lab's existing edge-guided pose estimation work |
| **HyperGraph ROS** | The on-tool sensor's CAN-FD interface integrates naturally into the lab's multi-device computing architecture |
| **Cooking Robot Focus** | Cutting is the single most requested missing capability in cooking automation — this directly enables complete food preparation pipelines |
| **Tianjin University × Meishanshi (美膳狮)** | The resulting technology is directly applicable to Meishanshi-class commercial cooking platforms, strengthening the university-industry connection |

**Strategic positioning:** The lab's portfolio excels at perception and policy learning. This proposal adds the **contact-level sensing and control layer** for tool-use tasks — a complementary research direction that opens up a new class of problems (cutting, peeling, scraping, spreading) for the lab's existing learning and planning frameworks.

---

## 5. Expected Contributions

1. **On-tool sensing module (TacBlade)** — the first sensorized tool interface designed for robotic cutting, with open-source design files and firmware
2. **Phase-switching impedance controller** — with formal passivity/ISS stability guarantee across fracture-induced phase transitions
3. **Large-scale cutting benchmark** — 750+ cuts with quantitative metrics across ripeness and sharpness (establishing a new standard for evaluation rigor in this domain)
4. **Vision-force hierarchical fusion framework** — a reusable architecture for combining slow visual planning with fast force-driven contact control, applicable beyond cutting

---

## 6. Publication Plan

| Target | Timeline | Focus |
|:-------|:---------|:------|
| **IEEE RA-L + IROS 2028** | Submit Mar 2028 | Full system: on-tool sensing + phase-switching controller + 750-cut benchmark |
| **ICRA 2029** (stretch) | Submit Sep 2028 | Extension: multi-food generalization + learned impedance profiles from Open TeleDex demos |

### Conference Fit

This work sits at the intersection of **contact-rich manipulation**, **impedance/force control**, and **sensing hardware** — all core topics at IROS and ICRA. The combination of:
- A **novel hardware sensing contribution** (on-tool, not just another fingertip sensor)
- A **formal control theory result** (passivity across hybrid phase transitions)
- **Large-scale quantitative benchmarks** (750 cuts, ablation studies, cross-food generalization)
- A **compelling application domain** (food automation)

makes for a strong submission that appeals to both the manipulation and control communities.

---

## 7. Timeline

| Period | Milestone |
|:-------|:---------|
| **Oct–Nov 2026** | Literature review; hardware design (sensorized tool adapter schematic + mechanical design) |
| **Dec 2026** | Prototype v0 (dev board + 3D-printed knife clamp — rapid proof of concept) |
| **Jan 2027** | Firmware: signal processing, phase detection, communication driver |
| **Feb 2027** | Integration with lab robot arm + ROS 2; first cutting experiments |
| **Mar–Apr 2027** | Impedance controller + energy tank passivity layer; iterative tuning |
| **May 2027** | Vision pipeline integration (segmentation + trajectory planning) |
| **Jun–Jul 2027** | Hardware v1: polished PCB, machined clamp, refined sensor layout |
| **Aug–Oct 2027** | Full experimental campaign (750 cuts + generalization) |
| **Nov 2027–Jan 2028** | Data analysis + paper writing |
| **Feb–Mar 2028** | Submit RA-L / IROS 2028 |
| **Apr–Jun 2028** | Thesis writing and defense |

---

## 8. Required Resources

| Resource | Details | Est. Cost |
|:---------|:--------|:----------|
| Microcontroller dev board | For rapid prototyping (v0) | ¥80 |
| Strain gauges + amplifier ICs | Force measurement components | ¥200 |
| Piezoelectric elements + front-end | Vibration/fracture detection | ¥100 |
| PCB fabrication | Sensorized tool adapter (v1, 10 pcs) | ¥1,500 |
| Machined clamp body | CNC aluminum (10 pcs) | ¥2,500 |
| Food items | Tomatoes + 10 other food types for 750+ cuts | ¥4,000 |
| Knives | 3 sharpness levels, controlled wear | ¥300 |
| Miscellaneous | Connectors, wiring, 3D printing, consumables | ¥500 |
| **Total** | | **~¥9,200 (~$1,300 USD)** |

All computation uses existing lab infrastructure (robot arm, cameras, workstation). No additional major equipment is needed.

---

## 9. Long-Term Vision

### 9.1 Completing the Cooking Robot Stack

In the near term, TacBlade fills the last major gap in robotic food preparation. A robot that can cut, slice, and dice — in addition to stirring, flipping, and pouring — becomes capable of **end-to-end meal preparation** for the first time. This positions the lab at the forefront of cooking automation research, with direct relevance to partners like Meishanshi and the broader food-service robotics industry.

### 9.2 Autonomous Food Experience Booths

Beyond the academic research, there is an exciting commercial application: **autonomous food-cutting experience kiosks**.

Imagine a compact booth — similar to a bubble tea kiosk or a takoyaki stand — where a robotic arm with TacBlade prepares fresh-cut dishes in front of the customer:

- **Fresh fruit platters** — the robot slices seasonal fruits to order, arranges them on a plate
- **Salad bars** — the robot dices vegetables live, customers choose ingredients
- **Sashimi / carpaccio stations** — precision thin-slicing as a visual performance
- **Smoothie prep** — robot cuts fresh fruit, loads the blender, serves

The appeal is twofold:
1. **The experience** — watching a robot skillfully cut food is inherently entertaining and shareable on social media. Customers come for the novelty, the "wow factor" of seeing precise robotic knife work
2. **Passive income** — once deployed, the booth operates autonomously with minimal staffing. It needs only periodic ingredient restocking and cleaning. Multiple booths can be deployed across malls, airports, university campuses, and tourist areas as a scalable, location-based business

This model is analogous to how automated coffee kiosks (Café X, Ratio) and ice cream robots have scaled — but with the added visual spectacle of live cutting. The booth format is particularly well-suited to China's thriving night market, shopping mall food court, and campus canteen ecosystems.

The research conducted during this Master's thesis — the sensing module, the adaptive cutting controller, the food-type generalization — forms the **core enabling technology** for such a product.

---

I would welcome the opportunity to discuss this direction further and refine it based on your guidance.

---

**[Your Name]**
[Your Email]
DEX-ROB Lab, Tianjin University
