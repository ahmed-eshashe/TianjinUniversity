# Offline unloading and reclosure after partial damage

**Unloading and supported reclosure pass in the declared offline model: no cut-face crossing beyond the declared numerical tolerance, no damage healing, and no loss of opening history.** Both branches naturally close after withdrawal, carry a positive compression load, reopen under a gentle pull, and close again. The damage map is exactly identical to the imported partial-damage map at all **72 independently audited checkpoints**.

**All 82 tests pass**, including eight new energy/contact-handoff/predictor tests and 74 existing damage, contact and volume regressions. No existing model, controller, memory guard or grasp-criteria file changed. No simulator, training or full cut was launched.

## Verified results

| Withdrawal step | Accepted states including supported probes | Elastic energy returned J | Unloading work error relative to initial elastic energy | Maximum gap after natural closure m |
|---|---:|---:|---:|---:|
| 0.25 mm | 28 | 0.00346696271298 | 0.202142% | 1.041e-15 |
| 0.125 mm | 44 | 0.0034683534965 | 0.162108% | 5.794e-16 |

The imported stored energy is **0.00347398510669 J**. Its previously dissipated fracture energy, **0.00030281674825 J**, remains exactly retained at every state; it is not returned as recoverable work when the faces close. Halving the withdrawal step changes recovered work by 0.040099%. Matched-depth wedge resistance differs by at most 1.13e-11 relative. Both satisfy the existing 10% step-comparison target.

Under the +0.05 mm supported push, contact carries **0.0172473469775 N**, balancing the back-cap force of 0.0172473469775 N. The faces stay closed without crossing. Under the -0.05 mm pull, the maximum gap opens to **5.874908 µm**, demonstrating that ordinary contact does not weld the faces shut. Returning the support to zero closes them again, with final stored energy 5.996e-26 J. These loads are synthetic-model measurements, not calibrated physical tomato predictions.

| Check across both complete paths | Result |
|---|---:|
| Patch damage and maximum-opening-history change from seed | Exactly zero |
| Retained maximum patch damage D | 0.18786211220311036 |
| Healed patches or decreased histories | 0 |
| Maximum signed-gap overlap, including interpolated cut-face paths | 1.25e-14 m (tolerance 1e-9 m) |
| Matched finite cut triangles per face | 448 |
| Minimum swept local volume ratio J | 0.478607 (floor 0.1) |
| Minimum normalized stability eigenvalue with weak contacts permitted to open | 0.001197356 (limit 1e-6) |
| Maximum recomputed normalized force residual | 9.322e-08 (limit 1e-6) |
| Maximum phase-local energy residual | 0.202711% (limit 1%) |
| Midpoint/endpoint proper surface intersections | 0 |
| Peak accepted worker RSS | 183.33 MiB |
| Longest accepted worker | 35.81 s |
| Sum of accepted worker runtimes, serially | 1105.52 s |

The independent auditor verifies source/state hashes, recomputes forces, work, stored/fracture energy and support positions, checks every damage/history transition, and verifies the common triangle topology and fixed-projection noncrossing certificate. Geometry can close while the material remains damaged: the affected patch retains only `1-D` of its original tensile stiffness. No state reset or artificial damage freeze is used.


## Starting state and experiment

Both test branches start independently from the accepted 4 mm partial-insertion checkpoint in `runs/offline/tomato_blade_damage_01/insertion_refined/08`. Source files, saved positions, contact multipliers and edge history are checked against that checkpoint's hashes before use. Its actual 47-patch damage map is imported, including two partially damaged patches; damage is not replaced by a uniform diagnostic value or manually frozen.

The full 4,032-node protected spring model and its original remainder fixture are retained. Cut-face y/z guides remain explicit. The blade is the same finite fixed-normal wedge surrogate used in the partial-insertion test, with uncalibrated geometry/material parameters; it is not a verified real knife edge or a native simulator object.

The stages are:

1. Repeat the 4 mm loaded equilibrium twice to check state/history retention.
2. Withdraw the wedge from 4 mm to zero insertion, allowing the still-connected, partially damaged bodies to close under their own elastic forces. There is no slice back-cap clamp during this stage.
3. With the blade fully withdrawn and the faces closed, engage the disclosed 193-node slice back-cap x support at its existing position. The program rejects engagement requiring displacement above 1e-9 m. Apply drives of 0, +0.025, +0.05, +0.025, 0, -0.025, -0.05, -0.025, 0, 0 mm. Positive drive tests compression/nonpenetration; negative drive checks that the faces can reopen. This support belongs to the diagnostic coupon and does not modify a robot controller or the saved tomato fixture.

The coarse withdrawal spacing is 0.25 mm and the finer spacing is 0.125 mm. Both use the same small support-drive sequence and original constitutive parameters. Neither branch advances the blade farther than its accepted starting depth, and a complete-interface failure cannot pass as a successful endpoint.

## Damage and contact checks

The existing irreversible update remains active. Every trial damage update starts from the last committed history; only a converged, accepted endpoint becomes a continuation state. Each patch must retain or increase both its damage and maximum-opening history. New growth still requires current positive blade load, a retained edge encounter and sufficient opening energy. Closure does not reset the damage variable or restore its tensile stiffness.

As wedge width reaches zero at a material site, its blade constraints disappear and ordinary cut-face contact returns. Cut-face contact depends on geometry, not on the damage value. At positive wedge width the two blade halfspaces imply a stronger positive gap, making a simultaneous closed-face tie redundant. Contact multipliers must remain nonnegative within 1e-9 N; a reopening path cannot be held shut by adhesive contact forces.

Both faces have 448 matching triangles and 257 matched vertex pairs. Fixed y/z projections and nonnegative signed x gaps at every matched vertex certify noncrossing over each entire triangle. Signed gaps are affine along the accepted linear interpolation between endpoints, so nonnegative endpoint gaps also cover those interpolated cut-face paths. The wedge width is a positive-part affine function below its thickness cap, allowing the same supported-path bound during withdrawal. These certificates depend on the declared guides and matched topology; they are not general rotated/sliding collision detection.

Every endpoint additionally checks equilibrium, exact swept local-volume minima, minimum spring length, fixed support positions, surface orientation, midpoint/endpoint proper outer-surface intersections, force/moment balance and a positive tangent in the space permitting weak contacts to open. The conditional loading-side damage correction is retained at the history boundary; genuine unloading below the old peak uses the frozen-damage elastic tangent.

## Energy bookkeeping

This is a new boundary-work experiment anchored at the saved partial-damage state. Its stored elastic/volume energy and already spent fracture loss are recomputed and retained. The earlier insertion ledger remains unchanged; the reported work accuracy applies to unloading/reclosure, not a newly claimed complete insertion-to-withdrawal cycle.

The check is:

`new blade work + support work = stored-energy change + new fracture dissipation`

Already spent fracture energy is not refunded when the faces close. A separate ledger for the small supported reclosure loop prevents its errors from being normalized by the much larger earlier insertion/fracture energy. Both ledgers retain a 1% relative gate plus 1e-12 J absolute allowance, and per-increment energy checks remain active.

The physical path starts at the previous accepted positions. A contact-following predictor changes only an uncommitted optimization guess for the retreating blade; it does not alter that path origin, committed history or any work calculation. Equilibrium and all path checks must still pass. The first large-step diagnostic without this predictor exhausted its 45 s CPU limit and was not accepted; that preliminary evidence is kept separately. No CPU or memory limit was raised.

## Safeguards and scope

No existing controller, model generator, bulk/cohesive law, simulator memory safeguard or frozen grasp criterion is edited. All new code is inactive offline test/audit code. Numerical workers remain serial under the shared controller lock, use one BLAS thread, and retain 512 MiB address-space, 45 s CPU and 55 s wall caps. Forbidden runtime imports are checked. No simulator, training, dependency installation or full cut is started.

This is quasistatic testing of a partial crack with fixed material axes, remainder fixation and cut-face guides. Gravity, board contact and inertia are not included in this work ledger. The small supported compression/reopening probe adds a disclosed back-cap x constraint after natural closure. It does not demonstrate unrestricted slice release, general 3D contact, frictional drawing, viscoelastic recovery or calibrated physical tomato behaviour.

Evidence is under `runs/offline/tomato_unloading_01`, with coarse/fine checkpoints, independent audit, source/input/state hashes, tests, preservation evidence and the retained rejected time-cap probe. The endpoint runner is `rl/offline_tomato_unloading.py`; it starts with `--phase withdrawal --depth-mm 4`, then uses `--previous` to continue downward in depth. Supported probes require `--phase reclosure --depth-mm 0 --drive-mm ...` after full withdrawal. Use fresh output directories, `.venv-native/bin/python`, and the recorded single-thread environment. The independent auditor is `rl/audit_tomato_unloading.py`.
