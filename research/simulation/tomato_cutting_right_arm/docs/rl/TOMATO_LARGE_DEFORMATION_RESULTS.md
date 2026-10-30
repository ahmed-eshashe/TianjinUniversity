# Larger tomato compression and shear results

Date: 19 October 2026. **The current spring model fails the large-deformation geometry screen.** Small-strain success did not establish adequate finite-deformation behaviour. Volume-cell inversion occurs at the first tested 5% compression level in all three remainder directions and in slice x compression, and at 10% in slice y/z. Shear produces local inversion or near-collapse in several directions.

These are localized material-mapping failures, not observed whole-tomato collapse or a simulator crash. All final solves meet the force-residual criterion, and the least free tangent stiffness eigenvalue is positive at every checked endpoint. A locally stable elastic energy minimum can still have an invalid material mapping in this spring network.

## Test scope

Use the exact saved finite-length spring coefficients, nodal coordinates, mass assignment and volume diagnostic cells from `tomato_surface_mechanics_04` and `tomato_surfaces_03`. The damage law, interface parameters, density and spring constants are unchanged. Each piece is tested independently without cross-cut interface springs, damage evolution, gravity, board or contact.

All surface nodes follow prescribed deformation; interior nodes minimize the actual nonlinear finite-length spring energy. Compression levels planned are 1%, 2%, 5%, 10%, 20%, 30%. Simple shear levels are 2%, 5%, 10%, 20%, 30%, 50%, in both signs of xy/xz/yz. Shear percentages are displacement gradients, not shear angles or compressive strain. This is an outer-boundary static coupon, not physical platen contact.

Paths stop on their first flagged state. Of 18 paths, 2 reach their full requested range; 71 load stages were evaluated, 55 passed. Higher levels after a stopped path remain untested. Reported failure levels bracket the onset with the previous tested passing level; they are not exact critical strains.

## Per-path findings

| Piece | Loading | Largest tested passing level | First flagged level | Reason |
| --- | --- | --- | --- | --- |
| remainder | compression_x | 2% | 5.0% | diagnostic_cell_inversion |
| remainder | compression_y | 2% | 5.0% | diagnostic_cell_inversion |
| remainder | compression_z | 2% | 5.0% | diagnostic_cell_inversion |
| remainder | shear_xy_negative | 10% | 20.0% | diagnostic_cell_inversion |
| remainder | shear_xy_positive | 10% | 20.0% | diagnostic_cell_inversion |
| remainder | shear_xz_negative | 5% | 10.0% | local_near_collapse |
| remainder | shear_xz_positive | 10% | 20.0% | diagnostic_cell_inversion |
| remainder | shear_yz_negative | 5% | 10.0% | diagnostic_cell_inversion |
| remainder | shear_yz_positive | 5% | 10.0% | diagnostic_cell_inversion |
| slice | compression_x | 2% | 5.0% | diagnostic_cell_inversion |
| slice | compression_y | 5% | 10.0% | diagnostic_cell_inversion |
| slice | compression_z | 5% | 10.0% | diagnostic_cell_inversion |
| slice | shear_xy_negative | 20% | 30.0% | diagnostic_cell_inversion |
| slice | shear_xy_positive | 20% | 30.0% | diagnostic_cell_inversion |
| slice | shear_xz_negative | 10% | 20.0% | diagnostic_cell_inversion |
| slice | shear_xz_positive | 10% | 20.0% | diagnostic_cell_inversion |
| slice | shear_yz_negative | 50% | none | None at requested maximum |
| slice | shear_yz_positive | 50% | none | None at requested maximum |

For example, remainder compression passes at 2% and fails at 5%; slice x compression likewise fails between those tested levels. Slice y/z compression first fails between 5% and 10%. One remainder shear path reaches positive but very small local volume at 10%, triggering the predeclared near-collapse screen rather than an inversion.

## Collapse and instability checks

Before the sweep, the runner defined inversion as any nonpositive signed diagnostic-cell volume, local near-collapse as a minimum volume ratio below 0.1, and near-singular springs as length below 10% of rest length. Nonlinear force residual must be below 1e-6 relative to boundary reaction. A negative free tangent eigenvalue below −1e-6 would indicate a local elastic instability; an inconclusive eigensolve or a near-zero mode is reported separately.

The initial optimizer sometimes stopped on relative energy reduction while residuals were a few parts per million. Those runs are preserved under `tomato_large_strain_01` and were not labelled physical failures. A Newton polish with energy-descent line search resolved the remaining forces without changing the model, adding volume barriers, relaxing tolerances or regularizing material stiffness. Final maximum force residual is 1.41e-11.

The minimum checked preconditioned free tangent eigenvalue is 0.051700; no negative or near-zero free mode was detected at the evaluated states. This is only an endpoint local static tangent check. It does not establish global uniqueness, absence of instabilities between tested levels, dynamic stability, or a safe integration timestep.

There are 15 inversion flags and 1 near-collapse flags across the stopped paths. Diagnostic tetrahedra are fixed material-volume markers, not FEM force elements. Their inversion signals a fold in that material interpolation; it does not by itself demonstrate a visible exterior self-intersection. Since the boundary is prescribed, a nearly expected total volume can also hide localized inversion. Total volume alone is therefore an inadequate acceptance check.

## Cell quality audit

The independent `inversion_quality_audit.json` examines saved final displacements, initial cell quality and the original volume represented by inverted cells. The maximum inverted reference-volume fraction is 0.02680%, so the observed folds are highly localized. Some initial integration cells are thin. However, failed sets also include cells with mean-ratio quality above 0.1, with inverted-cell quality as high as about 0.426; the evidence is not limited to numerical zero-volume cells.

The quality metric is 12 times (3V)^(2/3) divided by the sum of the six squared edge lengths, equal to one for a regular tetrahedron. This audit keeps every flagged fold; it does not remove inconvenient cells or loosen the screen. Better volume markers and surface coupling remain useful follow-up investigations, but cannot be assumed to fix the mechanics without retesting.

## Interpretation and next work

The spring energy has no explicit volume-preservation or inversion-prevention term. The failures are consistent with that omission and/or inadequate local surface-to-interior coupling; this test does not uniquely determine the cause. The prescribed boundary remains an orientation-preserving affine transform, so the detected problem is in the interior mapping rather than an imposed exterior crossing.

Do not proceed directly to cutting or RL with a claim that the large-strain material is validated. Next compare a local volume/inversion-control term and a revised surface-coupling discretization in small offline coupons. Distinguish bulk mechanical protection from cut-face nonpenetration: a volume term alone will not stop one released piece passing through another. A coarse FEM comparison remains an option if the reduced model cannot satisfy these gates.

No remedy was implemented in this task; the failed configurations, displacement arrays and parameters are preserved so a future refinement has an honest baseline. The two slice yz shear paths that reach 50% do not rescue the other failed paths or establish safe cutting.

## Tests and resources

Six independent tests pass: scalar force/energy and compressed-spring negative curvature, finite-difference gradient and Hessian, rigid-motion covariance/force balance, known signed-volume inversion, prescribed-DOF preservation in the equilibrium polish, and rejection of zero-length springs. The negative-curvature fixture demonstrates the tangent check can detect an instability, rather than merely always returning a positive result.

The final 18 paths ran serially in 15.93 s total, with maximum process VmHWM 191.73 MiB. Each worker retained a shared lock, 512 MiB address-space limit, 45-second CPU and 55-second wall limits, with single-threaded numerical libraries. No Newton, Warp, Torch, Isaac, USD or simulator module was imported. No time integration, simulator launch or training occurred.

All 182 pre-existing non-cache files checked under `rl` and `docs/rl` retain their hashes, including the runtime memory safeguard, controller, mass/stiffness proposal, damage law and frozen grasp criteria. Added files are `rl/tomato_nonlinear_checks.py`, `rl/offline_tomato_large_strain.py`, `rl/tests/test_tomato_nonlinear_checks.py`, this report and offline run evidence. Evidence and matching source snapshots are in `runs/offline/tomato_large_strain_02/`.
