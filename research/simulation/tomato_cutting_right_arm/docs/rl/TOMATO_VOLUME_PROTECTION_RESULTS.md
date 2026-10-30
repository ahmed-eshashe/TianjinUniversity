# Tomato volume protection refinement results

Date: 19 October 2026. The refined offline model passes **all 108 load stages across 18 compression/shear paths**, using the same acceptance checks as the failed baseline. Compression reaches 30% and both signs of all three shear directions reach 50%, for both slice and remainder. No accepted state has an inverted or near-collapsed material-volume cell. The smallest volume ratio is 0.2224; the minimum checked free tangent eigenvalue is positive.

This is now explicitly a **hybrid spring plus local volume-energy model**. Its reference cells were previously only diagnostics; they now also generate volume-protection forces and tangents. A pure central-spring model was not made safe by renaming its failures. The new volume term is uncalibrated and has no native Newton runtime implementation yet.

## Mechanical change

For each same-piece reference cell, let J be signed current volume divided by reference volume V0. Add energy kappa V0 times b(J), with kappa=10 kPa as a synthetic protection coefficient. The term is zero for J>=0.5. Below 0.5, define r=(J-0.1)/0.4 and b(J)=-log(r)+r-1. It diverges as J approaches 0.1 from above. Trials with J<=0.1 plus a 1e-12 roundoff margin are inadmissible and rejected.

The term and its gradient are continuous at activation, with a Hessian jump there; rest stiffness and energy are unchanged. Force and tangent come from analytic differentiation of the same energy and are checked independently by finite differences. The protection is rotationally invariant and balances total force and torque. Pure homogeneous unit-volume shear adds no volume energy, but local volume changes during interior relaxation can activate protection.

This is an inversion/near-collapse regularizer, not a calibrated nearly incompressible tomato law. It permits overall 30% compression under the prescribed boundary, and its local activation/floor values are engineering choices. Near-floor stiffness can be very large. This model does not inherit an assumed dynamic timestep from the earlier spring-only proposal.

The saved original masses, same-side spring constants, 403 cross-cut interface coefficients and damage law are unchanged. Volume cells belong entirely to one side; no new cell spans the cut or secretly reconnects a released slice. Existing acceptance still rejects any nonpositive cell volume and flags near-collapse below 0.1. The new material term enforces a stricter admissible domain without relaxing those checks.

## Static solve and stability

The tests use the same prescribed outer surfaces and interior equilibrium scope as the previous sweep, with exact finite-length spring energy plus the new volume term. A feasible continuation predictor supplies the initial guess. Inadmissible search trials are rejected; nodes are never projected back after crossing. An affine fallback, if needed, is a static initial-guess choice rather than a repair of a simulated trajectory.

A first protected compression-x solve at 20% found a stationary saddle: positive volume but negative free tangent stiffness. That intermediate run is preserved in `tomato_volume_protection_01` and was not accepted as stable. The final solver checks curvature at equilibrium, searches both signs of a true negative-curvature direction for lower energy, and re-minimizes. Three such branch escapes occurred in the full sweep. A numerical diagonal shift can be used only to obtain an energy-descent search direction; the physical energy and reported final tangent are not shifted.

This establishes a local stable static solution at the tested endpoints, not a unique equilibrium, a physically selected buckling trajectory, dynamic stability or proof against all possible folds. Branch choices in a quasistatic search must not be interpreted as robot motion. Physical force data and loading history will still matter.

## Results by path

| Piece | Loading | Highest tested level | Minimum J across path | Minimum checked scaled free eigenvalue | Result |
| --- | --- | --- | --- | --- | --- |
| remainder | compression_x | 30% | 0.2628 | 0.03367 | Pass |
| remainder | compression_y | 30% | 0.2539 | 0.02431 | Pass |
| remainder | compression_z | 30% | 0.2552 | 0.03434 | Pass |
| remainder | shear_xy_negative | 50% | 0.3404 | 0.05176 | Pass |
| remainder | shear_xy_positive | 50% | 0.3232 | 0.05171 | Pass |
| remainder | shear_xz_negative | 50% | 0.3453 | 0.05292 | Pass |
| remainder | shear_xz_positive | 50% | 0.3562 | 0.05266 | Pass |
| remainder | shear_yz_negative | 50% | 0.3360 | 0.04972 | Pass |
| remainder | shear_yz_positive | 50% | 0.3484 | 0.04940 | Pass |
| slice | compression_x | 30% | 0.2224 | 0.10916 | Pass |
| slice | compression_y | 30% | 0.3170 | 0.13252 | Pass |
| slice | compression_z | 30% | 0.3431 | 0.21831 | Pass |
| slice | shear_xy_negative | 50% | 0.2977 | 0.14157 | Pass |
| slice | shear_xy_positive | 50% | 0.2648 | 0.18632 | Pass |
| slice | shear_xz_negative | 50% | 0.2898 | 0.33337 | Pass |
| slice | shear_xz_positive | 50% | 0.2946 | 0.33117 | Pass |
| slice | shear_yz_negative | 50% | 0.4578 | 0.34875 | Pass |
| slice | shear_yz_positive | 50% | 0.4545 | 0.34889 | Pass |

All nonlinear residuals meet the unchanged 1e-6 requirement; the largest is 9.55e-08. No near-singular spring or inconclusive final tangent check occurred. Previous failures started at 5–10% compression and 10–30% shear; the unprotected model completed only 2 of 18 paths. Its old results remain intact under `tomato_large_strain_02`.

## Independent tests

Seven tests pass: energy/force/tangent finite differences in the active barrier region; unchanged rest energy/stiffness; exact-floor and inverted-trial rejection; rising energy toward the floor; rigid-motion covariance and force/torque balance; no volume term for homogeneous unit-J shear; and a known double-well stationary saddle that must be escaped rather than reported as a minimum. The initial floor test exposed floating-point ambiguity at exactly J=0.1; a conservative rejection margin resolves it without changing the acceptance thresholds.

The per-piece volume protection is separate from collision. It does not prevent a detached slice passing through another piece, supply blade contact, validate contact-buffer completeness or establish camera observations. Cut-face nonpenetration and native integration remain later gates.

## Resources and preservation

The full serial sweep took 51.35 seconds, with maximum process VmHWM 184.38 MiB. Each worker retained the shared controller lock, 512 MiB offline address-space cap, 45-second CPU limit, 55-second wall limit and single-threaded numerical libraries. These are offline numerical limits; the simulator's 10 GB available-RAM/4 GiB free-VRAM startup gate and runtime memory stops were not altered.

All 186 pre-existing non-cache files checked under `rl` and `docs/rl` retain their hashes. Added code is limited to `rl/tomato_volume_protection.py`, `rl/offline_tomato_volume_protection.py` and `rl/tests/test_tomato_volume_protection.py`. No controller, safeguard, frozen grasp criterion, prior model source or saved baseline run was edited. No Newton, Warp, Torch, Isaac, USD or simulator backend was imported or launched. No training occurred.

Evidence: `runs/offline/tomato_volume_protection_02/` contains all path summaries, iteration traces, final displacements, model parameters, source snapshots and preservation hashes. This is an inactive offline proposal; it was not exported as a simulator asset or wired into a controller.

Next work should assess protection-parameter/mesh sensitivity and calibrate compression behaviour, then design the native force/contact integration. The offline pass does not authorize simulator launch or full training.
