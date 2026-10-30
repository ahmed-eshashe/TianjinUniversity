# Offline blade contact and fracture energy results

**Blade contact is coupled to irreversible patch damage, and the bounded offline partial-insertion test passes its fracture-energy checks.** Two of the 47 patches begin damage under the surrogate wedge; at 4 mm insertion the maximum internal damage variable is 0.187862. None reaches complete failure. This is a shallow fixed-normal interface test, not a full cut, a detached slice or native simulator validation.

**All 74 tests, 94 independent blade/patch energy histories and 27 saved full-node states pass.** The 27 states comprise 17 insertion checkpoints at 0.25 mm spacing, two no-contact states, and eight refined damage-onset checkpoints at 0.0625 mm spacing. The first damaged refined checkpoint is at 3.625 mm, bracketed by the undamaged 3.5625 mm state. Insertion depth is measured from the crest of the prescribed cut face, not the visual tomato crown.

## Measured validation results

Over the 3.5 → 4.0 mm damage interval, the refined work ledger is:

| Quantity | Energy J |
|---|---:|
| Blade work | 0.0011235030167 |
| Increase in stored elastic and volume-protection energy | 0.00082087468574 |
| Exact constitutive fracture dissipation | 0.00030281674825 |
| Work minus stored energy minus fracture loss | -1.88417286083e-07 |

The residual is **0.062222% of fracture dissipation**, below the unchanged 1% gate. With the 0.25 mm steps it is 0.339763%. Quartering the step reduces the fracture-normalized error, while the final maximum damage differs by only 5.656e-10; no material parameter is fitted to obtain this agreement. The ledger starts at the common, independently equilibrated 3.5 mm undamaged state so that earlier elastic quadrature error cannot hide within the fracture comparison. The original cumulative total-energy checks also pass at every endpoint.

| Full-node check across accepted states | Result |
|---|---:|
| Maximum recomputed normalized force residual | 4.943e-08 (limit 1e-6) |
| Maximum cumulative total-energy residual | 0.309354% (limit 1%) |
| Minimum swept local volume ratio J | 0.478607 (floor 0.1) |
| Minimum normalized softening tangent eigenvalue | 0.001198634 (limit 1e-6) |
| Maximum contact penetration within numerical tolerance | 0 m (limit 1e-9 m) |
| Maximum actual cut-face penetration within numerical tolerance | 0 m (limit 1e-9 m) |
| Minimum surface area ratio and normal cosine | 0.807898, 0.625014 |
| Proper surface intersections at checked midpoints and endpoints | 0 |
| Maximum force and moment balance fractions | 1.264e-09, 5.271e-10 (limit 0.01) |
| Peak contact-worker RSS | 184.89 MiB |
| Longest accepted contact worker | 26.28 s |
| Sum of accepted contact-worker runtimes | 231.95 s |

The independent audit recomputes energy, fracture loss, contact eligibility, force residual, support/guide positions, actual cut gaps and surface orientation from saved positions, multipliers and history; it also checks checkpoint and source hashes. All 27 pass. No-contact motion from zero to 4 mm leaves damage and stored energy exactly zero.

The 74 tests consist of 14 new blade/damage tests and 60 existing cohesive/contact/volume regressions. New checks cover both contact-force signs, redundant constraints, edge plus current-load eligibility, preloaded no-edge rejection, below-onset history, rollback of tentative states, no healing, held-state irreversibility, exact fracture dissipation and consistent loading/history-boundary tangent derivatives. Face-rubbing/no-edge rejection is a synthetic gate-level control with edge history disabled; arbitrary 3D face rubbing is not validated.

All 47 supported local patches pass insertion/withdrawal at both 2,400 and 4,800 loading increments: 94 histories. Maximum net-work error is 1.299e-12% of the prescribed fracture budget; opening work and blade virtual work differ by at most 5.204e-17 J. The separately recorded explicit damage-jump quadrature differs from the budget by at most 0.115603%, and that difference halves under step refinement. This reference validates the energy kernel, not full-tomato release.


## Contact driven damage

The restricted wedge test uses the refined 4,032-node tomato, unchanged same-piece springs and volume protection, and all 47 surface-cohesive patches. The remainder fixture and fixed y/z cut-face guides are unchanged. No hand, controller or physical asset is modified.

A prescribed finite wedge advances down the predefined interface. For each matched surface vertex pair, its width is the positive part of `(z - tip_z) * thickness / bevel_length`, capped by the surrogate thickness. Separate unilateral constraints push the slice face toward negative x and remainder face toward positive x; cut-face nonpenetration remains independent of damage. At positive wedge width, the two blade halfspaces already imply a gap at least equal to that width, so the redundant closed-face row is inactive. Ahead of the edge, and again when the wedge withdraws, ordinary cut-face contact applies. Actual cut gaps are checked independently. Contacts with zero wedge width are absent rather than an invisible plane ahead of the edge.

This is still the previously disclosed surrogate: envelope length 265.93 mm, height 50.44 mm, unverified maximum thickness 7.609 mm and synthetic 8 mm bevel. It is not the measured physical knife edge. The shallow run is limited to 4 mm insertion and cannot pass complete-interface failure as a successful endpoint.

A patch is eligible for damage only when at least one of its eight weighted material sites has both a swept cutting-edge encounter and a current positive blade multiplier above 1e-9 N. An edge encounter is retained as history, but cannot authorize damage after contact load disappears. Opening/shear energy then determines the irreversible damage increment through the existing bilinear law; depth, elapsed time and a manual damage schedule do not determine failure. Eligibility is based on fixed cut-plane edge sweeps and current facet loads, not a general 3D knife-edge collision detector. Only opening-driven blade damage is tested here; compression-plus-shear fracture remains unsupported and rejected. Shared patch damage remains a nonlocal approximation: one contacted support can enable the patch's common energy budget. Spatial crack-front accuracy is not established.

For every endpoint, contact equilibrium and damage are iterated using trial states calculated from the last committed history. Optimization guesses do not accumulate irreversible damage. Geometry, damage and edge history become continuation inputs only after the endpoint passes its checks. Below-onset kappa history is preserved even when damage remains zero. Stopping or unloading cannot heal the interface.

`rl/tomato_blade_damage.py` supplies eligibility, exact fracture dissipation, patch-specific damage and the consistent softening tangent. `rl/offline_tomato_blade_damage.py` connects these to full-node equilibrium. The base cohesive class gains a patch-damage accessor whose default preserves its frozen-damage behaviour. The contact solver gains the negative-x blade constraint, initializes touching contacts in the constrained space, and excludes strictly dominated cut rows from active equalities. This prevents incompatible ties and inappropriate unconstrained linearization without changing endpoint tolerances. Optional cached positions are optimization guesses only; they cannot supply or overwrite committed damage/history, and all endpoint checks are rerun. No native runtime integration is installed or enabled.

## Fracture energy accounting

For onset `a`, failure opening `b`, patch stiffness `Kn` and committed maximum equivalent opening `kappa`, the exact cumulative dissipation on the bilinear loading envelope is:

`Dissipation = Kn*a*b/(2*(b-a)) * (clip(kappa, a, b) - a)`

At complete failure this is `Kn*a*b/2 = patch_area*Gc`. The parameters remain synthetic: opening stiffness per area 4e7 Pa/m, peak traction 40 kPa and fracture energy 80 J/m². No material retuning or energy rescaling is used.

Blade work is integrated from unilateral contact multipliers and geometric facet motion. The full-node ledger checks `blade work - stored-energy change - exact fracture dissipation`; fixed supports do no work. The existing 1% relative energy gate plus 1e-12 J absolute allowance is retained. The frozen numerical gates also retain 1e-6 relative equilibrium residual, 1e-9 m penetration tolerance, J >= 0.1, and positive normalized stability eigenvalue >= 1e-6.

The larger elastic energy drop produced by an explicit fixed-geometry damage jump is recorded separately in the reference coupons. It is not silently counted as physical fracture loss. Late activation of a preloaded patch can produce a jump larger than the constitutive dissipation; a unit test checks that distinction. The total work ledger must reject unaccounted loss rather than hide it as damping or fracture.

The stability check includes the negative rank-one softening correction for active damage loading, rather than checking only a frozen-damage elastic Hessian. It is evaluated with fixed geometric eligibility and strong-contact constraints; it is a local supported-coupon screen, not a general crack-propagation or dynamics stability proof.

## Independent reference coupons

All 47 revised surface patches are tested with unilateral wedge-driven uniform opening and return at two increment resolutions. Each local reference adds a disclosed elastic support of stiffness 0.5 Kn in parallel with its cohesive patch, making the displacement-controlled softening branch stable. This support is specific to the analytical reference and is not added to the full tomato model.

Opening work, reconstructed vertical blade virtual work, recoverable support/interface energy, exact constitutive fracture loss and explicit fixed-geometry damage loss are recorded separately. At the end of insertion and withdrawal, the support energy returns to zero and net work must equal the patch fracture budget. These independently supported histories are not assembled into a claim of one coherent tomato cut or free slice release.

## Scope and safeguards

The tests are quasistatic, frictionless and use fixed material axes and fixed cut-face y/z guides. Blade contact applies fixed-normal facet constraints with actuator work reconstructed from their changing bounds. General oblique force transfer, arbitrary pose/slip, extracted edge geometry, bulk blade collision and unrestricted slice motion remain unvalidated. The matched cut-face interpolation certificate covers this restricted wedge profile; midpoint/endpoint outer-surface intersection screens do not establish general continuous collision detection.

The existing simulator memory guard and frozen grasp criteria remain unchanged. Every numerical worker is serial under the shared controller lock, with one BLAS thread, a 512 MiB address-space cap, 45 s CPU cap and 55 s wall cap. Forbidden runtime imports are checked. No simulator, training, dependency installation or full-cut experiment is run.

Evidence is saved under `runs/offline/tomato_blade_damage_01`. Pilot failures are retained separately from final runs, along with original-source snapshots, individual logs/checkpoints, source hashes, tests and preservation checks. The endpoint command is `.venv-native/bin/python rl/offline_tomato_blade_damage.py --depth-mm ... --mode contact --output ...`, adding `--previous ...` after the initial zero-depth state. Use the recorded single-thread environment and fresh output directories; changed-source continuation is rejected. The independent reference worker is `rl/offline_tomato_blade_energy.py`, restricted to at most eight patches per call and 2,400 or 4,800 loading increments.

## Recommendation before a full cut

Keep the current result as a partial-fracture milestone. The next bounded mechanical gate is full-node partial-damage unloading and reclosure, including continuity when the wedge-covered region becomes ordinary cut contact again. A full-cut experiment additionally needs verified blade edge geometry, general blade/bulk and post-release contact, trustworthy separation detection and a declared independent-release observation. Material identification remains necessary before force/depth values can be interpreted as physical tomato predictions. Full cutting, independent release and native simulator behaviour remain untested.
