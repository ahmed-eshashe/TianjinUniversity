# A tomato that can be cut along new paths: method comparison and RL recommendation

**Research date:** 10 November 2026.  
**Project:** Dual-arm robotic cutting.  
**Scope:** Literature and implementation-availability review, checked against saved local evidence. No new solver was installed, benchmarked or adopted for this study. Published performance is separated from measurements on this laptop.

## 1. Recommendation

**Recommend a GPU material point method (MPM) with persistent, online-generated cutting discontinuities as the target architecture. Use BladeMaster as the first design to evaluate, subject to obtaining a usable implementation and passing a small local benchmark.** Preserve the existing robot, kitchen, grip and motion interface. Preserve DiSECt evidence as a reference; do not continue treating its prepared interface as the general slicing-and-dicing training environment.

This is a recommendation about the method, not a claim that a ready-to-install, validated tomato simulator has been found. The closest cutting-specific design is a recent preprint. Its official page does not currently provide a code link, and this review did not locate a verified public implementation. That availability issue must be resolved before committing development time. [BladeMaster project](https://jango6324.github.io/blademaster/)

My engineering ranking is:

1. **Persistent-discontinuity GPU MPM:** strongest fit to deformable cutting plus continued manipulation and force feedback.
2. **Energy-based XPBD with persistent breakable connectivity:** a credible alternative if implementation availability or measured MPM cost fails. It needs a cutting/contact model and material validation; generic particles alone are insufficient.
3. **Dynamic FEM/XFEM:** a legitimate alternative for accurate cutting mechanics, but a larger implementation burden for this project's immediate training goal.

Do not select an engine from a visually impressive video or a generic “millions of RL steps per second” claim. Require evidence for repeated cuts, independent fragments, useful reaction forces and complete training-loop throughput on this laptop.

## 2. What “cut anywhere without calculations” can mean

The achievable requirement is **no manually prepared cutting plane and no offline trajectory-specific solve before every attempt**. An RL action changes the knife motion; the simulator computes deformation, contact and new separation during that attempt. Every physical simulator still performs calculations.

Three costs should be distinguished:

| Cost | What we want |
|---|---|
| Preparing the tomato | Sample its shape and initialize material state at episode reset; automate this for different sizes/shapes. |
| Preparing a particular cut | Eliminate the need to insert a special fracture surface for every intended knife path. |
| Advancing physics | Keep it fast enough for training, but retain the calculations needed for a defensible response. |

A particle is a small sample of material, not necessarily a grain of sand. An elastic tomato needs resistance to stretching, compression and shear, plus a rule for irreversible separation. A pile of independent grains does not supply those properties. NVIDIA's standard particle-set documentation explicitly covers fluids and granular materials; selecting that feature does not automatically create a cuttable solid tomato. [NVIDIA particle documentation](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/dev_guide/particles/particles.html)

In MPM, material samples exchange mechanical information through a computational grid. The key cutting problem is deciding which samples must **stop sharing intact-material motion** after the knife passes. Pieces must still collide and slide when they touch again, without becoming bonded again. That distinction separates a lasting slice from a temporary opening around a blade.

“Anywhere, any time” also has finite-resolution limits. The desired operating envelope should include angled cuts, partial cuts, pauses, reversals, intersecting cuts and cutting an already separated piece. It cannot mean arbitrarily thin slices, unlimited cuts, infinite knife speed or exact response at every mathematical point.

### Resolution and size are still costs

For an illustrative 60 mm diameter sphere, one sample per cubic cell gives approximately 14,100 samples at 2 mm spacing, 113,100 at 1 mm, or 904,800 at 0.5 mm. Real MPM arrangements may use several particles per grid cell. These are geometric estimates, not required settings or measured memory consumption.

Halving spacing in 3D therefore increases sample count approximately eightfold. Doubling tomato diameter at fixed spacing does the same. Changing size can be automated; it is not computationally free. As a proposed starting constraint, a useful slice should span several material samples, and a thin skin may require a separate surface representation or local refinement.

## 3. Comparison of the main approaches

Rows describe method families, not interchangeable products. The judgments below concern this project's unrestricted cutting and RL goals; they are not measured speed rankings.

| Approach | New cuts during motion | Lasting separate pieces | Main advantage here | Main difficulty | Assessment |
|---|---|---|---|---|---|
| **Current DiSECt-derived FEM candidate** | Restricted by its prepared interface | Requires its cohesive connections to fail | Existing mechanics, geometry and saved evidence | General new paths require changing topology; current cost is prohibitive | Keep as a reference, not the general RL backend |
| **Dynamic FEM / XFEM / virtual-node methods** | Supported by specialized formulations | Supported through explicit discontinuities | Continuum mechanics with detailed constitutive models | Changing topology, contact and integration complexity | Scientifically valid; not my first implementation choice |
| **Ordinary MLS-MPM / CPIC** | Some formulations support blade-induced discontinuities | Must inspect how cut history is retained | GPU-friendly continuum representation | A temporary blade boundary is not sufficient evidence of persistent fragment independence | Useful foundation, incomplete specification |
| **Persistent-discontinuity MPM** | Target capability | Explicitly part of the design | Combines deformability, cutting history and fragment contact | Contact accuracy, complex cut histories and local throughput need verification | **Recommended architecture** |
| **PB-MPM / CRESSim-MPM** | Cutting available in CRESSim | Repeated-cut persistence needs independent testing | Accessible implementations and alternative time integration | Stable motion does not guarantee correct stiffness, forces or fragments | Best available MPM comparison platform |
| **TopoCut** | Multi-step cutting task framework | Tracks fragment topology | Directly relevant learning tasks and rewards | Reported reconstruction cost restricts large-scale online RL | Learn from its task design; do not assume its speed solves our problem |
| **XPBD with cohesive/breakable connectivity** | Possible with a suitable cutting extension | Requires permanently updated connectivity and fragment contact | Local iterative computation; potentially practical implementation | Force calibration, directional bias and cut-surface accuracy | Strong alternative, not an automatic tomato model |
| **Solid SPH / other meshless damage methods** | Possible with suitable damage/contact machinery | Depends on interaction and fracture treatment | Natural material sampling; handles large deformation | Neighbor interactions and cut boundaries still need correct treatment | Secondary candidates; no verified turnkey advantage found here |
| **Peridynamics / phase-field fracture** | Can evolve cracks without a prescribed path | Depends on fracture/contact formulation | Useful when material-driven tearing and crack growth matter | Additional damage modeling and resolution requirements; training throughput unverified here | Retain for fracture-focused research, not the first RL implementation |
| **Granular sand / fluid particles** | Tool can move through material | Material already consists of separate grains or fluid | Simple material rearrangement | Does not represent intact skin and flesh being fractured | Reject as the tomato's primary mechanics |
| **Geometric slicing / learned dynamics surrogate** | Can be designed to allow it | Can represent pieces geometrically | Potentially cheap task rollouts | Forces and unfamiliar trajectories can be wrong without detection | Later acceleration option, not initial physical ground truth |

Dynamic FEM is not inherently limited to predetermined cuts. For example, Sifakis, Der and Fedkiw describe arbitrary cutting of tetrahedralized objects, and Courtecuisse and colleagues demonstrate interactive heterogeneous soft-tissue contact and cutting. Our current implementation's limitations must not be generalized to all FEM. [Arbitrary cutting paper](https://graphics.cs.wisc.edu/Papers/2007/SDF07/cutting.pdf), [interactive FEM study and associated SOFA scenes](https://orbilu.uni.lu/handle/10993/15809)

For SPH, the solid/fluid formulation and boundary treatment matter as much as the use of particles; the method is a family of numerical approximations, not a no-computation cutting feature. [Author tutorial](https://arxiv.org/abs/2009.06944)

The original MLS-MPM/CPIC work does explicitly address cutting and two-way rigid coupling. Its full solver and minimal teaching example are different artifacts; the short example must not be mistaken for a complete cutting implementation. [Authors' repository and paper links](https://github.com/yuanming-hu/taichi_mpm/blob/master/README.md)

Peridynamics has been applied to large-deformation hyperelastic fracture; phase-field MPM also models evolving damage rather than just splitting geometry. Those are meaningful options if spontaneous tearing becomes central. For this project, I found insufficient evidence of a ready, fast, batched tomato-cutting implementation to rank them above the leading candidates. This is an implementation-selection judgment, not a claim that these methods are inherently slow. [Hyperelastic peridynamics study](https://www.sciencedirect.com/science/article/pii/S0045782522006946), [CD-MPM author paper](https://www.math.ucla.edu/~cffjiang/research/wolper2019fracture/wolper2019fracture.pdf)

## 4. What the closest research actually establishes

### BladeMaster — closest architectural match; implementation access unresolved

The September 2026 preprint uses total-Lagrangian MPM with persistent cut-side labels. It reports progressive/intersecting cuts, recontact without rebonding and two-way tool coupling. Its limitations include approximate particle-proxy contact, no strict nonpenetration guarantee, no general stress-driven cracking, and growing active state counts with cut complexity. The resistance law is empirical; geometric cut history is not equivalent to our existing cohesive fracture law. [Paper, methods and limitations](https://arxiv.org/html/2609.27342v1)

The official demonstrations include sequential slicing, partial cross-shaped scoring and independent manipulation after withdrawal. These are unusually close to the requested behavior. They do not establish unrestricted, validated tomato dicing under an arbitrary RL policy. [Official demonstrations](https://jango6324.github.io/blademaster/)

**Engineering implications:** test reversals, repeated entry into the same incision, changing blade orientation mid-cut and cuts on moving fragments. Audit how a “new cut” is identified; the learner must not need to supply a complete future cutting surface. Do not assume that adding more cut labels permits unlimited history at constant cost. A separate candidate would require an explicit model-change decision before adoption.

### TopoCut — most directly relevant learning framework

TopoCut combines particle mechanics, damage/topology reconstruction, shape-based rewards and learned multi-step cutting. It studies slice, stick and dice tasks. Its paper expressly identifies mesh reconstruction as a bottleneck limiting large-scale online RL, and also acknowledges stiffness/resolution limitations. Its trained diffusion policy should not be described as proof of cheap unrestricted online RL. [CoRL 2025 paper, especially Section 6](https://arxiv.org/html/2509.19712v1)

At review time, the project page labels code “Coming Soon.” My recommendation is to borrow its emphasis on target fragment geometry and topology-aware observations, without placing expensive full mesh reconstruction and spectral analysis in every physics substep. [Project and availability](https://topocut.github.io/)

### RoboNinja — important proof of learned adaptive cutting, different task

RoboNinja learns adaptive cuts around rigid cores using estimated core geometry and collision feedback. Its simulator generates optimized demonstrations; real experiments include fruit and kinetic-sand proxies. That is relevant evidence for learning cutting behavior, but not validation of arbitrary tomato slicing, fragment mechanics or tomato cutting forces. [RSS 2023 project](https://roboninja.cs.columbia.edu/)

Its public repository is useful for studying the simulator-policy boundary and data pipeline. It is not interchangeable with a qualified repeated-fracture tomato model. [Official code](https://github.com/real-stanford/roboninja)

### CRESSim-MPM and PB-MPM — practical open starting points, with specific risks

CRESSim-MPM provides CUDA MPM implementations, cutting/suturing examples and an external interface. Its published timing comparison includes a falling-cube benchmark; those measurements cannot be treated as tomato slicing throughput. [IROS 2025 paper](https://www.ece.ualberta.ca/~tbs/pmwiki/pdf/Ou-IROS-2025a.pdf)

The public repository supports standard MPM, MLS-MPM and PB-MPM. The current changelog warns that a newer dynamic contact impulse implementation is not well tested. Pin the exact code version and check wrench signs, magnitudes, origins and timing before coupling to our robot. [Repository](https://github.com/yafei-ou/CRESSim-MPM), [changelog](https://github.com/yafei-ou/CRESSim-MPM/blob/main/CHANGELOG.md)

BladeMaster's authors report unwanted motion coupling between pieces in their CRESSim comparison. This is a competing authors' experiment, not an independent verdict on every current CRESSim version. Our withdrawal-and-independent-piece test must decide whether the chosen implementation is acceptable. [Comparison demonstration](https://jango6324.github.io/blademaster/)

PB-MPM changes time integration using compliant constraints. It offers a promising stability/cost tradeoff, but insufficient convergence changes apparent material response. A large stable timestep is not evidence of accurate cutting forces, and the integrator alone does not supply persistent fracture. [PB-MPM paper](https://media.contentapi.ea.com/content/dam/ea/seed/presentations/seed-siggraph2024-pbmpm-paper.pdf), [EA implementation](https://github.com/electronicarts/pbmpm)

### XPBD and recent destructible-particle work — credible alternative

XPBD derives constraints from energy/compliance and provides constraint-force estimates. It is more useful for this problem than an arbitrary spring animation, but force accuracy and convergence still need testing. Cutting requires additional connectivity, damage, contact and surface handling. [Original XPBD paper](https://matthias-research.github.io/pages/publications/XPBD.pdf)

OmniBody, a SIGGRAPH 2026 poster, describes a GPU framework using oriented ellipsoidal particles and local interactions for deformable, destructible bodies. This is a relevant alternative to investigate. I verified its official conference description, but not a released implementation or calibrated tomato-force benchmark; it is not the basis for a promised laptop speed. [Official conference entry](https://s2026.conference-schedule.org/presentation/?id=pos_427&sess=sess432)

Also beware of methods optimized for visual dissection. A recent breakable-shape-constraint paper explicitly describes its method as non-physical and its cutting update as requiring the complete path. Those limitations conflict with this project's force-sensitive, continuously chosen actions. [Author paper through ACM](https://doi.org/10.1145/3820013)

### DiSECt — retain its useful scientific role

DiSECt combines FEM, contact and weakening connections across a cutting interface, with demonstrated parameter calibration and motion optimization. It remains valuable for controlled comparisons. That does not make our heavily modified local candidate a good general-purpose training engine, nor mean its measured cost represents the original paper's implementation. [Original DiSECt project](https://diff-cutting-sim.github.io/)

## 5. Speed, hardware and memory: what can be compared honestly

The laptop reports **RTX 5060 Laptop GPU, 8,151 MiB GPU memory**, and approximately **31 GiB usable system RAM**. Large batches must fit GPU memory alongside robot simulation and, when enabled, rendering.

The saved local v43 settling run advances 1 simulated second in **6,330.9 wall-clock seconds**, about **105.5 minutes**. It uses 1,020 substeps per simulated millisecond, approximately 0.98 microseconds per substep, with damage disabled. This is a settling measurement, not a completed-cut benchmark. The approved mesh contains 9,394 vertices and 42,523 tetrahedra. [Saved result](/home/omen/teamwork_projects/tomato_cutting_right_arm/work/disect_material_validation_20261110_v43/settle_contact_result.json), [mesh and scope record](/home/omen/teamwork_projects/tomato_cutting_right_arm/docs/rl/DISECT_SECTION4_EXECUTION_PLAN_20261109.md)

BladeMaster reports the following **simulation-loop** measurements on an **RTX 5090**, excluding surface reconstruction and rendering. [Paper, Table I](https://arxiv.org/html/2609.27342v1)

| Published example | Particles | Step | Cuts | Wall seconds per simulated second |
|---|---:|---:|---:|---:|
| Gravity-driven cutting | 8,960 | 2 ms | 1 | 0.33 |
| Slice lifting | 8,960 | 2 ms | 2 | 0.36 |
| Moving knives | 7,922 | 1 ms | 3 | 0.62 |
| Partial scoring | 3,584 | 2 ms | 2 | 0.30 |
| Sequential slicing | 7,922 | 1 ms | 4 | 0.56 |

These results support testing a different computational design. **They do not establish a numerical speedup factor over our model.** Hardware, discretization, contact law, material parameters, cut mechanism and accuracy tests differ. The paper's banana force comparison is not tomato calibration. Do not assume millisecond timesteps remain accurate for our selected stiffness, contact tolerances and thin skin. [Experimental conditions](https://arxiv.org/html/2609.27342v1)

Memory comparisons require peak **total process GPU memory**, not merely one tensor allocator's report. Record particles, active grid states, contact pairs, fragment history and reset buffers. No comparable laptop memory measurements for these alternative methods were produced by this study.

### Real time is useful, but not automatically fast RL

For an illustrative policy acting at 50 Hz, one million transitions correspond to 20,000 simulated seconds. Ignoring policy updates, resets and recording:

| Aggregate collection speed | Time for one million transitions |
|---|---:|
| 10 times slower than real time, one environment | 55.6 hours |
| Real time, one environment | 5.56 hours |
| 10 times real time in aggregate | 33.3 minutes |

Ten million transitions multiply those durations by ten. These are arithmetic examples, not convergence predictions. A policy might require more or fewer samples. Parallel environments help only if measured aggregate throughput improves; memory pressure and GPU contention can erase the benefit.

Proposed engineering targets are **at least real-time single-environment physics for iteration**, then **500 aggregate control transitions/second at 50 Hz** as a useful early training target. These are proposed planning targets, not passed gates or a replacement for the existing accuracy contract. A slower but useful model might still support imitation learning or limited fine-tuning.

## 6. Proposed tomato and integration architecture

This section is a design proposal, not a description of features already implemented or validated.

### Material representation

Start by sampling the existing exterior into a particle body with no prepared internal cutting planes. Store mass, material identity, deformation state and irreversible cut history. Preserve the measured/declared total mass when changing resolution. For size changes, explicitly choose whether density or total mass is held constant.

Use two development levels:

1. **Mechanism test:** a homogeneous soft solid, clearly labelled as a proxy, to test free-path cutting, fragment independence and speed.
2. **Tomato candidate:** flesh plus a distinct cuttable skin representation, then add internal structure or rate effects only when needed to explain measured behavior.

Neither level inherits experimental validation from the old model. The skin is particularly important to investigate for first penetration and cutting strategy; this is a modeling hypothesis to validate, not a claim that arbitrary chosen skin constants reproduce our specimen. Avoid adding a full seed/juice model before evidence shows it affects the task being learned.

### Online cutting and mechanics

The simulator should evaluate the swept **sharp edge** and distinguish it from the blade faces, spine and handle. Contact by an unsharpened surface must not automatically remove material. A partial incision must leave the remaining material connected. Subsequent contact between separated pieces must exchange contact forces without restoring intact-material bonds.

A convincing model must explain resistance before separation and how resistance changes during slicing. Geometric splitting can be legitimate for a declared task proxy, but must not be presented as a calibrated fracture-energy prediction. Changing from the current cohesive law to an empirical cutting model is a scientific scope change, not a mere performance optimization.

Use continuous/swept contact or adequately resolved substeps so fast actions cannot jump through the tomato. Blade speed, angular speed, minimum feature size and allowed number of cuts must be declared operating limits. Test the physical result when timestep and resolution change.

### Keep the robot and kitchen

Retain the verified hand-on-handle pose, outward/backward elbow, relaxed left arm, disclosed fixed attachment, scene and controller interface. Change the material backend in a separate candidate.

The intended data flow is:

```text
Policy or scripted controller
          |
          v
Robot dynamics -> actual mounted-blade pose and motion
          |                         |
          |                         v
          |                GPU tomato/contact solver
          |                  + persistent cut history
          |                         |
          +--- reaction wrench -----+
                                    |
                          observations and rewards
```

Assign each interaction to one owner. Do not add native Isaac knife–tomato forces on top of external solver forces. Preserve wrench frame/origin transformations, synchronized clocks and the distinction between commanded and actual motion. Surface rendering should display the same fragment topology as the mechanical state.

### Training execution

Keep material updates on the GPU; avoid per-particle Python work, repeated CPU copies and per-substep files. Update the policy on a slower declared control clock. Collect compact diagnostics and occasional checkpoints. Separate compilation/startup time from steady stepping time.

Run headless for training. If the policy needs camera observations, include rendering at the real observation rate in the benchmark; do not quote physics-only throughput as end-to-end training performance. Full reconstructed surfaces need not be regenerated at every material substep, but mechanically relevant contact geometry must remain correct.

Begin with demonstration-based learning and bounded policy corrections. Then increase action freedom once the simulator passes adversarial contact and topology tests. Standard RL does not require differentiating through the simulator; differentiability is useful for other purposes but should not dictate the engine choice here.

Proposed observations include knife pose/twist, measured contact wrench, target shape/pose information and a fragment-aware representation. Training-only internal damage information must be identified as privileged if unavailable to the real robot. Reward actual independent fragments, desired thickness/shape, material retained, low excess force and safe support contact. Do not reward a visible red-surface gap alone.

## 7. A bounded decision experiment before migration

The purpose is to decide whether to adopt a method, not to launch another open-ended sequence of diagnostics. This is a proposed future experiment; none of its results are claimed here.

### Gate A — availability and reproducibility

Spend at most one working day establishing access to a usable BladeMaster implementation, its license, dependencies and a stock example. No automatic author message is authorized by this study. An independent implementation from the paper would be a separate development project, not an implied quick installation.

If usable code cannot be obtained, record the availability block immediately. Benchmark the existing CRESSim implementation only as an accessible comparator. Do not silently relabel it as equivalent to BladeMaster, and do not spend days adding an unvalidated fracture algorithm before establishing its likely cost and benefit.

### Gate B — smallest meaningful cutting tests

Use a simple soft block first, then the same tomato exterior. Keep blade geometry, units, support conditions and material targets explicit. Start with three resolution levels rather than a large parameter search. Record how each method approximates the continuum law; do not pretend different constitutive formulations become equivalent merely by assigning the same Young's modulus.

Required tests:

1. No-contact rest and board support.
2. Blunt-face indentation without an accidental cut.
3. Partial sharp-edge cut, stop, withdraw; the intact bridge remains connected.
4. Full cut, withdraw, then move one piece independently.
5. Bring the pieces back into contact; they collide but do not heal.
6. Two parallel cuts producing a thin middle slice.
7. Cross-cutting that slice into pieces.
8. Change direction/orientation while already in material.
9. Pause, reverse, re-enter an old incision and cut a moving fragment.
10. Repeat with different sampled sizes/shapes, then reset after a cut.

Use shared boards/supports and a separate isolated-fragment probe where appropriate so ordinary contact or support constraints are not mistaken for unwanted internal bonding. Save mechanical state and reaction traces, not just screenshots.

### Gate C — accuracy and speed together

Measure a short warmed-up segment first, forecast runtime, and cap each pilot at ten wall-clock minutes with a recoverable state. Begin with at most two hours of timed trials. A timeout is useful evidence that a configuration misses the throughput target; it is not authorization for an unattended multi-day run. Limit a failed case to one diagnosed correction before reassessing the method.

For each case record:

- Wall seconds per simulated second; control transitions/second; batch sizes 1, 4 and 8 only if memory allows.
- Separate material solving, tool/material contact, fragment contact/history, robot stepping, observations/rendering, reset and file-writing time.
- Particle/element count, spacing, timestep, substeps, iterations, precision, material parameters and number of cuts.
- Peak GPU memory, host memory and active-history growth.
- Force curves, peak force, impulse, contact work, penetration, mass drift and unsupported drift.
- Fragment count, independent motion, intact bridges and repeated-contact behavior.
- Paired timestep and spatial-refinement outcomes, with cut events compared at common physical times.

Existing 2 N force stops and 0.1 mm penetration limits are **not relaxed by this study**. If a candidate cannot satisfy them, report that finding. The implementation-specific linear residual check from the old solver cannot simply be copied to a different algorithm; propose an equivalent physical/numerical acceptance contract before adoption.

Within one material formulation, the previously used 0.1 mm position and 5% force comparisons are useful provisional refinement checks where applicable, with explicit near-zero floors. Across different formulations, agreement with the old solver is only a comparison: it is not experimental truth. A different fracture law requires separate assessment of onset, cutting work and separation.

### Gate D — adopt or stop

Adopt only if the candidate demonstrates new-path cutting, persistent fragment independence, acceptable contact/force behavior, reset consistency and useful measured throughput. Otherwise issue one concrete outcome: unavailable implementation, failed topology, failed physical accuracy, or inadequate speed. Do not turn an unavailable or failed candidate into a new indefinite development branch.

After adoption, run a small imitation-learning experiment before a large RL run. Keep a modest set of stricter reference cases for regression and comparison. Experimental tomato validation remains pending until independent measurements support it.

## 8. What changes, and what does not

The recommendation changes the proposed **material simulation architecture**, not the project's robot work. The scene, grip, controller interface and useful evidence remain valuable.

The achievable result is a reusable tomato generator that accepts new blade actions during an episode and evolves its cuts online. It would avoid preparing each cutting surface beforehand. It would still calculate physics, have resolution and action limits, and require validation before claims about real tomato cutting forces or learned-policy transfer.

**Decision:** pursue persistent-discontinuity GPU MPM as the preferred method; resolve BladeMaster implementation access first, then run the bounded comparison. Do not claim RL readiness from generic MPM support, a sand demo, a pre-rendered separation or a faster GPU benchmark alone.
