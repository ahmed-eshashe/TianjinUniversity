# Surface mass and stiffness refinement results

Date: 19 October 2026. The inactive surface proposal now has volume-based nodal masses and positive directional spring stiffnesses. **All 18 small-strain compression/shear checks and nine independent numerical tests pass.** No simulator backend, time integration, contact solver or training was run. This remains an uncalibrated synthetic model.

## Mass refinement

The earlier fixed 25% surface-mass allocation is replaced with positive volume lumping. Each closed piece is tetrahedralized only to integrate its volume and nodal support: each integration cell contributes one quarter of its volume to each of its four nodes. These are quadrature/diagnostic cells, not FEM force elements. The model remains a spring model.

An independent outward-surface fan integral confirms the tessellated volumes and centroids to numerical precision. The total previous tomato mass is retained, with one common synthetic density of 1003.446 kg/m³ throughout both pieces. **Piece masses are recomputed from geometry**, rather than preserving the original coarse cap's approximate mass and creating different artificial densities in cap and remainder. The revised cap mass is 7.737 g versus the previous 7.262 g; total mass is unchanged. All node masses are positive.

| Piece | Revised mass | Volume-derived surface mass share | Lumped inertia error versus volume integral | Conservative undamped explicit step limit |
| --- | --- | --- | --- | --- |
| slice | 7.737 g | 56.82% | 3.91% | 31.86 microseconds |
| remainder | 113.934 g | 16.53% | 1.97% | 30.99 microseconds |

The large surface share on the thin cap comes from the actual locations of its nodes and tetrahedral volume partition, not an explicit skin mass. It must not be interpreted as biological skin density. Lumped inertia remains a quadrature approximation; the measured errors are below the preselected 5% check but are not a mesh-convergence study.

## Spring stiffness proposal

All same-side bulk, surface-tether and surface-edge springs receive positive stiffnesses. Start from volume support per incident bond and finite rest length, then make the smallest relative-entropy direction-weight correction needed to match an isotropic affine fourth-moment target. No spring is zeroed to hide an unsupported mode. Multipliers remain finite and positive; correction convergence and min/max stiffnesses are recorded per piece.

The engineering reference is **E=30 kPa and Poisson ratio 0.25**, with K=20 kPa and G=12 kPa. These are explicit synthetic values, not measured tomato properties. The fitted affine energy is a construction target, not independent evidence of realistic elasticity. Central-force isotropic springs impose the Cauchy relation lambda=G; this recipe cannot independently represent a nearly incompressible tomato by selecting Poisson ratio 0.49. A future volume constraint or different model would be needed for that response.

The original 403 cross-cut interface coefficients are copied using the prior patch assignment rule, with the corrected damage law and area budgets unchanged. Every one of the 29,790 springs receives exactly one proposed stiffness assignment. The bulk refinements do not change any node coordinates, surface triangles, patch membership, blade geometry, fixture or frozen grasp criterion. Saved assignments are not connected to a runtime model.

## Offline compression and shear checks

Each piece is checked independently, with its cross-cut cohesive springs absent from these bulk-only tests. All surface degrees of freedom follow a prescribed 0.2% small-strain compression or simple shear; the original interior degrees of freedom relax through a sparse linear equilibrium solve. This is more than an entirely affine probe, but it is still a fully prescribed outer-boundary coupon, not a tomato squeezed between physical platens or contacted by a knife.

For each piece: compress along x/y/z, and shear in xy/xz/yz in both signs. Acceptance requires positive energies, finite positive integration-cell volumes, free-node force residual below 1e-7 relative to boundary reaction, relaxed energy between 10% and 100% of affine energy, agreement of finite-length and linear spring energies within 3%, and the affine reference within 1e-7. The 10% floor is only a gross loss-of-stiffness check, not a material-calibration tolerance.

| Piece | Mode | Cases | Apparent constrained stiffness | Minimum cell-volume ratio | Outcome |
| --- | --- | --- | --- | --- | --- |
| slice | compression_x | 1 | 29.100 kPa | 0.9570 | Pass |
| slice | compression_y | 1 | 34.506 kPa | 0.9862 | Pass |
| slice | compression_z | 1 | 34.479 kPa | 0.9821 | Pass |
| slice | shear_xy | 2 | 10.747 kPa | 0.9916 | Pass |
| slice | shear_xz | 2 | 10.469 kPa | 0.9854 | Pass |
| slice | shear_yz | 2 | 11.593 kPa | 0.9949 | Pass |
| remainder | compression_x | 1 | 34.611 kPa | 0.9666 | Pass |
| remainder | compression_y | 1 | 34.486 kPa | 0.9337 | Pass |
| remainder | compression_z | 1 | 34.206 kPa | 0.9522 | Pass |
| remainder | shear_xy | 2 | 11.601 kPa | 0.9871 | Pass |
| remainder | shear_xz | 2 | 11.517 kPa | 0.9864 | Pass |
| remainder | shear_yz | 2 | 11.439 kPa | 0.9738 | Pass |

Worst free-node linear residual is 2.63e-14; worst finite-length versus linear energy difference is 0.154%. No diagnostic cell inverts. Compression reduces total volume by about the imposed 0.2%; shear volume remains close to unity. These conclusions apply only to the tested small strains, not large compression, cutting, crack-face closure or dynamic collapse.

The cap retains directional variation after interior relaxation: apparent normal stiffness is about 29.10 kPa in x versus 34.48–34.51 kPa in y/z. The full affine target was isotropic, but the finite network, thin geometry and boundary constraint still matter. No claim of fully isotropic relaxed behaviour is made. The apparent constrained normal coefficient is not a measurement of Young modulus; lateral boundary motion is prescribed.

## Stability and remaining limits

The undamped explicit timestep figures are conservative estimates from a mass-weighted stiffness row-sum spectral bound for each isolated bulk piece. They are **not** an executed dynamics test, an exact critical timestep or a selected VBD timestep. Intact interface stiffness, contact, damping and nonlinear geometry can change stability. In particular, the previous robot's 1/240 s step cannot be assumed suitable for this network. Benchmark an implicit contact solver or revise discretization after separate authorization; do not silently increase timestep or soften the interface.

Nine independent tests check analytic simplex volume/moments, boundary-fan agreement, rigid transforms, a known single-spring matrix, positive semidefiniteness with six rigid modes on a tetrahedral spring fixture, infinitesimal rotation/translation, finite-energy consistency and invalid/insufficient direction rejection. Missing shear directions cannot be manufactured by the positive orientation fit.

## Resources and preservation

Final analysis took 0.59 s and peaked at 154.99 MiB process memory. It used the already installed NumPy/SciPy numerical libraries with one BLAS thread. There were no dependency installations and no Newton, Warp, Torch, Isaac or USD imports. The new numerical worker has a 512 MiB offline address-space ceiling, 45 s CPU and 55 s wall limits, and uses the shared controller lock. This numerical-library budget is separate from the simulator's unchanged memory watchdog; the 10 GB available-RAM and 4 GiB free-VRAM startup reserves and runtime stops were not changed.

All 178 pre-existing non-cache files checked under `rl` and `docs/rl` retain their original hashes. New code is `rl/tomato_surface_mechanics.py`, `rl/offline_tomato_surface_mechanics.py` and `rl/tests/test_tomato_surface_mechanics.py`. No existing controller, safeguard, scene, damage law or acceptance file was edited.

Evidence is in `runs/offline/tomato_surface_mechanics_04/`: summary, complete mass/stiffness proposal, unchanged interface coefficients, matching source snapshots and preservation hashes. Earlier runs retain development evidence: the first stopped on JSON serialization before reporting; a later refinement replaced piece-dependent densities with the final common density. Final results supersede those intermediate mass proposals.

Next work should test larger-strain constitutive behaviour and settle contact/dynamics configuration. The current static pass does not authorize simulator launch, establish physical tomato calibration, or start training.
