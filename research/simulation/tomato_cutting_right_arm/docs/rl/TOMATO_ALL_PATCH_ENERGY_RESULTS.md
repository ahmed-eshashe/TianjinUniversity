# All tomato patch energy test results

Date: 19 October 2026. All **47 actual tomato interface patches** pass opening and shear fracture-energy checks at the unchanged 1% tolerance. This comprises **235 cases**: opening, positive/negative y shear and positive/negative z shear for each patch. No damage-law changes or per-mode fracture-energy fitting were required.

## Geometry and material scope

The sweep reads the original `runs/offline/tomato_layout_02/layout.json` rather than rebuilding a five-spring idealization. It uses all 403 registered interface bonds and each patch's saved area. Each actual rest vector is oriented from slice to remainder; patch ownership and all vectors were independently checked against original node positions. Every patch ID from 0 to 46 appears once. The fixed layout hash is `7d9b1b469c5b34ddfb291924bb4bb91f66d82634e3bdb16037f515650529a671`.

Both flesh and effective-skin-labelled patches use the same explicitly synthetic engineering material for this test: reference stiffness per area 4e7 N/m³, reference peak traction 40 kPa and fracture energy 80 J/m². These values are not calibrated tomato data and do not replace the provisional material registry. Per-patch equal bond stiffness is normalized so its initial opening tangent equals the patch reference stiffness; the same stiffness allocation is used for all five loading directions. No separate shear scaling or area budget per spring is introduced.

The corrected law derives the equivalent damage coordinate from the actual undamaged bundle energy. Each case prescribes a translation of one patch side, with no dynamics or blade. Contact eligibility is supplied as true; it is not inferred from simulated contact. Loading uses a 12 mm maximum path with 2,400 prescribed increments and stops at exact full damage. Frame is the original interface frame. This does not test the deforming whole tomato, collisions, damage locality or contact detection.

## Per-mode results

Both integrated force-displacement work and fixed-geometry damage energy loss must remain within 1% of Gc times the patch area. Every case reaches D=1 and has exactly zero residual elastic force, stored energy and cohesive damping force when checked with nonzero relative velocity.

| Mode | Passes | Largest absolute work error | Largest absolute damage-energy error |
| --- | --- | --- | --- |
| opening | 47/47 | 0.00017% (patch 8) | 0.2639% (patch 44) |
| shear_y_positive | 47/47 | 0.00011% (patch 45) | 0.2123% (patch 42) |
| shear_y_negative | 47/47 | 0.00011% (patch 1) | 0.2178% (patch 0) |
| shear_z_positive | 47/47 | 0.00010% (patch 44) | 0.2178% (patch 26) |
| shear_z_negative | 47/47 | 0.00010% (patch 42) | 0.2178% (patch 20) |

Detailed values, bond IDs, vectors, stiffnesses, failure displacements and maximum damage increments for every patch are in each batch's `summary.json`. `summary.json` at the sweep root collects coverage, per-mode totals and worst cases. All patches share one patch-area energy budget; totals can therefore be checked against 80 J/m² times the complete cut area.

Small positive damage-energy errors arise from evaluating finite damage increments at committed geometry; no tolerance was relaxed. The opening and shear work checks integrate vector force dotted with actual imposed displacement, independently of the damage energy coordinate. The earlier single-patch unloading, mixed-mode and no-contact tests remain historical evidence; this sweep adds actual-geometry coverage rather than claiming those histories were repeated for every patch.

## Resources and preservation

Runs were split into six serial batches of at most eight patches, each with the common controller lock, 256 MiB address-space ceiling, 30 s CPU limit and 45 s wall limit. Total measured batch runtime was 11.78 s; maximum process VmHWM was 31.57 MiB. No Newton, Warp, Torch, Isaac or USD module was imported by the runners. No simulator or training process was launched.

All 171 pre-existing non-cache files checked under `rl` and `docs/rl` retain their hashes. The corrected damage law, original layout, existing controller, memory watchdog, frozen grasp criteria and draft slicing criteria remain unchanged. Only a new offline sweep runner and its result artifacts were added. Matching source snapshots and baseline hashes are saved with the results.

## Interpretation and next gate

The energy law now passes on every actual patch geometry under the tested isolated opening/shear paths. It remains an uncalibrated constitutive model. This does not demonstrate that a blade can resolve contact, initiate local damage, cut through the bottom skin or release a slice without interpenetration.

Next work should address the contact-coupon design and explicit compression/cut-face handling before any later guarded physics experiment. The simulator and full training remain paused; neither is authorized by this result.
