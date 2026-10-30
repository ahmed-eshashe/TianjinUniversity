# Offline finite triangle blade contact results

**The between-vertex blade penetration defect is corrected in the new offline contact backend.** The saved 8.125 mm counterexample is rejected by the new finite-triangle constraints and resolved to numerical roundoff in a supported surface reference. The full protected tomato passes a separate 5 mm fixed-damage equilibrium and stability check. **Full cutting remains on hold:** deeper nonlinear mechanical probes did not pass the existing solver/resource limits. No simulator, training or full cut was launched.

All **103 tests pass**: 14 new triangle-contact and weighted-contact tests plus 89 existing contact, unloading, damage, bond and volume regressions. All pre-existing code and documentation, including memory safeguards and frozen grasp criteria, remain byte-for-byte unchanged. The new backend is exercised by the new offline workers; historical nodal-contact runners are retained for comparison and are not approved entry points for a new full-cut claim.

## Contact correction

Each cut triangle is split conceptually into the parts ahead of the finite edge, over the bevel and over the constant-thickness blade. A planar triangle's clearance is affine within each clipped region. Checking the region's vertices therefore covers its entire area. The new inequalities include triangle-edge intersections with both the physical knife tip and the bevel-to-thickness transition; they do not merely check the original mesh vertices or sample extra points.

The intersections are expressed as exact barycentric combinations of the adjacent mesh vertices, so contact forces are distributed back to those vertices. The solver enforces these inequalities during optimization. An independent Cartesian polygon-clipping auditor checks the resulting clearance without using the contact-row construction. Inactive row placeholders retain stable indexing but are excluded from the physical solve and carry zero force.

This remains the declared guided, fixed-normal, frictionless interface model. Cut-face y/z coordinates are fixed, the blade spans the entire face in y, and its back edge cannot pass the face. Unsupported partial-span or back-edge cases are rejected. This is not general 3D blade collision, arbitrary sliding/rotation, or native Newton/Isaac integration.

## Verified spatial results

| Check | Result |
|---|---:|
| Original independent clearance at the saved counterexample | -57.965994 micrometres |
| Corrected independent clearance | -3.469e-18 m |
| Matched triangles on each face | 448 |
| Matched vertex pairs | 257 |
| Loaded bevel-transition constraints in the surface reference | 12 |
| Maximum vertex correction in the surface reference | 59.422845 micrometres |
| Surface-reference force residual | 1.820e-14 |

The 8.125 mm reference uses the actual full cut-face mesh with explicitly disclosed quadratic supports in place of bulk tomato mechanics. It proves that the previously missed interior penetration is now detected and mechanically resisted by the contact solver; it does **not** validate the nonlinear tomato at that depth.

The separate 4,032-node protected spring/volume model at 5 mm retains the actual imported 47-patch damage map as a fixed material state. Its independently audited results are:

- Finite-polygon blade clearance: -3.469e-18 m; cut-face gap: 0.0 m. Both satisfy the unchanged 1e-9 m penetration tolerance.
- Relative equilibrium residual: 8.302e-12, below 1e-6; contact complementarity: 8.072e-20 N m.
- Minimum local volume ratio: 0.454846, above 0.1. Minimum normalized frozen-damage tangent eigenvalue: 0.001805, above 1e-6.
- Six loaded entry-edge constraints and no loaded cap-edge constraint at this shallow depth. Fixed support and cut-projection errors are exactly zero, and endpoint proper outer-surface intersections are zero.
- Peak worker RSS: 185.68 MiB; runtime: 8.08 seconds.

Damage evolution is deliberately disabled in this contact-only mechanical diagnostic. All damage/history values exactly retain the imported map; the existing evolving-damage/no-healing regressions also pass. This is not a new fracture-energy, softening-branch, unloading-after-cut, or slice-release result. The optimized positions are standalone static equilibria, not a validated trajectory from the earlier contact formulation.

## Swept contact and blade work

The new path check includes every vertex entry/cap event. With the fixed y/z guides, moving barycentric weights times linearly interpolated nodal positions give a quadratic clearance on each interval. Endpoint values and interior stationary points are checked. One regression has safe endpoints but a 2.5 micrometre interior-time penetration; the new check rejects that path.

Blade work includes the moving contact coordinates: resistance per metre of insertion is `lambda dot (db/ds - dC/ds times x)`. Using only changing nodal bounds would miss the work associated with moving barycentric constraints. A finite-difference virtual-work test and an insertion/withdrawal reference verify this term.

| Base steps per direction | Accepted reference states | Maximum work error relative to peak energy | Minimum swept clearance |
|---|---:|---:|---:|
| 180 | 515 | 0.833337% | -6.531e-10 m |
| 360 | 873 | 0.416670% | -6.531e-10 m |

Both satisfy the unchanged 1% energy and 1e-9 m contact gates. Halving the base step approximately halves the maximum energy error. The fine reference ends at zero stored energy with net cycle work 2.183e-14 J. These are reversible quadratic support references, with no fracture or bulk tomato mechanics.

A candidate segment that crosses the blade beyond tolerance is discarded before work/state acceptance and replaced by smaller steps. The two references discard 154 and 152 such uncommitted candidates. No crossed accepted trajectory is repaired afterward.

## Remaining gate before a full cut

The nonlinear 5.25 mm continuation probe exhausted the unchanged 45 s CPU cap. A direct, larger 8.125 mm optimization guess was also rejected because the free-space quadratic subproblem was nonconvex. Neither became an accepted state. These failures do not weaken the contact correction or justify treating the supported surface reference as bulk validation.

Next, make the protected-model nonlinear contact equilibrium converge beyond 5 mm within the current limits. Constraint-aware tangent/globalization and bounded numerical continuation need attention before extending insertion. Keep physical forces, volume protection and the final acceptance gates unchanged; optimization step conditioning must not be counted as added physical stiffness or dissipation.

Before retrying a coupled full cut, connect this backend's facet loads, moving-coordinate blade work and swept-path rejection to the evolving-damage runner. The load adapter retains the existing edge-history and current-load eligibility approximation, but its full coupled evolution is not validated here. Start a consistent new undamaged trajectory and energy ledger; do not count uncommitted optimization chunks or the imported old-contact equilibrium as physical cutting steps. Complete failure of all 47 patches, material disconnection, blade removal, independent motion and nonpenetrating reclosure remain mandatory future checks.

## Safeguards and evidence

Numerical workers run serially under the existing shared controller lock with one BLAS thread, 512 MiB address-space limit, 45 s CPU limit and 55 s wall alarm. OSQP's already installed builtin CPU backend is used; no dependencies were installed. The dense contact-load recovery is bounded to less than 64 MiB and does not assemble a dense full-system mechanical matrix. Final equilibrium, contact and stability checks use the unchanged model, without penalty contact springs or material retuning. Simulator/training import checks pass. The existing RAM/VRAM watchdog, frozen grasp criteria and robot controllers are not edited.

Final evidence is under `runs/offline/tomato_triangle_contact_01`: `validated5`, `audit5_final.json`, `surface_final`, `energy180_final.json`, `energy360_final.json`, `tests.json`, source/state hashes and `preservation.json`. Preliminary numerical experiments, resource-cap stops and superseded code snapshots are kept separately from these final results. A zero-contact release bug found during the preliminary regression run was corrected; the final release regression and all 103 tests pass.

New code is `rl/tomato_triangle_contact.py`, `rl/tomato_linear_contact.py`, the three `offline_tomato_triangle_*` workers, `rl/audit_tomato_triangle_contact.py` and `rl/tests/test_tomato_triangle_contact.py`.
