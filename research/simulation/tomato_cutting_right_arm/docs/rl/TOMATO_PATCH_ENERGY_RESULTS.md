# Offline patch damage correction results

Date: 19 October 2026. The corrected common-patch law passes opening, shear and proportional mixed-mode fracture-energy checks at the unchanged 1% tolerance. All 27 focused tests pass. The legacy scalar-to-bundle mapping is retained as a negative comparison and fails both new opening/shear regression tests when substituted.

## Change and energy basis

The previous mapping used geometric opening/shear magnitude to choose damage, while the actual finite-length oblique springs stored a different amount of energy. It therefore overpredicted opening work by 13.60% and underpredicted shear work by 64.20% in the five-spring coupon.

The new `update_bundle_damage` computes the **actual undamaged sum of spring elastic energies**, U0, for all bonds owned by one patch. It defines an equivalent energy coordinate q = sqrt(2 U0 / Kref), then applies the existing irreversible bilinear damage history to q. Kref, area, reference peak traction and fracture energy remain the same synthetic coupon inputs. No per-mode force correction, fracture-energy retuning or relaxed tolerance is used.

The finite-length spring forces remain their native elastic gradients, scaled by the shared factor (1-D). Because U0 = Kref q²/2, elastic work along a smooth loading path is (1-D) Kref q dq. The scalar reference curve therefore sets one fracture-energy budget for the entire patch, independent of oblique geometry along the tested paths. Area subdivision scales total patch stiffness and energy together, rather than granting each spring a complete area budget.

Kref and peak traction now parameterize the reference energy curve; they do not independently guarantee the actual directional peak force of a nonlinear spring bundle. Matching real normal/shear strength and distinct material fracture energies remains a calibration/model-design task. This change establishes energy consistency for the tested synthetic patch, not tomato material realism.

Damage still requires explicit current contact eligibility from a caller. No-contact updates freeze damage; compression alone freezes damage; rigid rotation produces no opening or stored elastic change. Compression combined with shear is explicitly rejected by this initial coupon interface instead of using compressive energy as fracture work. Objective frame construction, actual blade eligibility detection and compression contact remain unimplemented.

## Results

All three cases have target fracture work **0.002 J** and end at exactly D=1 with zero residual force. Stiffness and damping both vanish at complete failure.

| Coupon | Integrated work J | Work error | Discrete damage-energy error | Unchanged 1% gate |
| --- | --- | --- | --- | --- |
| opening | 0.0019999999 | -0.000003% | 0.0509% | Pass |
| shear | 0.0020000000 | -0.000002% | 0.0310% | Pass |
| mixed | 0.0020000000 | -0.000001% | 0.0421% | Pass |

Work is independently integrated from actual vector force dotted with imposed displacement increments, rather than simply returning Gc times area. Damage dissipation is separately measured as the drop in stored energy at fixed geometry. Its small positive discrepancy is finite-increment quadrature error. Large displacement jumps or abrupt reactivation after contact-gated overload still require substepping and energy checks before dynamic use; the coupon results do not validate arbitrary timesteps.

The original scalar coupon and deliberately uncorrected bundle comparison are still present in the summary, so legacy failures cannot be mistaken for the corrected gate results.

## Validation

Seven new tests supplement the existing 20: opening energy, both shear axes/signs, mixed and nonproportional paths, unloading/reloading work, area subdivision, compression/contact gating with unsupported combinations rejected, and rotation/post-failure residuals. New force-work checks reject the old mapping with assertion failures, not import errors. Existing topology, scalar law, exact zero damping/stiffness and degenerate-length tests continue to pass.

The node layout is unchanged: 979 nodes, 10,510 bonds, 403 cross-cut bonds and 47 patches. No material properties were assigned to those actual tomato bundles. This result is restricted to the synthetic five-spring constitutive coupon; applying the law to all patch geometries and checking strength/convergence remains future offline work.

## Resources and preservation

The bounded runner completed in 4.53 s with peak Linux VmHWM 47.40 MiB. It retained the 256 MiB address-space limit, 30 s CPU limit, 45 s wall deadline and shared controller lock. No Newton, Warp, Torch, Isaac, USD or simulator module was imported by that runner. No simulator or training process was launched.

Only three existing offline sources changed: `rl/tomato_bonds.py`, `rl/offline_tomato_probe.py`, and `rl/tests/test_tomato_offline.py`. All other 167 existing non-cache files checked under `rl` and `docs/rl` retained their hashes, including the memory watchdog, robot controller, layout generator, frozen grasp criteria and draft tomato specifications. Historical run outputs are preserved.

Evidence: `runs/offline/tomato_patch_energy_01/summary.json`, `tests.txt`, `legacy_regression.txt`, before/after source snapshots and `preservation_checks.json`.

The next useful step is offline testing on the actual 47 patch geometries and selecting strength/mode parameters, followed later by blade-contact validation after the memory upgrade. No contact, physical separation or training success is claimed here.
