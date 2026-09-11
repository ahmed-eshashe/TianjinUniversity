# Direction 5: Tactile-Guided Adaptive Cutting of Deformable Foods via Sensorized Tool Interface

**A Focused Thesis Proposal for DEX-ROB Lab, Tianjin University**

---

## Why Tomato Cutting Is a Killer Research Problem

Tomato cutting is the **"hydrogen atom" of contact-rich food manipulation** — deceptively simple, but it exposes every fundamental limitation of current robotic systems:

```
                    THE TOMATO CUTTING CHALLENGE
    
    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │   Phase 1: ELASTIC SKIN DEFORMATION                    │
    │   • Knife contacts taut skin under biaxial tension      │
    │   • Force rises nonlinearly (Hertzian → membrane)       │
    │   • Robot must push hard enough but NOT crush            │
    │                    │                                     │
    │                    ▼  ← CRITICAL TRANSITION              │
    │   Phase 2: SKIN PUNCTURE (Fracture Event)               │
    │   • Sudden force drop (50-80% in <5 ms)                 │
    │   • If robot doesn't adapt: knife slams through,        │
    │     crushes interior, sprays juice/seeds                 │
    │                    │                                     │
    │                    ▼                                     │
    │   Phase 3: VISCOPLASTIC INTERIOR CUTTING                │
    │   • Soft gel + seed cavities + variable density          │
    │   • Force is low but variable (hitting seeds, walls)     │
    │   • Must maintain blade angle and slice thickness        │
    │                    │                                     │
    │                    ▼                                     │
    │   Phase 4: EXIT / SKIN RE-ENCOUNTER                     │
    │   • Bottom skin resistance (second puncture)             │
    │   • Cutting board contact (hard stop)                    │
    │   • Must decelerate to avoid slamming the board          │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
```

### Why Current Robots Fail at This

| Approach | Failure Mode |
|:---------|:------------|
| **Position control** (fixed trajectory) | Crushes soft tomatoes, bounces off firm ones. Can't adapt to size/ripeness variation. |
| **Constant force control** (wrist F/T) | Fails at puncture transition — the sudden force drop causes the controller to slam forward. 10–30 ms wrist F/T latency is too slow to catch the 5 ms fracture event. |
| **Vision-guided** | Camera is occluded by knife, hand, and tomato at the exact moment of contact. Cannot see internal structure (seed cavities, ripeness gradient). |
| **Imitation learning** (position replay) | Learned trajectories are brittle to tomato size, ripeness, and knife sharpness variation. No closed-loop contact adaptation. |

### Why It's Perfect for You

| Your Strength | How It Maps |
|:--------------|:------------|
| Rigid-flex PCB design | Sensorized knife handle / blade-root interface |
| STM32 embedded control | On-tool 1 kHz cutting phase detection |
| CAN-FD protocols | Real-time impedance parameter updates to arm controller |
| Prof. An's cooking robot focus | Direct application to Meishanshi/Astribot-class platforms |
| Hardware "add-on" strategy | The module bolts onto ANY robot holding ANY knife — not a custom end-effector |

---

## 🎓 IROS/ICRA Academic Angle

### Fundamental Research Gap

**No existing work combines on-tool tactile sensing with phase-aware adaptive impedance control for cutting deformable objects.** The state of the art falls into two disconnected camps:

1. **Cutting mechanics modeling** (materials science): Characterizes force-displacement curves of food cutting in lab conditions (Atkins & Xu 2005, Schuldt et al. 2018) — but doesn't close the control loop
2. **Robot force control for cutting** (robotics): Uses wrist F/T sensors with fixed or slowly-adapted impedance (Lenz et al. 2015, Gemici & Saxena 2014) — but sensor bandwidth is too low to detect the puncture transition, and the models ignore the phase-switching nature of the cutting process

The gap: **treating cutting as a hybrid dynamical system with discrete phase transitions detectable only through high-bandwidth on-tool tactile sensing, with provable stability across the fracture discontinuity.**

### Mathematical Formulation

#### 1. Cutting Force Model (Fracture Mechanics)

The knife-tomato interaction follows a **piecewise nonlinear force-displacement law**. Let $\delta$ be the knife penetration depth and $\dot{\delta}$ the cutting velocity:

**Phase 1 — Elastic skin deformation** ($0 \leq \delta < \delta_{punct}$):

The tomato skin behaves as a biaxially pre-stressed membrane. The knife contact force rises nonlinearly:

$$F_{cut}(\delta) = \underbrace{\frac{4}{3} E^* \sqrt{R_{blade}} \, \delta^{3/2}}_{\text{Hertzian (initial)}} + \underbrace{\sigma_0 \cdot w \cdot \delta}_{\text{Membrane tension}}$$

where $E^*$ is the effective modulus of the skin, $R_{blade}$ is the blade-edge radius, $\sigma_0$ is the biaxial skin pre-stress, and $w$ is the blade contact width.

**Phase 2 — Puncture / Fracture** ($\delta = \delta_{punct}$):

Puncture occurs when the stress intensity factor at the blade tip reaches the critical fracture toughness:

$$K_I = \sigma_{tip}(\delta) \sqrt{\pi \, a_{crack}} \geq K_{Ic}^{skin}$$

At this instant, the force drops discontinuously:

$$F_{cut}(\delta_{punct}^+) = F_{cut}(\delta_{punct}^-) - \Delta F_{fracture}$$

where $\Delta F_{fracture} / F_{peak} \approx 0.5 - 0.8$ (measured experimentally — the force drops by 50–80%).

**Phase 3 — Viscoplastic interior** ($\delta_{punct} < \delta < \delta_{exit}$):

$$F_{cut}(\delta) = \underbrace{\tau_y \cdot A_{shear}(\delta)}_{\text{Shear yield of gel}} + \underbrace{G_c \cdot w}_{\text{Fracture energy rate}} + \underbrace{\eta \cdot \dot{\delta} \cdot A_{contact}(\delta)}_{\text{Viscous drag}}$$

where $\tau_y$ is the yield stress of the interior gel, $G_c$ is the fracture toughness (energy per unit crack area), and $\eta$ is the viscosity.

**Phase 4 — Bottom skin + board contact** ($\delta \geq \delta_{exit}$):

Second membrane puncture followed by rigid contact with cutting board.

#### 2. Hybrid Phase-Switching Impedance Controller

Model the cutting task as a **switched hybrid system** with four discrete modes $q \in \{1, 2, 3, 4\}$:

$$\dot{\mathbf{x}} = \mathbf{f}_{q}(\mathbf{x}, \mathbf{u}), \quad q \in \mathcal{Q} = \{1, 2, 3, 4\}$$

The impedance parameters switch based on the detected cutting phase:

$$\mathbf{M}_d \ddot{\tilde{\mathbf{x}}} + \mathbf{D}_d^{(q)} \dot{\tilde{\mathbf{x}}} + \mathbf{K}_d^{(q)} \tilde{\mathbf{x}} = \mathbf{F}_{ext}$$

| Phase $q$ | Target Stiffness $K_d^{(q)}$ | Target Damping $D_d^{(q)}$ | Rationale |
|:----------|:-----|:-----|:----------|
| 1 (Skin deformation) | **High** (stiff approach) | Medium | Push through skin resistance with controlled force |
| 2 (Puncture) | **Very Low** (compliant) | **Very High** (damped) | Absorb the force discontinuity — prevent forward slam |
| 3 (Interior cutting) | Low | Low | Gentle, steady-state cutting with minimal crushing |
| 4 (Exit / board) | **Medium → High** | **Very High** | Decelerate before hard board contact |

#### 3. Tactile Phase Detector (On-Tool)

The cutting phase is detected in real-time from on-tool tactile signals. Define the phase detection signal vector:

$$\mathbf{s}(t) = \begin{bmatrix} F_z(t) \\ \dot{F}_z(t) \\ \ddot{F}_z(t) \\ F_x(t) / F_z(t) \end{bmatrix}$$

where $F_z$ is the cutting force (normal to blade), $F_x$ is the slicing force (along blade), and the ratios capture the changing force signature across phases.

**Phase transition detection rules:**

$$q: 1 \to 2 \quad \text{when} \quad \dot{F}_z(t) < -\alpha_{punct} \quad \text{(rapid force drop)}$$
$$q: 2 \to 3 \quad \text{when} \quad |\ddot{F}_z(t)| < \beta_{settle} \quad \text{for } t > t_{dwell} \quad \text{(force stabilizes)}$$
$$q: 3 \to 4 \quad \text{when} \quad \dot{F}_z(t) > \gamma_{exit} \quad \text{(force rising again — bottom skin)}$$

These thresholds are computed on-chip at 1 kHz — **only possible with on-tool sensing, not wrist F/T.**

> [!IMPORTANT]
> **Why wrist F/T sensors can't do this:** The knife handle → wrist path introduces ~15–25 mm of lever arm and the arm's reflected inertia. A 5 ms puncture force drop arriving at the wrist F/T sensor is attenuated by the tool's mass and filtered by the arm's structural dynamics. By the time the wrist detects it, the knife has already plunged 3–5 mm into the interior. **On-tool sensing at the blade root detects the puncture within 1 ms, giving the controller 4 ms to switch impedance before damage occurs.**

#### 4. Stability Across Phase Transitions (Lyapunov + Dwell Time)

The critical stability challenge: switching $\mathbf{K}_d$ and $\mathbf{D}_d$ discontinuously at phase transitions injects energy. Use a **common Lyapunov function** with **virtual energy tank** to guarantee passivity across all transitions:

$$V(\tilde{\mathbf{x}}, \dot{\tilde{\mathbf{x}}}, s, q) = \frac{1}{2} \dot{\tilde{\mathbf{x}}}^T \mathbf{M}_d \dot{\tilde{\mathbf{x}}} + \frac{1}{2} \tilde{\mathbf{x}}^T \mathbf{K}_d^{(q)} \tilde{\mathbf{x}} + \frac{1}{2} s^2$$

At each transition $q_i \to q_j$, the potential energy change is:

$$\Delta V_{pot} = \frac{1}{2} \tilde{\mathbf{x}}^T \left(\mathbf{K}_d^{(q_j)} - \mathbf{K}_d^{(q_i)}\right) \tilde{\mathbf{x}}$$

The energy tank absorbs this:

$$s^+ = \sqrt{(s^-)^2 - 2\Delta V_{pot}} \quad \text{if } \frac{1}{2}(s^-)^2 > \Delta V_{pot}$$

If the tank has insufficient energy, the transition is **delayed** (dwell-time enforcement) until enough dissipation energy accumulates:

$$\tau_{dwell} \geq \frac{\Delta V_{pot,max}}{P_{diss,min}} = \frac{\Delta V_{pot,max}}{\lambda_{min}(\mathbf{D}_d^{(q_i)}) \cdot \|\dot{\tilde{\mathbf{x}}}\|_{min}^2}$$

**Theorem (sketch):** *Under the energy tank constraint and minimum dwell-time condition, the hybrid cutting impedance controller is Input-to-State Stable (ISS) with respect to bounded cutting force disturbances, for all admissible phase transition sequences.*

This is a publishable stability result — it extends the existing energy tank literature (Ferraguti et al.) to **event-triggered phase switching** driven by on-tool tactile signals, which is novel.

### Benchmarking Strategy (Publication-Ready)

| Experiment | Protocol | Metrics | Baselines |
|:-----------|:---------|:--------|:----------|
| **Tomato slicing quality** | 50 tomatoes × 5 ripeness levels × 3 knife sharpness levels = 750 cuts | Slice thickness uniformity (std dev), juice loss (% mass), visual deformation score (human-rated) | Position control, constant force, wrist F/T impedance (no phase switching) |
| **Puncture detection latency** | High-speed camera (1000 fps) ground-truth vs. sensor detection timestamp | Detection delay (ms), false positive rate, false negative rate | Wrist F/T detection, accelerometer-only, vision-based |
| **Phase-switching ablation** | Full controller vs. single-phase impedance vs. no impedance | Cut quality, peak overshoot force at puncture, board impact force | Proves phase-switching is essential |
| **Energy tank ablation** | Tank ON vs. tank OFF during phase transitions | Oscillation amplitude, energy injection events, stability violations | Proves passivity guarantee is necessary |
| **Generalization to other foods** | Cucumber, kiwi, bread, cheese, raw chicken breast (10 each) | Same metrics — does the phase detector generalize? | Re-trained per-food vs. zero-shot transfer |
| **Comparison with human cutting** | F/T profiles recorded from human chefs cutting same tomatoes | Force profile similarity (DTW distance), cutting efficiency | Human performance as upper bound |

> [!TIP]
> **The "750 cuts" experiment is your competitive moat.** No existing paper has this scale of quantitative cutting benchmarks. Most food cutting papers show 5–10 qualitative examples. A rigorous 750-cut dataset with statistical analysis across ripeness and sharpness will be extremely compelling to IROS/ICRA reviewers.

### Paper Framing Options

| Venue | Title Angle | Emphasis |
|:------|:------------|:---------|
| **IROS** | *"Phase-Aware Tactile Impedance Control for Robotic Cutting of Deformable Foods"* | Control theory + stability proofs + hardware system |
| **ICRA** | *"On-Tool Tactile Sensing for Real-Time Fracture Detection in Robotic Food Cutting"* | Sensing + detection algorithm + ablation benchmarks |
| **RA-L** | *"A Sensorized Knife Interface for Adaptive Cutting: From Fracture Mechanics to Passivity-Guaranteed Control"* | Full system paper (longer format allows both theory + experiments) |
| **CoRL** | *"Learning Cutting Impedance Profiles from Human Demonstrations via On-Tool Tactile Feedback"* | Learning angle (TP-GMM from Open TeleDex demos) — pairs with lab's strengths |

---

## 🔧 Hardware & Embedded Architecture

### The Module: "TacBlade" — Sensorized Knife-Tool Interface

The key insight: **don't sensorize the blade itself** (fragile, food-contact nightmare, blade replacement kills the sensor). Instead, sensorize the **blade-root clamp / tool adapter** that sits between the robot's wrist and any standard knife.

```
┌──────────────────────────────────────────────────────────────────────┐
│                   TacBlade: SENSORIZED TOOL ADAPTER                 │
│                                                                      │
│   Side View (cross-section through knife plane):                     │
│                                                                      │
│   Robot Wrist Flange (ISO 9409-1)                                   │
│   ═══════════════════════════                                       │
│          │                                                           │
│   ┌──────┴──────┐                                                   │
│   │  CLAMP BODY  │  6061-T6 Aluminum, hard-anodized                │
│   │  (40×30×15mm)│                                                   │
│   │              │                                                   │
│   │  ┌────────┐  │                                                   │
│   │  │RIGID-  │  │  4-layer rigid-flex PCB                          │
│   │  │FLEX PCB│  │  bonded to inner clamp surface                   │
│   │  │        │  │                                                   │
│   │  │ Sensors│  │  ← 6× strain gauge bridges (cutting forces)     │
│   │  │   +    │  │  ← 4× piezo elements (vibration/fracture)       │
│   │  │  MCU   │  │  ← 1× NTC (temperature)                        │
│   │  │        │  │  ← STM32H723 + CAN-FD PHY                      │
│   │  └────────┘  │                                                   │
│   │              │                                                   │
│   │  ┌────────┐  │                                                   │
│   │  │ KNIFE  │  │  Standard knife tang clamped here                │
│   │  │ TANG   │  │  Set screws + alignment pins                     │
│   │  │ SLOT   │  │  Accepts any knife with tang width 15-25mm      │
│   │  └────────┘  │                                                   │
│   │              │                                                   │
│   └──────────────┘                                                   │
│          │                                                           │
│      Knife Blade (standard commercial kitchen knife)                │
│          │                                                           │
│      ═══════════════ ← Cutting edge                                 │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Sensor Configuration

```
┌──────────────────────────────────────────────────────────────┐
│              SENSOR LAYOUT ON RIGID-FLEX PCB                 │
│                                                              │
│   Top View (looking down at clamp inner surface):            │
│                                                              │
│   ┌──────────────────────────────────────┐                  │
│   │            RIGID ZONE 1              │                  │
│   │   [SG1]──[SG2]    Strain gauge pair  │                  │
│   │   (Fz: cutting    for normal cutting │                  │
│   │    force)          force              │                  │
│   │                                      │                  │
│   │   [SG3]──[SG4]    Strain gauge pair  │                  │
│   │   (Fx: slicing     for lateral/      │                  │
│   │    force)          slicing force      │                  │
│   ├─── flex bridge ─────────────────────-┤                  │
│   │            RIGID ZONE 2              │                  │
│   │   [SG5]──[SG6]    Strain gauge pair  │                  │
│   │   (My: bending     for blade bending │                  │
│   │    moment)         moment             │                  │
│   │                                      │                  │
│   │   [PZ1] [PZ2]     Piezo elements     │                  │
│   │   (High-freq       for fracture/     │                  │
│   │    vibration,      puncture acoustic │                  │
│   │    100-5000 Hz)    emission detection│                  │
│   ├─── flex bridge ────────────────────-─┤                  │
│   │            RIGID ZONE 3              │                  │
│   │   [PZ3] [PZ4]     Additional piezo   │                  │
│   │                    for blade-tip      │                  │
│   │                    vibration sensing  │                  │
│   │                                      │                  │
│   │   [STM32H723]  [TCAN4550]  [NTC]     │                  │
│   │   MCU           CAN-FD     Temp      │                  │
│   │                 PHY        sensor     │                  │
│   └──────────────────────────────────────┘                  │
│                                                              │
│   Sensing Channels:                                          │
│   • 3× force axes (Fx, Fz, My) via strain gauges @ 2 kHz   │
│   • 4× piezo vibration channels @ 10 kHz (fracture detect) │
│   • 1× temperature (thermal drift compensation)             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Why This Dual-Modality Design

| Modality | What It Detects | Bandwidth | Role |
|:---------|:---------------|:----------|:-----|
| **Strain gauges** (quasi-static) | Cutting force magnitude and direction ($F_z$, $F_x$, $M_y$) | DC – 500 Hz | Phase 1/3/4 force tracking, impedance modulation |
| **Piezo elements** (dynamic) | Fracture acoustic emission, blade-skin rupture vibration | 100 Hz – 5 kHz | **Phase 2 puncture detection** — the "crack" of skin fracture produces a characteristic high-frequency burst (1–3 kHz) detectable in <1 ms |

> [!NOTE]
> **This is the key hardware insight.** Strain gauges alone can detect the force *drop* at puncture, but only after it's happened (~2–3 ms delay for the force to propagate). Piezo elements detect the fracture *acoustic emission* — the sound of the skin cracking — which arrives **before** the force drop is fully developed. This gives you an extra 1–2 ms of lead time. The fusion of both modalities is the hardware novelty.

### Bill of Materials

| Component | Part | Qty | Unit Cost |
|:----------|:-----|:----|:----------|
| Strain gauge (350Ω, half-bridge) | Micro-Measurements EA-06 series | 6 | \$8 |
| 24-bit strain ADC | ADS1262 (TI) | 1 | \$12 |
| Piezo disc element | Murata 7BB-20-6L0 (Ø20mm) | 4 | \$1.50 |
| Piezo front-end (charge amp + ADC) | AD7768-4 (4-ch, 24-bit, simultaneous) | 1 | \$15 |
| MCU | STM32H723VGT6 | 1 | \$6 |
| CAN-FD transceiver | TCAN4550 | 1 | \$3 |
| NTC thermistor | 10kΩ ±1% | 1 | \$0.30 |
| Rigid-flex PCB | 4-layer, 3 rigid zones + 2 flex bridges | 1 | \$20 (qty 100) |
| Clamp body | 6061-T6, CNC machined | 1 | \$25 (qty 50) |
| **Total BOM** | | | **~\$120** |

### Firmware Architecture

```
┌────────────────────────────────────────────────────────────────┐
│              STM32H723 FIRMWARE: TacBlade                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────────┐    ┌──────────────────────────────┐  │
│  │ ISR: STRAIN @ 2 kHz │    │ ISR: PIEZO @ 10 kHz          │  │
│  │ • DMA SPI read ADS  │    │ • DMA SPI read AD7768        │  │
│  │   1262 (3-axis force)│    │ • 4-channel simultaneous     │  │
│  │ • Thermal comp.      │    │ • Band-pass filter           │  │
│  │ • Calibration matrix │    │   (500-4000 Hz, IIR)         │  │
│  │ • Force vector:      │    │ • Envelope detection         │  │
│  │   Fz, Fx, My         │    │   (Hilbert via analytic)     │  │
│  └──────────┬──────────┘    │ • Fracture burst flag         │  │
│             │               └──────────────┬───────────────┘  │
│             ▼                              ▼                   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │         PHASE DETECTOR (runs @ 2 kHz)                    │ │
│  │                                                          │ │
│  │  Inputs:  Fz, dFz/dt, d²Fz/dt², Fx/Fz, piezo_burst     │ │
│  │                                                          │ │
│  │  State machine:                                          │ │
│  │  ┌─────────┐  dFz<-α OR    ┌──────────┐                │ │
│  │  │ Phase 1  │──piezo_burst──►│ Phase 2   │               │ │
│  │  │ APPROACH │               │ PUNCTURE  │               │ │
│  │  └─────────┘               └─────┬─────┘               │ │
│  │                                   │ |d²Fz|<β            │ │
│  │                                   ▼                      │ │
│  │  ┌─────────┐  dFz>γ        ┌──────────┐                │ │
│  │  │ Phase 4  │◄──────────────│ Phase 3   │               │ │
│  │  │ EXIT     │               │ INTERIOR  │               │ │
│  │  └─────────┘               └──────────┘                │ │
│  │                                                          │ │
│  │  Output: phase_id, Kd_target, Dd_target                 │ │
│  └──────────────────────────────────────────────────────────┘ │
│             │                                                  │
│             ▼                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  CAN-FD TX @ 1 kHz                                      │ │
│  │  Packed frame (16 bytes):                                │ │
│  │  • Fz, Fx, My (int16 × 3)     = 6 bytes                │ │
│  │  • phase_id (uint8)            = 1 byte                  │ │
│  │  • Kd_target, Dd_target (uint16 × 2) = 4 bytes          │ │
│  │  • piezo_energy (uint16)       = 2 bytes                 │ │
│  │  • timestamp (uint16)          = 2 bytes                 │ │
│  │  • flags + checksum            = 1 byte                  │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Interface with Robot Arm

```
  TacBlade Module              CAN-FD Bus               Robot Controller
  ┌──────────────┐           ┌────────────┐           ┌──────────────────┐
  │ STM32H723    │──CAN-FD──►│ ROS 2 Node │──topic───►│ Impedance        │
  │ phase_id +   │ 1 kHz     │ (micro-ROS │           │ Controller       │
  │ Kd, Dd       │           │  bridge)   │           │                  │
  │ force vector │           └────────────┘           │ Kd(q) ← TacBlade│
  └──────────────┘                                    │ Dd(q) ← TacBlade│
                                                      │ Energy tank check│
                                                      └────────┬─────────┘
                                                               │
                                                        Joint torques
                                                               ▼
                                                      xArm / UR5 / Franka
                                                      (or Astribot S1)
```

---

## 💰 Commercial Spin-Off

### Product: "TacBlade" — OEM Sensorized Tool Adapter

| Attribute | Specification |
|:----------|:-------------|
| **Form factor** | ISO 9409-1 wrist-side flange, universal knife clamp (15–25mm tang) |
| **Dimensions** | 40 × 30 × 15 mm, 85g (excluding knife) |
| **Sensing** | 3-axis force (±50N, 0.05N resolution) + 4-ch vibration (100–5000 Hz) |
| **Output** | Force vector + cutting phase + recommended impedance @ 1 kHz over CAN-FD |
| **Protection** | IP67 (splashproof), food-grade anodized aluminum body |
| **Knife compatibility** | Any standard chef's knife, santoku, or utility knife with tang |
| **Target price** | \$349–\$599 per unit |

### Why This Is a Compelling Product

> [!IMPORTANT]
> **The tool adapter is more commercially valuable than a tactile fingertip** for food automation, because:
> 1. Food prep robots use **tools** (knives, spatulas, ladles) — not bare fingers
> 2. Every food prep robot needs cutting capability, but none have on-tool sensing
> 3. The adapter is **tool-agnostic** — works with any knife, any robot
> 4. It's a **single-SKU product** (not sized per finger/hand model)
> 5. Consumable revenue from knife-specific calibration profiles (software)

### Target Customers

| Segment | Companies | Annual Knife-Cuts Problem |
|:--------|:----------|:------------------------|
| **Cooking robot OEMs** | Meishanshi (美膳狮), Nala Robotics, Dexai Robotics | Robots can stir-fry and flip, but CAN'T reliably cut/slice/dice — this is the missing capability |
| **Ghost kitchen prep lines** | Chef Robotics, Hyphen, Sweetgreen | Prep cutting (onions, tomatoes, lettuce) is 40% of kitchen labor — robots fail at it because of force control |
| **Fresh food processing** | Tyson Foods, JBS, Sysco (automated portioning) | High-volume protein and produce cutting with quality control |
| **Barista kiosks (adjacent)** | Richtech ADAM, Café X | Cutting pastries, slicing fruit garnishes for cocktail bots |
| **Humanoid demonstrations** | Astribot S1, Figure, Tesla Optimus | "Robot cuts a tomato perfectly" is the ultimate demo — currently faked or pre-cut |

### Business Model

- **Hardware sale**: \$349–\$599/unit (65%+ margin at \$120 BOM)
- **Software subscription**: \$29/month for cloud-based cutting profile library (pre-calibrated force models for 50+ food items — tomato, onion, bread, chicken, etc.)
- **Data licensing**: Aggregate anonymized cutting force data from deployed units → sell food texture datasets to food science companies

---

## How This Compares to the Original 4 Directions

| Dimension | Dir 1 (Impedance Fingertip) | Dir 5 (TacBlade Cutting) |
|:----------|:---------------------------|:------------------------|
| **Research novelty** | ⭐⭐⭐⭐ Strong (passivity + edge) | ⭐⭐⭐⭐⭐ Very Strong (hybrid fracture + phase switching + dual-modal sensing) |
| **Cooking robot relevance** | ⭐⭐⭐ General grasping | ⭐⭐⭐⭐⭐ Direct (cutting is THE bottleneck) |
| **Hardware complexity** | ⭐⭐ Low (magnetic taxels) | ⭐⭐⭐ Medium (strain gauges + piezo + clamp) |
| **Publication framing** | Control theory paper | **Control + sensing + food science** — interdisciplinary appeal |
| **Commercial defensibility** | Moderate (many tactile companies) | **Strong** — no competitor has on-tool cutting sensing |
| **Alignment with Prof. An** | Good (general manipulation) | **Excellent** (cooking robots, Meishanshi ties, Astribot demos) |
| **Experiment feasibility** | Needs diverse objects | **Just needs tomatoes + a knife** — cheap, repeatable, photogenic |
| **"Wow factor" for demos** | Robot holds a fragile object | **Robot cuts a perfect tomato** — viral demo potential |

---

## Recommended Combination Strategy

> [!TIP]
> **TacBlade + TacEdge as a two-product platform:**
>
> 1. **Year 1 thesis focus**: TacBlade (cutting) — single focused paper for IROS/RA-L
> 2. **Year 1 second paper**: Reuse the rigid-flex PCB design methodology and passivity framework for a TacEdge fingertip paper (ICRA)
> 3. **Post-graduation product line**:
>    - TacBlade (tool sensing for cutting/stirring/flipping) — \$349–\$599
>    - TacEdge (fingertip sensing for grasping) — \$149–\$299
>    - Shared firmware platform, shared CAN-FD protocol, shared ROS 2 driver
>    - Customer buys both for a complete "tactile upgrade kit" for their robot

### Why TacBlade Is the Stronger Lead Thesis

1. **Tighter scope** — one task (cutting), one tool (knife), one formulation (hybrid impedance)
2. **Cheaper experiments** — tomatoes cost ¥5 each; you need a knife, a cutting board, and a robot arm you already have
3. **Clearer novelty story** — "first on-tool tactile sensor for robotic cutting with phase-aware impedance control" is unambiguous
4. **Prof. An will love it** — it directly enables his cooking robot vision and pairs with Open TeleDex (record human chefs cutting → learn impedance profiles)
5. **Viral demo potential** — "Robot perfectly slices a tomato" gets millions of views; "Robot holds tofu without crushing" gets thousands
