# Proposed Gate 3 recovery: repair the isolated material/contact update

Status: **proposal only; not implemented or adopted**. Existing Isaac Sim, DiSECt, kitchen, robot, grip, environments and earlier evidence remain unchanged.

## Decision and evidence

Do not spend another long run trying to cut with the v02 prototype. Repair its numerical coupling in a separately named version, then requalify mechanics before further cutting.

The first coupled pilot allowed its reconstructed cells to deform far more than the constitutive strain recorded. Its final stored determinant stayed above 0.990, while the actual reconstructed cell had a negative corner determinant (−0.458). A new independent volume certificate rejects that state. The bounded retest with finer, area-preserving contact sampling stopped at 0.029175 simulated seconds: the next trial's reconstructed determinant was 0.09943, below the retained 0.1 limit. It paid zero fracture area and created no physical cut. Its 0.106 N peak was far below 2 N; raising that force limit would not repair the defect.

A double-precision algebraic control independently reproduced the mechanism: the 512-particle transfer matrix has rank 343 and 169 unresolved particle modes. A nonrigid mode moved particle positions by 0.25 μm in one 12.5 μs step while stored strain changed by only 1.25e−17. The reconstructed material strain changed by 2.56e−5. Pure FLIP retains this motion, and direct particle contact loads can excite it. Contact-force balance and small energy residuals do not make this a trustworthy solid.

Evidence: `reports/null_mode_diagnosis.json`, `reports/geometry_strain_diagnosis.json`, `volume_controls.json`, `runs/paid_cut_refined_guard/result.json`. Saved-frame audits and raw failed states are retained.

## Proposed change

Evaluate an APIC-style particle/grid transfer together with a mechanically consistent material/contact update. The published APIC method addresses accumulated particle velocity modes while retaining linear/angular momentum properties: [Jiang, Schroeder and Teran, 2017](https://arxiv.org/abs/1603.06188). This is a research-supported repair direction, **not proof that APIC is a drop-in fix** for our reference-grid, persistent-cut backend. Its coupling and conservation properties must be derived and tested in this specific implementation.

1. Create v03 and freeze v02. Derive one complete update: particle state, grid transfer, constitutive gradient, constraints, tool contact, fragment contact and cut-history transfer. Use the same discrete velocity map and its adjoint for contact motion and force/work. Do not bypass the represented mechanical degrees of freedom with unchecked particle impulses.
2. Include any affine momentum state in the conserved angular-momentum calculation, checkpoint and reset. Explicitly account for transfer/filtering dissipation; do not relabel removed numerical energy as fracture work.
3. Keep the existing material constants, synthetic Gc, actual blade CAD, area budgets, 2 N limit and 0.1 mm whole-material penetration limit. Keep the independent reconstructed-volume guard. No artificial mass changes, force clipping, deformation clipping, teleportation or early code changes.
4. Preserve persistent history, intact bridges and fragment independence. A published Eulerian APIC result is not evidence that our modified reference-grid history transfer is correct. Derive a compatible extension; stop if this cannot be justified within the bounded attempt.

## Checks and order

First reproduce the null-mode failure and demonstrate its treatment in a small independent CPU reference. Test rigid translation/rotation and affine deformation before GPU implementation. Verify that filtering does not create unexplained energy and that geometry and constitutive deformation respond consistently to localized loading.

Then repeat the applicable Gate 1 and Gate 2 controls, including angular momentum, localized nonuniform deformation, load/unload, intact bridges and moving cut history. Earlier v01 component passes remain historical evidence and cannot automatically qualify the revised algorithm.

Only after those pass, repeat Gate 3 CAD contact, whole-volume bounds, material recontact and force/impulse/work refinement at shared physical times. The finest recontact run made for v02 is not a matched-refinement pass and must not be promoted to one.

Finally retry one paid crack-front patch with a transactional work ledger. A subcell crack front and a whole particle-row topology change must not be confused: paying a small fraction of the row's area cannot authorize opening its full area. If a consistent work/front discretization needs a further physical-model change, report the measured obstacle. Do not tune Gc until the knife passes.

## Budget and stop

One focused formulation/null-mode attempt, up to two hours; up to four further hours of bounded qualification only if that first test succeeds. Retain the 600-second per-pilot cap, making any shorter comparison windows explicit in advance. These are decision budgets, not promises of success or a finished tomato.

Stop and report if conservation, constitutive/geometry consistency, persistent topology or admissible contact still fails after the single diagnosed repair. Do not start another engine, broaden into kitchen work or begin training. A further scope decision is needed if another formulation is required.

## What this would and would not establish

A pass would reopen Gate 3 on a more defensible isolated backend. It would not establish real-tomato calibration, a finished slice, arbitrary cutting paths, robot integration or RL speed. The present full-contact harness is orders of magnitude below the learning throughput target; no speed promise is made. Later development must measure complete step time and memory after correctness is demonstrated.

This is a scope review under the original execution plan's instruction to stop a failed physical candidate and present the concrete blocker. No production setup changes are proposed.
