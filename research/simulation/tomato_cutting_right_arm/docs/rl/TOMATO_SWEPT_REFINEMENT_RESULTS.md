Updated 25 October 2026, 23:48 UTC: current accepted insertion **8.84375 mm**, force residual 4.49946429e-08, physical stability 0.00178752887, work error 0.057675%, swept penetration 0.375821 nm. Two patches fully failed; graph remains connected. The sections below preserve the earlier refinement/diagnostic evidence. Next bounded work is specified in TOMATO_FIRST_FAILURE_STEP_COMPARISON_PLAN.md.

# Offline swept-contact refinement results

Updated 25 October 2026, 23:28 UTC. Guided, frictionless quasistatic toy model with synthetic material parameters.

Last independently qualified insertion: **8.837890625 mm**, `runs/offline/tomato_curvature_search_01/insertion20_small_global/attempt004`. Two of 47 patches have fully failed; 45 remain active. The material graph is one component. Latest force residual 4.3291863e-08; physical stability 0.00178766791; work error 0.057742%; swept penetration 0.371989 nm. Detailed current interpretation is in TOMATO_SWEPT_PATH_DIAGNOSTIC_RESULTS.md; earlier rows below preserve the prior refinement history.

## Physical path checks

A clear endpoint does not guarantee a clear path. Every interpolated segment must meet the unchanged 1-nanometre penetration allowance. Passing equilibrium, energy and physical stability cannot override this contact gate. Failed states remain uncommitted.

| Previous depth mm | Target depth mm | Interval mm | Swept gap nm | Result |
|---:|---:|---:|---:|:---|
| 8.812500000 | 8.843750000 | 0.031250000 | -32.8054414 | Rejected: contact |
| 8.812500000 | 8.828125000 | 0.015625000 | -2.49800181e-07 | Independent pass |
| 8.828125000 | 8.843750000 | 0.015625000 | -16.4017158 | Rejected: contact |
| 8.828125000 | 8.835937500 | 0.007812500 | -2.21845875 | Rejected: contact |
| 8.828125000 | 8.832031250 | 0.003906250 | -3.12250226e-07 | Independent pass |
| 8.832031250 | 8.835937500 | 0.003906250 | -1.10925422 | Rejected: contact |
| 8.832031250 | 8.833984375 | 0.001953125 | -0.183894525 | Independent pass |

Latest actual force residual: 4.3291863e-08. Physical stability eigenvalue: 0.00178766791. Work error: 0.057742%. Swept penetration: 0.371989342 nm, within the unchanged 1 nm allowance.

## Numerical guesses and provenance

The cycle guard rejects identical uncommitted restart states; it never accepts a physical state. Its fingerprint includes positions, ordered contacts, provisional damage/history, target depth, the actual predecessor and source hashes. Eight tests and saved-path replays pass, alongside the unchanged earlier 143 checks. No tests were unnecessarily repeated this session.

Target-specific frozen-state guesses use the same provisional damage and exact accepted predecessor. They transfer positions/contact bookkeeping only; work, reactions and committed history are not copied. The unchanged v3 worker then recomputes coupled damage consistency and every physical criterion, followed by an independent audit. A seed is never reused at a different target or predecessor.

Supplemental qualification verifies 6 generic seeds, all existing source/state digests and extra helper snapshots. New read-only evidence checker `runs/offline/tomato_global_search_01/qualify_seed_provenance.py` invokes the preserved physical qualifier and checks seed lineage, source preservation, finite diagnostic metrics, numerical energy descent and recorded call budgets. Its source hash/copy are archived separately in source_snapshot_v3.json and source_v3. It does not solve mechanics or accept failed states.

## Safeguards and next bounded experiment

Workers remain serial under shared locks: 512 MiB address-space cap, 45 CPU seconds, 55 s alarm, 60 s parent timeout, one thread and at most 12 calls per batch. The original RAM/VRAM watchdog, frozen grasp criteria, physical laws, force/stability/work/contact thresholds and deadline are unchanged. No simulator/native imports, training, installation or robot controller changes. Reported usage is 5%, leaving 95%; the secondary window remains unknown.

Next target: 8.83984375 mm from the newly accepted 8.837890625 mm checkpoint, preserving the smaller 0.001953125 mm interval. Use a new cycle-guarded batch with the positions-only predictor. If a cycle recurs, create a new target-specific frozen guess against the same actual predecessor. If physical contact fails, halve again without repairing history or relaxing the threshold. Stop at any unresolved physical stability frontier. Run the saved evidence checker and refresh the results after checking quota.
