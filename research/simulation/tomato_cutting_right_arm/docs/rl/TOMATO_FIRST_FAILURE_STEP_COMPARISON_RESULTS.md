# First complete patch failures: insertion-step comparison results

26 October 2026, 00:14 UTC. Local quasistatic model check; separate from the main path and from native timestep or spatial convergence.

**All four finer endpoints pass the original physical checks and independent audits. Both paths meet the existing 1% local fracture-energy criterion.** They identify the same fully failed patches and closely matching state/force results at the shared depths. This qualifies the stated local energy check; it does not validate a complete cut, release or real tomato material.

## Experiment

Both paths start from the exact same accepted 8.75 mm geometry, partial damage/history, source hashes, fixture and blade. The existing coarse path uses two 0.03125 mm increments. The separate finer path uses four 0.015625 mm increments. No material law, controller, acceptance threshold or memory safeguard changed. The authoritative main path remains 8.84375 mm; no comparison work/history was spliced into it.

| Path | Accepted sample depths mm | Final relative fracture-work error | Fully failed IDs at 8.8125 mm |
|:---|:---|---:|:---|
| coarse | 8.78125, 8.8125 | 0.001499715% | [19, 33] |
| fine | 8.765625, 8.78125, 8.796875, 8.8125 | 0.003552468% | [19, 33] |

Local fracture-work residual means blade work since the common baseline minus the stored-energy change minus the fracture-dissipation change. It is normalized by positive local fracture loss. Every new state also passes the unchanged force, contact/swept-path, stability, volume, surface, support, irreversibility and independent source/state checks.

## Measured agreement

| Common depth mm | Maximum damage difference | Maximum history difference m | Blade-force difference N |
|---:|---:|---:|---:|
| 8.78125 | 9.88098492e-15 | 2.11636264e-16 | -4.30766534e-14 |
| 8.8125 | 1.535024e-09 | 3.34912775e-11 | -7.22315496e-09 |

Both paths have patch 19 fully failed at 8.78125 mm and patches 19 and 33 fully failed at 8.8125 mm. The finer samples narrow patch 19’s completion bracket to 8.765625–8.78125 mm and patch 33’s bracket to 8.78125–8.796875 mm. These are sampled synthetic-model brackets, not calibrated physical cutting depths. At the endpoint the graph remains one component with 45 active patches.

## Energy cancellation matters

The finer final NET error is slightly larger, so these data do not show monotonic convergence of that one aggregate quantity. The coarse first/second common-interval errors have opposite signs and partly cancel. Report both net and accumulated absolute errors rather than choosing only the more favourable measure.

| Path | Signed per-step residuals J | Sum of absolute per-step residuals J | Net residual J |
|:---|:---|---:|---:|
| coarse | -4.9233e-09, 7.73322e-09 | 1.26565242e-08 | 2.80992502e-09 |
| fine | -4.86954e-11, 2.93398e-09, 3.8347e-09, -6.39459e-11 | 6.8813257e-09 | 6.65604314e-09 |

Accumulated absolute per-step residual falls by 45.630%. Both original 1% local energy gates pass, but only two insertion-step levels were tested. No cross-path damage tolerance was invented, and neither exact identity nor full convergence is claimed.

## Numerical failures and provenance

The predicted third and fourth finer attempts each exhausted their unchanged bounded worker budget before equilibrium; their candidates remain uncommitted. Fresh frozen-state numerical guesses, anchored to the same actual predecessor, then allowed the unchanged worker and independent auditor to pass. A guess never supplied committed damage, forces or work. Resource caps and rejected evidence were retained.

A separately versioned saved-evidence checker now includes every seed folder containing its diagnostic file, so the comparison seed is verified regardless of its folder prefix. All original lineage/hash/energy/call-budget checks remain. Its prior source is preserved; new source copy/hash is in the global cohort source_snapshot_v5.json. The saved-data comparison analyzer and frozen plan are archived in this comparison cohort’s source snapshot. Full results and source/state digests are in the matching JSON and comparison.json.

## Next work

The local comparison is complete. Before investing in many more tiny forward increments, a separate geometry-only diagnostic can test whether a contact-compatible cubic candidate path reduces the moving-junction interpolation error between saved endpoints. That would create no accepted physical trajectory and cannot replace the old rejection labels. It needs analytic reference checks and continuous contact evaluation first; energy/work, volume, surface and coupled-damage validation remain mandatory before any adoption. No physical law or controller change is authorized by this result.
