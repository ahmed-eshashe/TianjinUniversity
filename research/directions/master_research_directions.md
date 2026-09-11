# Master's Research Directions: Tactile Edge Intelligence for Contact-Rich Manipulation

**For:** Incoming Master's Student, Control Science & Engineering, Tianjin University (DEX-ROB Lab)
**Advisor:** Prof. Shan An (安山) — Embodied Intelligence, Imitation Learning, Dexterous Manipulation
**Date:** September 2026

---

## Executive Summary

This document proposes **four distinct research directions**, each architected to satisfy three simultaneous constraints:

1. **IROS/ICRA-publishable rigor** — formal control theory, provable stability, quantitative ablation benchmarks
2. **Hardware-centric "add-on" strategy** — rigid-flex PCB tactile modules that bolt onto existing manipulators (no full-arm builds)
3. **B2B commercial spin-off** — OEM-ready mechatronic subsystems for food automation and humanoid robotics

Each direction exploits a **specific gap** identified in the research landscape:

| Gap | Evidence |
|:----|:---------|
| Existing tactile sensors (GelSight, DIGIT, BioTac) run at 30–60 Hz with 20–60 ms latency — **incompatible with 500–1000 Hz impedance loops** | TacO benchmark (ICRA 2025), NeuralTouch (IROS 2025) |
| No commercial tactile module is **food-safe (IP69K + FDA 21 CFR)** — GelSight paint flakes, XELA silicones delaminates in 80°C washdown | Commercial survey: all existing products fail EHEDG Doc 44 |
| Edge tactile computing exists in isolation (GelNeuro, TinyML) but **none close the loop to real-time impedance control** over CAN-FD | Edge computing survey: no paper demonstrates full sensor→edge→motor loop at 1 kHz |
| DEX-ROB Lab has strong **Open TeleDex** and **DexCatch** but lacks hardware-level tactile sensing — a complementary fit | Lab publication survey: no tactile hardware papers in lab portfolio |

> [!IMPORTANT]
> **Strategic Alignment with DEX-ROB Lab:** Prof. An's lab has world-class expertise in teleoperation (Open TeleDex), policy learning (DexCatch/SCRL), and food-service robotics context (Tianjin University's deep ties to Meishanshi cooking robots, Embodied-R1.5 milk tea demonstrations). What the lab currently **lacks** is the hardware tactile sensing layer — your rigid-flex PCB and embedded control expertise fills this gap precisely. Every direction below is designed to produce a hardware module that plugs directly into the lab's existing software/learning pipelines.

---

## Direction 1: Tactile-Driven Variable Impedance Control with Provable Passivity for Food Manipulation

### The Thesis in One Sentence
*Design a rigid-flex PCB tactile fingertip module with on-board STM32 edge inference that closes a passivity-guaranteed variable impedance control loop at 1 kHz over CAN-FD, enabling a robot to manipulate fragile food items (tofu, eggs, pastries) without crushing or dropping them.*

---

### 🎓 IROS/ICRA Academic Angle

#### Fundamental Research Gap
Current tactile-driven impedance controllers face a **fatal bandwidth mismatch**: vision-based tactile sensors (GelSight, DIGIT) output at 30–60 Hz, while stable impedance control demands ≥500 Hz. Feeding low-rate, phase-lagged tactile signals into inner impedance loops **injects energy and violates passivity**, causing contact bounce, limit cycles, or explosive oscillations (documented in the Virtual Energy Tank literature). No existing work demonstrates a complete **sensor → edge inference → impedance modulation** pipeline that runs entirely at 1 kHz with formal passivity guarantees.

#### Mathematical Formulation

**1. Tactile-Modulated Variable Impedance Law:**

The Cartesian impedance equation at the end-effector:

$$\mathbf{M}_d (\ddot{\mathbf{x}} - \ddot{\mathbf{x}}_d) + \mathbf{D}_d (\dot{\mathbf{x}} - \dot{\mathbf{x}}_d) + \mathbf{K}_d(t) (\mathbf{x} - \mathbf{x}_d) = \mathbf{F}_{ext}$$

The stiffness matrix $\mathbf{K}_d(t)$ is decomposed in a contact-aligned frame defined by the tactile surface normal $\hat{\mathbf{n}}$:

$$\mathbf{K}_d(t) = \mathbf{R}(\hat{\mathbf{n}}) \begin{bmatrix} K_{\parallel}(s_{slip}) & 0 & 0 \\ 0 & K_{\parallel}(s_{slip}) & 0 \\ 0 & 0 & K_{\perp}(F_n^{tac}) \end{bmatrix} \mathbf{R}^T(\hat{\mathbf{n}})$$

where:
- $K_{\perp}(F_n^{tac})$: Normal stiffness adapted by the tactile normal force to limit impact — softens on contact to absorb collision energy
- $K_{\parallel}(s_{slip})$: Tangential stiffness modulated by the incipient slip metric $s_{slip} \in [0,1]$ — stiffens to arrest slip, relaxes to allow controlled sliding
- $s_{slip}$: Computed on-board from the ratio of shear-to-normal force approaching the friction cone boundary: $s_{slip} = \|\mathbf{f}_t\| / (\mu \cdot f_n)$

**2. Passivity Guarantee via Virtual Energy Tank:**

When $\dot{\mathbf{K}}_d(t) \neq \mathbf{0}$, variable stiffness injects virtual energy:

$$P_{inj}(t) = \frac{1}{2} \tilde{\mathbf{x}}^T \dot{\mathbf{K}}_d(t) \tilde{\mathbf{x}}$$

A scalar energy tank state $s(t)$ enforces passivity:

$$\dot{s}(t) = \frac{\sigma(t)}{s(t)} \dot{\tilde{\mathbf{x}}}^T \mathbf{D}_d \dot{\tilde{\mathbf{x}}} - \frac{\gamma(t)}{s(t)} P_{inj}(t)$$

$$\gamma(t) = \begin{cases} 1, & \text{if } T(s) = \frac{1}{2}s^2 \geq T_{min} \\ 0, & \text{if } T(s) < T_{min} \text{ and } P_{inj} > 0 \end{cases}$$

When the tank is depleted, stiffness adaptation is frozen — guaranteeing the interconnected system remains strictly passive w.r.t. the external port $({\mathbf{F}_{ext}}, \dot{\mathbf{x}})$.

**3. Lyapunov Stability Proof (ISS under tactile noise):**

$$V(\mathbf{x}, \dot{\mathbf{x}}, s) = \frac{1}{2} \dot{\mathbf{q}}^T \mathbf{M}(\mathbf{q}) \dot{\mathbf{q}} + \frac{1}{2} \tilde{\mathbf{x}}^T \mathbf{K}_d \tilde{\mathbf{x}} + \frac{1}{2} s^2$$

$$\dot{V} \leq -c_1 \|\tilde{\mathbf{x}}\|^2 - c_2 \|\dot{\tilde{\mathbf{x}}}\|^2 + \alpha(\|\tilde{\mathbf{F}}_t\|)$$

proving Input-to-State Stability (ISS) bounded by tactile measurement noise $\tilde{\mathbf{F}}_t$.

#### Benchmarking Strategy (Publication-Ready)

| Experiment | Metrics | Baselines |
|:-----------|:--------|:----------|
| **Fragile food grasping** (tofu blocks, eggs, cream puffs, paper cups with liquid) | Success rate, max contact force, force overshoot ratio, object deformation | Vision-only (no tactile), constant-impedance (no adaptation), low-rate GelSight at 30 Hz |
| **Wet/oily object handling** (condensation bottles, greased containers) | Slip arrest time (ms), grip force efficiency $F_{grip}/F_{min,required}$ | Open-loop force, wrist F/T only (no fingertip sensing) |
| **Ablation: sampling rate** | Sweep tactile loop from 30 Hz → 100 Hz → 500 Hz → 1 kHz; measure passivity violations, contact bounce events | Demonstrates hardware contribution is essential |
| **Ablation: energy tank** | Tank ON vs. tank OFF — measure oscillation amplitude, energy injection events | Proves theoretical contribution |
| **Comparison with TacO benchmark tasks** | Align with TacO standardized protocols for cross-paper comparability | GelSight Mini, ReSkin, capacitive baselines from TacO |

#### Novelty Claim for Reviewers
*"We present the first tactile variable impedance controller that operates entirely at 1 kHz via edge-computed 3-axis force inference on a rigid-flex PCB fingertip, with formal passivity guarantees via a virtual energy tank — eliminating the bandwidth bottleneck of vision-based tactile sensors in contact-rich food manipulation."*

---

### 🔧 Hardware & Embedded Architecture

#### The Module: "TacEdge Fingertip"

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CROSS-SECTION: TacEdge Fingertip                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│    ┌─────────────────────────────────────────────────────┐          │
│    │  Food-Grade Silicone Overmold (FDA 21 CFR 177.2600) │          │
│    │  Shore A 30-40, IP69K hermetic seal                 │          │
│    │  ┌─────────────────────────────────────────────┐    │          │
│    │  │  Embedded NdFeB Micro-Magnets (3×4 array)   │    │          │
│    │  │  Ø1.5mm × 1mm, N52 grade                    │    │          │
│    │  └─────────────────────────────────────────────┘    │          │
│    └────────────────────┬────────────────────────────────┘          │
│                         │ (Compression changes B-field)             │
│    ┌────────────────────┴────────────────────────────────┐          │
│    │     RIGID-FLEX PCB STACK (4-layer, 0.8mm total)     │          │
│    │  ┌──────────────────────────────────────────────┐   │          │
│    │  │ Layer 1 (Top): 3×4 = 12 MLX90393 3-axis Hall │   │          │
│    │  │   magnetometers (I2C, 14-bit, 1 kHz/channel) │   │          │
│    │  ├──────────────────────────────────────────────┤   │          │
│    │  │ Layer 2: GND plane + EMI shielding            │   │          │
│    │  ├──────────────────────────────────────────────┤   │          │
│    │  │ Layer 3: Power distribution (3.3V, filtering) │   │          │
│    │  ├──────────────────────────────────────────────┤   │          │
│    │  │ Layer 4 (Bottom): STM32H723 MCU + CAN-FD PHY │   │          │
│    │  │   + NTC thermistor (thermal drift comp.)      │   │          │
│    │  └──────────────────────────────────────────────┘   │          │
│    │                                                      │          │
│    │  [Rigid Island]──flex──[Rigid Island]──flex──[MCU]   │          │
│    │   (sensor array)  ↕    (sensor array)  ↕   (compute) │          │
│    └──────────────────────────────────────────────────────┘          │
│                         │                                           │
│                    CAN-FD Bus (5 Mbps)                              │
│                    ↓                                                │
│    [Robot Joint Controller / ROS 2 Bridge Node]                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### Bill of Materials (Core)

| Component | Part | Qty | Unit Cost (est.) |
|:----------|:-----|:----|:-----------------|
| 3-axis Hall magnetometer | MLX90393 (Melexis) | 12 | \$2.50 |
| MCU | STM32H723VGT6 (Cortex-M7, 550 MHz, DSP+FPU) | 1 | \$6.00 |
| CAN-FD transceiver | TCAN4550 (TI) or MCP2518FD | 1 | \$3.00 |
| NTC thermistor | 10kΩ ±1% | 2 | \$0.30 |
| Rigid-flex PCB | 4-layer, polyimide flex, ENIG | 1 | \$15 (qty 100) |
| Food-grade silicone cap | Custom LSR mold (Shore A 35) | 1 | \$3 (qty 1000) |
| NdFeB magnets | N52, Ø1.5×1mm, Ni-coated | 12 | \$0.15 |
| **Total BOM** | | | **~\$65** |

#### Firmware Architecture (STM32H723)

```
┌──────────────────────────────────────────────────────────────┐
│                   STM32H723 FIRMWARE STACK                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────┐     ┌─────────────────────────┐ │
│  │ TIMER ISR @ 1 kHz      │     │ CAN-FD TX @ 1 kHz       │ │
│  │ ┌────────────────────┐ │     │ ┌───────────────────────┐│ │
│  │ │ 1. DMA I2C burst   │ │     │ │ Packed 24-byte frame: ││ │
│  │ │    read 12× Hall   │ │     │ │ • Fx, Fy, Fz (int16)  ││ │
│  │ │    (Bx,By,Bz)×12   │ │ ──► │ │ • s_slip (uint8)      ││ │
│  │ │ 2. Thermal comp.   │ │     │ │ • contact_normal (3×   ││ │
│  │ │    via NTC lookup   │ │     │ │   int8, unit vec)      ││ │
│  │ │ 3. Calibration     │ │     │ │ • contact_centroid     ││ │
│  │ │    matrix multiply  │ │     │ │   (2× uint8, taxel    ││ │
│  │ │    B → F (36 coeff) │ │     │ │   coordinates)         ││ │
│  │ │ 4. Slip metric     │ │     │ │ • temperature (int8)   ││ │
│  │ │    s = |Ft|/(μ·Fn) │ │     │ │ • timestamp (uint16)   ││ │
│  │ │ 5. Contact centroid│ │     │ └───────────────────────┘│ │
│  │ │    & normal estim.  │ │     └─────────────────────────┘ │
│  │ └────────────────────┘ │                                  │
│  └────────────────────────┘                                  │
│                                                              │
│  ┌────────────────────────┐     ┌─────────────────────────┐ │
│  │ Background Tasks       │     │ ROS 2 Micro-ROS (opt.)  │ │
│  │ • Auto-calibration     │     │ • Topic: /tactile/wrench│ │
│  │ • μ estimation (EKF)   │     │ • Topic: /tactile/slip  │ │
│  │ • Health monitoring    │     │ • Service: /tactile/cal │ │
│  └────────────────────────┘     └─────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

#### Interface with Robot Trajectory Planner

```
  TacEdge Fingertip          CAN-FD Bus (5 Mbps)           Robot Controller
  ┌─────────────┐            ┌───────────────┐            ┌──────────────────┐
  │ STM32H723   │ ──CAN-FD──►│ CAN-FD Bridge │──EtherCAT──►│ Impedance Loop   │
  │ 1 kHz wrench│            │ (STM32 or     │  or ROS 2  │ Kd(t) = f(slip)  │
  │ + slip flag │            │  ROS 2 node)  │            │ Energy tank check│
  └─────────────┘            └───────────────┘            └──────────────────┘
                                                                    │
                                                           Joint torque commands
                                                                    ▼
                                                          Existing Robot Arm
                                                    (xArm, UR5, Franka, Astribot)
```

---

### 💰 Commercial Spin-Off

#### Product: "TacEdge" — OEM Tactile Fingertip Module

| Attribute | Specification |
|:----------|:-------------|
| **Form factor** | Snap-on fingertip cartridge (18mm × 14mm × 8mm) |
| **Interface** | CAN-FD (5 Mbps), optional Micro-ROS over USB-C |
| **Output** | 3-axis force vector, slip metric, contact normal, contact centroid @ 1 kHz |
| **Protection** | IP69K, FDA food-grade silicone, -20°C to +120°C |
| **Replaceable skin** | Snap-fit silicone cap (consumable, \$3/unit) |
| **Target price** | \$149–\$299 per fingertip (vs. \$355 DIGIT, \$3,400 Robotiq TSF) |

#### Target Customers

| Segment | Companies | Pain Point Solved |
|:--------|:----------|:-----------------|
| **Barista/cooking kiosks** | Richtech Robotics (ADAM), Café X, Miso Robotics, Meishanshi (美膳狮) | Grip wet cups, handle hot food, detect slip on oily surfaces |
| **Ghost kitchen automation** | Chef Robotics, Hyphen, Sweetgreen Infinite Kitchen | Fragile food portioning without crushing (tofu, pastries, lettuce) |
| **Humanoid hands** | Agibot (OmniHand), Fourier (GR-2/3), UBTECH (Walker S), Unitree (Dex5-1), Apptronik (Apollo) | Drop-in tactile upgrade for "numb" fingers at 10× lower cost than in-house development |
| **Cobot integrators** | Robotiq, Schunk, Weiss end-users | Retrofit existing 2F grippers with tactile feedback |

#### Business Model
- **Hardware sale**: \$149–\$299/fingertip (margins ~65% at BOM ~\$65)
- **Consumable revenue**: Silicone skin replacements at \$3/unit, replaced every 2–4 weeks in food environments
- **Licensing**: License the on-board slip detection firmware + passivity controller IP to humanoid OEMs

---

## Direction 2: Incipient Slip Detection & Arrest via Edge Spiking Neural Networks on Rigid-Flex Tactile Arrays

### The Thesis in One Sentence
*Develop a 12-taxel magnetic tactile array on a rigid-flex PCB that runs a spiking neural network (SNN) on-chip for sub-2ms incipient slip detection, coupled with a real-time grip force reflex controller — demonstrating that neuromorphic edge computation eliminates the latency bottleneck of deep-learning-based slip detectors.*

---

### 🎓 IROS/ICRA Academic Angle

#### Fundamental Research Gap
Incipient slip detection is a solved *classification* problem but an unsolved *real-time control* problem. Deep learning methods (3D CNNs, transformers on GelSight marker optical flow) achieve >95% detection accuracy but at 25–60 ms latency — by which time the object has already entered gross slip. Frequency-domain heuristics (vibration high-pass filters) are fast but fragile under varying surface textures, motor vibrations, and unknown friction. **No existing work co-designs a neuromorphic spike-based slip detector with a provable grip-force reflex law that guarantees slip arrest within a bounded time.**

The key physics: incipient micro-slip follows **Mindlin-Cattaneo mechanics**. When tangential force $T$ increases on an elastic fingertip pressed with normal force $P$, the contact patch of radius $a$ develops a growing annular slip zone with inner stick radius:

$$c = a \left(1 - \frac{T}{\mu P}\right)^{1/3}$$

The *rate of change* of the shear-to-normal force ratio across taxels encodes incipient slip as a **spatio-temporal wavefront** propagating from the contact periphery inward. This is naturally represented as asynchronous spike events — a perfect fit for SNN processing.

#### Mathematical Formulation

**1. Spike Encoding of Tactile Shear Rate:**

Each taxel $i$ outputs 3-axis magnetic flux $(B_{x,i}, B_{y,i}, B_{z,i})$ at 1 kHz. Define the shear rate signal:

$$\dot{s}_i(t) = \frac{d}{dt}\left(\frac{\sqrt{B_{x,i}^2 + B_{y,i}^2}}{|B_{z,i}|}\right)$$

Convert to spike trains via threshold crossing (Leaky Integrate-and-Fire neuron model):

$$\tau_m \frac{dv_i}{dt} = -v_i(t) + \dot{s}_i(t), \quad \text{spike when } v_i \geq v_{th}$$

**2. SNN Slip Classifier:**

A 2-layer spiking convolutional network processes the 12-channel spike raster:
- Layer 1: Spatial convolution over the 3×4 taxel grid (detecting peripheral-to-center wavefront)
- Layer 2: Temporal integration with lateral inhibition (distinguishing texture vibration from slip onset)
- Output: Binary slip probability $p_{slip}(t) \in \{0, 1\}$ with latency $\leq 2$ ms

**3. Reflex Grip Force Law with Bounded Arrest Time:**

Upon $p_{slip} = 1$, execute a proportional grip force increment:

$$\Delta F_n(t) = k_{reflex} \cdot \left(1 - \frac{c(t)}{a}\right) \cdot F_n(t)$$

where $k_{reflex}$ is tuned such that the stick zone recovers to $c \geq 0.9a$ within a guaranteed time bound $t_{arrest} \leq 5$ ms. Prove this bound via Lyapunov analysis on the Mindlin-Cattaneo stick-zone dynamics.

#### Benchmarking Strategy

| Experiment | Metrics | Baselines |
|:-----------|:--------|:----------|
| **Slip detection latency** | Time from incipient slip onset to detection (ms) | GelSight + CNN (25–60 ms), PapillArray + threshold (5–10 ms), HD computing (0.5 µs but no spatial info) |
| **Slip arrest on diverse objects** | Arrest success rate across 30+ objects (YCB set + food items: wet bottles, oily containers, eggs, raw tofu) | Fixed grip force, wrist F/T reflex, vision-only re-grasp |
| **Unknown friction coefficient** | Online $\mu$ estimation accuracy and adaptation speed across dry/wet/oily surfaces | Pre-calibrated $\mu$ baseline |
| **Ablation: SNN vs. conventional CNN** | Same tactile data, compare latency, power, and detection accuracy | INT8 quantized CNN on same STM32 |
| **Power consumption** | Total module power during active manipulation | Desktop GPU pipeline power |

#### Novelty Claim
*"We demonstrate the first neuromorphic incipient slip detector that processes spatio-temporal shear wavefronts from a magnetic tactile array using a spiking neural network running entirely on-chip at sub-2ms latency, coupled with a Mindlin-Cattaneo-grounded grip reflex law with provable bounded arrest time."*

---

### 🔧 Hardware & Embedded Architecture

Same rigid-flex PCB platform as Direction 1 (TacEdge fingertip), but with a firmware variant:

**Key Difference:** The STM32H723's DSP pipeline implements the SNN in fixed-point arithmetic using the CMSIS-NN library (or a custom SNN kernel exploiting the Cortex-M7 dual-issue FPU). The SNN model is trained offline in Python (snnTorch/Norse framework), exported as quantized weight tables, and compiled into the firmware.

**Alternative edge chip (stretch goal):** Replace STM32 with **SynSense Speck2e** neuromorphic SoC for true event-driven, sub-mW operation — relevant for battery-powered humanoid fingers.

#### Firmware Pipeline

```
┌──────────────────────────────────────────────────────────┐
│              SNN SLIP DETECTION PIPELINE                 │
│                                                          │
│  Hall Readout     Spike Encoder    SNN Inference   Reflex│
│  (DMA, 1kHz)  →  (LIF neuron)  →  (2-layer SCNN) → ΔFn │
│                                                     │    │
│  Total latency budget:                              │    │
│  ├─ I2C burst read: 400 µs                          │    │
│  ├─ Spike encoding: 50 µs                           │    │
│  ├─ SNN forward pass: 100 µs                        │    │
│  ├─ Reflex computation: 50 µs                       │    │
│  └─ CAN-FD TX: 200 µs                              │    │
│  TOTAL: ~800 µs (< 1 ms)                           │    │
│                                                     ▼    │
│                                              CAN-FD frame│
│                                              to gripper  │
│                                              motor driver│
└──────────────────────────────────────────────────────────┘
```

---

### 💰 Commercial Spin-Off

#### Product: "TacEdge Reflex" — Slip-Proof Fingertip Module

Same hardware as Direction 1, differentiated by firmware:
- **Standard firmware**: Outputs raw wrench + slip metric (for customer's own controller)
- **Reflex firmware**: Autonomously commands grip force adjustments over CAN-FD — the fingertip itself handles slip arrest without waiting for the host controller

**Key selling point for food automation**: *"Your robot will never drop a wet cup again."* The reflex loop is entirely local — even if the host PC or ROS 2 stack has a 50 ms hiccup, the fingertip catches slip autonomously.

---

## Direction 3: Sensorized Active-Compliance Wrist for Contact-Rich Tool Use

### The Thesis in One Sentence
*Design a compact, sensorized series-elastic wrist module with embedded 6-axis force sensing and tactile contact detection that provides programmable mechanical compliance for tool-use tasks (spatula flipping, knife cutting, ladle pouring), with an adaptive impedance controller that learns tool-specific compliance profiles from teleoperation demonstrations.*

---

### 🎓 IROS/ICRA Academic Angle

#### Fundamental Research Gap
Cooking and food-service robots must use **rigid tools** (spatulas, ladles, tongs, knives) that create high-bandwidth contact impacts. Current approaches either:
1. Use stiff industrial arms with wrist F/T sensors (ATI Nano17, Bota MiniONE) — these measure forces **after** they propagate through the arm's inertia, introducing 10–30 ms delay and heavy filtering artifacts
2. Use software-only compliance (virtual spring-damper in the joint controller) — which cannot absorb sharp impacts faster than the servo rate (typically 1 kHz max, often 250 Hz for ROS 2 controllers)

The gap: **no compact wrist module provides physical series-elastic compliance (mechanical bandwidth >100 Hz) combined with embedded multi-axis force sensing and a learning-based adaptive impedance policy** that tunes compliance to different tool-surface interactions.

#### Mathematical Formulation

**1. Series Elastic Actuator (SEA) Wrist Dynamics:**

The wrist introduces a compliant element with physical stiffness $K_s$ between the arm flange and the tool:

$$\mathbf{F}_{tool} = K_s (\mathbf{x}_{flange} - \mathbf{x}_{tool}) + D_s (\dot{\mathbf{x}}_{flange} - \dot{\mathbf{x}}_{tool})$$

The physical spring provides **intrinsic mechanical filtering** of high-frequency impacts — the arm "sees" a filtered force signal, while the tool absorbs the shock mechanically.

**2. Rendered Impedance via Wrist Actuation:**

A small rotary actuator in the wrist adjusts the rest position of the elastic element, rendering a desired task-space impedance:

$$\mathbf{F}_{rendered} = \mathbf{K}_d^{task}(\mathbf{x} - \mathbf{x}_d) + \mathbf{D}_d^{task}(\dot{\mathbf{x}} - \dot{\mathbf{x}}_d)$$

$$\mathbf{K}_d^{task} = f(\mathbf{z}_{demo}) \quad \text{— learned from teleoperation demonstrations}$$

**3. Impedance Profile Learning from Open TeleDex Demonstrations:**

Using Prof. An's Open TeleDex teleoperation framework, collect human demonstrations of tool-use tasks. Extract the implicit human impedance profile via:

$$\hat{\mathbf{K}}_h(t) = \mathbf{F}_{measured}(t) \cdot [\mathbf{x}(t) - \mathbf{x}_{ref}(t)]^{\dagger}$$

Fit a task-phase-conditioned Gaussian Mixture Model (TP-GMM) or Diffusion Policy to reproduce the impedance trajectory $\mathbf{K}_d^{task}(\phi)$ as a function of task phase $\phi \in [0, 1]$.

**4. Stability under Switching Tool Contacts:**

Tool-use tasks involve hybrid contact dynamics (free motion → impact → sliding → lift-off). Using switched-system Lyapunov theory with dwell-time conditions:

$$V_{total} = V_{elastic}(K_s) + V_{impedance}(\mathbf{K}_d) + V_{tank}(s)$$

Prove that the cascade of physical compliance + rendered impedance + energy tank remains passive across all tool-surface impact transitions.

#### Benchmarking Strategy

| Experiment | Metrics | Baselines |
|:-----------|:--------|:----------|
| **Spatula flipping** (pancakes, eggs, burgers on hot surface) | Success rate, peak impact force, food damage score | Stiff wrist + software compliance only, passive RCC (remote center compliance) |
| **Knife cutting** (vegetables, bread, soft cheese) | Cut quality (straightness), peak lateral force, blade tracking error | Position-controlled cutting, pure force control |
| **Ladle pouring** (soup, batter) with viscosity variation | Spill volume, pouring accuracy, flow rate control | Open-loop trajectory replay |
| **Tool generalization** | Transfer learned compliance to novel tools without re-training | Fixed-parameter impedance |
| **Comparison with Open TeleDex demonstrations** | Policy reproduction fidelity (DTW distance to human demo) | BC without impedance (position-only cloning) |

#### Novelty Claim
*"We present a compact series-elastic wrist module with embedded 6-axis force sensing that learns tool-specific impedance profiles from teleoperation demonstrations, providing physically-grounded mechanical compliance for contact-rich cooking tasks — bridging the gap between the Open TeleDex demonstration pipeline and safe, high-bandwidth tool-surface interaction."*

---

### 🔧 Hardware & Embedded Architecture

#### The Module: "CompliWrist" — Active Series-Elastic Wrist

```
┌─────────────────────────────────────────────────────────────┐
│              CompliWrist: Exploded Assembly View             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────────────┐                                      │
│   │ Robot Flange      │  ISO 9409-1 (31.5mm or 50mm)       │
│   │ (Bolt Pattern)    │                                      │
│   └────────┬─────────┘                                      │
│            │                                                │
│   ┌────────┴─────────┐                                      │
│   │ Hollow-Shaft BLDC │  Ø40mm, 0.5 Nm continuous          │
│   │ + Harmonic Drive  │  100:1 reduction, backdrivable      │
│   │ (1 DoF: roll)     │  Encoder: 16-bit absolute           │
│   └────────┬─────────┘                                      │
│            │                                                │
│   ┌────────┴─────────┐                                      │
│   │ Elastic Element   │  Titanium flexure (Ti-6Al-4V)       │
│   │ (Torsional Spring)│  K_s = 2–5 Nm/rad (tunable)        │
│   │ + Strain Gauges   │  4× half-bridge for torque sensing  │
│   └────────┬─────────┘                                      │
│            │                                                │
│   ┌────────┴─────────┐                                      │
│   │ 6-Axis F/T PCB   │  Rigid-flex, 6× strain gauge bridges│
│   │ (Embedded)        │  24-bit ADC (ADS1262), 2 kHz        │
│   │ + STM32H723       │  On-board wrench computation        │
│   └────────┬─────────┘                                      │
│            │                                                │
│   ┌────────┴─────────┐                                      │
│   │ Tool Quick-Connect│  Pneumatic or magnetic tool changer │
│   │ + Tactile Ring    │  4× Hall taxels around tool shaft   │
│   └──────────────────┘  (detect tool slip/rotation)         │
│                                                             │
│   Overall: Ø50mm × 45mm height, ~250g                      │
│   Interface: CAN-FD (dual-bus: force data + motor commands) │
└─────────────────────────────────────────────────────────────┘
```

#### Key Design Decisions
- **Physical compliance (not just virtual)**: The titanium flexure absorbs impact energy mechanically at >500 Hz bandwidth — impossible for any software controller
- **1 DoF actuation**: Only roll axis is actively compliant (sufficient for most tool-use tasks: flipping, stirring, cutting). Keeps cost and complexity low
- **Embedded F/T**: No external ATI/Bota sensor needed — the strain gauge bridges are integrated into the rigid-flex PCB, reducing cost from \$5,000+ to ~\$50 in components
- **Tool-shaft tactile ring**: 4 Hall-effect taxels around the tool quick-connect detect tool rotation and slippage — critical for spatula/ladle tasks

---

### 💰 Commercial Spin-Off

#### Product: "CompliWrist" — OEM Active-Compliant Wrist Module

| Attribute | Specification |
|:----------|:-------------|
| **Form factor** | ISO 9409-1 flange mount, Ø50mm × 45mm |
| **Degrees of freedom** | 1 DoF active (roll) + 2 DoF passive (pitch/yaw via flexure) |
| **Force sensing** | 6-axis, embedded, 2 kHz, ±50N / ±2Nm range |
| **Compliance range** | 0.5–10 Nm/rad (software-adjustable via motor) |
| **Interface** | CAN-FD + optional EtherCAT |
| **Target price** | \$800–\$1,500 (vs. \$5,000+ for Bota SensONE + ATI tool changer) |

#### Target Customers

| Segment | Companies | Pain Point Solved |
|:--------|:----------|:-----------------|
| **Cooking robot OEMs** | Miso Robotics, Meishanshi (美膳狮), Aniai, Chef Robotics | Tool-use compliance for flipping, stirring, cutting — their robots currently break eggs and shatter plates |
| **Barista kiosks** | Richtech ADAM, Café X, Artly Coffee | Tamping espresso with consistent force, pouring latte art with controlled flow |
| **Humanoid tool-use** | Astribot S1, Figure, Tesla Optimus | Drop-in compliant wrist for human-like tool manipulation |
| **Industrial assembly** | Cobot integrators (UR, Fanuc CRX users) | Compliant insertion, polishing, deburring |

---

## Direction 4: Whole-Finger Tactile Skin with Distributed Edge Computing for In-Hand Manipulation Policy Learning

### The Thesis in One Sentence
*Design a multi-segment rigid-flex tactile skin covering the entire finger surface (tip, pad, sides, and proximal phalanx) with distributed edge MCUs, and demonstrate that whole-finger tactile coverage — not just fingertip sensing — is essential for learning robust in-hand manipulation policies via the lab's imitation learning pipeline.*

---

### 🎓 IROS/ICRA Academic Angle

#### Fundamental Research Gap
The DexSkin (Stanford, CoRL 2025) demonstrated that high-coverage conformable tactile skins enable contact-rich manipulation learning. However, DexSkin uses **capacitive sensing** — susceptible to EMI from motor drivers, parasitic cross-talk at high taxel density, and viscoelastic creep. More critically, **no existing work quantifies the marginal value of extending tactile coverage beyond the fingertip**: how much does adding phalanx and palm sensing improve manipulation policy success rate? This ablation is essential for the hardware design community to justify the engineering complexity of whole-hand sensorization.

#### Mathematical Formulation

**1. Distributed Tactile State Representation:**

Define the tactile observation as a spatially-indexed field over the finger surface $\Omega_{finger}$:

$$\mathcal{T}(t) = \{(\mathbf{p}_i, \mathbf{f}_i(t)) \mid i = 1, \ldots, N_{taxels}\}, \quad \mathbf{p}_i \in \Omega_{finger}, \; \mathbf{f}_i \in \mathbb{R}^3$$

**2. Tactile Coverage Ablation Framework:**

Define coverage configurations $\mathcal{C}_k \subseteq \{1, \ldots, N_{taxels}\}$ with increasing spatial extent:
- $\mathcal{C}_1$: Fingertip only (standard)
- $\mathcal{C}_2$: Fingertip + finger pad
- $\mathcal{C}_3$: Fingertip + pad + lateral sides
- $\mathcal{C}_4$: Full finger (tip + pad + sides + proximal phalanx)
- $\mathcal{C}_5$: Full finger + palm

For each $\mathcal{C}_k$, train a manipulation policy $\pi_k$ using the lab's Action Chunking with Transformers (ACT) or Diffusion Policy framework, and measure:

$$\Delta J_k = J(\pi_{\mathcal{C}_k}) - J(\pi_{\mathcal{C}_{k-1}})$$

where $J$ is the task success rate. This produces a **marginal value curve** for tactile coverage — a rigorous, hardware-relevant contribution.

**3. Tactile Tokenization for Transformer Policies:**

Encode the distributed tactile field as spatial tokens for transformer-based policies:

$$\mathbf{z}_i^{tac} = \text{MLP}(\mathbf{f}_i) + \text{PE}(\mathbf{p}_i)$$

where $\text{PE}(\mathbf{p}_i)$ is a learned positional encoding over the finger surface mesh. These tokens are concatenated with visual tokens from the lab's eye-in-hand cameras and fed to the policy transformer.

**4. Contact Migration Tracking:**

During in-hand manipulation, contact points migrate across the finger surface. Define a contact migration velocity:

$$\mathbf{v}_{contact}(t) = \frac{d\bar{\mathbf{p}}(t)}{dt}, \quad \bar{\mathbf{p}}(t) = \frac{\sum_i f_{n,i}(t) \cdot \mathbf{p}_i}{\sum_i f_{n,i}(t)}$$

Show that this signal is informative for predicting manipulation failures (object about to roll off the finger) and can be used as an early-termination signal in policy learning.

#### Benchmarking Strategy

| Experiment | Metrics | Baselines |
|:-----------|:--------|:----------|
| **In-hand rotation** (cylinders, cubes, irregular food items) | Rotation angle achieved, success rate, drop rate | Fingertip-only sensing, no tactile (proprioception only), DexSkin (capacitive) |
| **Coverage ablation** ($\mathcal{C}_1$ through $\mathcal{C}_5$) | Marginal success rate improvement per coverage level | This IS the core contribution — quantifying coverage value |
| **Contact migration prediction** | Prediction accuracy of impending drop (AUC-ROC) | Fingertip-only baseline, vision-only |
| **Cross-object generalization** | Policy trained on 10 objects, tested on 20 novel objects | Vision-only policy, proprioception-only |
| **Comparison with RoTO 2.0 benchmark** | Baoding ball rotation frequency, dynamic bouncing | Published RoTO 2.0 baselines |

#### Novelty Claim
*"We present the first systematic ablation study of tactile spatial coverage for dexterous in-hand manipulation, enabled by a whole-finger rigid-flex magnetic tactile skin with distributed edge computing, demonstrating that extending coverage beyond the fingertip yields a [X]% improvement in manipulation success rate — quantifying the diminishing returns curve that guides practical hardware design decisions."*

---

### 🔧 Hardware & Embedded Architecture

#### The Module: "TacSkin" — Whole-Finger Tactile Sleeve

```
┌──────────────────────────────────────────────────────────────────┐
│                WHOLE-FINGER RIGID-FLEX TACTILE SKIN              │
│                                                                  │
│   Proximal Phalanx ──► Middle Phalanx ──► Distal (Fingertip)    │
│                                                                  │
│   ┌──────────┐  flex  ┌──────────┐  flex  ┌──────────┐         │
│   │Rigid PCB │ ═══════│Rigid PCB │ ═══════│Rigid PCB │         │
│   │Island A  │ bridge │Island B  │ bridge │Island C  │         │
│   │(4 taxels)│        │(4 taxels)│        │(6 taxels)│         │
│   │STM32G431 │        │I2C slave │        │I2C slave │         │
│   │(bus      │        │          │        │          │         │
│   │ master)  │        │          │        │          │         │
│   └────┬─────┘        └────┬─────┘        └────┬─────┘         │
│        │                   │                    │               │
│        └───────────────────┴────────────────────┘               │
│                            │                                     │
│                       CAN-FD Bus                                │
│                     to finger base                               │
│                                                                  │
│   Coverage per finger: 14 taxels (3-axis each = 42 force dims)  │
│   Total for 5-finger hand: 70 taxels, 210 force dimensions      │
│   All at 500 Hz update rate                                      │
│                                                                  │
│   Physical: Wraps around finger like a sleeve                    │
│   Secured with medical-grade adhesive + silicone overmold        │
│   Replaceable as a single snap-on unit                           │
└──────────────────────────────────────────────────────────────────┘
```

#### Distributed Computing Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  DISTRIBUTED EDGE ARCHITECTURE                  │
│                                                                 │
│  Finger 1    Finger 2    Finger 3    Finger 4    Finger 5      │
│  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐        │
│  │G431  │   │G431  │   │G431  │   │G431  │   │G431  │        │
│  │14 tax│   │14 tax│   │14 tax│   │14 tax│   │14 tax│        │
│  └──┬───┘   └──┬───┘   └──┬───┘   └──┬───┘   └──┬───┘        │
│     │          │          │          │          │              │
│     └──────────┴──────────┴──────────┴──────────┘              │
│                           │                                     │
│                      CAN-FD Bus                                │
│                     (5 Mbps, 500 Hz)                           │
│                           │                                     │
│                  ┌────────┴────────┐                            │
│                  │  Palm Hub MCU   │                            │
│                  │  STM32H723      │                            │
│                  │  • Aggregates   │                            │
│                  │    70 taxels    │                            │
│                  │  • Contact map  │                            │
│                  │  • Migration    │                            │
│                  │    velocity     │                            │
│                  │  • Slip detect  │                            │
│                  └────────┬────────┘                            │
│                           │                                     │
│                    USB-C / EtherCAT                             │
│                    to host (ROS 2)                              │
│                           │                                     │
│              ┌────────────┴────────────┐                       │
│              │  ACT / Diffusion Policy │                       │
│              │  (Host GPU)             │                       │
│              │  Tactile tokens + Vision│                       │
│              └─────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

#### Design Choice: STM32G431 (not H723) per Finger
- **Why**: G431 is Cortex-M4F at 170 MHz with built-in FDCAN — much smaller package (LQFP48, 7×7mm) and lower power (80 mW). Suitable for the per-finger "leaf node" role where it only reads 14 taxels and packs CAN frames.
- The palm hub H723 handles aggregation and higher-level computation.

---

### 💰 Commercial Spin-Off

#### Product: "TacSkin" — Modular Whole-Finger Tactile Sleeve Kit

| Attribute | Specification |
|:----------|:-------------|
| **Form factor** | Snap-on finger sleeves (sized for Inspire Hand, LEAP Hand, Allegro, LinkerHand) |
| **Coverage** | Full finger: tip + pad + sides + proximal (14 taxels per finger) |
| **Kit contents** | 5 finger sleeves + 1 palm hub + CAN-FD harness + ROS 2 driver |
| **Interface** | CAN-FD (per-finger) → USB-C (palm hub to host) |
| **Target price** | \$1,200–\$2,500 per hand kit (vs. \$15,000+ for full XELA uSkin hand coverage) |

#### Target Customers

| Segment | Companies | Pain Point Solved |
|:--------|:----------|:-----------------|
| **Dexterous hand OEMs** | LinkerBot (灵心巧手, Prof. An's collaborator!), Inspire Robotics, LEAP Hand users | Drop-in tactile upgrade for research and production hands |
| **Humanoid companies** | Agibot, Fourier, Unitree, UBTECH | Whole-hand tactile at 10× lower cost than in-house development |
| **Research labs** | Any lab using Allegro, Shadow, or LEAP hands for manipulation research | Standardized tactile data for policy learning |
| **Teleoperation companies** | Open TeleDex ecosystem, HaptX, Dextrous Robotics | Bilateral tactile feedback for human-in-the-loop training |

> [!TIP]
> **Strategic note:** Prof. An's lab already collaborates with LinkerBot on the Open TeleDex platform. A whole-finger tactile skin designed to fit LinkerHand would have an immediate research customer (the lab itself) and a built-in commercial partner (LinkerBot as OEM integrator).

---

## Comparative Decision Matrix

| Criterion | Direction 1: Variable Impedance | Direction 2: SNN Slip Reflex | Direction 3: Compliant Wrist | Direction 4: Whole-Finger Skin |
|:----------|:---:|:---:|:---:|:---:|
| **Publication risk (lower = safer)** | ⭐⭐ Low | ⭐⭐⭐ Medium | ⭐⭐ Low | ⭐⭐⭐ Medium |
| **Hardware complexity** | ⭐⭐ Low | ⭐⭐ Low | ⭐⭐⭐⭐ High | ⭐⭐⭐ Medium |
| **Alignment with DEX-ROB Lab** | ⭐⭐⭐⭐ High | ⭐⭐⭐ Medium | ⭐⭐⭐⭐⭐ Very High | ⭐⭐⭐⭐⭐ Very High |
| **Commercial TAM** | ⭐⭐⭐⭐ Large | ⭐⭐⭐⭐ Large | ⭐⭐⭐ Medium | ⭐⭐⭐⭐⭐ Very Large |
| **Time to prototype** | 3–4 months | 4–5 months | 6–8 months | 5–7 months |
| **BOM cost** | ~\$65 | ~\$65 | ~\$250 | ~\$180/hand |
| **Defensible IP** | ⭐⭐⭐ Moderate | ⭐⭐⭐⭐ Strong | ⭐⭐⭐⭐ Strong | ⭐⭐⭐ Moderate |

---

## Recommended Strategy: The "Platform Play"

> [!IMPORTANT]
> **Don't choose just one.** Directions 1, 2, and 4 share the **same rigid-flex PCB hardware platform** (magnetic Hall-effect taxels on rigid-flex with STM32). The differentiation is in **firmware and control algorithms**. This means:
>
> 1. **Build the hardware once** (the TacEdge rigid-flex PCB with 12 taxels + STM32H723 + CAN-FD)
> 2. **Write your thesis on Direction 1** (Variable Impedance + Passivity) — safest publication path, strongest control theory, clearest benchmarks
> 3. **Add Direction 2** (SNN Slip Reflex) as a **second paper** — same hardware, different firmware, complementary contribution
> 4. **Scale to Direction 4** (Whole-Finger Skin) as the **commercial product** — extend the single-fingertip PCB into a multi-segment sleeve
>
> Direction 3 (CompliWrist) is the most mechanically complex but has the highest value for the cooking robot application — consider this as a **post-graduation product extension** or a **second-year stretch goal**.

### Suggested Timeline

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        MASTER'S RESEARCH TIMELINE                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Year 1, Semester 1 (Sep–Jan)                                           │
│  ├─ Months 1–2: Rigid-flex PCB design in Altium, component sourcing     │
│  ├─ Month 3: PCB fabrication, silicone mold, assembly                   │
│  ├─ Month 4: Firmware (Hall readout, calibration, CAN-FD driver)        │
│  └─ Month 5: Basic integration with lab's xArm/UR5 + ROS 2 bridge     │
│                                                                          │
│  Year 1, Semester 2 (Feb–Jun)                                           │
│  ├─ Month 6: Implement Variable Impedance + Energy Tank controller      │
│  ├─ Month 7: Fragile food manipulation experiments                      │
│  ├─ Month 8: Ablation studies (rate sweep, tank ON/OFF, baselines)      │
│  ├─ Month 9: Paper writing → submit to IROS 2028 (Mar deadline)        │
│  └─ Month 10: Begin SNN slip reflex firmware (Direction 2)              │
│                                                                          │
│  Year 2, Semester 1 (Sep–Jan)                                           │
│  ├─ Month 11–12: SNN training, on-chip deployment, slip experiments    │
│  ├─ Month 13: Second paper → submit to ICRA 2029 (Sep deadline)        │
│  └─ Month 14: Begin whole-finger skin prototype (Direction 4)           │
│                                                                          │
│  Year 2, Semester 2 (Feb–Jun)                                           │
│  ├─ Month 15–16: Integration with LinkerHand + Open TeleDex            │
│  ├─ Month 17: Coverage ablation experiments                              │
│  ├─ Month 18: Thesis writing + defense                                  │
│  └─ Post-graduation: Spin out "TacEdge" as B2B hardware startup        │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Appendix A: Key References for Proposal Writing

| Topic | Key Papers | Venue |
|:------|:-----------|:------|
| Variable Impedance + Energy Tanks | Kronander & Billard (2016), Ferraguti et al. (2019) | T-RO, مکانیکs Letters |
| Mindlin-Cattaneo Slip Mechanics | Tremblay & Bhatt (2023), Dong et al. (2024) | ICRA, RA-L |
| Rigid-Flex Tactile Hardware | DexSkin (Stanford, CoRL 2025), uSkin (XELA) | CoRL, Sensors Journal |
| Edge Tactile Computing | GelNeuro (2025), HD Computing on PapillArray | RA-L, IROS |
| TacO Benchmark | UCSD/CMU/SNU (ICRA 2025) | ICRA |
| Open TeleDex | Xu Chi, An Shan et al. (2025) | arXiv |
| DexCatch | An Shan et al. (CoRL 2024) | CoRL |
| Series Elastic Actuators | Pratt & Williamson (1995), Paine et al. (2014) | pedestrian pedestrian pedestrian IROS, pedestrian pedestrian pedestrian pedestrian pedestrian TRO |
| Spiking Neural Networks for Tactile | Ward-Cherrier et al. (2020), Taunyazov et al. (2020) | RA-L, ICRA |

## Appendix B: IP & Patent Landscape Considerations

| Area | Existing Patents to Watch | Your Differentiator |
|:-----|:--------------------------|:-------------------|
| Magnetic tactile sensing | ReSkin (Meta, open-source), XELA uSkin (commercial IP) | Food-grade hermetic packaging + on-chip impedance control co-design |
| Series elastic wrist | Multiple SEA patents (MIT, DLR) — but mostly for full actuators | Miniaturized, tool-specific, with embedded F/T on rigid-flex |
| Tactile skins | DexSkin (Stanford, academic), BioTac (SynTouch, expired/discontinued) | Distributed CAN-FD architecture + coverage ablation methodology |
| Edge inference on tactile | GelNeuro (academic), PaXini (commercial) | SNN specifically for slip reflex with provable arrest time bound |

## Appendix C: Certification Roadmap for Commercial Product

| Phase | Certification | Timeline | Cost (est.) |
|:------|:-------------|:---------|:------------|
| Prototype | None (research use) | Months 1–12 | \$0 |
| Alpha product | CE marking (EMC + LVD) | Month 15–18 | \$5,000–\$10,000 |
| Food-contact | FDA 21 CFR 177.2600 (silicone skin material) | Month 18–20 | \$3,000–\$5,000 |
| Industrial | IP69K testing (third-party lab) | Month 18–20 | \$2,000–\$4,000 |
| Full commercial | NSF/ANSI 169 + EHEDG Doc 44 compliance | Month 20–24 | \$10,000–\$15,000 |
