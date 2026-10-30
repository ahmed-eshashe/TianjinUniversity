Updated 25 October 2026, 23:48 UTC: current accepted insertion **8.84375 mm**, force residual 4.49946429e-08, physical stability 0.00178752887, work error 0.057675%, swept penetration 0.375821 nm. Two patches fully failed; graph remains connected. The sections below preserve the earlier refinement/diagnostic evidence. Next bounded work is specified in TOMATO_FIRST_FAILURE_STEP_COMPARISON_PLAN.md.

# Why the current swept-contact check needs small steps

25 October 2026, 23:28 UTC. Diagnostic of saved offline states only.

The latest independently accepted insertion is **8.837890625 mm**. Two of 47 cohesive patches have completely failed; the other 45 still connect the pieces. The model has not demonstrated full separation or independent release.

## Confirmed finding

All seven examined path minima occur at the model’s bevel-to-constant-width junction, where the contact point moves across a triangle edge. The worst times are approximately halfway through the step. The saved endpoints can be clear while their straight-line interpolation penetrates the blade. The existing safeguard correctly rejects paths beyond the unchanged 1 nm allowance.

The diagnostic reconstructs each quadratic gap over its exact activation interval, locates its stationary minimum, and compares it with the original swept calculation and direct row evaluation. It then checks the actual intermediate shape using the separate Cartesian polygon audit. All comparisons agree within 1e-12 m. No intermediate diagnostic shape is accepted or added to physical history.

| Previous → target depth mm | Original endpoint status | Minimum gap nm | Constraint |
|:---|:---|---:|:---|
| 8.812500000 → 8.843750000 | Rejected: swept contact | -32.8054414 | cap_edge |
| 8.828125000 → 8.843750000 | Rejected: swept contact | -16.4017158 | cap_edge |
| 8.828125000 → 8.835937500 | Rejected: swept contact | -2.21845875 | cap_edge |
| 8.832031250 → 8.835937500 | Rejected: swept contact | -1.10925422 | cap_edge |
| 8.832031250 → 8.833984375 | Accepted with independent audit | -0.183894525 | cap_edge |
| 8.833984375 → 8.835937500 | Accepted with independent audit | -0.370802257 | cap_edge |
| 8.835937500 → 8.837890625 | Accepted with independent audit | -0.371989342 | cap_edge |

## Why this happens

Both the triangle’s shape and the barycentric contact weights change as the blade descends. Their product contains a quadratic term even when the node positions and blade height are each interpolated linearly. The diagnostic independently computes that mixed term from the change in weights multiplied by the change in node positions. Its largest difference from the fitted quadratic coefficient is 2.51684988e-17 m.

This identifies the source of the interpolation error on these seven paths. It does not prove that a larger step is physically valid, establish a general convergence rate, or replace the force, energy, material-stability or surface checks. Source endpoint flags and acceptance decisions are preserved exactly.

## Current accepted state and safeguards

Force residual: 4.3291863e-08. Supported physical stability eigenvalue: 0.00178766791 (required >=1e-6). Work error: 0.057742%. Audited swept penetration: 0.371989342 nm, within 1 nm.

The diagnostic took 1.545 s and used 118.852 MiB high-water RSS. All work stayed serial under shared locks and the unchanged 512 MiB / 45 CPU-second / 55-second alarm limits. Physical model, robot controller, memory watchdog and frozen grasp criteria remain unchanged. No simulator/native import, training, installation, damage update or new physical endpoint occurred in this diagnostic. Source copies/hashes are archived under the global cohort’s source_snapshot_v4.json and source_v4.

## Next bounded step

Continue from the latest accepted 8.837890625 mm checkpoint to 8.83984375 mm using the validated 0.001953125 mm interval and all original gates. Retain the early cycle stop and target-specific uncommitted guess procedure. If the swept gate fails, refine from the accepted predecessor. A future numerical path redesign would need fresh independent continuous-contact, energy/work, volume, surface and constitutive-history validation before use; none is implemented here.
