# Slice compression mesh sensitivity: offline refinement

The refined slice family meets the unchanged **10% energy/reaction comparison target** at every tested load level and comparison direction. Maximum thickness-compression differences between the refined 4 mm and 5 mm variants are **5.74% in energy density and 6.91% in normalized reaction**, previously 9.58% and 10.52% for the original variants. The 4.5 and 6 mm comparisons also pass.

These labels describe the original bulk lattice spacing. Slice interior sampling is now at half that spacing: 2, 2.25, 2.5 and 3 mm respectively. The same construction rule is applied to every variant, including the **refined 5 mm comparison reference**. This is not agreement with an unchanged old 5 mm response. The refined reference itself changes by up to 22.97% in energy density and 31.13% in normalized reaction relative to the prior model. Material coefficients and acceptance limits were not rescaled to obtain agreement.

No simulator, training, dependency installation or controller work occurred. Existing memory safeguards, grasp criteria and physical assets remain unchanged. This is an inactive offline proposal.

## Investigation and rejected trial

The 10 mm slice initially contains only two free interior material layers through its thickness at each bulk spacing; the 4 mm layout additionally has a fixed pole node. Layer positions, populations and surface attachment geometry vary with spacing. The 0.2% compression probes already show non-monotonic apparent stiffness: approximately 26.94, 27.51, 29.10 and 26.49 kPa at 4, 4.5, 5 and 6 mm. Corresponding relaxed-to-affine energy ratios range from 0.736 to 0.808. Thus the original discrepancy exists before the larger nonlinear stages; an optimization failure is not required to explain it.

The original graph combines a coarse material lattice with dense surface samples, a sparse nearest-anchor tether rule and surface edges. The positive weight correction matches the piece's aggregate affine fourth moments, but that alone does not enforce local affine equilibrium or resolve the interior displacement field. The observations implicate interior resolution and attachment topology; they do not isolate a unique cause or prove continuum consistency.

First, connect every edge of the existing slice volume cells while retaining all existing bonds. This graph-only trial passes preparation and static compression but makes 4-versus-5 mm disagreement worse: 14.77% energy and 14.33% reaction. The 4.5 mm reaction difference is also above target at 10.84%. Its evidence is retained under `meshes_cell_edges` and `cases_cell_edges`; this variant is not the recommendation.

## Accepted construction rule

`rl/tomato_slice_topology.py` adds half-spacing lattice samples strictly inside the existing closed slice. New points retain at least 2% of the original spacing in clearance from the faceted boundary, using the existing geometry-resolution scale rather than a load-dependent criterion. Existing material and surface nodes keep their coordinates. New points do not lie on or alter the cut face.

Regenerate the slice volume tessellation and add its missing same-side cell-edge springs, keeping the original bonds intact. Every cell edge is then mechanically connected. Existing positive isotropic spring assignment, volume lumping and common density rules determine masses and stiffnesses; there is no per-mesh force fitting, material multiplier or extra affine constraint. This remains a central-force spring graph with the existing local volume barrier, not tetrahedral FEM.

Only the slice gains interior nodes and edges. Its cut triangles, visual/contact boundary, original interface bonds and patch IDs, fixture, zero cut-face gap and side identities remain unchanged. Every previously existing bond remains unchanged. Every prescribed boundary node remains the same; all new samples are free interior nodes. Provisional slice masses are redistributed by the existing volume-lumping recipe while preserving piece/total mass. A direct regression confirms that the remainder's standalone mass/stiffness assignment is exactly unchanged.

| Original bulk spacing | Actual new slice sampling | New slice interior nodes | Total proposal nodes | Total proposal bonds | Whole preparation |
| --- | --- | ---: | ---: | ---: | --- |
| 4 mm | 2 mm | 648 | 5,318 | 48,754 | Pass |
| 4.5 mm | 2.25 mm | 452 | 4,582 | 40,521 | Pass |
| 5 mm | 2.5 mm | 297 | 4,032 | 34,399 | Pass |
| 6 mm | 3 mm | 167 | 3,512 | 28,710 | Pass |

The 4 mm slice now has 1,598 total nodes, versus 950 before refinement. The other slice totals are 1,384, 1,195 and 1,037. All existing positive-mass, geometry, inertia, small-strain and volume/moment gates pass for both pieces. The original 7,000-node/50,000-bond caps are unchanged; the 4 mm design has limited remaining bond headroom.

## Matched mesh comparison and holdouts

Compression x/y/z uses strains 1, 2, 5, 10, 20 and 30%; negative xz shear uses 2, 5, 10, 20, 30 and 50%. Compare matched endpoints at 4, 4.5 and 6 mm against the refined 5 mm variant. Test every level, not just the endpoints with the smallest difference.

| Comparison with refined 5 mm | Compression x energy difference | Compression x reaction difference | Largest energy difference over other tested directions | Largest reaction difference over other tested directions |
| --- | ---: | ---: | ---: | ---: |
| Refined 4 mm | 5.74% | 6.91% | 3.64% | 3.64% |
| Refined 4.5 mm | 4.00% | 4.52% | 2.09% | 2.09% |
| Refined 6 mm | 1.77% | 1.76% | 2.71% | 3.96% |

The other tested directions are y/z compression and negative xz shear. All 12 direction/mesh comparisons meet the original 10% target for both metrics. The 4 mm slice additionally completes the remaining shear directions/signs, giving all nine deformation paths on that variant. In total, **21 accepted paths / 126 checked endpoints** pass the unchanged nonlinear static screens.

Across this accepted set: minimum local J=0.21619, maximum force residual=8.63e-8, and minimum scaled free-tangent eigenvalue=0.01519. There are no checked inversions, near-collapse endpoints, near-singular springs or failed tangent screens. The force residual threshold remains 1e-6 and independent near-collapse threshold remains J>=0.1. The shared spring/volume energy, gradient, tangent and optimizer code were not edited.

Energy and strain-conjugate reaction are normalized by each piece's actual volume. Reaction is an energy derivative with respect to dimensionless strain, not a physical platen force in newtons. Every comparison uses the same synthetic E=30 kPa, Poisson ratio 0.25, barrier modulus 10 kPa, activation J=0.5 and strict floor J=0.1. The existing feasible linear initial guess and continuation are used, with final nonlinear equilibrium and stability checks retained.

## Verification, resources and evidence

Evidence root: `runs/offline/tomato_slice_refinement_01/`.

- `baseline_diagnostics.json`: original layer populations and small-strain responses.
- `experiment_manifest.json`, `cell_edges_rejected_comparison.json`: initial hypothesis, unchanged target and rejected graph-only comparison.
- `meshes_half_spacing`: all four accepted geometry/mass/stiffness proposals; `cases_half_spacing`: complete traces and final displacements.
- `summary.json`: all accepted path resources and detailed matched comparisons; `refinement_response_changes.json`: changes from the original model, including the changed reference.
- `geometry_reaudit.json`: independent final geometry checks and accurate separate counts for added surface/interior nodes. Preparation outputs made before that reporting correction retain the old `added_surface_nodes` field, which counted all additions; it is not used to infer boundary-node counts.
- **45 regression tests pass**: five new tests cover a known tetrahedron, unique/idempotent edges, unchanged old coordinates/bonds/cut/fixture/fixed nodes, preserved mass, interior clearance, complete cell-edge connectivity, small-strain response and unchanged remainder assignments. The 40 existing surface, mechanics and barrier regressions also pass. Test logs and summaries are retained.
- `baseline_hashes.json`, `preservation.json`, `source_before`, `source_after`: source provenance and frozen-file checks. All historical evidence directories remain intact.

Accepted path workers ran serially for 49.25 s total, with maximum peak RSS 157.48 MiB. Accepted preparations took 29.89 s total; maximum peak RSS was 252.35 MiB. These figures exclude rejected trials and tests. Numerical workers retain the shared controller lock, one BLAS thread, 512 MiB address-space, 45 s CPU and 55 s wall caps. The simulator's separate startup reserve and runtime memory safeguard remain unchanged. Forbidden simulator modules are checked after numerical runs/tests.

Reproduce a fresh accepted offline proposal with the existing local environment:

```text
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 .venv-native/bin/python rl/offline_tomato_sensitivity_mesh.py --spacing-mm 4 --refine-near-boundary --slice-half-spacing --output runs/offline/fresh_slice_proposal
```

Use a fresh output directory; keep existing evidence. The feature is an explicit offline option and does not activate a runtime model.

## Interpretation and next boundary

The requested sampled comparison target is met, with a genuine increase in free interior resolution and no relaxed criteria. Agreement is better, but the curves are not yet a demonstrated asymptotic convergence sequence: spacing changes layer alignment and attachment topology, and the refined reference response changed substantially. Additional independent resolution checks and physical calibration remain necessary before treating reaction magnitudes as predictive.

All tests prescribe the full outer/cut surface and solve static interior equilibrium. They do not validate time integration, contact-driven loading, physical tomato properties or robotic cutting. Interface damage resolution was not refined and no damage evolves in these compression tests. Preserve the previous thin-cell warning for future contact/dynamics work. Keep the corrected remainder and safeguards as they are; do not launch the simulator or training on the strength of this offline result alone.
