# Blade contact and cut face test plan

Status: offline planning only, 19 October 2026. No geometry, solver, collision pipeline or controller is implemented or activated by this document. No simulator imports, simulator runs or training are authorized by it. The existing memory safeguard and grasp criteria remain unchanged.

## Recommendation and evidence

Begin with two very small contact coupons before the full tomato: a blade pressing into a deformable surface, and two separate deformable pieces closing against each other. Add damage only after these contact paths work independently. A visible cut and zero connecting spring force do not establish that pieces cannot pass through each other.

Additional installed-source inspection identifies a candidate beyond particle-only contact:

- Newton `CollisionPipeline` documents `enable_rigid_soft_full_surface_contact`, adding soft triangle-interior and edge contacts against rigid SDFs. It requires suitable rigid SDFs and is consumed only by `SolverVBD`; the semi-implicit solver rejects those records.
- VBD's spring accumulation reads spring indices, rest length, stiffness and damping. This is source evidence that springs and full-surface contact may coexist; it does not establish runtime compatibility with our damage updates, colouring, reference frames or reaction logging.
- The collision pipeline has vertex–triangle and edge–edge self-contact detection with topology and external exclusion maps. It requires triangles. Rest-shape proximity exclusions can hide close opposing cut faces. Its documentation warns that contacts beyond per-vertex/per-edge capacity can be silently dropped.
- The semi-implicit particle contact path uses particle radii and all active neighbour particles in the inspected kernel, without a material-side exclusion argument there. Inflating radii is not a reliable way to turn a sparse network into a closed cut surface. Its legacy particle–triangle kernel also skips extremely small distances; it cannot be assumed to prevent crossing through coincident cut faces.

**Preferred capability test:** evaluate VBD with the same reduced spring mechanics and explicit contact triangles in a future isolated experiment. Do not switch the robot backend. VBD damage-update behaviour must reproduce the offline energy tests before it becomes the selected mechanics solver. If it cannot, investigate a contact implementation compatible with the simple solver; do not silently discard spring or fracture behaviour to enable contact.

These are source-confirmed entry points, not tested guarantees. No continuous collision detection guarantee was established for either contact path. Swept geometry checks and conservative substeps remain necessary test requirements.

## 1 Contact geometry must be designed first

The current layout has 979 nodes and 47 area patches, but no collision triangles. An area patch is an accounting region, not a face. The existing two mechanical node layers lie on opposite sides of the intended cut; placing collision faces on those layers would leave an artificial gap about one lattice spacing wide. Do not interpret that gap as a real blade kerf.

For the contact prototype, author two separate, closed material surfaces: the slice and remainder. Each includes its own cut face, exterior and perimeter rim. They have separate node identities, even where initially geometrically coincident. No triangle, interior structural element or surface-reinforcement spring may connect them. Intact finite-length interface bonds supply cohesion until damage removes them.

Preferred geometry route is cut-conforming surface/mechanical nodes at the actual cut plane, connected by finite-length springs only within their own side. Existing finite-length cross-cut bonds can remain between distinct interior nodes. Never join coincident opposing cut nodes with an ordinary zero-length spring. Recompute mass accounting, fixture membership and topology when adding surface nodes; collision nodes are not new material mass on top of the original tomato.

This is a proposed layout revision, not implemented geometry. It requires renewed offline geometry and patch-registry checks. In the first two-piece coupon, use a known positive initial gap to validate closure. Only then test the physically contiguous intact interface, including exactly coincident faces if supported. A small numerical clearance is permissible solely as an explicitly measured approximation with a convergence test; it must stay much smaller than blade thickness and the penetration tolerance. If the backend needs a large gap or produces initial preload, it fails this gate.

Contact surfaces should use geometric normals, winding and material-side identity. They follow material deformation, not knife animation. Avoid unconstrained decorative nodes. If an embedded representation is chosen instead, its interpolation and transpose force transfer must conserve force and moment and cannot extrapolate blindly from one side's interior nodes. That route needs its own validation.

## 2 How opposing cut faces resist crossing

Keep compressive contact available independently of damage. Cohesion transmits tension/shear while intact; compression contact supplies unilateral nonpenetration. At full damage, cohesion and cohesive damping vanish, but nonadhesive compression/friction contact remains. Pieces may separate, slide or touch without being glued back together.

Conceptual contact rule for a consistently oriented opposing face pair:

- Compute the signed material-side gap g, a consistent outward/contact normal, and the relative normal velocity. Initially touching means g=0, not automatically a penetration or a finite contact force.
- During closure, negative gap produces a repulsive normal reaction; positive gap has zero normal reaction except any explicitly documented small activation offset.
- Damping resists closure and is clamped so that it never creates attraction during separation. Friction is bounded by the compressive normal reaction and cannot hold the faces together in tension.
- Distribute reaction forces to participating surface vertices using the contact coordinates. Verify opposite total forces and moments on the two pieces. Do not apply the same contact twice through duplicated face/edge/particle paths.

Use finite-face tests rather than an infinite plane alone. Surface interiors, perimeter rims and edge–edge approaches all need coverage. An unsigned nearest-distance penalty can repel objects after they have already crossed and flipped sides; it is not enough to certify non-crossing. Track material-side ordering and swept vertex/face and edge/edge events over each substep. Any unresolved crossing or flipped/inverted face invalidates the run.

A penalty method permits small numerical overlap; the requirement is bounded penetration without a surface crossing, not mathematically exact zero overlap. If a predicted substep would cross, reduce the step and recompute consistently before accepting it. Do not repair a completed crossing by teleporting a slice back into place. If no stable bounded-step configuration resolves the geometry, report contact failure.

## 3 Contact exclusions and duplication

Create explicit pair classes: own-side adjacent topology, own-side nonadjacent surfaces, opposing cut faces, blade–slice, blade–remainder, board–material, and fixture–material. Keep exclusion decisions and affected counts in the run manifest.

Exclude only true local same-side adjacency needed to avoid self-repulsion. Distinct opposing cut faces must stay eligible even when they began close together or are connected by intact interface springs. A rest-distance exclusion must not permanently mask the future cut. Check the backend's actual filter semantics rather than assuming triangle adjacency equals spring connectivity.

Do not temporarily solve a contact problem by globally disabling material self-contact or by removing all blade contact after rupture. Opposing cut surfaces must resist reclosure at D=0, partial damage and D=1. The blade must retain contact with each piece after separation.

Avoid unintended extra compression stiffness from the sum of bilateral interface springs and contact penalties. First measure each contribution in a compression coupon. Calibrate or redesign the compression branch if double-counting is significant; the energy law already excludes compression-plus-shear fracture and must continue to reject that unsupported case rather than reporting a successful cutting event.

## 4 Blade contact coupon

Use a small slab or two short spring blocks with a closed triangulated surface and a disclosed support. Begin with the existing knife's measured edge/face shape, not a thickened box. Extract and record actual blade thickness and the finest geometric feature to be resolved. Use the same fixed physical geometry across resolution tests.

For a full-surface VBD candidate, precompute the blade's required rigid SDF with a bounded grid and check its zero surface against the source mesh, especially the edge. SDF memory and cooking belong in resource accounting. Solver support and thin-feature accuracy must be established before selecting a resolution; no SDF is created in this planning task.

Proposed sequence:

1. Hold the slab at rest; blade remains separated. Expect zero blade contact and no damage.
2. Press lightly, with damage disabled, at a surface vertex. Verify reaction direction, deformation and recovery.
3. Repeat at a triangle centre and across an edge. The blade must not fall through gaps between material vertices.
4. Repeat with an oblique approach and a tangential drawing component. Check normal/friction work and absence of artificial adhesion on withdrawal.
5. Use a bounded dynamic test body where appropriate to check equal-and-opposite momentum transfer. For a prescribed blade, directly log contact reaction and actuator work; its enforced motion is not a momentum-conservation test for an isolated system.
6. Only then enable patch damage with local blade-edge eligibility and verify progressive, spatially local failure.

For damage eligibility, require swept cutting-edge proximity/intersection and actual current blade/material contact in the same material region. Blade face rubbing, elapsed time or final depth alone cannot rupture every patch. If the current model enters unsupported compression-plus-shear fracture, stop and record it. Do not reinterpret an unsupported state as passing because pieces appear separated.

## 5 Two-piece cut-face coupon

Use two independently labelled small spring blocks with matching finite cut faces. Cohesive damage may be prescribed as a diagnostic state here; these are contact tests, not successful cuts. Record that distinction explicitly.

| Case | Loading | Required behaviour |
| --- | --- | --- |
| Positive gap | Both faces stationary | No attractive force or false contact preload. |
| Normal reclosure | Bring separated blocks together | Repulsion prevents side swapping; bounded penetration; correct reaction signs. |
| Tangential slide | Close lightly, then slide | No passage through face interior or rim; friction is compressive-load limited. |
| Edge approach | Offset and rotate one piece | Edge–edge and vertex–face events detected; no rim escape through the other solid. |
| Reopen | Reverse closure | Normal/friction force disappears after separation; no cohesive residue at D=1. |
| Intact and partial damage | Repeat closure at D=0 and intermediate D | Contact remains available without initial explosion or an artificial cross-cut wall. |
| Exactly touching rest state | Faces at the intended intact interface | No singular normal, filter omission or preload instability. |
| Blade between pieces | Insert and withdraw the real-thickness test blade | Both pieces contact it, then reclose physically; no permanent blade-sized clearance. |

Re-test with the actual cut-face boundary once a conforming tomato surface exists. Merely keeping two ideal parallel planes apart is insufficient for the tomato rim and deforming slice.

## 6 Substep ordering and bounded memory

Suggested future substep: validate material/triangle state; construct or refit contact geometry; generate bounded candidates; evaluate current local blade eligibility; update damage using committed geometry; solve spring and contact response; check swept crossings, energy and buffer completeness; accept only a valid substep. VBD iterations and collision refits must keep contact geometry synchronized. A constitutive update should not run repeatedly per solver iteration and multiply irreversible damage history.

Choose substeps from both spring stability and contact motion. A proposed kinematic ceiling is that maximum relative surface motion per substep stays below one quarter of the smallest resolved blade/contact feature. It is a heuristic to test, not proof of collision safety. Include angular motion, particle displacement and SDF interpolation error. Halve timestep to verify penetration, loads and fracture work.

Allocate contact capacity explicitly. Log generated, retained, rejected and overflow/saturation counts where exposed. Since installed self-contact code can silently drop excess per-vertex/per-edge candidates, offline broad-phase bounds or independent small-coupon reference counts must establish completeness. If completeness cannot be observed, mark that test inconclusive. Increasing buffers is a bounded design change, not permission for unbounded allocation.

Later physics runs remain one headless environment with the existing common lock, minimum 10,000,000,000 available host bytes and 4 GiB free VRAM at startup, and unchanged runtime checkpoint/hard-stop thresholds. Keep a 60-second worker cap and account for SDF, topology, compilation and solver setup. An unfinished stage is inconclusive. Do not launch until after the RAM upgrade and a subsequent execution instruction. A dedicated reviewed worker/guard route is still required.

## 7 Proposed acceptance and evidence

Before any future run, freeze numerical tolerances based on physical blade dimensions. Suggested research targets, pending that measurement, are penetration and geometry-error budgets no larger than min(0.1 mm, 10% of local blade thickness). Do not claim these budgets are feasible until SDF/surface resolution is checked. Load limits and human-robot clearance remain separate unresolved hardware inputs.

Contact acceptance requires all of the following:

- No swept surface crossing or material-side swap, including at triangle centres and cut rims; no invalid/inverted triangles.
- Maximum penetration within the frozen budget, no unexplained rest preload, and zero attraction after separation.
- Correct equal-and-opposite force/moment accounting; proposed relative force-balance residual below 1% for nonzero-force coupon cases, with a declared absolute floor near zero.
- Bounded friction and explicit work accounting: prescribed tool/fixture work, elastic storage, contact/friction dissipation and damage energy are distinguished. A moving prescribed tool can add energy legitimately.
- All relevant candidates retained; no silent contact-buffer truncation or filter-induced blind region.
- Half-timestep and refined-contact-geometry comparisons give stable penetration and load/work estimates; proposed load/work change below 10%. The existing 1% constitutive fracture-energy checks remain unchanged and must be rerun if mechanics are modified.
- Every case discloses whether motion or damage was prescribed. Only a later integrated blade-driven test can claim cutting and independent slice release.

Record IDs and material labels of all contacts near the cut, signed gap, normals, relative velocities, forces, penetration maxima, contact lifetime, excluded-pair reasons, candidate capacities, triangle orientation, blade reaction, fracture state and process/GPU resource peaks. Use bounded traces plus per-case summaries rather than saving every large array at every step.

## 8 Offline handoff and stop point

Next authorized implementation can first produce a cut-conforming surface/topology specification, pair-filter table and analytical contact-geometry tests without importing Newton. Check face winding, rest gaps, finite spring lengths, triangle-edge coverage and independent component identity. This must also resolve how added face nodes preserve mass and the existing patch energy registry.

After those offline checks, a separately authorized guarded physics coupon can determine whether the native VBD route works. If it fails, report the failing capability and propose a bounded custom-contact or alternate-solver investigation. No model is selected merely because its API exists. Robot integration and training remain later stages.

## Source references

Installed sources inspected as text, without imports:

- `/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/sim/collide.py`: `CollisionPipeline` constructor documentation around lines 1265–1288; self-contact initialization around lines 1968–2037; full-surface generation around lines 2625–2646.
- `/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/solvers/vbd/solver_vbd.py`: spring accumulation around lines 3203–3220 and self-contact handling immediately afterwards.
- `/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/solvers/semi_implicit/kernels_contact.py`: particle contact around lines 36–86, legacy triangle contact around lines 90–143 and particle-only record assertion around line 663.
- Project `TOMATO_ALL_PATCH_ENERGY_RESULTS.md`, `tomato_bonds.py`, `slicing_criteria.json` and `rl/guard_benchmark.py`: energy evidence, known constitutive exclusions, draft acceptance and preserved watchdog.
