# Coupled-curvature numerical search: offline results

## What changed

The previous numerical fallback discarded off-diagonal stiffness terms and stalled. The new, separately versioned search keeps those terms and shifts only its dimensionless reduced search matrix when needed. All true model energies, forces and physical tangents are unchanged. An approximate search eigenvalue is never a physical stability certificate. Every saved endpoint still requires the original independent physical audit. Original/v2 sources remain untouched.

## Analytical checks

All 132 combined tests pass. Eleven exercise the new solver, including indefinite positive-diagonal curvature with both ascending and descending ordinary Newton directions, weighted contacts, release, blocking, fixed supports and chunk resume. Stored physical Hessians are checked unchanged.

## Fixed-damage diagnostic

On an uncommitted 8.78125 mm candidate, current fitted force residual fell from 8.2354909e-06 to 7.6633239e-08 in five search iterations. Exact frozen-state energy fell from 0.0054332065193144988 to 0.0054332064962123996 J. Damage was held fixed. This alone is not a physical cutting endpoint.

## Verified backend transition

Backend `triangle_spectral_evolving_v1` verifies every source/state hash of its predecessor. The same-depth 8.75 mm hold preserves positions, edge history, damage/history, energy, fracture loss and accumulated work exactly. Normal multipliers are recomputed and independently audited; blade resistance differs by 9.134677e-9 N. These recomputed hold forces, rather than old candidate reactions, are the next physical work-ledger predecessor.

## Coupled contact and damage results

- `insertion01`: bounded_worker_budget; target 8.78125 mm; 11 serial worker/audit calls; accepted checkpoint `None`.
- `insertion02_seeded`: worker_failed; target 8.78125 mm; 1 serial worker/audit calls; accepted checkpoint `None`.
- `insertion03_seeded`: independently_passed; target 8.78125 mm; 4 serial worker/audit calls; accepted checkpoint `runs/offline/tomato_curvature_search_01/insertion03_seeded/attempt002`.
- `insertion04_predicted`: independently_passed; target 8.8125 mm; 11 serial worker/audit calls; accepted checkpoint `runs/offline/tomato_curvature_search_01/insertion04_predicted/attempt008`.
- `insertion05_predicted`: bounded_worker_budget; target 8.84375 mm; 11 serial worker/audit calls; accepted checkpoint `None`.
- `insertion06_global_seed`: physical_gate_failed; target 8.84375 mm; 6 serial worker/audit calls; accepted checkpoint `None`.
- `insertion07_refined`: independently_passed; target 8.828125 mm; 11 serial worker/audit calls; accepted checkpoint `runs/offline/tomato_curvature_search_01/insertion07_refined/attempt008`.
- `insertion08_refined`: bounded_worker_budget; target 8.84375 mm; 11 serial worker/audit calls; accepted checkpoint `None`.
- `insertion09_refined_global`: physical_gate_failed; target 8.84375 mm; 5 serial worker/audit calls; accepted checkpoint `None`.
- `insertion10_quarter`: repeated_uncommitted_optimizer_state; target 8.8359375 mm; 4 serial worker/audit calls; accepted checkpoint `None`.
- `insertion11_quarter_global`: physical_gate_failed; target 8.8359375 mm; 5 serial worker/audit calls; accepted checkpoint `None`.
- `insertion12_eighth`: independently_passed; target 8.83203125 mm; 11 serial worker/audit calls; accepted checkpoint `runs/offline/tomato_curvature_search_01/insertion12_eighth/attempt008`.
- `insertion13_small`: repeated_uncommitted_optimizer_state; target 8.8359375 mm; 4 serial worker/audit calls; accepted checkpoint `None`.
- `insertion14_small_global`: physical_gate_failed; target 8.8359375 mm; 5 serial worker/audit calls; accepted checkpoint `None`.
- `insertion15_sixteenth`: repeated_uncommitted_optimizer_state; target 8.833984375 mm; 4 serial worker/audit calls; accepted checkpoint `None`.
- `insertion16_sixteenth_global`: independently_passed; target 8.833984375 mm; 5 serial worker/audit calls; accepted checkpoint `runs/offline/tomato_curvature_search_01/insertion16_sixteenth_global/attempt003`.
- `insertion17_small`: repeated_uncommitted_optimizer_state; target 8.8359375 mm; 4 serial worker/audit calls; accepted checkpoint `None`.
- `insertion18_small_global`: independently_passed; target 8.8359375 mm; 6 serial worker/audit calls; accepted checkpoint `runs/offline/tomato_curvature_search_01/insertion18_small_global/attempt004`.
- `insertion19_small`: repeated_uncommitted_optimizer_state; target 8.837890625 mm; 4 serial worker/audit calls; accepted checkpoint `None`.
- `insertion20_small_global`: independently_passed; target 8.837890625 mm; 6 serial worker/audit calls; accepted checkpoint `runs/offline/tomato_curvature_search_01/insertion20_small_global/attempt004`.
- `insertion21_small`: repeated_uncommitted_optimizer_state; target 8.83984375 mm; 4 serial worker/audit calls; accepted checkpoint `None`.
- `insertion22_small_global`: independently_passed; target 8.83984375 mm; 6 serial worker/audit calls; accepted checkpoint `runs/offline/tomato_curvature_search_01/insertion22_small_global/attempt004`.
- `insertion23_small`: repeated_uncommitted_optimizer_state; target 8.841796875 mm; 3 serial worker/audit calls; accepted checkpoint `None`.
- `insertion24_small_global`: independently_passed; target 8.841796875 mm; 6 serial worker/audit calls; accepted checkpoint `runs/offline/tomato_curvature_search_01/insertion24_small_global/attempt004`.
- `insertion25_small`: repeated_uncommitted_optimizer_state; target 8.84375 mm; 3 serial worker/audit calls; accepted checkpoint `None`.
- `insertion26_small_global`: independently_passed; target 8.84375 mm; 6 serial worker/audit calls; accepted checkpoint `runs/offline/tomato_curvature_search_01/insertion26_small_global/attempt004`.
- `transition_hold`: independently_passed; target 8.75 mm; 3 serial worker/audit calls; accepted checkpoint `runs/offline/tomato_curvature_search_01/transition_hold/attempt001`.

Last independently qualified checkpoint: `runs/offline/tomato_curvature_search_01/insertion26_small_global/attempt004` at 8.84375 mm. Physical force residual 4.49946429e-08; physical stability eigenvalue 0.00178752887 (unchanged required floor 1e-6); work-balance error 0.0576747%. Maximum damage 1; fully failed patches 2; material components 1.

A failed seed adapter initially required identical multiplier-file hashes and then an unnecessary reaction-equality tolerance. Neither was a physical acceptance criterion. The final adapter instead requires exactly identical positions/edge history/constitutive state and work ledger, plus the actual passing independent hold audit; it records the small recomputed reaction difference explicitly. The original physical criteria were never changed. The aborted adapter launch and failed reporting-path reconstruction remain disclosed in the journal.

## Safety and limitations

All preservation manifests and qualified-source snapshots pass. Peak physical-worker RSS 216.270 MiB; cap 512 MiB, CPU45s, alarm55s, parent timeout60s. Separate frozen diagnostic high-water RSS 366.070 MiB also remained below the cap. Shared nonblocking locks, one CPU/BLAS thread, quota leases and the original hard deadline remain active. Original simulator RAM/VRAM watchdog and frozen grasp criteria remain unchanged.

This is a guided, fixed-plane, frictionless quasistatic NumPy/SciPy model with synthetic material values. It is not native Newton/Isaac validation, dynamic cutting, robotic control, learned behavior or real tomato calibration. Full cut requires complete bond failure, graph separation, blade clearance and independently checked release/reclosure; blade depth alone proves none of these. No simulator, training, installation or controller change occurred.

## Next bounded work

Read OVERNIGHT_PROGRESS.md and the current qualified checkpoint before continuing. Do not repeat a stalled starting configuration. Use verified positions-only guesses, keep trial damage uncommitted until coupled consistency and all physical audits pass, and preserve the source-hash lineage. Stop on any unresolved physical stability failure; do not step past it. The previous cleared withdrawal/reclosure checks remain separate validation branches and are not concatenated into insertion history.
