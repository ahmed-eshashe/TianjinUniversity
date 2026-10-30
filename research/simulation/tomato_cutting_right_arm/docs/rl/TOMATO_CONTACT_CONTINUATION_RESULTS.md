# Offline tomato contact continuation results

26 October 2026. Local numerical diagnostics only.

**Both static contact and a fresh evolving-damage trajectory now pass 8.125 mm insertion, including the bevel transition that previously blocked qualification. The tomato remains materially connected: a complete cut and independent slice release are still unvalidated.**

All **111 tests in the offline tomato and contact suite pass**. The physical material, damage law, volume protection, robot controllers, frozen grasp criteria and existing memory safeguards are unchanged. No simulator, training or dependency installation was used.

## What changed and why

The earlier optimizer formed its quadratic step using the full free-space Hessian. That matrix can include directions blocked by active contact; a convex quadratic solver can reject it even when the constrained equilibrium is locally stable. It hit its CPU cap at 5.25 mm, and a larger direct guess produced a nonconvex quadratic subproblem. The new offline solver computes a Newton optimization step (a numerical method, separate from the Newton physics engine) after eliminating the active contact equalities and fixed supports. It uses sparse iterative linear solves and energy-descent backtracking; it adds no physical stiffness, contact penalty spring, damping or fracture dissipation.

An active constraint is a surface that is currently preventing motion. These constraints can push, but cannot pull. The solver releases attractive constraints and activates a new constraint when a feasible optimization step reaches it. An early batched approach was discarded because it could turn future inequalities into incompatible simultaneous ties.

Bounded chunks now retain both positions and the optimizer contact set. Saving positions alone caused a later chunk to repeat contact bookkeeping. These chunks are explicitly uncommitted numerical guesses: they never advance damage history, accumulate cutting work or count as physical cutting states. A regression compares resumed and uninterrupted solves.

The stability calculation at 7.75 mm initially exhausted its 1,600-iteration allowance. A separate worker uses an 80-vector search subspace instead of 40, while retaining the same iteration allowance, numerical tolerance, stability threshold and worker resource caps. It passes. Early resource stops and all rejected candidates remain in the evidence directory.

A positions-only predictor was also tested using two accepted states. At 4.25 mm it reproduced the unpredicted endpoint with zero difference in damage and stored energy, a maximum coordinate difference of 6.94e-18 m and a blade-force difference of 1.33e-15 N. It used five mechanical optimization chunks instead of twelve in that comparison. It supplies only an initial optimizer guess; physical history, blade work, damage and swept-path checks still begin at the actual previous checkpoint.

## Independently audited static endpoints

Insertion is measured from the crest of the predefined cut face. These are separate static equilibria with the actual 47-patch damage map imported from the earlier 5 mm checkpoint and held fixed. They do not form a validated evolving-damage trajectory. J is the ratio of a local cell volume to its undeformed volume; J=1 means unchanged volume. Staying above the numerical floor prevents inversion but does not establish realistic tomato compressibility. The model has 4,032 nodes, 257 matched cut-face vertex pairs and 448 triangles on each cut face.

| Insertion mm | Equilibrium residual | Minimum local volume ratio J | Minimum normalized stability eigenvalue |
|---:|---:|---:|---:|
| 5.25 | 2.375e-10 | 0.433556 | 0.001814 |
| 5.5 | 2.561e-08 | 0.418720 | 0.001811 |
| 5.75 | 9.511e-09 | 0.406736 | 0.001812 |
| 6 | 4.198e-08 | 0.392391 | 0.001809 |
| 6.25 | 6.408e-08 | 0.383016 | 0.001812 |
| 6.5 | 4.989e-09 | 0.375721 | 0.001813 |
| 6.75 | 1.095e-08 | 0.370195 | 0.001812 |
| 7 | 1.249e-08 | 0.368169 | 0.001809 |
| 7.25 | 6.590e-12 | 0.365836 | 0.001809 |
| 7.5 | 4.787e-12 | 0.363533 | 0.001806 |
| 7.75 | 1.064e-11 | 0.361771 | 0.001802 |
| 8 | 1.766e-08 | 0.360042 | 0.001801 |
| 8.125 | 2.993e-08 | 0.359198 | 0.001798 |

At 8.125 mm the independent Cartesian polygon audit finds a minimum blade gap of -5.096e-17 m, within the unchanged 1e-9 m penetration allowance. Actual paired cut-face gap is zero or positive; support and guide errors are zero. There are 6 loaded bevel-transition constraints and 2 loaded entry-edge constraints. The equilibrium residual is below the unchanged 1e-6 limit; J exceeds 0.1 and the stability eigenvalue exceeds 1e-6.

The surrogate blade resistance at this frozen-damage endpoint is 13.4408 N. This is an uncalibrated model output, not a measured physical knife force or evidence that the robot hand can support cutting loads.

## Contact coverage and reversible work references

The full-surface quadratic support reference detects the original 57.965994 micrometre between-vertex penetration and resolves it to -3.469e-18 m. Its quadratic supports deliberately replace the tomato bulk mechanics; this reference is separate from the protected-model endpoints above.

| Base steps per direction | Accepted reference states | Maximum work error relative to peak energy | Minimum swept clearance m |
|---:|---:|---:|---:|
| 180 | 515 | 0.833337% | -6.531e-10 |
| 360 | 873 | 0.416670% | -6.531e-10 |

Both references return to zero stored energy and satisfy the original 1% energy and 1e-9 m contact checks. Halving the base step approximately halves the maximum work error. Blade work includes the motion of the barycentric contact coordinates. A segment that crosses the blade is rejected before acceptance and refined; no accepted trajectory is repaired afterward. These are reversible support references, not fracture-energy or full-tomato release results.

## Fresh evolving damage path

The new evolving runner starts at zero insertion with an undamaged tomato and a zero work ledger. It does not import the static probes or old nodal-contact history. At each endpoint it couples finite-triangle equilibrium to the existing blade-load and edge-history eligibility gate, recomputes trial damage from the last committed history, and checks irreversible damage, work, geometry, volume and the loading-side softening tangent. The companion auditor independently reconstructs the saved endpoint and previous step.

Damage ranges from 0 for an intact patch to 1 for complete failure. Energy supplied by the blade must match stored deformation energy plus irreversible fracture loss. A normal process exit or a converged force balance alone cannot pass the endpoint. Rejected endpoints and provisional damage iterations never become continuation history.

**Fresh undamaged path**. Run `evolving_preflight`: stop reason `requested_preflight_depth_reached`. Accepted endpoints: 20; rejected endpoints: 6; uncommitted optimizer chunks: 21.

Last independently accepted insertion: **4 mm**. Damaged patches: **2/47**; completely failed patches: **0/47**; maximum damage: 0.187864. Total-energy work residual: 0.023155%. Material components: 1; material disconnection: False.

**Refined damage interval**. Run `evolving_refined`: stop reason `requested_preflight_depth_reached`. Accepted endpoints: 5; rejected endpoints: 0; uncommitted optimizer chunks: 8.

Last independently accepted insertion: **4 mm**. Damaged patches: **2/47**; completely failed patches: **0/47**; maximum damage: 0.187864. Total-energy work residual: 0.074739%. Material components: 1; material disconnection: False.

**First complete cut attempt**. Run `evolving_full_cut_attempt`: stop reason `unaccepted_endpoint_optimization_chunk_budget`. Accepted endpoints: 0; rejected endpoints: 0; uncommitted optimizer chunks: 12.

Last independently accepted insertion: **4 mm**. Damaged patches: **2/47**; completely failed patches: **0/47**; maximum damage: 0.187864. Total-energy work residual: 0.074739%. Material components: 1; material disconnection: False.

**Smaller step continuation**. Run `evolving_full_cut_half_step`: stop reason `unaccepted_endpoint_or_optimization_budget`. Accepted endpoints: 3; rejected endpoints: 0; uncommitted optimizer chunks: 35.

Last independently accepted insertion: **4.375 mm**. Damaged patches: **5/47**; completely failed patches: **0/47**; maximum damage: 0.301877. Total-energy work residual: 0.030784%. Material components: 1; material disconnection: False.

**Same endpoint predictor comparison**. Run `evolving_predictor_reference`: stop reason `requested_preflight_depth_reached`. Accepted endpoints: 1; rejected endpoints: 0; uncommitted optimizer chunks: 4.

Last independently accepted insertion: **4.25 mm**. Damaged patches: **4/47**; completely failed patches: **0/47**; maximum damage: 0.266458. Total-energy work residual: 0.037940%. Material components: 1; material disconnection: False.

**Complete cut attempt with predictor**. Run `evolving_full_cut_predicted`: stop reason `bounded_worker_budget`. Accepted endpoints: 15; rejected endpoints: 0; uncommitted optimizer chunks: 49.

Last independently accepted insertion: **6.25 mm**. Damaged patches: **5/47**; completely failed patches: **0/47**; maximum damage: 0.690423. Total-energy work residual: 0.021144%. Material components: 1; material disconnection: False.

**Focused bevel transition extension**. Run `evolving_cap_extension`: stop reason `requested_preflight_depth_reached`. Accepted endpoints: 15; rejected endpoints: 0; uncommitted optimizer chunks: 31.

Last independently accepted insertion: **8.125 mm**. Damaged patches: **5/47**; completely failed patches: **0/47**; maximum damage: 0.946031. Total-energy work residual: 0.067084%. Material components: 1; material disconnection: False.

The 3.40625 to 4 mm fracture interval was repeated from the same undamaged checkpoint with 0.25 and 0.125 mm base steps. The fracture-specific energy error decreases from 0.583148% to 0.060903%, both below 1%. Final patch damage and blade resistance match exactly between those two saved endpoints. The refined path first records nonzero damage at 3.53125 mm; this is a sampling bracket for the corrected backend, not a calibrated physical cutting onset.

At the final 8.125 mm evolving checkpoint, six bevel-transition constraints and two entry-edge constraints carry load. Independent audit checks 490 clipped polygon vertices; blade and swept-path clearances differ from zero only by floating-point roundoff. Blade resistance is 3.3637 N, an uncalibrated model result. The 10 mm nominal end-cap thickness is a different dimension from downward insertion: the complete-cut attempts targeted 48 mm insertion. The verified 8.125 mm endpoint is still a partial cut.

Interrupted unloading/reclosure on this backend, work accounting over the later fracture path, complete failure of all 47 patches, blade removal and independent release remain separate gates. The passing shallow comparison does not qualify the full cut.

## Resource protection and preserved files

Workers remain serial under the existing shared controller lock, with one BLAS thread, 512 MiB address-space limit, 45 s CPU limit and 55 s wall alarm. Maximum recorded RSS among completed workers in this evidence directory is 200.07 MiB. An accepted endpoint can require several bounded optimization chunks; those costs are additional and are not simulated time.

Byte comparisons confirm all 250 pre-existing project files in the baseline registry remain unchanged. This includes the physical model, robot controller, original RAM/VRAM watchdog and frozen grasp criteria. Simulator startup still requires at least 10,000,000,000 available RAM bytes and 4 GiB free VRAM. The lightweight offline workers use their existing separate resource caps; no simulator memory gate was bypassed.

The 111-test suite includes eight new optimizer regressions: weighted constraints, unilateral release, dependent constraints and fixed supports, contact-constrained negative free curvature, newly blocking constraints, correct resume bookkeeping, the cap-crossing triangle wrapper, and incompatible future ties. It retains the prior 103 tests. Forbidden simulator/training imports are checked. A final saved-data qualification also verifies all 13 static endpoints and 59 evolving endpoints, including repeated branches: every source/state hash matches, all saved arrays and numerical metrics are finite, all independent audits pass and all recorded worker caps match the unchanged limits.

## Scope and next gate

This remains a guided, frictionless, fixed-normal quasistatic model with a predefined end-cap cutting plane, explicit remainder fixture and fixed cut-face y/z guides. It does not validate unrestricted 3D blade collision, free-body slice dynamics, arbitrary cut placement, camera perception, robot grasping, native Newton/Isaac integration or calibrated tomato material parameters.

The last accepted evolving checkpoint is `runs/offline/tomato_contact_continuation_01/evolving_cap_extension/attempt045_01` at 8.125 mm. Continue from it only if its source/state hashes still match. Resolve any failed contact, energy, convergence or stability gate before increasing depth. Before a complete-cut claim, require blade-driven failure of every patch, two disconnected material components, withdrawal, independent relative motion and nonpenetrating reclosure without healing. Keep the original robot grasp and memory requirements unchanged.

## Evidence and entry points

Evidence: `runs/offline/tomato_contact_continuation_01`. Final static endpoints are `final_static5.25`, `final_static5.5`, `final_static5.75`, the accepted `feasible_static6*` through `feasible_static7.5*`, and accepted `spectral_static7.75*` through `spectral_static8.125*`. Each has a separate audit JSON. Preliminary source versions and failed probes remain distinct from these final results. An earlier parent reporting exception involving relative paths was corrected; its status was reconstructed from the saved optimizer candidates, with no deeper endpoint accepted by that failed attempt.

Machine-readable report: `docs/rl/tomato_contact_continuation_results.json`. Preservation registry: `runs/offline/tomato_contact_continuation_01/preservation.json`. New source snapshots are in that directory under `source/rl`.

Guarded workers: `rl/offline_tomato_contact_continuation.py` for shallow static checks; `rl/offline_tomato_contact_spectral.py` for the larger stability subspace; `rl/offline_tomato_continuation_geometry.py` and `rl/offline_tomato_continuation_energy.py` for the support references; `rl/offline_tomato_triangle_evolution.py` and `rl/audit_tomato_triangle_evolution.py` for fresh damage paths and saved-state audits. The positions-only starting guess comes from `rl/offline_tomato_evolution_predictor.py`. Despite living under `rl/`, these workers diagnose mechanics and do not train a policy. Use one worker at a time with the recorded single-thread environment. Outputs must use fresh directories; do not overwrite archived evidence.
