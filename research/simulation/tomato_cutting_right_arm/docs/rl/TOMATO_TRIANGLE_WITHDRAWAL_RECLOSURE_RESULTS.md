# Corrected triangle-contact withdrawal and supported reclosure

Updated 2026-10-25T21:27:56.491771+00:00. Offline quasistatic diagnostics only.

## Verified withdrawal

The blade has withdrawn from the qualified 8.125 mm insertion state to **0.0 mm**. **71 accepted checkpoints** pass independent recomputation. Complete withdrawal validated: **True**. Damage and opening history remain exactly unchanged: **True**.

| Check | Result |
| --- | --- |
| Maximum local withdrawal work error | 0.202075% (unchanged limit 1%) |
| Minimum swept blade gap | -2.41127e-15 m (unchanged tolerance -1e-9 m) |
| Minimum cut-face gap | -2.41127e-15 m |
| Peak accepted worker RSS | 193.47 MiB |
| Existing regression tests | 111 passed |

Last accepted withdrawal: `runs/offline/tomato_triangle_withdrawal_01/withdrawal_batch09/attempt006_00`. The imported seed retains five partially damaged patches, zero fully failed patches, and one material component. Source and saved-state hashes are checked at explicit version transitions; the complete insertion work ledger and spent fracture energy are retained. A separate 1% local withdrawal energy gate prevents the old fracture loss from masking unloading errors.

The first unpredicted withdrawal stopped on a nonpositive Newton search diagonal. It was never accepted as a physical state. A bounded signed secant position guess, derived from verified saved positions, resolved initialization without changing committed damage, physical path origins, work or acceptance limits. Optimization-only candidates remain separate from qualified states.

## Supported reclosure

Supported cycle qualified: **True**. Independently audited phase indices: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]`. Complete declared cycle: **True**.

| Drive mm | Back-cap load N | Cut contact load N | Maximum cut gap m | Local work error % |
| --- | --- | --- | --- | --- |
| 0.000 | 4.1138032e-11 | 2.7399461e-12 | 1.863093e-15 | 1.53965e-11 |
| 0.025 | 0.0086311994 | 0.0086311994 | 0 | 0.0290114 |
| 0.050 | 0.017247347 | 0.017247347 | 0 | 0.0145364 |
| 0.025 | 0.0086311994 | 0.0086311994 | 0 | 0.00725706 |
| 0.000 | -1.7701642e-13 | -2.756143e-14 | 1.0044049e-14 | 1.19752e-07 |
| -0.025 | -0.0085168044 | 0 | 2.9368086e-06 | 0.00693302 |
| -0.050 | -0.017048127 | 0 | 5.8719493e-06 | 0.0141538 |
| -0.025 | -0.0085168044 | 0 | 2.9368086e-06 | 0.00693301 |
| 0.000 | -4.6205256e-13 | 9.3212885e-16 | 8.1393225e-15 | 1.05445e-07 |
| 0.000 | -4.6205256e-13 | -3.9877671e-13 | 8.1393225e-15 | 1.05445e-07 |

Explicit cycle checks:

- ten_phases_independently_audited: True
- damage_and_history_exactly_retained: True
- baseline_sources_unchanged: True
- compression_positive_load: True
- compression_faces_closed: True
- compression_load_balanced: True
- negative_drive_reopens_faces: True
- final_faces_reclose: True
- final_stored_energy_returns: True

The zero-insertion control retained a load-bearing edge: one knife constraint carried 0.000534710206 N during compression, with a 21.548 micrometre face opening. This control failed the declared compression closure/load checks and is retained as a failed experiment, despite passing generic equilibrium/energy checks. Zero insertion is not the same as an absent blade. The corrected test moves the edge to 1 mm above the entire undeformed tomato and checks at least 0.5 mm actual clearance above both endpoints' nodes and exactly zero blade multipliers throughout. It starts from the same qualified withdrawal checkpoint; no material state is reset.

The diagnostic engages the existing disclosed 193-node slice back-cap x support only at zero drive and with engagement displacement at most 1e-9 m. The sequence is 0, +0.025, +0.05, +0.025, 0, -0.025, -0.05, -0.025, 0, 0 mm. All support reactions and support work are recomputed. The small loop has its own 1% energy ledger, independent of earlier fracture energy. Positive drive tests compression, negative drive tests reopening without an adhesive contact weld, and final zero drive tests reclosure. The remainder fixture and fixed cut-face y/z guides remain disclosed.

## Safeguards and limits

Original preservation manifests (250 original files and 241 pre-session source/doc files) are checked. Original model laws, material parameters, controllers, memory watchdog and frozen grasp criteria remain unchanged. Workers are serial under the original lock, with one BLAS thread, 512 MiB address space, 45 s CPU, 55 s wall and 60 s parent timeout. Quota leases and the overnight deadline separately bound batch launch. No simulator/native-engine import or launch, training or dependency installation occurs.

This is the same uncalibrated guided spring/volume/cohesive model with finite wedge/triangle contact. It excludes gravity, board contact, inertia, friction, arbitrary blade pose and general 3D sliding contact. Loads are synthetic diagnostic values, not measured real-tomato predictions. The support is a disclosed test fixture, not a robot hand. A passing withdrawal/reclosure cycle does not establish a completed cut or free slice release.

## Next gate

Only after complete withdrawal and supported cycle qualify, resume deeper insertion from the original accepted insertion trajectory with its committed histories intact. Require physical blade-dependent failure of all 47 patches, two disconnected material components, blade removal, independent motion and nonpenetrating reclosure before declaring full cutting success. Resolve every failed contact, energy, convergence or stability check before proceeding; never weaken limits or force bond deletion.

Evidence: `runs/offline/tomato_triangle_withdrawal_01/qualification.json`, `reclosure_qualification.json` when available, per-endpoint independent audits, preserved failed attempts, `tests.json` and `handoff.json`.

Latest separate insertion branch: **8.3125 mm**, 5 partially damaged patches and 0 fully failed patches. It remains materially connected. New branch summaries and failures are in `insertion_qualification.json`; interrupted withdrawal/reclosure states are not concatenated into its work ledger.
