# Offline blade/bond and cut-face contact coupons

**The local coupon checks pass. A coupled deformable tomato cut, independent release and general nonpenetration are NOT validated.** This is the first contact gate on the refined model, not a successful robot slice or a substitute for the required post-release observation.

No simulator, Newton/Warp/Torch/USD runtime, training or dependency installation was started/imported. Existing controllers, physical assets, model-generation code, damage law, memory safeguard and frozen grasp criteria were not edited. All new code is offline and inactive.

## Model and exact scope

Use the accepted refined 5 mm reference from `runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5`: 4,032 nodes, including a 1,195-node slice with 2.5 mm added interior sampling, and a 2,837-node remainder. Its 403 original interface bonds still belong to the same 47 area patches. Both actual finite cut faces have 448 triangles, separate node IDs and zero rest gap.

There are two deliberately restricted physical references:

1. **Local blade/bond coupon:** one actual finite-length patch bond bundle, with constrained lateral motion and one opening freedom. A prescribed finite single-bevel wedge drives unilateral opening; the supported coupon uses massless quasistatic contact equilibrium. Full nodal spring/volume deformation and inertia are not solved. Existing bundle forces and irreversible damage are evaluated without modifying their law or fracture-energy budget.
2. **Cut-face contact coupon:** actual convex cut outlines, rigid piece shapes, fixed lateral offset, normal translational motion of the slice and a fixed remainder. An exact swept impact time prevents normal crossing before a step is accepted. Contact remains active independently of the prescribed diagnostic damage value. This is not the original deformable fixture configuration or general 3D self-contact.

These reduced references intentionally suppress many modes. Their results do not show that the refined full spring/volume model can cut or collide successfully under blade loading. In particular, no full nodal contact/damage integrator is currently connected to that model.

## Blade geometry disclosure

The wedge is a **surrogate**, not the original knife's extracted edge mesh. Its envelope uses the saved collision-blade audit: length approximately 265.93 mm, height 50.44 mm and maximum z extent 7.609 mm. That z extent is an envelope dimension, not verified local blade thickness. The single-bevel length is an explicitly synthetic, uncalibrated 8 mm coupon choice. No SDF is cooked and no actual bevel/edge accuracy is established.

The existing knife asset is unchanged. A thinner 2 mm wedge is a negative control and does not fully break the test bond under the same law. Thus the thick-surrogate result cannot be transferred to a physically thinner knife without checking its actual geometry, local deformation and calibrated material response.

## Blade-driven patch checks

Run all 47 actual patch bundles at 2,400 and 4,800 increments along the bevel: **94 complete local coupon cases**. Their contact sites are verified inside both actual finite cut-face triangulations. A continuous finite cutting-edge sweep must reach a site's region, and current bevel contact must carry positive load, before damage becomes eligible. Face rubbing without the edge event, off-plane motion and a missed finite blade do not enable damage.

Opening follows the unilateral bevel/contact equilibrium, not an elapsed-time rule. The contact region supplies the opening while intact cohesion resists it. Blade work is independently computed through the bevel's virtual-work relation and agrees with opening work. The supported, massless approximation provides no dynamic impact or free-slice motion claim.

| Check | Result |
| --- | --- |
| Full patch failure | 47/47 at each increment resolution |
| Largest fracture-work relative error | 0.0000673% |
| Largest damage-dissipation relative error | 0.1673%, within unchanged 1% gate |
| Broken elastic force and cohesive damping | Exactly zero |
| Half-increment change in peak local blade reaction | At most 0.0470% |
| Half-increment change in damage dissipation | At most 0.0837% |
| Half-increment change in work | Below 0.0000570% |
| Stationary final state with unchanged contact eligibility | Damage/history unchanged |
| No-contact, off-plane and face-rubbing controls | Zero damage |
| Partial-bevel control | Partial damage, not full release |

The actual constitutive law and parameters are unchanged: synthetic reference normal stiffness 4e7 times patch area, peak traction 40 kPa and fracture energy 80 J/m2, shared by the uncalibrated skin/flesh test patches. Compression-plus-shear fracture remains unsupported and rejected by the existing law/tests; this new coupon uses pure opening only. No tangential drawing/friction result is claimed.

At the finer increment size, the lowest tool-tip height associated with coupon failure is 8.718 mm in the ideal board frame. This is a geometric accessibility diagnostic only; an actual board contact solution was not run. Peak reactions are **per independently supported patch**, not the total load of a single coherent tomato-cutting trajectory.

## Connectivity after failure

Assemble the final damage states from the independent 4,800-increment coupons, and remove only interface bonds whose owning patch has D exactly equal to 1. All 403 interface bonds then have zero cohesive stiffness/damping. The actual refined graph has exactly two single-material components of **1,195 and 2,837 nodes**. Retaining even one interface bond keeps one connected component. No small-positive stiffness threshold is used to manufacture release.

All existing volume cells stay on their own side and the saved fixture contains only remainder nodes. No slice is spawned, welded, attached or teleported. This establishes a **conditional topology result assembled from separate coupons**, not independent physical release in one coupled trajectory. The required one-second post-withdrawal deformable observation remains unperformed.

## Finite cut-face nonpenetration checks

Run six contact cases at dt=1 ms and 0.5 ms: normal press/reopen at diagnostic D=0, 0.5 and 1; stationary exactly touching faces with no load; a disjoint lateral offset; and near-rim finite overlap. **All 12 pass within this parallel rigid-shape scope.**

Finite polygon separating-axis tests determine overlap, including rims; disjoint faces do not create an infinite invisible plane. For overlapping faces, continuous normal impact time is solved before accepting motion. The remainder and slice remain in their ordered x half-spaces, so the translated closed solids cannot overlap in these cases. This is not post-crossing position repair. After pressing, reversing the force allows separation without adhesive contact. Exactly touching stationary faces have no preload.

Maximum overlap penetration is zero; no material-side swap is accepted. Friction is zero. Equal-and-opposite scalar contact impulses are accounted for analytically, with the fixed remainder's constraint absorbing its impulse. External work, kinetic energy and inelastic impact dissipation balance within 1.2e-18 J. Half-dt work differences are below 2.2e-19 J and gap differences below 1.8e-18 m. These are exact low-dimensional reference checks, not measured accuracy of a general contact solver.

Every actual cut-triangle centre on both sides (896 samples total) also passes finite inclusion and continuous edge-sweep geometry checks. Unit tests cover triangle interiors, edges and vertices. This verifies coverage of those geometric probes; it does not establish full deformable vertex-face/edge-edge response, rotated approaches, contact friction, native contact-buffer completeness or non-crossing under arbitrary nodal deformation.

## Evidence and safeguards

Evidence root: `runs/offline/tomato_contact_01/`.

- `manifest.json`: restricted scope, surrogate dimensions and offline tolerances, recorded before final sweeps.
- `patches_final`: all 12 final worker batches / 94 patch cases; `contact_cases`: 12 contact references and negative controls.
- `coupon_damage_topology.json`: exact bond removal assembled from coupon damage, component sizes and one-bond-remaining rejection.
- `summary.json`: energy errors, increment/dt comparisons, resources and explicit false full-model validation flags.
- `tests.txt` and `test_summary.json`: **36 tests pass**, comprising nine new contact/coupon tests and 27 existing geometry/constitutive tests. No forbidden simulator modules were imported.
- `source`, `baseline_hashes.json` and `preservation.json`: source provenance and unchanged-file checks. The preliminary diagnostic-control eligibility mismatch and corrected preliminary run are retained separately; they do not enter the final totals.

Final patch/contact workers took 26.45 s total, serially, with peak RSS 103.19 MiB. They retained the shared controller lock, one BLAS thread, 512 MiB address-space, 45 s CPU and 55 s wall caps. The simulator startup reserve and runtime warning/hard-stop safeguards are unchanged. No GPU runtime was allocated by these checks.

## Remaining gate and recommendation

The requested **full deformable blade-contact, bond-breaking and non-pass-through cut test remains inconclusive/not demonstrated**, because the necessary coupled solver is absent. Coupon success cannot be promoted to that result. The blade trajectory and damage were never applied to the full deformable tomato, and general post-separation contact was not evaluated.

Next offline development should extract and verify the actual knife surface/edge geometry, then connect the refined same-side spring/volume mechanics, real interface bundle forces, irreversible committed damage updates and current-geometry blade/cut-face contact in one bounded nodal solver. Start with damage-disabled indentation and reclosure coupons, including rotated/rim and tangential cases; only after those pass attempt progressive cutting with the original disclosed fixture and a free slice. Keep full energy accounting, swept-crossing rejection, unchanged numerical/grasp criteria and a real one-second independent release observation. No simulator launch or training is authorized or implied by this report.
