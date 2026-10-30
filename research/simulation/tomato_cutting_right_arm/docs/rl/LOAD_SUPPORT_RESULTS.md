# Knife load support checks and refined terminal grip

The three offline checks are complete. The knife's authored scale and provisional mass calculations are internally consistent. A finite surface-contact model confirms that the previous near-flat grip layouts cannot balance its turning moment within the tested budgets. **A different terminal orientation does have conditional load support:** rolling the knife about its length toward an edge-on pose preserves its outward blade direction and admits a static solution for 1.25 times the assumed weight, with the existing actuator limits.

The selected 90-degree rolled proposal is saved in [load_support_candidate.json](load_support_candidate.json). **It is inactive and is not a physical grasp success.** Positive contact gaps, uncooked collision geometry, approach/settling and the route from a flat central start remain unvalidated. It exceeds the separate existing 20-degree in-place diagnostic motion limit; that limit and the active plan were not changed or bypassed. No simulator or training was started.

## Knife scale and mass properties

[The independent mass audit](../../runs/offline/load_support_01/knife_mass_audit.json) recomputed the handle/blade convex volumes, component centres of mass, parallel-axis inertia and authored principal-axis reconstruction.

| Quantity | Result |
| --- | --- |
| Visual dimensions in the native metre-based root | 438.27 × 51.95 × 21.10 mm |
| Handle collision length | 172.58 mm |
| Authored total mass | 0.25 kg |
| Assigned handle/blade masses | 0.10 / 0.15 kg |
| Recomputed local centre of mass | Approximately (-190.94, 5.03, 1.38) mm |
| Authored versus recomputed COM difference | 0.00000188 mm |
| Maximum inertia component discrepancy | 1.07e-10 kg m² |
| Geometry change caused by scale baking | Less than 0.000018 mm per vertex |

The 0.7625 uniform scale was correctly baked into the derived vertices; the current rigid transform has unit axis scales. There is no evidence of a second scale multiplication in this composition. The positive inertia eigenvalues and original report values agree with the recomputation. The mass split and uniform component densities are internally consistent assumptions, **not measurements of the physical knife**. They were not reduced to make the grasp pass.

A standalone open of `phase3_grasp.usda` reports USD's default 0.01 metres per unit because its root has no explicit stage-unit metadata. The native runtime instead authors 1 metre/unit on its parent root in the installed `SimulationContext._init_usd_physics_scene`, then composes the derived scene. An in-memory USD root reproduces that composition without starting the simulator. Therefore the bare-layer fallback must not be used to reinterpret this native task as a 4.38 mm knife. This unit dependency remains part of the interface contract; no layer was edited here.

## One point versus a finite contact surface

The new [contact load solver](../../rl/contact_load_model.py) uses friction-cone forces and balances all six components of force/moment. Surface candidates come from original convex exteriors and verified closest witnesses, not invented torsional joints. Friction uses an inscribed eight-ray cone at coefficient 0.6. Normal force is capped at **10 N per part shared across all its points**, so adding points does not invent force capacity. The existing 80 Nm arm, 1 Nm thumb-coordinate and 0.3 Nm finger-coordinate limits are applied through coupled point Jacobians. Robot self-weight, full drive equilibrium and calibrated compliance remain outside this conditional model.

The [finite-surface comparison](../../runs/offline/load_support_01/multipoint_load_audit.json) tests both previous proposals at maximum hypothetical gaps of 0.25, 0.5, 1, 2 and 4 mm. Both representative-point and finite-surface versions fail load balance in their original near-flat orientation. Force-only probes pass, but full wrench balance fails. Removing actuator limits while retaining the 10 N shared normal budget does not fix it. Diagnostic 100 N force-cap probes can balance the wrench if actuator limits are also removed; with actual actuator limits restored, they fail. These probes do not authorize higher forces or modify any runtime setting.

This separates a contact-layout/moment limitation from merely insufficient upward force. It also prevents the conclusion that increasing friction, pressure or finger curl alone is justified.

The single-point approximation is nevertheless restrictive in some cases. For the 60-degree rolled variant, one fixed representative point per part fails while the finite-surface version passes **under the same shared force and actuator budgets**. At 75 and 90 degrees both pass. An analytic regression case also demonstrates how finite longitudinal contact spacing can balance a moment that coincident point contacts cannot; duplicating points at the same place provides no such benefit. These findings do not identify the cause of the earlier live pinch-collapse event, which remains unresolved.

## Load-aware refinement

Twenty rigid layout variants explored closer-to-blade shifts and reversed longitudinal hand orientation. Ten reached load evaluation; the others were rejected by blade/support clearance or arm IK. None passed the conditional margin test in the original knife orientation. Two further bounded wrist/finger optimizations improved an approximate required-budget score but still failed the fresh surface-contact test. Their geometry also retained or introduced intersections, so they were not promoted.

An axial-roll screen then found load support when the knife and hand are rotated together about the knife's length. This changes which contact directions resist gravity and the knife moment. **It does not pitch the blade tip upward or turn the blade back toward the robot:** the long-axis direction is unchanged to numerical precision. The grip was checked again with fresh surface points, actual terminal arm IK and the original torque budgets.

| Axial-roll change from supported reference | Conditional nominal and 1.25× weight balance | Maximum actuator knife-load fraction at 1.25× | Terminal self-envelope result |
| --- | --- | --- | --- |
| 60 degrees | Pass | 0.744 | Additional ambiguous arm-base/torso overlaps; not selected |
| 75 degrees | Pass | 0.681 | Only the existing link 5/7 decomposition ambiguities |
| 90 degrees | Pass | 0.604 | Only the existing link 5/7 decomposition ambiguities; selected |

For the selected 90-degree case, the hypothetical 1.25× load solution uses approximately 6.33 N thumb, 3.29 N palm, 1.92 N little finger and 0.06 N each index/middle normal load. The force-bearing geometric layout has palm support, thumb opposition, three curled fingers, two inner fingers and radial enclosure under the frozen geometric definitions. These forces are an **offline equilibrium solution**, not measured contacts or a positive physical oracle example. Some finger loads are close to the minimum classification threshold, so dynamic robustness is not established.

The 1.25× calculation corresponds to the gravity load of 0.3125 kg under the assumed 0.25 kg task. Actual task mass remains 0.25 kg. Single-variable probes at friction 0.4/0.8 and local COM shifts of ±20 mm also pass for the rolled variants. They are isolated model sensitivities, not combined uncertainty coverage, hardware calibration or a deployment guarantee.

The selected mathematical terminal pose raises the knife reference by 50 mm and gives at least 51 mm hand clearance above the board plane. Its arm IK position error is below 0.001 mm. No handle intersections above the numerical check were detected for this proposal. The old decomposed arm link 5/7 envelope ambiguities remain; cooked-shape inspection and full arm/environment/trajectory checks are still required.

Relative to the handle, palm/thumb gaps remain approximately 0.648/0.235 mm, index proximal gap 0.522 mm and little-finger inner gap 0.460 mm. A static contact solution assumes these can close without destroying the contact arrangement. A final seating optimization retained conditional load feasibility and brought some finger regions closer, but introduced 0.016–0.022 mm inscribed handle-intersection radii and worsened the palm gap. **That adjustment was rejected.** The selected proposal retains the nonintersecting geometry and explicit gap limitations.

Detailed results: [orientation candidates](../../runs/offline/load_support_01/oriented_support_candidates.json), [sensitivity checks](../../runs/offline/load_support_01/oriented_support_sensitivity.json), [rigid layout search](../../runs/offline/load_support_01/load_refinement.json), [original-orientation optimization](../../runs/offline/load_support_01/load_optimized_candidates.json), and [rejected rolled seating adjustment](../../runs/offline/load_support_01/seated_rolled_candidate.json).

## Verification and remaining gate

All **62 automated tests pass**. New analytic tests check force/friction balance, moment support from finite contact spacing, shared force budgets, actuator and inner-contact constraints, coordinate invariance, and honest reporting when a diagnostic requires expanded budgets. Offline modules compile. Searches were bounded and numerical threads limited to one; the recorded offline processes peaked below 480 MB RAM. This does not validate live logging or future training memory consumption.

Before/after hashes confirm that the guard, runtime controller/logging code, frozen criteria, source robot, derived scenes, active plan and mass/friction properties are unchanged in this continuation. Source snapshots and machine-readable checks are in [the evidence directory](../../runs/offline/load_support_01).

The next gate is **physical credibility of the contact arrangement**, not full training: resolve cooked collider ambiguities and contact gaps, validate the new diagnostic timing/force conventions under the unchanged memory guard, and separately assess terminal retention. A retained terminal pose would still not prove pickup from a flat central start. A route to the rolled orientation needs explicit staged planning because the current in-place test only permits 20 degrees. The current launcher must not be used to force this candidate through that limit. No route, attachment, teleport or relaxed success threshold is supplied by this offline result.
