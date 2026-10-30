# Closed tomato cut surface geometry results

Date: 19 October 2026. Separate closed surfaces for the end cap and remainder have been designed and pass the offline rest-geometry checks. **No collision solver, Newton model, blade simulation or training was imported or launched.** Passing geometry does not demonstrate dynamic nonpenetration.

## Design

Both solids are triangulated clipped ellipsoids, with analytic ellipsoid points on the exterior and concentric planar rings filling the cut. The cut plane is the original 10 mm end-cap plane. Each side has its own 257 cut-face nodes and 448 cut triangles. Corresponding coordinates and triangulations match exactly, with opposite outward normals, separate IDs and zero artificial rest gap. Each rim is part of its own watertight boundary; there is no polygon spanning the two solids.

Surface nodes are proposed mechanical nodes, not an animated collision shell. Each is connected to four original nodes on its own side, with three independent tether directions verified by normalized determinant. Same-side triangle edges are also finite-length proposed springs. Their stiffnesses remain unset; no force model is activated. This expands the original 979-node design to **3,735 nodes and 29,790 bonds**, so the original approximate 2,500-node prototype target is exceeded. The expanded offline design is capped at 7,000 nodes and 50,000 bonds; these are offline construction caps, not permission to change runtime memory reserves.

The original 10,510 bonds remain an identical prefix of the new registry. All 403 cross-cut bonds, their finite rest lengths, all 47 patch assignments/areas, damage-law source and fixture membership remain unchanged. Added tethers and surface edges never connect opposite sides. The graph is initially connected and becomes exactly two components, of 898 and 2,837 nodes, after removing all original interface bonds.

## Geometry checks

| Check | Result |
| --- | --- |
| Closed surfaces | Every edge has exactly two opposite directed uses; each vertex link is one cycle; Euler characteristic is two per solid |
| Exterior and cut normals | Outward; cut normals point in opposite directions |
| Degenerate or repeated geometry | Positive triangle areas, unique coordinates within each piece, no zero-length or duplicate bonds |
| Rest self-intersection screen | Convex supporting-plane certificate for every face against all vertices, plus manifold/link checks |
| Original-node containment | All original material nodes lie inside the correct new closed solid |
| Rest piece overlap | Separate x half-spaces; only the intentionally coincident cut boundary is shared geometrically |
| Cut coverage | Matching triangulations, no open rim, areas tile the same regular-polygon cut disk |
| Cut area approximation | 0.1606% below the analytic ellipse area |
| Solid volume approximation | End cap 0.5519% low; remainder 0.3292% low, both within the proposed 1% offline volume check |
| Segment crossing probes | 2,688 triangle-interior, edge and vertex samples detected; no misses |

There are 1,664 triangles on the slice and 3,840 on the remainder. Facet approximation and source points have not yet been checked against the blade-thickness-dependent contact tolerance. The figures above establish geometric accounting, not that a thin edge cannot tunnel through a time-stepped solver.

The segment/triangle reference also rejects outside-triangle hits, parallel paths and separated paths, and identifies a prescribed gap-crossing time. It is an analytic geometric detector, not a continuous collision response or an edge–edge dynamic solver. The convex rest-shape certificate is specific to this construction and does not certify arbitrary deformed meshes.

## Mass accounting and mechanical limitations

The proposal reassigns 25% of each piece's existing mass to its new surface nodes, weighted by incident triangle area; the remaining 75% stays on its original nodes. Total mass and each piece's mass are preserved to numerical precision, and every node has positive mass. The new mass is not added on top of the original tomato.

This 25% split is explicitly provisional: it is not volume-based mass lumping or calibrated anatomy. It changes the total centre of mass by 0.0575 mm and changes inertia. No inertia or continuum convergence is claimed. Surface tether stiffness and compression/shear behaviour need selection and checks before any Newton asset can use the design. Geometry passes do not make the expanded mechanics training-ready.

## Contact pair design

The offline exclusion policy removes an incident own-side vertex/face pair, while keeping opposite-piece faces eligible even at zero gap. A total of **230,272 opposing cut vertex–face combinations** were evaluated and none was excluded. Own-incident exclusions were also checked. There are 200,704 potential cut-face triangle pairs; this is a combinatorial bound, not a native buffer allocation or a measured contact count.

The saved policy table specifies zero rest-shape proximity exclusion radius, no blanket particle-radius inflation, and continued blade eligibility for both pieces at every damage state. These are proposed rules, not installed Newton filter settings. Native topological filters, exactly coincident-face behaviour, edge–edge contact, candidate-buffer completeness and compressive nonpenetration still require later validation. Zero gap does not mean the native solver can safely normalize coincident positions.

## Adversarial tests

All **13 focused tests pass**. They check known cube volume/cut area, deliberately missing/flipped/duplicate/degenerate faces, wrong material labels, out-of-plane cut vertices, interior/edge/vertex crossings, finite-triangle bounds, parallel/no-crossing paths, gap-crossing order and pair-policy failures. Bad inputs are rejected by the checks instead of being repaired silently.

## Resources and preservation

Final offline construction/checking took 4.64 seconds with peak Linux VmHWM 58.66 MiB. The worker held the common controller lock and had a 256 MiB address-space ceiling, 45-second CPU ceiling and 55-second wall deadline. These are bounded offline limits; the simulator watchdog and its 10 GB available-RAM/4 GiB free-VRAM startup gates are unchanged.

All 174 pre-existing non-cache files checked under `rl` and `docs/rl` retain their hashes. Added code is limited to `rl/tomato_surfaces.py`, `rl/offline_tomato_surfaces.py` and `rl/tests/test_tomato_surfaces.py`; existing controller, scenes, damage law, frozen grasp criteria, draft slicing criteria and memory safeguards were not edited. No runtime asset or configuration was created or activated.

Evidence is saved in `runs/offline/tomato_surfaces_03/`: `surface_design.json`, `summary.json`, `collision_pair_policy.json`, source snapshots and preservation hashes. Earlier surface runs are preserved as intermediate checks; the final run adds original-node containment and exhaustive cross-piece vertex–face policy checks.

## Next gate

Choose mechanically defensible surface mass/stiffness assignments and validate compression/dynamic stability before a separately authorized native contact coupon. Then test actual blade contact, zero-gap reclosure, surface crossing and buffer completeness under the unchanged runtime safeguards after the RAM issue is resolved. No physical cut, slice retention or trained policy success is claimed by this offline result.
