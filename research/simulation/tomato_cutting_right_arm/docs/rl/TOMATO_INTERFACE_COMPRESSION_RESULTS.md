# Offline interface compression correction

The supported normal-contact prototype now uses zero-thickness cut-face cohesion rather than bilateral springs between interior nodes. Compressive load belongs to unilateral cut-face contact; the cohesive potential supplies tensile opening and elastic shear resistance. This is an explicit interface-model revision, not a material calibration or a native Newton implementation.

This report supersedes only the interface compression finding in `TOMATO_COUPLED_CONTACT_RESULTS.md`. Earlier run evidence is preserved in `runs/offline/tomato_coupled_01`; the new evidence is in `runs/offline/tomato_interface_compression_01`.

## Cause and correction

The old 403 finite-length interface bonds connected interior nodes across the future cut. Those bonds shortened under bulk compression even when the two cut surfaces were closed. At +0.05 mm guided reclosure, the intact interface supplied 48.56% of the compressive load in parallel with contact. The total actuator force was 7.5% above the broken case; it was not doubled.

The correction uses the 257 coincident but independently indexed cut-face vertex pairs. For each original damage patch:

`U_patch = (1-D)/2 * sum_i w_i [Kn * max(g_n,i, 0)^2 + g_t,i^T Kt g_t,i]`

- `g` is the actual relative displacement of matched face vertices in the fixed material frame; it no longer includes bulk shortening between interior nodes.
- The normal axis is x. Negative normal gap has zero cohesive normal force, normal energy and normal tangent; penetration remains prohibited by the separate contact solver. At zero opening the force is continuous and the solver uses the tensile-side generalized tangent.
- `Kn = 4e7 Pa/m * patch area`, preserving the original patch's small-displacement opening stiffness. `Kt` is the original undamaged axial bundle's y/z small-strain tangent block, including its y/z coupling. Normal/shear coupling is deliberately removed in the new separable potential. The old finite-displacement oblique-bundle law is not claimed to be preserved.
- Each patch distributes its one stiffness/energy budget over the eight closest face vertices. Weights are proportional to lumped face area divided by `(distance^2 + (5 mm)^2)` and normalized per patch. Overlapping supports add forces and tangents. The 47 eight-vertex supports use 231 unique face pairs; all 257 pairs remain registered for contact. The endpoint field `active_surface_cohesive_pairs` counts the enabled registry, not the number of nonzero quadrature supports. This is a provisional transfer of the original patch registry, not a calibrated spatial material map; no mesh-independence claim is made for it.
- One common patch damage variable multiplies the entire patch potential. Opening/shear coupon damage uses `q = sqrt(2 U_undamaged / Kn)` and the existing bilinear onset/failure rule. Peak traction remains 40 kPa and fracture energy 80 J/m², both synthetic and uncalibrated. Each patch retains one area/energy budget.
- Damage eligibility remains an explicitly supplied coupon input. Compression alone does not drive damage. Compression-plus-shear fracture remains rejected as unsupported. No damping or inertia is present in this quasistatic test.
- The same-piece springs, local volume protection, fixture, mesh, boundary guides, solver tolerances and acceptance thresholds are unchanged. Fully broken cohesion is exactly zero without residual stiffness.

The new potential and its nodal forces/tangents are implemented in `rl/tomato_surface_cohesion.py`, composed with the existing protected bulk model in `rl/tomato_coupled_contact.py`. Test assertions were updated to distinguish surface quadrature pairs from the removed interior interface springs. Both audit tools accept a separate run directory so old evidence is retained.

## Validation

**All 68 contact checkpoints, 60 targeted tests, 235 patch/mode fracture-energy cases, and all 68 weak-contact stability checks pass.**

The same six sequences were rerun from fresh states/source hashes: coarse/fine indentation (7/13 checkpoints), coarse/fine broken-interface reclosure (13/25), and intact/half-damaged reclosure (5 each). Indentation reaches 0.05 mm with D=0. Broken reclosure traverses an opening of 0.10 mm through contact to +0.05 mm drive and back. Intact/partial reclosure uses 0 → +0.025 → +0.05 → +0.025 → 0 mm.

At +0.05 mm reclosure:

| Frozen D | Actuator force (N) | Contact force (N) | Cohesive force on slice x (N) | Cohesive energy (J) |
|---|---:|---:|---:|---:|
| 0 | 0.017247346977 | 0.017247346978 | -0.0 | 0.0 |
| 0.5 | 0.017247346977 | 0.017247346978 | -0.0 | 0.0 |
| 1 | 0.017247346977 | 0.017247346978 | -0.0 | 0.0 |

The old intact actuator force was 0.018541834472 N. Its 48.56% compressive cohesive load fraction is now zero. Intact, partial and broken responses agree to numerical precision, without changing the bulk stiffness or weakening any acceptance threshold.

| Check | Result |
|---|---:|
| Maximum normalized force residual | 7.287e-08 (limit 1e-6) |
| Minimum endpoint/swept local volume ratio J | 0.756597 (floor 0.1) |
| Maximum contact penetration within numerical tolerance | 2.247e-14 m (limit 1e-9 m) |
| Proper opposite-surface intersections at checked midpoint/endpoints | 0 |
| Minimum surface area / rest area | 0.997203 |
| Minimum active-contact normalized tangent eigenvalue | 0.0009266349 |
| Minimum weak-contact-opening audit eigenvalue | 0.0001589973 (limit 1e-6) |
| Maximum force / moment balance fractions | 4.616e-08 / 2.304e-08 (limit 0.01) |
| Indentation loading-work change on halving step | 0.136084% |
| Broken reclosure loading-work change on halving step | 0.010903% |
| Maximum matched-force change on halving step | 2.234e-10 relative |
| Peak contact worker RSS | 167.52 MiB |
| Total contact-worker runtime | 219.10 s |
| Longest contact endpoint | 5.00 s |

All endpoint work balances retain the original 1% energy tolerance plus 1e-12 J absolute allowance. The weak-contact audit only ties contacts with multiplier above 1e-9 N; at zero opening the tensile-side quadratic is a conservative extension for feasible opening directions in these fixed-normal coupons. It is not an arbitrary-rotation stability certificate.

The 235 fracture checks are all 47 patches in opening, ±y shear and ±z shear, each sampled at 2,400 increments to complete failure. Maximum traction-work error is 5.995e-13%; maximum fixed-geometry damage-loss quadrature error is 0.115603%, below the unchanged 1% gate. Complete damage leaves exactly zero cohesive force/energy. These are controlled, uniform patch-separation histories, not blade-triggered cuts or validation of spatially nonuniform patch damage.

The 60 tests include 9 revised-interface tests and 51 coupled-contact, volume-protection, local-contact and original bond regressions. They explicitly check closed-face bulk compression, zero compressive cohesion, retained tensile stiffness, partial damage, shear under compression, energy/force/tangent finite differences, zero-opening continuity, damage eligibility/no healing and broken-interface zero adhesion. Compression-plus-shear damage is rejected rather than silently assigned a fracture response.


## Scope and next gate

These checks remain full-node, nonlinear **offline quasistatic coupons**, with fixed y/z cut-face guides, matched cut-face triangles, frictionless normal contact, a finite planar blade-face surrogate, and driven slice back-cap supports during reclosure. They do not establish arbitrary 3D sliding/rotation, a real knife edge, unrestricted slice motion, dynamic stability, calibrated tomato material behaviour or a successful full cut.

The 47 patch opening/shear damage checks exercise the revised surface potential independently. Coupled indentation/reclosure damage is still **frozen** at D=0, 0.5 or 1: no evolving damage or blade-triggered fracture is integrated into these tests. The source still needs a native implementation and validation before use in Newton/Isaac.

The next bounded gate is an offline blade-eligibility and damage-evolution coupling design/check, with explicit fracture work accounting. A full-cut claim must additionally show blade-dependent damage, independent post-break piece motion and cut-face nonpenetration. Passing the current compression tests is not permission to skip those checks or launch simulation/training.

## Safeguards and reproduction

Each numerical worker uses the existing shared control lock and one BLAS thread, with a 512 MiB address-space cap, 45 s CPU cap and 55 s wall cap. Workers check that simulator/training modules are absent. All runs are serial. The simulator startup guard and the frozen grasp criteria are hash-checked against the pre-edit baseline; neither is changed.

The run directory contains `manifest.json`, the coordinator/test harness, individual endpoint states and logs, per-mode fracture-energy records, force/work/geometry summary, a separate weak-contact stability audit, source/input hashes and preservation evidence. The endpoint runner remains `rl/offline_tomato_coupled.py`; use a fresh output directory for each endpoint and `--previous` for continuation. Prior checkpoints with different solver hashes are intentionally rejected.

The fracture runner is `rl/offline_tomato_interface_energy.py` with one of `opening`, `shear_y`, `shear_y_negative`, `shear_z`, `shear_z_negative` and an output JSON path. The audit tools take `--run-directory runs/offline/tomato_interface_compression_01`. Use `.venv-native/bin/python` and `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`. Do not rerun the saved coordinator into the existing evidence directory; create a new run directory first.
