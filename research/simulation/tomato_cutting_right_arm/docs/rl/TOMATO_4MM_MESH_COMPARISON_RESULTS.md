# 4 mm node reuse and slice compression comparison

The coincident-node defect is fixed: a same-piece surface point reuses the existing material node, without moving either cut side or welding the cut faces. The corrected 4 mm geometry passes all geometry checks. The independently passing slice completes all protected static compression/shear paths tested. However, **the whole 4 mm mesh remains rejected**: the remainder's unprotected small-strain preparation still inverts some local volume cells. No simulator, controller, training or runtime model was activated.

## Geometry correction

`rl/tomato_surfaces.py` now indexes same-side material/surface nodes with a 1e-12 m coordinate-roundoff tolerance. The 4 mm slice pole reuses original node 0 at exactly zero distance. Existing material coordinates and original bond/patch registries are preserved. Already coupled material nodes receive no zero-length surface tether; duplicate undirected bonds are prevented. Reused nodes retain their original scaled mass share plus their surface mass share. Ambiguous coincident originals are rejected rather than silently merged. Opposite-side cut-face nodes retain different IDs even at identical coordinates.

The first corrected preparation exposed eight remainder lattice nodes up to 26.24 micrometres outside the faceted exterior. `rl/tomato_surface_conformity.py` promotes those existing nodes into a convex exterior boundary, retriangulates only that piece's exterior and rebuilds proposed surface edges. It preserves every coordinate, the existing cut triangulations, original bonds, patch registry, fixture, total mass and side identities. No padding, jitter or parameter tuning was used. This is a small geometric discretization change and is disclosed rather than treated as an identical exterior mesh. The slice exterior is unchanged. Regression checks confirm 5 mm nodes, triangles, masses and bonds are unchanged by this conformity operation.

Final 4 mm proposal: 1,903 original material nodes; 4,658 total nodes; 40,502 bonds; 5,520 triangles. Every piece is closed, oriented and convex; no zero-length or duplicate bonds remain; original nodes are contained; the two cut faces match geometrically but share no topological vertices. Closed-volume errors remain below the existing 1% limit. The design stays inside the existing 7,000-node/50,000-bond bounds.

## Remaining preparation failure

At 0.2% imposed strain, all nine unprotected slice checks pass. The remainder fails its three compression checks despite converged linear force equilibrium:

| Direction | Minimum remainder cell volume ratio J |
| --- | ---: |
| x compression | -0.7720 |
| y compression | -0.1257 |
| z compression | -0.7360 |

Its six unprotected shear checks pass. These are failures of the bare-spring small-strain preparation, not results of a protected nonlinear remainder test. The volume-protected remainder was **not** admitted into the comparison. Boundary containment fixes the geometry defect but does not establish adequate interior volume-cell quality or mechanical coupling. The exact cause of these remaining local inversions requires a separate diagnostic; they are not simply asserted to be harmless slivers.

The default path runner still rejects a failed whole mesh. An explicit `--isolate-passing-piece` diagnostic option permits only a side that independently passes all its existing small-strain checks, and only when global geometry and the regenerated original layout audit pass. Every resulting trace states `whole_mesh_preparation_passed: false` and `isolated_passing_piece_only; whole_mesh_still_rejected`. Failed geometry or a failed selected piece cannot be bypassed. Tests exercise those rejection paths. No acceptance threshold was relaxed.

## Rerun comparison

Run four slice paths at each of 4, 4.5, 5 and 6 mm: compression x/y/z at 1, 2, 5, 10, 20 and 30%; negative xz shear at 2, 5, 10, 20, 30 and 50%. The other three meshes use the previously prepared, unchanged assignments; their path tests were rerun. The 4 mm slice uses the new geometry/assignments and is explicitly isolated from its rejected remainder.

All 16 paths / 96 sampled endpoints pass the unchanged protected static screens: force residual <=1e-6, no inverted cell, J>=0.1, no near-singular spring, and positive free-tangent screen. Minimum J across this rerun is 0.18335. The physical model remains the same uncalibrated E=30 kPa, Poisson ratio 0.25, barrier coefficient 10 kPa, activation J=0.5, floor J=0.1, with the same volume-lumping and isotropic spring-weight recipe. No mesh was fitted to match another.

The table reports maximum absolute differences from 5 mm across matched load levels. Reaction is the energy derivative with respect to dimensionless strain, divided by piece volume; it is **not a measured platen force in newtons**. Energy is likewise divided by actual piece volume. The existing comparison target remains 10% for both measures.

| Mesh | Slice path | Energy-density difference | Reaction-density difference | 10% target |
| --- | --- | ---: | ---: | --- |
| 4 mm | x compression | 9.58% | 10.52% | Not met |
| 4 mm | y compression | 0.68% | 0.68% | Met |
| 4 mm | z compression | 1.54% | 1.54% | Met |
| 4 mm | negative xz shear | 1.44% | 1.44% | Met |
| 4.5 mm | x compression | 7.74% | 8.53% | Met |
| 4.5 mm | y compression | 0.34% | 0.44% | Met |
| 4.5 mm | z compression | 1.67% | 1.71% | Met |
| 4.5 mm | negative xz shear | 1.50% | 1.96% | Met |
| 6 mm | x compression | 10.82% | 12.58% | Not met |
| 6 mm | y compression | 2.33% | 2.30% | Met |
| 6 mm | z compression | 3.04% | 3.59% | Met |
| 6 mm | negative xz shear | 1.38% | 1.38% | Met |

The most sensitive response is compression through the 10 mm slice thickness (x). The largest 4 mm versus 5 mm difference occurs at 10% compression. The 4 mm and 4.5 mm curves are closer to one another, but this limited fixed-surface comparison does not prove asymptotic convergence or justify accepting the failed whole 4 mm mesh. Static stability and mesh independence remain separate requirements.

## Evidence, verification and safeguards

Evidence is in `runs/offline/tomato_4mm_reuse_01/`: intermediate mesh preparations in `meshes/bulk4` and `meshes/bulk4_conforming`, all 16 new path traces in `cases`, matched numerical comparisons in `slice_mesh_comparison.json`, and 30 passing regression tests in `regression_tests.txt`. Tests cover coordinate reuse, cut-side separation, ambiguous duplicates, bond/mass accounting, boundary repair, unchanged 5 mm geometry, rejected preparation gates and the unchanged volume-energy mechanics.

Path workers ran serially for 10.71 s total, with peak VmHWM 119.89 MiB. Final 4 mm preparation took 9.19 s with peak 210.15 MiB. Workers retain the shared controller lock, single BLAS thread, 512 MiB address-space ceiling, 45 s CPU and 55 s wall limits. These are offline worker caps; the existing simulator startup reserve and runtime watchdog are unchanged. No simulator/GPU runtime was imported or launched and no training was started.

Preservation hashes and source snapshots are saved alongside the evidence. Only offline surface generation, mesh preparation, diagnostic path admission and their tests changed. The existing controller, memory safeguard, frozen grasp criteria, material/volume energy implementation and prior run evidence are unchanged. These tests impose every outer-surface displacement and solve static interior equilibrium: they do not validate dynamic contact, blade cutting, slice separation under contact or physical tomato properties.

## Recommendation

Keep 5 mm as the unchanged reference, with 4.5 mm as a currently admissible finer comparison. Do not promote 4 mm to a complete model yet. The next bounded offline task is to locate the remainder's inverted preparation cells and inspect their aspect ratios, boundary proximity and spring coupling, then decide whether a conforming interior volume mesh or coupling correction is needed. Preserve the failed evidence and test any correction against both the original small-strain gates and protected compression before comparing complete pieces. Resolve thickness-direction discretization sensitivity before selecting material parameters or moving to blade-contact integration.
