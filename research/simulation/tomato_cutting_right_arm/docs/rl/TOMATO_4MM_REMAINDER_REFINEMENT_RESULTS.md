# 4 mm remainder inversion diagnosis and correction

The corrected **whole 4 mm proposal now passes** the original geometry and small-strain preparation gates. Both pieces also complete all 18 protected static compression/shear paths (108 endpoints). The remainder's selected normalized reaction curves differ from the 5 mm reference by at most 1.74%. Slice thickness compression still differs by 10.52%, above the unchanged 10% comparison target; this study therefore does not establish complete mesh convergence.

Everything remains offline and inactive. No simulator, GPU runtime, training, installation or controller change was performed. Frozen grasp criteria, runtime memory reserves, watchdog and acceptance thresholds remain unchanged.

## Diagnosis

Reproduce the old remainder failure from the prior conforming 4 mm design and its saved mass/stiffness assignments. Solve the same unprotected 0.2% linear Dirichlet problems and inspect each cell's signed volume, altitude, node positions, nonaffine displacement and spring edges.

Each compression direction inverted eight cells. The failing cells lie beside four free material nodes, IDs 1766, 1774, 1820 and 1828, just below exterior facets. Their relevant altitudes are only about 4.789 micrometres across cells whose longest edge is about 3.18 mm. Their nonaffine displacements are several micrometres, enough to cross those facets even under a small imposed strain. Some failed cells already contain all six cell-edge springs: missing springs alone cannot explain the defect. Linear force residuals were small, so convergence of the linear equations did not imply valid geometry.

The measured before/after unprotected remainder results are:

| 0.2% compression | Before: minimum J | After: minimum J | Inverted cells before → after |
| --- | ---: | ---: | ---: |
| x | -0.77197 | 0.66166 | 8 → 0 |
| y | -0.12566 | 0.64060 | 8 → 0 |
| z | -0.73605 | 0.45466 | 8 → 0 |

J is current signed cell volume divided by its positive rest volume. Refinement regenerates the tessellation; no deformation-dependent cell filtering was used, and every regenerated cell is checked under the original rules. Both pieces pass all nine original small-strain modes, including both shear signs, and retain positive mass, acceptable inertia and the same volume/moment/isotropy gates.

## Geometry and attachment correction

The optional offline construction rule `--refine-near-boundary` samples the **existing analytic ellipsoid** above original material nodes whose exterior-facet clearance is below 2% of lattice spacing. Selection uses rest geometry only, without consulting loads, displacement results or success flags. It adds 12 exterior samples to the 4 mm remainder and none to the slice, then rebuilds the convex exterior while keeping the existing cut triangles exactly.

Every pre-existing node retains its coordinates. Original material bonds and their IDs/rest lengths, interface patches, cut-side identities, zero rest gap, fixture IDs and total mass remain intact. The four previously problematic material nodes remain free interior nodes; they are not clamped, projected or tied to the prescribed boundary. The added nodes lie on the analytic ellipsoid and do not create cross-cut bonds. Surface mass is accounted for before the usual volume-lumping assignment.

New samples use the same four-anchor directional-rank test as the base surface generator, with anchors at least one quarter of a lattice spacing away. An initial refinement trial connected samples to extremely close material anchors; it passed preparation but made the nonlinear solve expensive enough to hit the resource limit. The resolved-anchor rule avoids those short, buckling-prone new tethers. It changes proposed attachment topology, not material coefficients. Both trial and final evidence are retained.

This is **local exterior refinement, not a general quality tetrahedral mesher**. The smallest rest cell altitude anywhere in the remainder remains approximately 1.804 micrometres. Passing the prescribed-surface static checks does not establish that these thin cells are suitable for unconstrained dynamic contact. That limitation remains important before native integration.

## Numerical corrections and bounded trials

The refined geometry exposed cancellation in the isotropic spring-weight fitter's descent check. Near convergence, subtraction of two order-one objective values could falsely reject a small decrease. The check now evaluates the mathematically equivalent difference using `expm1` and the directional derivative. Positive weights, the isotropic fourth-moment target, residual tolerances and all mechanical acceptance checks are unchanged. The refined-remainder regression exercises this case, and the existing missing-direction rejection still passes.

Some preliminary nonlinear shear workers ended under the unchanged resource caps before producing a checked endpoint. They are inconclusive, not accepted physics results. An explicit `--linear-initial-guess` option now initializes the first nonlinear endpoint from linear Dirichlet equilibrium **only if that guess respects the same volume floor**; otherwise it retains the original guess. Subsequent endpoints use the existing continuation predictor. Final force residual, cell-volume, spring-length and exact free-tangent checks are unchanged; no linear solution is substituted for nonlinear equilibrium.

The three completed 4 mm remainder compression paths retain their original affine initial guesses. All final shear paths and the new comparison runs use the feasible linear starting option. These are static initial guesses, not imposed trajectories or altered physical constraints. Different local equilibria remain possible in this nonconvex model; no uniqueness claim is made. No isolated-piece override was used for the final corrected 4 mm proposal: its whole-mesh preparation passes.

## Larger deformation and mesh comparison

At 4 mm, run compression x/y/z through 30% and shear xy/xz/yz in both signs through 50%, on both pieces. All 18 paths / 108 endpoints pass. Compression levels are 1, 2, 5, 10, 20 and 30%; shear levels are 2, 5, 10, 20, 30 and 50%.

Regenerate 4.5, 5 and 6 mm proposals with the same local-refinement and resolved-anchor rules, then rerun x compression and negative xz shear for both pieces. All their preparation gates and 12 comparison paths pass. There are **30 distinct completed paths / 180 checked endpoints** in the final accepted evidence set. Across that set, minimum J is 0.16759, maximum force residual is 9.22e-8 and minimum scaled free-tangent eigenvalue is 0.02133.

Keep the synthetic material and protection settings fixed: E=30 kPa, Poisson ratio 0.25, barrier modulus 10 kPa, activation J=0.5, strict floor J=0.1. The independent near-collapse threshold remains J>=0.1. No material parameters were fitted to obtain these results.

| Bulk spacing | Original bulk nodes | Total nodes | Total bonds | Added local samples | Whole-mesh preparation |
| --- | ---: | ---: | ---: | ---: | --- |
| 4 mm | 1,903 | 4,670 | 40,590 | 12 | Pass |
| 4.5 mm | 1,350 | 4,130 | 34,275 | 24 | Pass |
| 5 mm | 979 | 3,735 | 29,790 | 0 | Pass |
| 6 mm | 573 | 3,345 | 25,302 | 16 | Pass |

All retain 64 angular segments and the existing meridional resolution, plus the disclosed adaptive samples. The 5 mm geometry is unchanged. Adaptive samples change the discretized exterior/topology of the other meshes, including the 4.5 mm slice; this is not a comparison of identical exterior node sets. The volume-lumping and positive isotropic stiffness recipe is the same at every spacing. All stay inside the original 7,000-node/50,000-bond limits.

Maximum absolute differences from 5 mm across matched load levels:

| Mesh | Piece/path | Energy-density difference | Reaction-density difference | Existing 10% target |
| --- | --- | ---: | ---: | --- |
| 4 mm | Slice compression x | 9.58% | 10.52% | Not met |
| 4 mm | Slice shear xz negative | 1.44% | 1.44% | Met |
| 4 mm | Remainder compression x | 1.76% | 1.74% | Met |
| 4 mm | Remainder shear xz negative | 1.04% | 1.02% | Met |
| 4.5 mm | Slice compression x | 6.88% | 7.79% | Met |
| 4.5 mm | Slice shear xz negative | 1.20% | 1.62% | Met |
| 4.5 mm | Remainder compression x | 0.88% | 0.90% | Met |
| 4.5 mm | Remainder shear xz negative | 0.35% | 0.35% | Met |
| 6 mm | Slice compression x | 10.82% | 12.58% | Not met |
| 6 mm | Slice shear xz negative | 1.38% | 1.38% | Met |
| 6 mm | Remainder compression x | 0.40% | 1.41% | Met |
| 6 mm | Remainder shear xz negative | 0.27% | 0.31% | Met |

Both quantities are divided by each piece's actual volume. Reaction is the energy derivative with respect to dimensionless imposed strain, not a platen force in newtons. Static stability and mesh independence remain separate gates. In particular, this correction resolves the tested remainder inversions without establishing convergence of compression through the 10 mm slice thickness.

## Evidence, verification and safeguards

Evidence root: `runs/offline/tomato_4mm_remainder_01/`.

- `diagnostic_before/summary.json` and `diagnostic_after/summary.json`: cell positions, altitudes, edges, nonaffine displacements and inversion counts.
- `meshes/bulk4_refined_03/`: accepted 4 mm design, mass/stiffness assignment and passing preparation; `meshes/bulk4p5`, `bulk5`, `bulk6`: new comparison preparations.
- `summary.json`: explicit accepted case paths, matched curve comparisons and resource totals. Only the three completed compression summaries from `cases_final` and the complete summaries in `cases_linear` enter this set.
- `regression_tests.txt` and `regression_summary.json`: **40 tests passed**, including preservation, free-node identity, cut geometry, no short refinement tether, idempotent refinement, original small-strain checks, isotropy/matrix references, and volume-energy/force/tangent tests. No forbidden simulator modules were imported.
- `source_before`, `source_after`, `baseline_hashes.json` and `preservation.json`: source provenance and safeguard checks. Prior evidence remains unchanged.

Accepted path workers took 273.69 s total, serially; maximum completed single-path runtime was 31.55 s and peak RSS was 237.51 MiB. Every numerical worker retained the common lock, one BLAS thread, 512 MiB address-space cap, 45 s CPU and 55 s wall caps. Preliminary limited/aborted trials are retained and excluded from completed-path totals; those totals are not total project wall time. The simulator startup reserve, runtime monitor and frozen grasp criteria were not edited.

Example offline preparation command, using the existing local environment and one BLAS thread:

```text
.venv-native/bin/python rl/offline_tomato_sensitivity_mesh.py --spacing-mm 4 --refine-near-boundary --output <fresh-output-directory>
```

Paths use `rl/offline_tomato_sensitivity_path.py` with that mesh directory and optionally `--linear-initial-guess`. The environment variables `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1` and `PYTHONDONTWRITEBYTECODE=1` were set for every numerical invocation. Do not overwrite existing evidence directories.

## Recommendation

Use this corrected 4 mm proposal for further **offline** studies, retaining 5 mm as the existing reference. Before selecting a final mesh or calibrating material parameters, investigate slice thickness-direction discretization and attachment sensitivity. Preserve the remaining thin-cell warning when designing future dynamic/contact tests. This work does not validate native Newton integration, blade-dependent damage under contact, self-contact after separation, real material response or robotic slicing, and it does not authorize simulator launch or training.
