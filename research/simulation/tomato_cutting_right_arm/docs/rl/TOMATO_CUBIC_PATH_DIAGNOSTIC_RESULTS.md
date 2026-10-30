# Saved-state cubic contact-path diagnostic

26 October 2026. Offline geometry diagnostic only; no accepted cutting trajectory changed.

**Smoother candidate curves reduce the measured swept penetration in all seven saved intervals, but the two largest intervals still fail the original 1 nm clearance allowance.** This does not resolve the full cutting problem. Previously rejected endpoints and straight-line paths remain rejected, including cases whose new candidate curves have smaller gaps.

## What was tested

The existing exact triangle-contact constraints depend on blade insertion: the bevel-cap intersection moves along each mesh edge. A straight-line nodal interpolation can violate the moving surface between otherwise clear endpoints. This experiment retains each original endpoint and constructs a cubic Hermite curve between them. Its endpoint velocities are the closest chord velocities satisfying the strongly loaded endpoint contact derivative constraints and zero fixture/guide velocities. They are kinematic derivatives, not velocities obtained from mechanical equilibrium or a time integration.

Each activation interval is split at the same original vertex-entry and bevel-cap events. A cubic nodal curve multiplied by an affine contact matrix gives a quartic gap polynomial. Endpoints and resolved real stationary roots are evaluated. Near-real ambiguous roots or inconsistent velocity constraints fail closed. Independent Cartesian polygon clipping checks the worst witness. Floating-point root calculations are numerical evidence, not certified interval arithmetic.

| Saved interval | Original penetration nm | Candidate penetration nm | Candidate geometry only |
|---|---:|---:|---|
| insertion06_global_seed | 32.8054414 | 8.15111887 | exceeds allowance |
| insertion09_refined_global | 16.4017158 | 4.08786935 | exceeds allowance |
| insertion11_quarter_global | 2.21845875 | 0.553763423 | within allowance |
| insertion14_small_global | 1.10925422 | 0.277100739 | within allowance |
| insertion16_sixteenth_global | 0.183894525 | 0.0459559814 | within allowance |
| insertion18_small_global | 0.370802257 | 3.15829216e-07 | within allowance |
| insertion20_small_global | 0.371989342 | 3.15928327e-07 | within allowance |

Ten analytic reference tests pass: endpoint positions and derivatives, fixed coordinates, affine recovery, interval reparameterization, gap coefficients, quartic interior extrema, deliberate between-endpoint penetration, constant/linear degeneracy, activation knots and nonfinite rejection. The largest direct geometry versus polynomial discrepancy is 9.321e-18 m. Maximum loaded-contact endpoint velocity residual is 1.542e-19 m per normalized path parameter. Supported velocities are exactly zero. The last two curves reduce the gap to roundoff; this is not proof of exact continuous feasibility.

Runtime 2.739 seconds; high-water resident memory 125923328 bytes. Workers retain the 512 MiB address-space,45 CPU-second,55-second alarm,60-second parent timeout and one-thread caps, both common locks and quota/deadline checks. No simulator/native engine, training or installation was used.

## Why this is not a new physical solution

No intermediate equilibrium, contact multipliers along the curve, cohesive evolution, fracture/work balance, continuous volume validity or surface validity has been qualified. Endpoint velocity projection alone is insufficient: residual penetrations remain where contact membership changes. The original force, stability, energy, contact and volume thresholds remain authoritative. No history, work, damage, material parameters, frozen grasp criteria or robot controller was modified. No new endpoint or full cut is accepted.

The authoritative main checkpoint remains8.84375 mm, two fully failed patches,45 active patches and one connected material component. The comparison branch remains separate at8.8125 mm. Independent slice separation remains unvalidated.

## Recommendation and next bounded experiment

Do not adopt cubic interpolation into the mechanical worker. Preserve this diagnosis and return to a physically qualified task: withdrawal from the accepted two-failed-patch checkpoint, followed eventually by blade-cleared reclosure. Earlier withdrawal/reclosure evidence starts at8.125 mm before any patch completely failed, so it does not cover this damage state. The existing withdrawal worker explicitly accepts only its earlier backend; do not bypass this provenance check. Prepare a separate spectral-withdrawal adapter and independent auditor, preserving all physical laws and acceptance checks. First qualify a same-depth source transition and then one small withdrawal segment; stop and diagnose any new damage, loss of stability, work failure or penetration. Keep the withdrawal ledger and checkpoint separate from the forward path. This is planned next work only.

Source/state hashes, seven candidate coefficient arrays and full diagnostics are under runs/offline/tomato_cubic_path_diagnostic_01. Original qualified sources remain unchanged; source_snapshot.json and source/ preserve this diagnostic version. The source/ snapshot is not authorization to modify the original physical modules.
