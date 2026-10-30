# Offline full cut qualification results

**A complete cut and independent slice separation are not validated.** The guarded continuation passed eight full-node checkpoints from 4.125 to 5 mm insertion without damage healing or cut-face crossing beyond the 1e-9 m tolerance. The slice is still materially attached. A finite-triangle contact counterexample demonstrates why the current nodal blade constraints cannot certify the deeper cut, so continuation was intentionally stopped after the in-flight 5 mm checkpoint. This was not a solver failure or an exhausted memory/time cap.

**All 89 regression and qualification tests pass.** Passing those tests and the partial checkpoints does not mean the requested full cut passed. No simulator or training was launched. All pre-existing model code, controllers, safeguards and frozen grasp criteria remain unchanged.

## Accepted continuation

The starting state is the previously accepted 4 mm insertion checkpoint in `runs/offline/tomato_blade_damage_01/insertion_refined/08`, including its actual 47-patch damage and opening history. No damage is prescribed, reset or frozen. Steps are 0.125 mm; failed or unvalidated states cannot supply continuation history. The existing blade-loaded, edge-encounter eligibility law remains active.

| Insertion mm | Damaged patches | Completely failed patches | Maximum damage | Cumulative work residual |
|---|---:|---:|---:|---:|
| 4.125 | 2 | 0 | 0.228531 | 0.1774% |
| 4.250 | 4 | 0 | 0.266421 | 0.1909% |
| 4.375 | 5 | 0 | 0.301810 | 0.1823% |
| 4.500 | 5 | 0 | 0.334932 | 0.1713% |
| 4.625 | 5 | 0 | 0.366000 | 0.3035% |
| 4.750 | 5 | 0 | 0.395198 | 0.2871% |
| 4.875 | 5 | 0 | 0.422691 | 0.2724% |
| 5.000 | 5 | 0 | 0.448889 | 0.4668% |

At 5 mm, five patches have partial damage, none has completely failed, and all 47 patches retain a material connection. An independent graph check includes actual bulk spring bonds, volume-cell couplings and nonzero cohesive patches. It finds **one connected material component**, with no unintended cross-piece bulk couplings. This confirms attachment rather than inferring separation from blade depth or visible opening.

Across the eight accepted states:

- Damage and maximum-opening history never decrease; retained edge encounters are verified from the blade path. Damage updates are independently recomputed from the saved geometry and current contact loads.
- The minimum cut-face gap is 0 m. Matching 448-triangle faces and unchanged y/z guides certify noncrossing across each face and the affine interpolation between checkpoints. This certificate covers guided cut-face contact, not unrestricted rotated or sliding bodies.
- Maximum independently recomputed force residual is 8.137e-8, below 1e-6. Maximum cumulative work residual is 0.466817%, below the unchanged 1% gate. Work, stored energy and exact irreversible fracture dissipation are independently recomputed; old fracture loss is retained.
- Minimum swept local volume ratio is 0.460141, above 0.1. Minimum normalized softening stability eigenvalue is 0.001783, above 1e-6. Endpoint/midpoint outer-surface intersection screens report zero intersections.
- Peak accepted worker RSS is **184.95 MiB**. Accepted workers ran serially for a combined 283.42 seconds.

## Why a full cut cannot yet pass qualification

The predefined interface is 39.688 mm high. The edge must traverse that extent, and approximately 47.688 mm insertion would present the full 8 mm surrogate bevel at its bottom. The validated earlier shallow regime is therefore insufficient for complete failure.

At 8.125 mm insertion, an independent geometry construction places every cut-face vertex exactly on its permitted capped blade facet. Seven finite surface triangles still intersect the capped bevel between their vertices; the largest constructed penetration is **57.966 micrometres**, above the 0.001 micrometre contact tolerance. This is a **synthetic, vertex-feasible counterexample**, not a crossing observed in an accepted mechanical state. It proves that vertex constraints alone cannot guarantee blade clearance through the full cut. Sampling more nodal positions or checking only paired cut-face gaps would not fix this spatial gap in coverage.

A second limitation is independent release: the current tests fix the remainder and guide both cut faces in y/z. They have neither unrestricted post-release contact nor a validated relative-motion experiment after all material bridges fail. A positive local supported tangent is not proof of free-body release; a detached body can legitimately have neutral rigid translation modes.

The continuation was paused after the geometry counterexample was confirmed, allowed to finish its in-flight bounded endpoint, and stopped before scheduling more shallow increments. Saved accepted states remain intact. No zero-damage reset, forced bond deletion, added slice attachment, weakened tolerance or artificial separation displacement was used to manufacture success.

## Required next work

First extend blade contact to finite triangles across the bevel-to-constant-thickness transition. Triangle clipping or equivalent barycentric constraints must include interior facet intersections and their continuous swept motion; the contact solve must enforce those constraints, not merely report them afterward. Start with the saved seven-triangle counterexample and prove it is rejected or resolved without changing the contact tolerance.

Then add an explicit independent-release diagnostic. Require every one of the 47 cohesive patches to reach failure through blade-loaded damage evolution, two disconnected material components with no bulk/volume bridge, blade removal, and a small outward relative translation without cohesive force or healing. Reclose the fully damaged faces under unilateral contact and verify noncrossing. Numerical frame fixing must be disclosed separately from physical supports, and rigid-body null modes must not be confused with local collapse. The existing energy, equilibrium, volume and resource gates remain mandatory throughout. General 3D slice dynamics and calibrated tomato properties remain outside this guided quasistatic model.

## Evidence and preservation

Evidence is in `runs/offline/tomato_full_cut_01`: `attempt.json`, `audit.json`, `finite_triangle_preflight.json`, `tests.json`, saved checkpoints and hashes, and `preservation.json`. The final in-flight checkpoint has its complete state/summary, independently audited even though the paused parent did not copy its captured console output into a per-step log.

New offline code comprises `rl/offline_tomato_full_cut.py`, `rl/tomato_full_cut_checks.py`, `rl/audit_tomato_full_cut.py` and seven qualification regression tests. The remaining 82 tests are the earlier unloading, damage, contact, cohesive, bond and volume regressions.

Every mechanical worker retains the shared controller lock, one BLAS thread, 512 MiB address-space cap, 45 s CPU cap and 55 s wall alarm. Forbidden simulator/training imports are checked. The simulator startup RAM/VRAM guard and frozen grasp criteria are byte-for-byte unchanged. No dependencies were installed, and no native simulator, training or physical robot execution occurred.
