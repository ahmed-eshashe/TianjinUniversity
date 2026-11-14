# Section 4 execution handoff for Sol — 9 November 2026

## Objective and authority

Develop and verify the first genuine slice, then assess reliability and successive slices. Execute sequentially through the gates below without asking for routine implementation approvals. Preserve failed trials and report a concrete blocker if a gate fails; do not substitute a visual split or relax limits. The user explicitly deferred speed qualification to finish physical qualification first. Speed is still failed, and neither training readiness nor experimental validation is established.

Read the latest dated entries of `RESEARCH_ROADMAP_REVIEW_20261102.md` and `work/disect_physical_20261109_v22/RESULT.txt` first. Older statements that section 4 is blocked on speed are historical, superseded only by this explicit deferral. Section 3 numerical/precontact passes are not fracture passes.

## Frozen starting point

Project root: `/home/omen/teamwork_projects/tomato_cutting_right_arm`.

- Evidence: `work/disect_physical_20261109_v22/qualification_review.json`, `settling_qualification.json`, `contact_comparison_result.json`, source manifest and saved final states.
- Approved mesh: v18; 9,394 vertices, 42,523 tetrahedra, original exterior, mass, cut plane and 25 support coordinates. Preserve 47 original cohesive groups, constitutive parameters and total fracture-energy budget 0.11696391110288158 J; verify these against actual source metadata before implementing.
- Operator: v20 GPU material/cohesion/closure plus v22 assembly and original-CAD contact. `cohesion_gpu.py` is explicitly damage-disabled: enabling cutting requires new implementation and validation.
- Settling passed at 12.5/6.25 microseconds; blade contact at 3.125/1.5625 microseconds. Those are starting references, not proof that a damage-enabled step is adequate.
- Fixed knife attachment, robot, kitchen, grip, elbow posture, motion interface and production checkpoint remain unchanged. Initial section 4 tests use prescribed blade motion; native robot coupling belongs to section 5.
- Use a new versioned work directory. Do not overwrite v18–v22 evidence. Record source hashes, environment, parameters and commands. Keep one GPU simulation running at a time.

## Gate A — progressive failure implementation and independent controls

1. Trace the original CPU fracture law and its history/commit API, group interpolation, contact eligibility and energy accounting. Document the actual rule, units, onset/failure thresholds and ownership of each history variable. Do not invent a different damage law or inherit DiSECt defaults silently.
2. Implement equivalent forward GPU evaluation and irreversible history. Trial evaluations must be pure: commit history once per accepted physical step, never during nonlinear iterations, rejected steps, force probes or logging. Checkpoint/reset must include every damage, maximum-opening, eligibility and contact-history variable.
3. Test original CPU versus GPU on opening, shear, mixed loading, unload/reload, rotated frames, onset/failure boundaries and complete failure. Include zero-opening controls, multiple samples within one group, rejected-step rollback, restart and fresh reset. Use independent analytic/energy checks where defined; an implementation compared to itself is insufficient.
4. Audit full-surface sampling weights so group force distribution does not multiply fracture energy. Retain the 47 group budgets and account explicitly for elastic stored energy and dissipated fracture energy. Damage must not heal. Failed cohesion must cease transmitting tensile/shear bonds while valid compressive cut-face contact remains possible.
5. Verify blade contact can reach the appropriate newly exposed surfaces. Exterior-only node collocation passed the tiny nonfracturing probe but does not establish deep cutting contact. Prevent duplicate forces, force transmission through the blade and artificial attachment across the cut. Distinguish supported cut-face contact from fracture preparation. If a materially different contact law or physical sampling is necessary, present the concrete change and evidence before adoption.

Deliver `fracture_contract`, independent control results, source manifest, and reset/rollback evidence. Reuse existing precision limits and reference conventions. Record numerical floors explicitly; do not use the 5% trajectory allowance to excuse incorrect constitutive algebra. Proceed only after all required controls pass.

## Gate B — bounded shallow scripted cut and stop

1. Start from the verified settled assembly. Recompute blade clearance and map the requested bodyward horizontal direction between model/world/robot frames. Keep original CAD orientation and fixed mount semantics.
2. Freeze a short trajectory and acceptance file before launching: approach, shallow contact-driven loading, controlled stop, horizontal withdrawal at fixed height toward the robot and a brief observation. Derive stroke/depth from geometry and the existing fracture law; do not arbitrarily prescribe damage or schedule deletion. A successful test must show nonzero irreversible damage caused by blade loading, not simply replay the nonfracturing probe.
3. Log time, actual blade pose, forces/moments and their origin, material deformation, damage/history, fracture dissipation, contact eligibility, support reactions, element volumes, residuals and mass. Separate contact-law reaction from native motor effort. Preserve start/end states and failure checkpoint.
4. Carry forward physical stops: finite states; minimum volume ratio >0.1; board penetration <=0.1 mm; fixed-support error <=1e-7 m; board-edge margin >=1 mm; discrete force balance <=1e-6 N; solver residual <=1e-9 under the existing normalization. Retain the existing 2 N blade-force stop and 0.1 mm CAD-penetration stop initially. A stop is a failure/review point, not permission to raise the threshold.
5. Repeat independently from the same initial state at half timestep. Compare on common physical times: position <=0.1 mm, velocity <=5 mm/s, force and moment <=5% with existing floors (1e-6 N and 1e-8 Nm). Also compare damage evolution, dissipated energy, failure events and connectivity; define these additional tolerances before the runs, explain any onset-time alignment, and never hide disagreement by resampling away an event.
6. Require controlled termination, no healing, no inadmissible state, and a consistent damage result. Log actual wall time and peak memory. Speed is informational/deferred; do not create another open-ended optimization branch.

Deliver trajectory, refinement report, genuine-damage evidence and a clear pass/fail. If no damage occurs, investigate once from saved geometry/loading evidence and design a justified next bounded trajectory. Do not weaken material to create a cut.

## Gate C — full stroke, horizontal withdrawal and separation proof

Only after Gate B passes, extend the same verified approach in checkpointed segments. Forecast runtime from measured segment cost and use a finite declared simulated duration and wall cap; preserve recoverable state if the cap is reached. A cap is not a physical pass or a reason to discard evidence.

- Continue through the intended cut interface without penetrating the board or fixtures; use geometry-derived clearance and the original stops.
- Withdraw by sliding horizontally toward the robot, not lifting upward through tomato material. Verify actual blade clearance.
- Evaluate connectivity using the actual load-bearing bulk/cohesive structure, not rendering mesh gaps. All ties connecting the two intended pieces must fail under the original law. Compressive contact does not itself imply bonded connectivity.
- Predeclare intended piece membership/mass from the cut geometry. Require two intended substantial pieces, conserved total mass within numerical accounting tolerance, and no surviving tissue bridge. Report small fragments separately; do not count a detached vertex as a slice.
- Validate the evaluator with negative controls: intact target, partial damage/one remaining bridge, visually displaced but bonded geometry, and isolated tiny fragments must not pass. A fully disconnected known fixture must pass.

Deliver full state, surviving-bond report, component masses, damage/energy history, clearance and evaluator controls. Do not claim complete separation until these checks pass.

## Gate D — post-cut stability and restart reliability

Observe at least one simulated second after clearance with cut-face and board contact active. Verify finite stable states, no healing or excessive penetration, mass conservation, supported piece shape and force decay. Document the artificial fixed supports and which piece each supports; do not describe this as free slices or left-hand stabilization.

Repeat from a fresh/reset state; verify a mid-cut checkpoint restart against uninterrupted execution. Include failed-episode reset. Repeat/refine at least one damage-enabled case and compare geometry, force, energy and separation verdict. Record repeatability separately from timestep convergence. No training data accepted before these pass.

## Gate E — one size change and one path change

Use separate versioned cases. Audit mass/density, material coefficients, cut position, supports and fracture-energy scaling. Preserve the law rather than forcing the same total energy onto a different physical cut area. A new physical scaling interpretation requires explicit documentation and review.

Distinguish a newly prepared interface for a new path from a path deviating after preparation. The present precomputed interface does not establish arbitrary-path cutting. Run one supported changed-size and one supported changed-path case with the same success evaluator; keep baseline and variants separate. Report unsupported path freedom plainly.

## Gate F — successive slices

One successful interface is not multiple slicing. Inspect whether the current model can prepare additional interfaces in the remaining body while preserving already accumulated damage, mass, stresses, supports and contact history. Plan and validate that transfer before execution. Do not rebuild the remainder as an undamaged tomato or spawn pre-separated pieces. If this needs new connectivity/sampling beyond approved scope, prepare the concrete proposal and ask once. Demonstrate at least two successive genuine separations only after this capability passes independent controls; otherwise leave this checklist item open with the precise limitation.

## Execution discipline and handoff

- Complete gated work continuously; no approval between routine steps. Ask only for a physical-model/scope decision not covered by existing authorization. Do not launch a simulation merely to fill time while blocked.
- Limit each failed gate to a diagnosed correction and bounded retest before reassessing. Repeated identical failure requires a written cause and next decision, not many diagnostic branches.
- No robot scene edits, engine adoption, learning, video work or renewed motor-work investigation in section 4.
- Save per-run plan/results/manifest, checkpoints and concise status with completed simulated time, total planned time, timestamp, actual process state and last error. Write results atomically. A stale process/status must not appear as running.
- Update `/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs/disect-execution-checklist.json` and rebuild with `build_disect_checklist_page.py`. Mark each of section 4's six items complete only for its own verified result. Preserve section 2 speed as deferred and experimental validation as pending. Keep downloadable checklist text synchronized.
- Final report: passed/failed gates, exact new capability, runtime/memory, limits, evidence paths and next action. Never call a visible groove complete separation or a scripted policy learned.

First action for Sol: inspect the frozen source and implement Gate A in a new directory. The current request is this plan; no section 4 fracture run was launched while preparing it.


## Execution revision — 10 November 2026

The user chose to finish the bounded pilot and revise execution strategy after measured contact cost projected several days. The 80 ms pilot is finished without damage; do not automatically resume the former multi-day sequence. Gates A–F and all physical limits above remain unchanged. Speed is still deferred, and experimental validation pending.

A final-state audit found that the current adapter excludes cut-to-cut physical edges. v34 corrects that coverage while retaining the total 960-unit sampling budget; independent static controls pass. It is a separate physical-coverage candidate and must start fresh, not resume the overlapping v33 loaded state.

A bounded profile attributes about 91% of saved-step time to CAD queries. v35 supplies a faster implementation of the same geometry formulas, with strict static controls and a local saved-solve equivalence check (7.45x faster). This is not a full-trajectory speed or cutting pass. Three short fresh controls isolate coverage, implementation and half-timestep effects before adopting their combination.

Follow the detailed revised ordering, caps, equivalence criteria, rollback and reporting rules in `/home/omen/teamwork_projects/tomato_cutting_right_arm/work/disect_execution_strategy_20261110_v35/EXECUTION_STRATEGY.txt`. Read `/home/omen/teamwork_projects/tomato_cutting_right_arm/work/disect_execution_strategy_20261110_v35/fresh_control_review.json` for actual fresh-control status. Do not turn a component pass into Gate B or remove the full-volume guard. No engine, force-limit, material/fracture, robot or training changes are authorized by this revision.


### Validated revision outcome and prepared next run

All three fresh 2 ms coverage/query/half-step controls completed and passed at 641 shared times. Same-model implementation position/force differences are near roundoff; maximum half-step nodal-force discrepancy is 0.5693%, below the unchanged 5% limit. The same-step probe took 199.74 s with the reference query and 55.14 s with the faster query (stepping/sampling), a measured 3.62x improvement. This is a nonfracturing component result, not Gate B, full-cut speed, separation or engine adoption.

A new runner is prepared but unlaunched at `/home/omen/teamwork_projects/tomato_cutting_right_arm/work/disect_cutting_candidate_20261110_v36/loading.py`. Read `/home/omen/teamwork_projects/tomato_cutting_right_arm/work/disect_cutting_candidate_20261110_v36/execution_contract.json`. Its default first horizon is45 ms, cap900 s, fresh initial state, h3.125 us/ref1.5625 us, original 2 N/0.1 mm and all other stops; no old loaded-state reuse. It uses the separately corrected cut-edge coverage and validated faster query. Continue only under the revised bounded ordering and recent loaded-cost forecast. Do not start full stroke/training from these component passes.


### Section 4 execution outcome — 10 November 2026: 50 ms accepted, arithmetic repair, runtime reassessment

The user authorized proceeding under the latest plan. The fresh v36 45 ms prefix passed all accepted guards in 551.13 s, with zero damage. Its next continuation stopped at 47.625 ms on uncertain winding arithmetic, and the legacy final sampler failed to write a complete result. Raw evidence remains unchanged. One v37 replay captured the actual point: 0.949 picometres inside the CAD surface; both original and faster float64 queries fail, while 60/100-digit winding sums agree on inside.

Separate v38 repeats the same winding formula at 40/80 digits only for uncertain queries, requiring strict agreement. No geometry, force, material/fracture law, timestep or physical tolerance changed. The actual captured case, 60 independent analytical box controls, shared pre-failure prefix equivalence and the bounded 45-to-50 ms retest passed. The latter took 164.36 s, with maximum opening 0.013046 mm against 1 mm onset, zero damage/dissipation and all accepted guards. Whole-volume guarding stayed at 0.1 mm; sampled penetration is not a whole-volume maximum.

Measured contact-loaded cost is 32,784 wall s/s. A constant-loaded-cost scenario for remaining motion, one-second stability and a half-step reference is about 55.5 h, before repeats/variants. Actual clear/deeper-contact costs may differ. Per the latest revision, no full multi-day campaign is launched automatically. One bounded read-only profile of the corrected 50 ms checkpoint, with no history commits, finds contact assembly ~70% of saved-step time; the old 91%-CAD-query figure no longer describes this version. Recommended next decision: one finite implementation-only contact batching candidate with independent static/equivalence/fresh-refinement controls; no model or timestep change and no open-ended optimization tree. The proposal is not an adopted implementation.

No worker running. All six complete cutting milestones remain open. Gate B, separation, native robot coupling and training remain unqualified; speed deferred, experimental validation pending. Evidence: `/home/omen/teamwork_projects/tomato_cutting_right_arm/work/disect_precision_sign_20261110_v38/RESULT.txt`, `section4_execution_review.json`, `controls_result.json`, `precise0050_review.json`, `loaded_profile_result.json`, `runtime_reassessment.json`. The failed attempt and replay are preserved in v36/v37.


### Continued Section 4 authorization — 10 November 2026

After the 50 ms result and runtime reassessment, the user explicitly requested continuous work until all of Section4 is finished. A single implementation-only contact batching candidate (v39) preserves the same 5,871 physical edges, 960 sampling budget, CAD, positive Gauss rules, adaptive tolerances and force law. Independent analytical/saved-CAD controls pass; full saved forces and energy agree exactly. Fresh 2 ms coarse/half-step probes and strict comparison to the prior fresh reference pass, with maximum half-step nodal-force difference 0.5693%. Same-state 50-to-50.5 ms loaded parity passes strict limits (force/moment identical; motion/history at roundoff), with measured 1.62x stepping/sampling improvement in that short segment. No full-trajectory speed claim.

The new v40 campaign continues the same physical operator/path from 50.5 ms toward first damage or the 180 ms loading horizon, in 5 ms checkpoint windows. Each window has a finite cap; any physical/numerical failure or wall-cap hit stops the campaign without an automatic retry. Total loading-phase cap4 h; no new timestep, physical model, fixture, material threshold or engine. The renewed user instruction accepts continued work after the runtime warning; all scientific gates remain. First damage still requires independent actual-damage half-step, controlled stopping and authorized horizontal withdrawal before GateB. No full stroke, training or milestone completion is inferred from nonfracturing windows.

Evidence: work/disect_batched_contact_20261110_v39/{controls_result.json,fresh_control_review.json}, work/disect_batched_cutting_20261110_v40/{paired_loaded_review.json,execution_contract.json,continuation_contract.json,campaign_status.json}. All prior evidence retained.


### Section4 loading stopped before fracture — 10November2026

The bounded v40 campaign accepted155.971875ms (49,911steps from the fresh state), then rejected the155.975ms trial BEFORE fracture commit because one tetrahedron would reach volume ratio0.0999979671, below the unchanged0.1 limit. Last accepted ratio0.1000025095; maximum damage0, maximum committed opening0.0633157mm against1mm onset. Blade load1.1128N stayed below2N; whole-volume proof, solver residual and force balance passed. All six complete cutting milestones remain open. No worker running. Evidence: work/disect_batched_cutting_20261110_v40/{final_campaign_review.json,load160500_rejected_volume_guard.json,final_loading_geometry_review.json,RESULT.txt}.

The v39 batching change passed static, fresh/half-step and loaded-prefix controls; no physical laws changed. A1.2degree alignment proposal (v41) was screened on explicitly inadmissible frozen penetration fixtures, showed no convincing remedy to contact direction, and was discarded WITHOUT adoption or a dynamic run. Do not launch an angle sweep or imply those fixtures passed physical stops.

A read-only material-parameter audit found an interpretation error in this execution's earlier30kPa/nu0.25 description. The actual stabilized stress law with kernel coefficients mu=lambda=12,000Pa has effective small-strain mu_linear=9,000Pa and lambda_linear=4,500Pa, hence E=21,000Pa and nu=1/6. Analytic and independent numerical stress tangents agree; no original forces or passes change. This is not a newly discovered numerical force bug.

A single material candidate is PREPARED, NOT ADOPTED in work/disect_bulk_material_proposal_20261110_v42/{parameter_audit.json,scope_proposal.json,PROPOSAL.txt}: target E0.4MPa, nu0.3 from Jamdagni/Jia2024 TableII tomato chopping, converted to the existing stabilized kernel as mu=205128.205128Pa, lambda=358974.358974Pa. Published values are a prior for a separate sensitivity candidate, not identified parameters or independent validation for our specimen/model. Keep original47 fracture laws,1/4mm onset/failure,0.11696391110288158J budget, CAD/grip, mesh/mass/supports and every existing stop. It must requalify constitutive response, step stability, fresh settling/contact and actual damage/refinement/withdrawal. No force-limit increase or repeated material tuning is implied.

The current plan freezes material parameters and requires review of this physical-model change. A genuine user scope decision is required before the candidate is implemented; experimental validation remains pending and speed deferred. The available evidence does not prove that stiffness alone causes the failure or guarantee a cut. Do not repeat the failing plunge, bypass the volume stop, or weaken fracture to manufacture success.


### User-approved material candidate — 10 November 2026

The user explicitly approved the single literature-inspired E0.4MPa/nu0.3 candidate described in v42. Separate v43 changes only bulk kernel mu/lambda, in float64, and starts from rest. Original evidence and every other law/stop remain unchanged. Constitutive energy-gradient/objectivity/actual CUDA-vs-independent-CPU force controls pass; isolated blade packet differs only in these two arrays and reset retains them. A rest bulk mass-normalized stiffness row bound is1.0384512498135492e12s^-2 (undamped rest bulk limit1.9626232483us). The declared conservative hold step is1/1020ms=0.9803921569us, referencehalf. This rest bound is not a nonlinear contact/cutting stability guarantee. Fresh supported1s settling+half-step must pass before planning the new contact trajectory; no original loaded state reused. Per-run caps coarse4h/fine8h, stop at any failed guard or cap; speed deferred, experimental validation pending. See work/disect_material_validation_20261110_v43/{approval.json,validation_contract.json,constitutive_controls.json,packet_isolation.json}. No damage/cutting gate newly passed.
