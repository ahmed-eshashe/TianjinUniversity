# Astra High execution plan for a reusable cuttable tomato

Date: 10 November 2026. Status: plan prepared; implementation not started.

## Objective and limits

Build a separate GPU simulation candidate that accepts new knife motions during an episode, retains completed cuts after withdrawal, supports further cuts on the remaining material, and can be measured as an RL environment. Preserve the existing robot, kitchen, natural handle grip, outward/backward elbow, fixed attachment, controller interface and all research evidence.

**CRESSim is reusable infrastructure under evaluation, not a selected final engine.** Its current public implementation failed persistent-fragment independence. Extending it is research development, not finishing a nearly complete tomato asset. A successful prototype may require a separate numerical backend rather than a small patch.

The first deliverable is an **uncalibrated, physically checked tomato approximation for controlled learning experiments**. It is not an exact real tomato. Experimental tomato validation remains pending, as requested. Separate skin puncture, internal chambers, seeds, juice flow, spontaneous tearing and accurate real-world force prediction are outside this first deliverable. Do not silently claim those capabilities from a red exterior or a bulk elastic material.

All physical simulation still requires calculations. The target is online computation without preparing a new fracture mesh or solving an entire future trajectory before each episode. Size changes can be generated at reset; arbitrary resizing of a damaged tomato in the middle of an episode is not required.

This is a proposal for a new isolated candidate. Preparing this document does not adopt a new material/fracture model or change the existing model. Execute the prototype scope only after the user instructs execution of this plan. Routine work inside that scope should then proceed without repeated approval requests. Changes to the specified scope or retained physical limits require a concrete decision.

## What the evidence currently establishes

| Evidence | Established result | What remains unestablished |
|---|---|---|
| Local unmodified CRESSim build | CUDA compatibility on this RTX 5060 laptop | Suitability for tomato physics |
| 8000-particle block | MLS median 0.762 and PB median 1.455 wall seconds per simulated second | Equal accuracy, tomato forces, robot throughput or RL batching |
| Two intersecting blade passes | Both trajectories execute | Independent fragments: failed in both solvers |
| Close-gap independent-body controls | Motion isolation with blade held off grid nodes; unwanted coupling with blade absent | Robust recontact without healing |
| Existing DiSECt candidate | Useful constitutive and component evidence | Latest candidate's complete cutting qualification must be read from actual result files |

Read these before code changes:

- [Local CRESSim report](/home/omen/Documents/Codex/experiments/cressim_20261110/REPORT.txt), [results](/home/omen/Documents/Codex/experiments/cressim_20261110/evaluation.json), and the preserved harness/contract in that directory.
- [Method review](/home/omen/teamwork_projects/tomato_cutting_right_arm/docs/rl/ARBITRARY_CUTTING_RL_METHOD_STUDY_20261110.md).
- [Existing integration plan](/home/omen/teamwork_projects/tomato_cutting_right_arm/docs/rl/DISECT_SECTION5_EXECUTION_PLAN_20261110.md) and [existing cutting gates](/home/omen/teamwork_projects/tomato_cutting_right_arm/docs/rl/DISECT_SECTION4_EXECUTION_PLAN_20261109.md).

The v43 status file inspected during planning still describes a half-step settling run; its recorded worker/supervisor PIDs were absent when checked. Treat that status as stale until actual result files establish otherwise. This plan does not restart that expensive run. A newly completed DiSECt cut is **not a prerequisite** for the separate prototype. Use existing evidence as a reference, not experimental truth.

## Research basis and method choice

[CRESSim's paper](https://www.ece.ualberta.ca/~tbs/pmwiki/pdf/Ou-IROS-2025a.pdf) supplies an accessible CUDA simulation framework and cutting geometries. Its published demonstrations do not qualify our repeated-cut tomato task; the local measurements govern that decision.

[BladeMaster](https://arxiv.org/html/2609.27342v1) is the most directly relevant published design reference: total-Lagrangian MPM with persistent particle-side history, topology-aware transfers and separate material contact. Its resistance treatment is empirical and its topology follows the tool; this is not the existing cohesive failure law. It does not guarantee strict nonpenetration or general stress-driven cracking. Published speed uses an RTX 5090 and excludes reconstruction/rendering. Its [official page](https://jango6324.github.io/blademaster/) still presents no code download in the inspected links. Do not contact its authors or claim our implementation is their official code.

**Preferred development attempt:** reuse CRESSim's build, storage and interfaces where useful; implement a separately named, paper-informed persistent-discontinuity backend. Derive and test the numerical formulation. Do not attach a few permanent labels to the current Eulerian solver and assume that reproduces a total-Lagrangian method.

Geometry-triggered separation and force-dependent material failure are different models. For this candidate, document which mechanism is used. A force/damage threshold that controls new physical separation is an additional modeling decision requiring its own validation; it must not be advertised as a feature already supplied by the paper. A geometry-only mechanism may pass a topology unit test but cannot by itself pass the physically checked tomato gate below.

[TopoCut](https://arxiv.org/html/2509.19712v1) reports reconstruction costs that restrict large-scale online RL. This motivates benchmarking the complete learning loop and keeping visualization reconstruction out of material substeps. It does not justify ignoring mechanically necessary contact geometry.

## Definition of the first finished model

Completion requires all of the following within a declared resolution, size and action envelope:

1. Generate the existing tomato exterior at its measured baseline size and two size variants at reset, with consistent density, mass and material units.
2. Deform under contact; resist a blunt tool without creating a cut.
3. Produce a partial cut that leaves an intact bridge, and a complete cut that remains separated after withdrawal.
4. Produce two successive slices, then cross-cut a separated piece; preserve the remaining material's state throughout.
5. Allow the policy to choose its next incremental blade action without supplying a future cutting plane or complete path.
6. Let pieces move independently when apart and collide/slide when touching, without rebonding.
7. Reset and checkpoint/restart consistently after cutting.
8. Provide actual blade state, a verified contact reaction channel, observations, termination flags and a mechanically meaningful success measure.
9. Meet a measured speed/memory target for the intended learning mode.

Passing a block test does not finish the tomato. Passing the tomato test does not finish robot integration. Passing a scripted episode does not establish a learned policy. Keep these statuses separate.

## Scope and operating envelope

- Use one knife and one tomato initially. Keep the disclosed fixed hand attachment.
- Preserve the real CAD blade and scene transforms for later contact/integration. Simple analytical tools are allowed only in labeled component tests.
- Keep the approved two-stage horizontal withdrawal: move along the blade until geometrically clear, then toward the body. Do not replace it with an upward lift in the robot demonstration. Unit tests may use other explicitly labeled paths to isolate mechanics.
- Begin with state observations and headless physics. Camera-policy training, dual-arm stabilization and video production are later work.
- Preserve existing 2 N force-stop and 0.1 mm penetration limits for project contact/robot qualification. Preserve applicable board, support and volume guards. Do not copy an old solver's algebraic residual tolerance onto a different algorithm; replace it with justified equivalent numerical checks and retain physical checks.
- The existing DiSECt speed deferral does not establish RL suitability for the new candidate. Speed must be measured for its new purpose.
- The first tomato may use effective bulk behavior rather than resolved skin/interior anatomy. State this explicitly in its configuration and reports. Do not soften it merely to pass a force stop or to permit a larger timestep.
- Determine baseline diameter D0 from the asset. Use 0.8 D0, D0 and 1.2 D0 for size tests; include one equal-volume ellipsoidal shape. No blade-path-specific preprocessing.
- Predeclare a minimum reliable slice thickness and maximum blade translation/rotation speed. As a starting screen, require slice thickness at least four grid cells; confirm by refinement rather than presenting it as a universal physical rule.
- Start resolution trials at grid/particle spacings of 6/3 mm for diagnostics, 3/1.5 mm for a candidate, and 1.5/0.75 mm for a short refinement check. These are proposed search points, not evidence of accuracy or a requirement to run every long scenario at every resolution. For a 60 mm sphere these particle spacings imply roughly 4200, 33500 and 268000 samples; actual sampling must be recorded. Thin slices may require further resolution and may miss the speed target.
- Cap initial evaluation at four cuts per episode. Capacity exhaustion must stop explicitly; never merge incompatible material states or erase old cuts to keep running. Expand the envelope only after measurements support it.

## Gate 0 Freeze the experiment and remove stale assumptions

Work budget: one focused hour.

1. Inventory actual source, assets, saved results, active processes and GPU memory. Record hashes, compiler, driver and dependency paths. Do not install another CUDA stack or change the working Isaac environment.
2. Create a new candidate directory under `/home/omen/Documents/Codex/experiments/`, with a unique version. Never overwrite `cressim_20261110` or existing project evidence. Use an isolated checkout only if needed; first establish the actual repository location.
3. Write `contract.json`: operating envelope, units, selected material formulation, fracture/contact model, timestep policy, thresholds, stop conditions and time budget. Separate sourced parameters from provisional parameters.
4. Specify the implementation modules and tests before coding: bulk update; persistent cut state; compatible transfer; tool and fragment contact; tomato generator; reset/checkpoint; controller bridge; benchmark runner.
5. Reuse one small failing CRESSim probe to verify that the harness can detect coupling. Check the held-tool and wide-gap controls. Account for the known exact-grid-plane sensitivity; test translated/rotated configurations rather than hiding it.

Deliver `manifest.json`, `contract.json`, `architecture.md` and `gate0.json`. The architecture must explain partial cuts, completed cuts, recontact, and why an intact bridge is preserved.

**Stop condition:** the chosen design cannot represent these behaviors without invisible fixed barriers, pre-separated bodies or a known future path. Do not proceed to kitchen visuals.

## Gate 1 Establish trustworthy intact mechanics

Work budget: up to two focused hours for the first diagnosis and one correction.

1. Choose one bulk backend for physical work. Prefer a formulation with defined elastic energy and stress. Treat PB material parameters as a distinct model unless independently calibrated; matching names or Young's modulus inputs is insufficient.
2. Investigate the observed MLS free-translation loss. Audit grid-mass thresholds, mass-to-velocity conversion, transfer weights and dimensional scaling. The existing 1e-4 kg cutoff is a hypothesis, not a proved diagnosis. Change only a diagnosed numerical issue in a separate version.
3. Test no-load rest, uniform translation, rigid rotation, uniform deformation and a small compression/unload cycle. Use independent analytic invariants or a small CPU reference, not only old-versus-new GPU agreement.
4. Check CPU/GPU constitutive agreement, frame objectivity, force/energy consistency and response to a halved timestep. Explain any deliberate damping or plasticity.
5. Save an intact reference state and the exact tests that must remain unchanged when cutting is added.

Proposed engineering screens, not experimental calibration: relative mass error <=1e-6; no-load linear momentum error <=1e-3 over the test; no-load translation error <=0.1 mm over 0.1 simulated second; finite state and positive admissible material volume. Use dimensional absolute floors in the contract. An independently justified angular-momentum screen must accompany rotation tests.

Deliver `intact_controls.json`, short traces and any reviewed patch. If a baseline needs repeated patches or arbitrary unit/mass rescaling to appear stable, stop this implementation route.

## Gate 2 Prove persistent cuts on a small block

Work budget: five focused hours for a minimal proof; total Gates 0–2 budget eight hours. This is an early decision budget, not a promise of success.

1. Implement a minimal CPU reference for the chosen transfer/history update and a GPU version. Preserve numerical consistency when adding logical states; do not create or lose material mass when a cut is introduced.
2. Store cut history with the material, not as a stationary world-space obstacle. Verify it continues to work when a fragment translates and rotates.
3. Determine the affected region from actual blade motion during the current step, including finite edge length and swept motion. No plane-wide instantaneous division or knowledge of the future trajectory.
4. Preserve intact connections ahead of a partial cut. Global connected-component IDs alone are not an adequate design: the two sides of a partial incision can still belong to one globally connected body.
5. Separate incompatible mechanical transfers while allowing explicit surface contact. No unconditional velocity averaging across old cuts, no permanent artificial repulsion across open space, and no rest-state recreation of a remaining piece.
6. Run, in order: untouched block; partial score and withdrawal; full cut and withdrawal; two parallel cuts; an intersecting cut; cut history carried by a moving fragment. Initially a prescribed discontinuity can isolate transfer mathematics, but label this as a unit fixture rather than physical cutting.
7. Repeat the impulse-independence probe after real tool-generated cuts and with the cutter removed from the scene or moved fully clear. Include no-friction/no-support isolation controls and translations relative to the grid.

Pass screens: unchanged material mass; no incorrect full split in the partial-cut fixture; completed fragments retain independence; untouched separated fragment velocity <=1% of the applied probe velocity over the declared window; same topology verdict after timestep refinement. Require a physically resolved gap for this probe so genuine contact is not misclassified as bonding. Do not use a manufactured empty gap in place of the actual post-cut test.

Deliver `persistent_cut_controls.json`, persistent-state snapshots and timing/memory versus zero, one, two and four cuts. Record active state counts and overflow behavior.

**Decision at eight focused hours:** if persistent separation or intact-bridge preservation is still failing, save one concrete diagnosis and stop this candidate campaign. Do not automatically start a second engine, implement a week of repairs, or declare progress from a visible groove. Continuing would require a revised scope based on the measured obstacle.

## Gate 3 Establish cutting resistance and reliable contact

Proceed only after Gate 2. Work budget: one focused working day, with short tests.

1. Write the candidate's cutting law, state variables, units and update rule explicitly. Distinguish elastic strain energy, dissipated fracture/cutting work, frictional dissipation and numerical damping.
2. For the physical tomato milestone, new separation must be tied to a declared irreversible contact/material-work or failure criterion. Blade-plane crossing alone is not evidence of physical failure. Any change from the existing cohesive law must be labeled a new model; no inherited DiSECt qualification.
3. Map any resistance/fracture parameter to an area or volume measure so changing particle spacing does not multiply total toughness. Do not assign the old whole-interface energy budget to every new cut or fit a threshold simply until the knife passes through.
4. Commit irreversible state once per accepted step. Rejected trials, queries, logging and reset previews must not advance damage. Test unloading, re-entry, pause, reversal and replay without double-counting damage/work.
5. Validate CAD blade contact with finite thickness, edge/tip/spine distinction, sweep checks and newly exposed faces. Compare analytical contact fixtures before using the tomato. Include a blunt-face press, a near miss and shallow contact as negative cutting controls.
6. Verify the reaction's units, sign, origin and sampling interval. Existing CRESSim `getShapeForce()` records accumulated momentum exchange in the tested path; do not treat it as newtons without appropriate normalization. Confirm force balance against an independent momentum/impulse test.
7. Test fragment recontact: approach, collision, sliding, separation again. Contact should transmit compressive/frictional load while active, without restoring cohesive bonds after unloading.
8. Check force/impulse/work and position under a halved timestep at shared physical times. Provisional refinement screens: positions <=0.1 mm and integrated impulse/work and meaningful force segments <=5%; define near-zero floors before running. Also require consistent onset/separation classification and no unsupported volume collapse. A finite state alone is not stability evidence.

Retain the 2 N stop and 0.1 mm penetration limit for qualification. A particle-center distance is not a bound on whole-material penetration. Supply a conservative geometric bound or independent resolved-surface check; otherwise mark the penetration test unproven and leave physical qualification blocked. A paper's approximate particle contact does not waive this requirement.

Deliver `physical_model.md`, `contact_fracture_controls.json`, a force/work ledger, and a short runtime forecast. If the physically plausible model requires different limits, prepare the actual evidence and ask once; do not weaken material or skip checks to manufacture a cut.

## Gate 4 Build the reusable tomato and complete one slice

Work budget: up to one focused working day after the mechanics gates.

1. Sample the saved tomato exterior with a deterministic seed and documented units. Check dimensions, sampled volume, center of mass and total mass. If changing size at constant density, mass must scale with volume; material constants must not silently change with size.
2. Choose clearly labeled provisional bulk and cutting parameters. The existing literature-inspired E=0.4 MPa and nu=0.3 may inform a candidate only after translating them into the chosen constitutive law. They are not calibrated tomato measurements and are not required if they do not describe that law.
3. Start with the declared effective-bulk approximation. Do not spend this gate adding seeds, fluids, decorative skin or a new kitchen. A separately resolved skin layer is a later model extension with additional resolution and validation cost.
4. Establish gravity and board support with an admissible starting configuration. Preserve applicable support constraints for reference tests and disclose them. A permanently anchored region must not masquerade as a freely moving slice. Record fixture reactions separately from knife reaction.
5. Run one simple prescribed cut, controlled stop and horizontal withdrawal. Stop before forbidden knife/board contact. Determine whether a whole slice can detach within those constraints; do not push through the board to release the last bridge.
6. Demonstrate no remaining tensile connection across the completed cut and independent motion of the detached piece. Measure the remaining bridge in partial-cut controls. Preserve material mass, strain state, damage and support state in the uncut remainder.
7. Render the same mechanical fragments for inspection. Do not swap in pre-cut geometry, force pieces apart for the camera or use animation as evidence.

Deliver a reproducible single-slice configuration, raw mechanical evidence, inspected still views and `tomato_slice_result.json`. This is the first useful tomato milestone. Report it promptly; experimental validation remains pending.

## Gate 5 Verify freedom to change the cutting technique

Work budget: four focused hours; reuse short regression cases rather than long parameter sweeps.

Use a small frozen matrix with one case per capability and a few held-out variations:

| Capability | Required observation |
|---|---|
| Two parallel cuts | A middle slice becomes independent; neighboring pieces remain correct |
| Cross-cut a detached slice | New pieces are generated without forgetting the earlier cuts |
| Partial score then deeper cut | Intact bridge first, separation only after completion |
| Pause, reverse and re-enter | No spontaneous healing or duplicate resistance charge |
| Change blade direction during contact | New action is consumed online; no precomputed future plane |
| Translate/rotate a fragment and cut it | Cut history follows the material and contact uses current geometry |
| Three sizes and an ellipsoid | Automatic reset-time generation and valid mass/volume scaling |
| Invalid or too-fast action | Explicit rejection/termination, without tunneling or silent clamping |

Run matched refinement checks on the hardest accepted case, not every combination. State the tested envelope, minimum slice thickness, maximum motion increments and maximum cut count. Outside that envelope, reject actions or label results unqualified. Do not claim unlimited cuts or arbitrary real-world tomato behavior.

Deliver `capability_matrix.json` and regression configurations.

## Gate 6 Measure interactive and RL performance

Work budget: four focused hours, including at most two hours of timed trials.

1. Freeze the smallest resolution/timestep that passed the physical gates. Measure the same configuration; do not benchmark a softened/coarsened replacement and present its speed as the qualified result.
2. Time bulk solve, topology/history, tool contact, fragment contact, observation packing, resets, file writing and surface generation separately. Include all required computations in total time.
3. Test batch sizes 1, 4 and 8 only while memory permits. Benchmark both early and late in a four-cut episode; active history and contact cost can grow. Record peak total GPU and host memory, not just one allocator.
4. Measure median and slow-tail step times, aggregate policy transitions per second, reset time and the cost of a lightweight policy's inference/update. Include rendering at its actual rate if camera observations are proposed.
5. Run a small action-response latency test with a visible scene only after headless measurements. Rendering FPS alone is not physics throughput. Never skip physical time or show saved playback as live interactive response.

Proposed product targets to freeze in Gate 0:

- Interactive mode: at least one simulated second per wall second with the chosen display/observation load, plus recorded input latency and display cadence.
- Small-learning entry: at least 100 aggregate transitions/second with the intended environment loop. Below this, restrict to demonstrations/offline imitation and report the time cost; do not label it efficient online RL.
- Preferred laptop RL target: at least 500 aggregate transitions/second at 50 Hz control, with safe GPU headroom for policy training and robot state. This is a project target, not a published capability.
- At 500 transitions/second, collecting one million transitions takes about 33 minutes, ten million about 5.6 hours, before any excluded optimization/evaluation overhead. At single-environment real time and 50 Hz, those collection costs are about 5.6 hours and 55.6 hours. None predicts how many samples learning will need.

If the target fails, profile once and make at most one equivalent implementation optimization. Rerun affected physical regressions. Do not quietly enlarge timesteps, suppress history/contact, relax stops or pursue unlimited acceleration branches. Return an explicit result: interactive-only, small-learning-capable, or preferred-throughput pass.

## Gate 7 Connect the existing robot and verify resets

Work budget: one focused working day after the tomato passes.

1. Reuse the interface contract and analytic wrench fixtures from the existing Section 5 plan. Assign each contact to one owner. Do not apply both external and native knife–tomato forces.
2. Drive the candidate from actual mounted-blade pose on a declared clock; map the equal-and-opposite reaction once, with the correct torque origin. Keep commanded motion separate from measured tracking and measured native effort.
3. Use the existing natural pickup and approach, then nonfracturing contact, then the qualified cut. Preserve the fixed mount, arm posture, kitchen and approved retreat. Do not teleport the hand or regenerate a fresh tomato during the cut.
4. Compare a replay driven by recorded actual poses with the coupled run. Halve the coupling interval and compare geometry, reaction and cut verdicts. Load-responsive robot behavior must be distinguished from a purely prescribed tool.
5. Test reset from fresh, loaded, failed and post-cut states. Include cut history, active grid states, contact caches, damage/work, material state, RNG, robot/controller state and queued reactions. Check for memory growth across repeated resets.
6. Test one checkpoint/restart during contact against an uninterrupted continuation. Match discrete history exactly and compare continuous quantities within the frozen numerical tolerances.

Deliver a separate launcher, integration/reset reports and an updated capability status. Leave unresolved native motor-work interpretation unresolved; it must not be relabeled as closed by an external contact-force display.

## Gate 8 Prepare a small learning demonstration

Work budget: four focused hours for the interface and smoke test; no large training run in this plan.

Implement `reset(seed, tomato_spec)`, `step(action)`, observation/action specifications, reward terms, termination reasons, episode metrics and a deterministic scripted baseline. Use bounded blade increments or residual commands around the safe baseline first. The simulator must still consume actions online; do not hide a preplanned cut surface inside the environment.

Reward detached volume/thickness and verified mechanical separation, with penalties for excess force, board collisions, wasted material and numerical termination. Avoid rewards based only on a visible gap or internal damage value. Identify privileged simulation observations that a real robot could not measure.

Collect a small set of successful demonstrations and negative examples. Test behavior cloning or a small residual policy only after resets and throughput pass. Keep a held-out size/path set. Compare against the same scripted baseline and report failed episodes. A short smoke test demonstrates pipeline operation, not solved RL or sim-to-real transfer.

Deliver `env_contract.json`, the adapter, demonstration index, sample-budget forecast and a next-training proposal. Large training, separate skin/juice modeling and experimental calibration remain later decisions.

## Execution discipline and schedule

Use Astra High for hands-on implementation and verification. Do not delegate or launch parallel agents unless the user explicitly requests it. One GPU physics process at a time on this laptop; CPU preparation can continue independently. Do not terminate an unrelated user application without authorization.

Every gate must have a frozen input/acceptance file, finite runtime cap, result file and evidence paths. Begin expensive tests with a 0.02–0.1 simulated-second forecast segment. Initial individual pilots have a 10-minute wall cap; use recoverable checkpoints. A timeout records a performance failure, not permission for an automatic overnight retry. Allow one diagnosed correction and bounded retest per failure, then reassess.

The first eight focused hours are reserved for an architecture/intact-mechanics/persistence decision. Later gate budgets total roughly another four working days if earlier gates pass. These are spending limits and planning allowances, **not a guaranteed delivery date**. An independent numerical method can take longer; reaching a cap without the required result means report the obstacle instead of extending the schedule silently. No credible completion date for real-tomato calibration exists without independent data.

Do not wait for all gates to communicate a useful result: report a passed gate, a failed gate, a material change in estimated cost, or a decision needed. Continue through passing gates without asking permission between small steps. Keep routine progress concise.

Suggested candidate directory layout:

```text
manifest.json
contract.json
architecture.md
status.json
src/
tests/
configs/
runs/<unique-run-id>/
reports/
```

`status.json` must distinguish pending, running, passed, failed and deferred; include actual timestamp, current hypothesis, next action, process/checkpoint identity and evidence. Never infer liveness from a stale running flag. Keep all raw failed evidence. Checklist updates must reflect these results, and the new experimental track must not turn old DiSECt milestones green.

## Stop or adoption decision

Stop this candidate if it cannot retain independent fragments, loses intact bridges, needs fake separation, cannot supply admissible contact behavior, or cannot meet the selected throughput envelope without changing physics. Present the smallest demonstrated blocker and one justified alternative scope; do not automatically start another engine or contact anyone.

Adoption requires the tomato's own topology, physical, reset, integration and speed evidence. Any accepted approximation must be visible in the model description. Experimental validation remains pending until independent measurements support it. The useful outcome is a reproducible model with a known operating envelope, not a promise that it is exactly like every real tomato.

## First instruction for the executing agent

Read this plan and the linked local reports. Start Gate 0 in a new experiment directory. Do not restart long DiSECt work, modify the existing kitchen/demo, or begin RL. Follow passing gates continuously within the declared scope and budgets. At the first failed decision gate, preserve the evidence and report the concrete blocker and next scope decision.
