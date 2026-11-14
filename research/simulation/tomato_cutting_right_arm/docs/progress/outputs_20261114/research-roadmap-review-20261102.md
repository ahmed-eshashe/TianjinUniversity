# Cutting research: milestone review and next-stage plan

Reviewed 2 November 2026. Scope: local simulation research using the existing robot, the user-selected fixed knife mount, and the saved Newton tomato model. Experimental validation remains pending at the user's request. This is an evidence review and proposed execution plan, not a report of new cutting experiments.

## 1. Decision and status

Continue the project, but complete the integration prerequisites before attempting to count a first cut as successful. Sol produced substantial, reproducible numerical and scene diagnostics. Those results establish components; they do not yet establish a complete robot–tomato cutting environment.

The previous roadmap existed and was more detailed than the short checklist suggested:

- `TOMATO_SLICING_IMPLEMENTATION_PLAN.md`, especially sections 5–8, already specified staged cutting, a conventional controller, residual learning, observations, curriculum and evaluation.
- `NEWTON_TOMATO_PROTOTYPE_PLAN.md` specified local blade eligibility, fracture energy, connectivity, cut-face contact and release tests. It already identified the end-cap/thickness issue.
- `BLADE_CONTACT_AND_CUT_FACE_TEST_PLAN.md` supplied contact classes and proposed numerical gates.
- The dual-arm work was mainly a curriculum item, not a sufficiently detailed implementation or experiment plan.
- The bibliography was too narrow to constitute a literature review. The research synthesis below supplies direct cutting research and clearly labelled evidence from other manipulation tasks.

This document supplements those plans and takes precedence for the upcoming simulation sequence. It does not change frozen acceptance files or claim that old unpassed tests passed. Old 60-second and quota-checking clauses are obsolete relative to the user's subsequent instructions. Runs still need resource monitoring, cleanup and budgets sized to the experiment; there is no need to request permission after each small subtask. This review does not start a training run or physical robot experiment.

### Audit method and limits

Reviewed the original plans, saved reports, native worker/supervisor records, current implementation paths and input hashes. Nine selected native run records were inspected, covering startup, analytic collision, full-model/material/coupling/blade checks and the mounted robot. Earlier milestones were reviewed through their scoped diagnostic reports; this was not a fresh rerun of every historical experiment. No simulator was launched for this review.

Independent hash recomputation found all 20 final fixed-mount inputs, 45 frozen production files and 13 pinned installed dependencies unchanged. Twenty-four existing learning-contract/history tests pass on the host. An initial test invocation lacked the project's import path; the corrected invocation passed without code changes. These tests verify offline interfaces, not native learning readiness.

Evidence and the pre-review checklist are preserved in `milestone-evidence-audit-20261102.json` in the handoff outputs folder. Historical failures remain evidence; later passing fixtures do not erase them.

### Milestone verdicts

| Items | What the evidence supports | Review verdict / remaining limit |
|---|---|---|
| 1–3: computer, guard, startup | Saved RAM/VRAM monitoring and an empty CPU PhysX step with successful cleanup | Retain done for startup scope. This is not a forecast of long-run capacity. |
| 4: initial coupon | Isolated construction/rest diagnostics | Retain done for those fixtures; no cutting inference. |
| 5–6: geometry and contact conventions | Reference distances/normals and explicit frame/sign/weight contracts | Retain done as diagnostics. Failed earlier SDF/mesh routes are not production qualifications. |
| 7–8: snapshot and native buffers | Full-prefix validation, storage/capture, overflow refusal and generation clearing | Retain done for owned diagnostic captures, not arbitrary concurrent live capture. |
| 9–10: analytic collision | Six box fixtures, including interior edge/face contact and transformed coordinates | Retain done for box geometry; not general swept collision completeness. |
| 11: force precision | Separate geometric tolerances and binary32 arithmetic replay pass | Retain done under disclosed reference version 2. The older combined absolute-force comparison remains failed. |
| 12: authored blade | Original surface, full tomato contact generation, short force transfer and replay | Retain scoped component pass. No full cut, high-speed sweep or physical force calibration. |
| 13–14: scatter and dynamics | Stationary distribution and minimal one-step momentum/discrete-energy checks | Retain done for component verification. |
| 15: Newton–PhysX exchange | Free rigid probe/blade and earlier articulated proxy diagnostics | Retain scoped component pass. Actual mounted robot feedback is a new integration gate under 23B. |
| 16: material solver for cutting | All 47 patches under prescribed tensile loading; bulk volume protection | **Partial/open against the original cutting goal.** Rotating material frames, supported mixed loading and whole-fruit reclosure remain unresolved. |
| 17: measurements | Published curve is a provisional comparison only | **Pending by user decision.** Do not block numerical development or mark it validated. |
| 18: small coupon separation | Small interface/solid coupon failure, reclosure and replay | Retain done precisely as a small-coupon milestone. |
| 19: placement and frames | Actual robot and original knife, one active knife, ideal fixed mount | Retain done for the derived scene. No manufactured bracket or finger-grasp qualification. |
| 20: target support/collisions | Authored support nodes, short gravity probe, working rigid contact monitor | **Partial/open for sustained support and deformable contact under cutting loads.** |
| 21: dry motion | Two offset approach/stroke/retreat cycles under robot gravity | Retain done for the tested route only. Actual cutting route still needs clearance and reach checks. |
| 22: reset | Rigid reset, separate material reset and generated-contact clearing | **Partial/open for the assembled loaded/post-cut episode.** |
| 23–32 | No completed first cut, dual-arm cutting baseline or learning pilot | Remain upcoming. |

The reviewed checklist therefore has **18 completed scoped milestones, 3 partial integration milestones, 1 experimentally pending milestone and 10 upcoming milestones**. The interface combines the partial and pending items as four open checks. This is a scope correction from the earlier 21/1/10 count, not lost work or three newly failing runs. Milestone counts are not percentages of engineering effort.

### Most important evidence

- The full model has 4,032 nodes, 33,996 springs, 16,291 volume cells and 47 cohesive patches. Its material-loading pass prescribes 514 interface nodes; it is not a free knife-driven fracture experiment.
- The final authored-blade exchange has 17 Newton and 17 PhysX steps at 1/2400 s, about 7.08 ms in total across baseline, replay and clear control. The 16 contact intervals are two 3.33 ms sequences. Damage eligibility is disabled during this contact qualification. Its 101.19 s process runtime includes setup and diagnostics; it cannot be treated as steady-state simulator throughput.
- The actual robot test has 3,851 PhysX steps and two approximately 8.02 s dry cycles. Its target gravity test is separate: only 5 ms per repetition, with 25 fixed support nodes. These clocks do not establish an eight-second deformable scene.
- Minimum dry-route target gap is 34.4 mm. Minimum board clearance is 6.01 mm despite a planned 12 mm height. That difference matters when designing the contact route; it is not a ready-made cutting tolerance.
- The 11,439-contact reset challenge generates contacts from an artificially shifted target but does not integrate those contact forces. It cannot establish reset after loaded coupled cutting.
- `tomato_native_full_model.py` rejects the combination of full-model volume stepping and mesh self-contact. `tomato_native_volume_steps.py` rejects eligible, unfailed patches in compression with nonzero shear. The fixed world-X material frame is explicitly disclosed. These are implementation boundaries, not hypothetical concerns.

## 2. Research basis: a focused literature review

Selection: primary papers directly addressing food cutting, forceful stabilization, residual control, transfer and evaluation. This is a targeted engineering review, not a systematic review or proof of an exhaustive novelty search. The recommendations below are our project-specific synthesis. A paper's successful experiment does not validate this implementation or supply its safety limits.

### R1. Jamdagni and Jia, IROS 2019

**Robotic Cutting of Solids Based on Fracture Mechanics and FEM.** DOI: 10.1109/IROS40897.2019.8967988. [Author-hosted paper](https://robolab-iastate.github.io/papers/IROS19.pdf).

Direct food-cutting evidence: force, torque and work comparisons include a tomato. The setup uses scanned geometry, food with a pre-cut flat base and downward motion at 6.25 mm/s. The model makes restrictive material and fracture-plane assumptions. Use it to define comparison quantities and document differences in support, geometry and motion. Do not copy its curve as independent specimen data or treat its speed as our validated control setting. Its printed modulus-unit issue is clarified by the later paper below.

### R2. Jamdagni and Jia, IEEE Transactions on Robotics 40, 2024, pp. 4526–4543

**Robotic Cutting of Fruits and Vegetables: Modeling the Effects of Deformation, Fracture Toughness, Knife Edge Geometry, and Motion.** DOI: 10.1109/TRO.2024.3462943. [Author-hosted manuscript](https://faculty.sites.iastate.edu/jia/files/inline-files/TRO24.pdf); [laboratory publication page](https://robolab-iastate.github.io/ResearchModelingOfCutting/).

Extends the analysis to slicing and curved knife motions, connecting fracture, deformation and blade geometry. Table II labels modulus in MPa and gives tomato E = 0.4 MPa; thus the old unit ambiguity need not remain unresolved in our bibliography. This does **not** identify our tomato's modulus or justify replacing the current synthetic law. The table lists tomato for chopping; slicing/rock-chop demonstrations involve other foods. The discussion retains quasi-static, planar-fracture and material assumptions and describes coordinated holding-hand work as future work. Two arms used in different experiments are not a demonstrated simultaneous dual-arm tomato cut. This is an extension of earlier work, not an independent replication of the older tomato dataset.

### R3. Heiden et al., Robotics: Science and Systems, 2021

**DiSECt: A Differentiable Simulation Engine for Autonomous Robotic Cutting.** DOI: 10.15607/RSS.2021.XVII.067. [Project and paper links](https://diff-cutting-sim.github.io/); [paper](https://arxiv.org/abs/2105.12244).

Uses FEM, continuous contact and weakening springs across a planned cutting interface. It demonstrates calibration against both commercial simulation and real cutting measurements, and constrained trajectory optimization. This supports investigating a reduced predefined-plane model and optimizing motion only after its force response is checked. It does not validate our spring/barrier implementation, arbitrary cuts or tomato parameters. Public simulated comparison data must not be relabelled tomato experiments. Real apple/potato force fits in the paper also do not establish independent tomato validation. Keep calibration and held-out prediction separate.

### R4. Mitsioni, Karayiannidis, Stork and Kragic, Humanoids 2019

**Data-Driven Model Predictive Control for the Contact-Rich Task of Food Cutting.** DOI: 10.1109/Humanoids43949.2019.9035011. [Author manuscript](https://arxiv.org/abs/1903.03831).

Uses learned recurrent dynamics with model predictive control, a velocity-controlled robot and force/torque measurements; evaluates cutting on familiar and unfamiliar objects and force-critical cases. It is directly relevant to the alternative to expensive RL. It does not establish that our wrist has those sensing channels or that this model transfers to our robot. Adopt MPC as a justified comparator/fallback when data and sensing support it, not as an obligatory extra system before a basic cut works.

### R5. Holladay, Lozano-Pérez and Rodriguez, IJRR, extended manuscript 2023 / publication 2024

**Robust Planning for Multi-stage Forceful Manipulation.** DOI: 10.1177/02783649231198560. [Author manuscript](https://arxiv.org/abs/2208.00319).

Plans forceful tasks using joint torque and friction constraints along the chain transmitting a wrench. The extended work includes vegetable cutting and different stabilization strategies. This motivates testing whether the supporting arm can actually resist the cutting wrench, rather than merely reaching a plausible pose. Its simplified cutting formulation assumes negligible deformation, quasi-static behavior and specified forces. It is not a tomato deformation model or a complete dual-arm compliant-cutting controller. We adopt the load-path reasoning, not its rigid approximation as our validation standard.

### R6. Johannink et al., 2018 manuscript / ICRA 2019

**Residual Reinforcement Learning for Robot Control.** [Author manuscript](https://arxiv.org/abs/1812.03201).

Combines a conventional controller with a learned residual and demonstrates contact-rich block assembly. This supports our architectural choice to learn small corrections around a competent baseline. The evidence is not food cutting, and a residual alone supplies no safety guarantee. In our plan, a separate constraint layer bounds commands and the policy cannot modify mechanics or success criteria.

### R7. Peng et al., ICRA 2018

**Sim-to-Real Transfer of Robotic Control with Dynamics Randomization.** DOI: 10.1109/ICRA.2018.8460528. [Author project and paper](https://xbpeng.github.io/projects/SimToReal/).

Demonstrates transfer for robotic object pushing with dynamics variation in training. This motivates testing sensitivity to uncertain properties. It neither proves cutting transfer nor supplies reasonable tomato parameter distributions. Our ranges must come from measurements or clearly labelled sensitivity studies, stay within solver validity and be held separate from test cases. Randomization cannot repair a missing force path or incorrect fracture mechanism.

### R8. Agarwal et al., NeurIPS 2021

**Deep Reinforcement Learning at the Edge of the Statistical Precipice.** [Proceedings paper](https://papers.nips.cc/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf).

Shows why few-run point estimates can give unreliable RL comparisons and advocates uncertainty-aware reporting. Apply the principle through multiple training seeds, paired held-out cases and interval estimates. Its benchmark recommendations do not prescribe a sufficient sample size for robot safety. Three seeds and 30 cases are an initial project design, not a literature-certified proof of superiority or reliability.

### Synthesis and research questions

The most defensible contribution is controlled robot-cutting research built on explicitly qualified simulation. Detailed fruit anatomy and a new general fracture simulator are not prerequisites unless the measured task behavior demands them.

1. **RQ1:** Within the supported model and matched cases, how does draw-and-down motion change peak cutting load, work and release quality relative to downward-only motion? First establish that both motions produce genuine separation. R1–R4 motivate this question; no improvement percentage is assumed.
2. **RQ2:** Can a contact-based left-hand support replace the disclosed rigid fixture while maintaining cut quality and resisting the measured wrench? R5 motivates the load-path tests; a successful pose alone is insufficient.
3. **RQ3:** Does a bounded residual controller improve success or reduce load/work over the best tuned scripted controller on held-out conditions at acceptable compute cost? Compare against a data-driven MPC approach only if sufficient identification data and sensing exist. R4, R6–R8 motivate the method and evaluation, not an expected positive result.

Simulation-only conclusions remain useful if labelled as such. Real tomato force accuracy and hardware transfer require reopening item 17 with independent measurements. None of these papers demonstrates the exact current robot, mount, tomato model and two-way solver combination.

## 3. Before milestone 23: complete the integration prerequisites

### P0 — Freeze the benchmark contract and measurement definitions

Create a versioned simulation contract without overwriting `slicing_criteria.json` (currently draft/inactive). Record mesh, material registry, knife geometry/mass/inertia, fixture nodes, coordinates, controller, clocks, collision classes and all tolerances with provenance. Distinguish existing fixture-specific thresholds, proposed engineering targets and missing hardware limits.

The saved cut plane is 10 mm from the ellipsoid's extreme left end. Call this **a nominal 10 mm end cap**, report its expected curved thickness profile, and compare the released shape against that profile. Do not demand uniform 10 mm thickness at five points on this geometry. A uniform slice is a separate pre-trimmed specimen or two-plane/two-cut benchmark requiring new topology/contact qualification. Keep the existing one-plane model for the first cut.

Declare allowable board interaction: initially stop above the board or cut a supported specimen with a documented clearance arrangement. If full separation requires blade–board contact, qualify that contact and its force budget before using it. Do not extend the dry route downward and presume its 6 mm clearance proves this.

**Exit:** an unambiguous case and evaluator specification, including numerical stop criteria and a register of unresolved hardware limits. Every metric can be computed from saved traces. No new material constants claimed from appearance or a plotted curve.

### P1 — Finish material and full-fruit contact support (reopens 16)

Implement and independently verify a material frame that follows the intended deformation; common rigid rotation must rotate forces and preserve scalar energy/damage. A fixed-world restriction may support limited diagnostics but cannot justify freely rotating separated fragments. Define the admissible normal/shear law, energy budget, unloading and compression behavior before enabling it. Pure compression must not create opening damage; irreversible history must not accumulate from rejected solver trials.

Combine volume admissibility with cut-face/self-contact. Test intact, partially damaged and fully failed interfaces, including reclosure; do not disable all self-contact to obtain a successful video. Audit cross-interface bulk, skin, volume, damping and fixture connections so failure genuinely removes material ties while contact can still transmit compression.

Implement current-deformation blade-edge eligibility with a swept check or a documented substep bound verified against a finer reference. Time, depth, proximity alone and a permanently activated row are not eligibility evidence. Preserve prequalified force arithmetic and fracture budgets when extending the operator.

**Exit:** small independent mixed-loading/rotation tests, followed by actual full-mesh nonfracturing and partial-fracture cases, with no unsupported state, unintended damage, invalid volume or spurious reclosure force. If the existing law cannot meet this, revise a versioned model or narrow the experiment explicitly; do not weaken pass criteria after seeing a failure. This is the main technical risk.

### P2 — Sustained support and environment contact (reopens 20)

Keep the disclosed 25-node remainder fixture initially; no slice node may be pinned. Advance the actual deformable target under gravity on the same simulation clock as the robot. Establish a settling criterion using velocity/energy drift, then hold for at least the planned full episode duration, including withdrawal and one-second release. The existing 5 ms result is the starting check only.

Add and verify deformable–board and fixture contact where applicable, with positive-contact and clear controls. Measure reaction forces, deformation and support work. Challenge the support with bounded forces and moments representative of progressively measured cutting loads. Resolve whether the board carries weight or the fixture suspends the target; log the actual load path.

**Exit:** target remains in the declared admissible pose/deformation envelope for the full duration; no creeping through the board, hidden support of the slice or fictitious fixture energy. The load envelope is documented as synthetic until experimentally measured.

### P3 — Performance profiling and budget sizing

Measure setup/compilation separately from warmed-up contact generation, solver steps, cross-engine synchronization, logging and rendering. Report seconds per simulated second, peak RAM/VRAM and cost per complete episode. Profile the existing full-surface coverage path before planning thousands of rollouts; the 101 s short diagnostic is an obvious concern, but not a steady-state speed measurement.

Use one environment initially, then consider batching only after demonstrated memory and correctness headroom. Set watchdogs from measured episode costs plus a documented allowance, retain cleanup and reserve checks, and checkpoint long studies. A watchdog expiry is incomplete evidence, not a physical failure or a passed cut. Larger wall-time budgets do not fix numerical instability.

**Exit:** credible cost estimates for one baseline matrix and a small learning pilot. If too expensive, optimize contact bookkeeping while retaining equivalence tests, use fewer well-chosen experiments, or investigate a separately validated surrogate/coarser model. Never substitute a faster model silently.

## 4. First controlled cut — milestones 23–26

### 23A — Contact-capable robot route

Starting from the proven offset dry route, compute an actual reachable approach and draw/down stroke for the saved plane. Recheck joint limits, tracking, mount transform and swept distances to both hands, robot links, board and fixture. Include observed tracking error and geometric uncertainty in the envelope. Retain the ideal right-hand fixed mount. The initial blade orientation stays within the supported plane.

**Exit:** actual intended path passes dry checks and an explicit contact/forbidden-contact classification. AABB separation is a useful coarse screen, not the final near-contact distance test.

### 23B — Actual mounted-blade force feedback, before fracture

PhysX must own the articulated robot/tool motion; Newton owns deformable motion. At explicit timestamps, exchange blade pose/velocity, integrate deformable contact and return its opposite wrench to the correct robot link and origin. Do not duplicate the same force in both engines or teleport the blade to a prescribed path while calling it dynamically coupled. Document subcycling, when the wrench is held and any exchange delay.

Begin with a nonfracturing coupon and low-amplitude contact. Include free-space, reversed direction, off-center contact moment and controller-enabled/disabled comparisons. Verify reaction signs, wrench-origin shifts, articulation response and queue clearing. Account for gravity, actuator work and fixed-base/fixture reactions in momentum and energy ledgers; a driven robot is not an isolated free body. Check integrated exchanged impulse/work, not just equal reported force arrays. Reduce coupling time step to detect lag-induced energy injection.

**Exit:** independently reconciled state, wrench and work traces for actual robot contact, within a preregistered fixture-specific error budget that tightens under refinement. Unsupported compression/shear or material invalidity is a stop. Do not reuse free-blade tolerances without scaling/justification.

### 23C — Progressive short cuts

Use a conventional bounded draw/down controller with phases: settled rest → nonfracturing indentation → shallow cut → stop → withdrawal. Extend depth only after each preceding trace is interpretable. First compare pure downward and drawing motion at matched specimen, cut plane and comparable completion conditions. Force/admittance control is conditional on a verified signal, delay and bandwidth; simulated ground-truth force may be used for a clearly labelled simulation controller.

Log at synchronized physics timestamps: actual and commanded tool pose/velocity; contact force and moment; maximum penetration and contact count; eligibility, damage and patch energy; volume ratios; fixture reactions; robot effort/tracking; stored/kinetic/fracture/friction/numerical work terms; resource use; termination cause. Log state around first contact, fracture onset, stop and withdrawal, not just the final frame.

**Exit:** a slow short cut with current-contact-driven damage, bounded numerical behavior and complete provenance. This completes 23, not 24. A visually open groove or a high damage average is not separation.

### 24 — Genuine separation and post-cut behavior

Extend the qualified stroke to the intended interface and withdraw the blade. Check the complete mechanical connectivity graph: zero remaining material connections between the two intended pieces, including residual stiffness/damping and support bridges. Separate material bonds from temporary compressive contact. The model must contain two physical pieces, not two visual groups still sharing a constraint.

Observe at least one continuous simulated second after withdrawal. Confirm independent motion, no healing, admissible volume and stable board/cut-face contact. If a probe is needed to demonstrate independence, first prove disconnection and bound the probe so it cannot finish tearing an attached piece. Measure mass and the end-cap profile; report deformation and taper explicitly.

Negative controls: no contact, off-plane blade, partial-depth stop, withdrawal before release and a deliberately surviving connection. They must not receive full-success labels. Blade penetration depth, elapsed time, reward or forced bond deletion cannot substitute for this evaluator.

**Exit:** all release conditions pass with valid traces. A partial attached cut, detached-but-unverified piece, numerical failure and timeout remain distinct outcomes.

### 25 — Repeatability and numerical sensitivity

Run the same saved case from fresh state and from reset. Refine the coupling/mechanics time step through at least three levels (for example h, h/2, h/4), contact quadrature independently, and solver iterations. Refine the material mesh separately while preserving physical mass, modulus and fracture energy per area; changing mesh-dependent raw spring constants without consistent reconstruction is not a convergence study.

Compare peak/resultant force, cutting work, fracture timing/path, release status, minimum volume, penetration, end-cap profile and remainder motion. Use a relative error with an explicit absolute floor near zero. Existing proposed targets of under 10% change in peak force/work and under 1 mm profile change are starting engineering gates, not experimentally validated truth. Require the two finest levels to agree and investigate nonmonotone results. Exact replay on one GPU is useful but does not prove numerical accuracy or cross-platform determinism.

Then run a small documented matrix of geometry, speed and supported material variations. Separate repeatability from robustness; synthetic parameter changes test sensitivity, not biological validity.

**Exit:** a reproducible region of supported operating conditions and a numerical error/cost table. Failed conditions remain in the report.

### 26 — Freeze the single-arm baseline and complete loaded reset (22)

After an actual partial and complete cut, reset both engines, robot/controller state, contact caches/counters, queued wrenches, integrator buffers, material history, eligibility, clocks and observation history. Compare the following episode against a clean launch. Include failure/abort reset, not only successful completion.

Archive a versioned scene, mesh, parameters, source hashes, seeds, hardware/software versions, command, evaluator, raw synchronized traces, compact video and known limits. Provide one-command reproduction with a declared cost. Record which old milestones are now closed and which remain pending.

**Exit:** independently reproducible scripted single-arm cuts and clean loaded resets. This is a numerical baseline, not experimental tomato validation or a hardware-ready controller.

## 5. Dual-arm extension — milestones 27–29

### 27 — Introduce the left arm as physical support

Keep the right fixed knife mount and single-arm controller unchanged to isolate the support change. Verify left-arm frames, joint/effort limits, reachable support patches and collision geometry. First rehearse with a rigid surrogate, then use the actual deformable tomato. Build two-way hand–tomato contact with correct normals, friction and opposite hand reaction; a static visual hand or teleported object is not stabilization.

Use a broad, reachable support on the remainder away from the cut plane. Test the support alone under gravity and incrementally applied forces/moments before allowing the knife near it. Measure slip, object rotation, contact forces, local deformation and joint load margin. A fixed attachment may be a labelled intermediate kinematic test, but not the final grasp/support result.

Transfer support from the 25-node fixture gradually, checking that it no longer supplies load once left-hand stabilization is claimed. No hidden pins or direct left-hand force on the released cap. Qualify the actual grasp/contact arrangement under the measured cutting wrench envelope, including uncertainty. Without measured bruise/crush limits, report deformation and compression as synthetic metrics, not food-damage safety.

**Exit:** sustainable contact-based support without the rigid fixture, with an explicit operating envelope and a demonstrated clear retreat route.

### 28 — Coordinate motion and force transfer

Use a simple state machine before a learned bimanual policy: approach support → establish and verify support → remove fixture load → verify cut corridor → cut → withdraw knife → release/reposition support. The left arm stabilizes the remainder while the right cuts. Do not command incompatible rigid poses that create an artificial closed-chain squeeze.

At each stage, verify force/moment transmission through hand contact and both articulations, relative motion and delay. Evaluate loss of support, low friction, pose error, stale sensing, effort saturation and attempted knife–hand approach. A support failure stops cutting and triggers a prechecked retreat/hold strategy; an arbitrary retreat through the hand is not an acceptable fallback.

Use exact relevant surface distances plus uncertainty, not just link origins. The old 20 mm blade-to-left-hand margin is a proposed simulation starting point; verify feasible geometry and stopping distance before freezing it. Deliberate hand–food and right-mount contact are allowed; blade–hand contact is forbidden. Establish positive controls for the detectors.

**Exit:** synchronized support and cutting motions under bounded disturbance, correct load paths, no forbidden contact and clean bimanual reset. If support cannot resist the load, revise support/controller geometry; do not make friction arbitrarily large to force a pass.

### 29 — Matched dual-arm cutting comparison

Repeat milestones 23–25 with the left support replacing the fixture. Use paired cases and the same right controller. Compare success, end-cap profile, force/work, remainder drift, hand–food slip, maximum compression, minimum knife–hand clearance and compute cost. Include support failure cases rather than reporting only successful videos.

**Exit:** reproducible dual-arm baseline with all support loads genuinely carried through contact. Keep a separate fixed-fixture baseline for diagnosis. Knife finger grasp, knife pickup, fruit reorientation and repeated slicing are later experiments with their own retention/topology gates; they are not silently included in this milestone.

## 6. Learning and experiments — milestones 30–32

### 30 — Freeze the environment and learning question

Build on the existing offline `tomato_learning_contract.py`, `tomato_learning_episode.py` and staged evaluator; do not rewrite them as if no preparation exists. Their current flags explicitly do not authorize native commands/training or claim native reset validation. Complete the runtime bindings and independent provenance checks before changing those flags in a versioned implementation.

Initial policy: bounded residual draw and downward velocity around the best scripted baseline. Lock the orientation residual initially because the first benchmark has a predefined cutting plane; enable additional axes only after their mechanics are qualified. The existing three-axis reference can represent this with zero orientation residual. Keep left support scripted during the first dual-arm learning experiment.

Actor observations: verified joint position/velocity, tool kinematics, previous action and timestamped target/plane estimates with validity masks. Known simulator pose is permissible for a labelled known-state development task, not a claim of camera deployment. Damage, exact material parameters, connectivity and contact IDs stay evaluator/privileged-critic information, never hidden actor inputs. Add wrist channels only after confirming what the hardware measures, axes, origin, units, rate, bias and delay; joint torque is not automatically a calibrated six-axis wrist wrench.

Reward: terminal bonus only for the independent release/quality evaluator; bounded progress shaping plus normalized penalties for force/work, tracking, slip and time. Normalize using frozen baseline scales, not per-episode future data. Do not reward damage fraction or knife depth as successful cutting, and do not let a large task reward cancel a hard violation. Record all component rewards and ablate shaping that can encourage hacking.

Termination: success only after release observation; separate task failure, numerical invalidity, sensor/state staleness, constraint violation and time/resource truncation. A policy cannot change material parameters, detach bonds, reset the scene or alter termination criteria. Controller clipping alone does not establish joint-load feasibility.

**Exit:** reviewed observation/action/reward/termination schemas, units and masks; conventional baseline runs through the identical API and evaluator. The suggested 20 Hz policy rate remains provisional until timing and closed-loop tests support it.

### 31 — Repeated episodes and held-out registry

Challenge successful, partial, failed and interrupted resets. Verify no episode-to-episode history in either engine, the controller, sensor filters or actor observation stack. Repeated rollout records must agree with fresh-launch references within declared tolerances. Randomized cases need stable IDs and hashes of their physical configuration.

Split cases by specimen/geometry/material condition before tuning; changing only a seed is not independent physical generalization. Use training, development/validation and final held-out roles, with the final set unopened during method selection. The existing offline registry supports baseline/train/heldout labels: extend its schema deliberately if a validation split is added, retaining physical-configuration leakage checks. Baseline and policy evaluation must still be paired on the same held-out cases; “baseline” is a method, not a reason to exclude a test case from paired evaluation.

Start variation only over supported mechanics: size/pose, documented stiffness/toughness/friction ranges, sensor noise/delay and initial conditions. Preserve correlations and physical constraints where known. Randomize mesh/cut plane only when the geometry builder and evaluator support them. Label unmeasured ranges sensitivity ranges, not identified tomato distributions.

**Exit:** reliable repeated native episodes, a frozen case registry and measured rollout cost. Dataset preprocessing and normalization use training/development information only.

### 32 — Small pilot and research comparison

First measure baseline performance and train nothing until the environment passes. Choose PPO only as a provisional convenient baseline, not a proven best algorithm. A residual pilot uses one nominal condition, then supported variability. Retain the best tuned deterministic scripted baseline; compare on identical cases and equal declared evaluation conditions.

Use measured warm throughput to set an explicit transition and wall-time budget, then estimate the full study cost including evaluation. Record time-to-first-usable-controller and failed rollouts. If sample generation is impractical, prioritize low-dimensional trajectory search or data-driven MPC/system identification. A differentiable optimizer requires actual reliable gradients; citing DiSECt does not make our implementation differentiable. A surrogate requires held-out error and policy-behavior checks against the reference model.

Proposed initial study: at least three independent training seeds where feasible and at least 30 fixed held-out cases per trained policy, with paired scripted-baseline evaluation. Report each seed and case, success counts, confidence intervals, peak/typical loads, work, quality, constraint violations and wall time. Account for shared cases and training-seed dependence; do not treat correlated episodes as independent specimens. If intervals are too broad, report inconclusive or enlarge the study rather than declare a winner from the best seed.

The earlier 90% success target is a proposed advancement criterion, not proof of 90% population reliability. For illustration, even 30/30 independent successes have a two-sided exact 95% lower confidence bound of about 88.4%. Zero observed hard violations is required for advancement but does not certify hardware safety.

Minimum comparisons: scripted downward vs scripted draw/down; fixed fixture vs left support; scripted vs residual; residual with vs without supported parameter variation. Keep comparisons staged to avoid an unaffordable full factorial. Add MPC only when its sensing/data requirements are met. Report negative results and ablations using the same evaluator.

**Exit:** a small reproducible pilot with an honest conclusion (better, equivalent, worse or inconclusive), a compute ledger and a justified proposal for the larger study. Real-world transfer remains a separate later gate.

## 7. Acceptance register and execution order

| Quantity | Existing/proposed status | How to use it |
|---|---|---|
| Independent release ≥1 simulated second | Carried from prior plan | Mandatory release observation after blade withdrawal; not total episode length. |
| Mass discrepancy <1% | Prior proposed physical check | Explain numerical accounting and any removed mass; no disappearing material shortcut. |
| 10 mm ±2 mm thickness | Prior uniform-slice proposal | Not directly applicable to the current curved end cap; use profile-relative error first. |
| Remainder drift ≤5 mm / 5° | Prior proposed benchmark target | Validate feasible support/measurement definitions before freezing. |
| Contact penetration ≤min(0.1 mm, 10% local blade thickness) | Prior proposed contact target | Confirm local thickness and reference accuracy; failure requires refinement/model review, not hidden tolerance changes. |
| <10% peak-force/work and <1 mm profile change on refinement | Prior proposed convergence targets | Compare finest levels, include absolute floors and investigate nonmonotone results. |
| Whole-system energy residual | Not yet frozen | Derive a discrete ledger including actuators, supports, friction and numerical dissipation. The tensile fixture's 1% gate is not automatically transferable. |
| Force/torque, sensor and crushing limits | Hardware/measurement inputs missing | Version explicit synthetic simulation bounds; do not assert hardware-safe values. |
| Knife–left-hand clearance 20 mm | Prior simulation proposal | Include uncertainty and stopping distance; verify reachability before freezing. |
| 3 seeds, 30 cases, 90% success | Initial study proposals | Report uncertainty; increase sample size for the intended claim. |

Execution dependency: **P0 contract → P1 mechanics and P2 sustained scene → 23A/B mounted contact → 23C short cut → 24 release → 25 convergence → 26 archive plus loaded reset → 27 support → 28 coordination → 29 dual-arm baseline → 30/31 environment → 32 pilot.** P3 profiling runs early and is revisited after integration. Offline design for later stages can proceed before earlier experiments pass; later claims cannot.

The next implementation work should start with P0 and a minimal nonfracturing mounted-contact case while resolving P1/P2, not a deep cut or a training launch. No clarification is needed to begin that work under the current simulation scope. Hardware sensor details, experimental specimens and uniform-slice requirements become necessary only when those specific branches are taken.

## 8. Reproduction and evidence locations

Engineering root: `/home/omen/teamwork_projects/tomato_cutting_right_arm`.

Handoff outputs: `/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs`.

Key reviewed reports: `physics-materials-integration-20261101.txt/.json`, `fixed-mount-robot-scene-20261101.txt/.json`, `analytic-force-reference-recheck-20261031.txt`, `dynamic-proxy-momentum-work-check-20261031.txt`, `native-contact-buffer-roundtrip-20261031.txt`, and `isaac-startup-verification-20261031.txt` in the outputs folder.

Key raw runs beneath the engineering root: `runs/native/full_model_20261101_07`, `full_damage_20261101_06`, `full_blade_20261101_08`, and `fixed_mount_20261101_06`. Source boundaries: `rl/tomato_native_full_model.py:93`, `rl/tomato_native_volume_steps.py:34`, `rl/tomato_fixed_mount_target.py:30`, and `rl/tomato_fixed_mount_worker.py:153`.

New review evidence: `milestone-evidence-audit-20261102.json`. Primary TRO24 and DiSECt manuscripts were retrieved from the authors/arXiv and text-inspected locally because the browser text service rejected their file sizes; source PDFs and extracted text are in `work/review_20261102`. No synced files under the ChatGPT project's `sources/` directory were edited.
