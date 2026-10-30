# Integrated work reference: scope and next adapter responsibilities

The new pure Python module integrates step-average loads against a declared
constant step twist. For example 2 N times 0.5 m/s plus 3 N m times 2 rad/s over
0.1 s yields 0.7 J. Reversing motion returns signed work. Twelve new analytic
cases plus ten load-sample regressions pass under the unchanged capped worker.
These tests use synthetic fixtures, not native contact or motion measurements.

The ledger keeps elastic/kinetic/gravitational storage, tool/fixture/other
external work, and fracture/friction/damping dissipation explicit. Gravity is
potential storage in this boundary convention, preventing double counting it as
an additional external-work channel. A zero-activity balanced ledger is explicitly
flagged and does not establish physical cutting or a meaningful loading case.

The normalized residual uses max(abs(total external work), abs(storage change)
+ dissipation). This is a NEW reference diagnostic and does not replace the
original physical auditors, fracture-specific denominator, or their acceptance
expressions. The helper refuses tolerances above existing 1%/1e-12 J ceilings;
that restriction alone does not establish equivalence or native applicability.
Native channels and convergence must be specified and checked independently.
Do not feed step-average force and a varying unmeasured within-step velocity
into this rule and call its answer exact. Timestep/refinement and energy-channel
completeness remain native runtime gates.

NEXT: P4 explicit full episode reset and irreversible damage/history registry.
Inspect DamageState and accepted/candidate schemas in existing sources. Use a
separate adapter contract, not edits to the hashed physical implementation.
Reset needs material history, eligibility, contact/multipliers, solver pose
history, work sums, stage clocks and randomization/episode provenance. Returning
joint positions alone is not a full reset. Preserve accepted forward history.
