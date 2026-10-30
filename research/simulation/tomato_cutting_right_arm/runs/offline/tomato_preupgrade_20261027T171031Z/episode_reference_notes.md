# Episode reset/history contract: tested reference, not native reset

Eleven synthetic tests pass for an explicit JSON episode export, deep expected
reset snapshots, exact state comparison and no-healing transitions. The export
covers positions, velocities, damage/kappa, edge hits, contact multipliers/active
IDs/eligibility, declared backend histories, work ledger, phase clock, previous
action, random state and topology. Metadata includes episode identity and seed.
The original DamageState fields are read from tomato_bonds.py:40–42; accepted
versus trial state separation is visible in offline_tomato_search_evolution.py.
Original sources were inspected but not modified.

A reset expected-export is only a comparison oracle. It does NOT write arrays,
restore solver buffers or reset a simulator. Its backend_state_fields must
match the exported history keys and include known pose/contact/coupling classes.
A future adapter must inspect and declare all additional actual buffers; unknown
omitted engine state cannot be detected by comparing partial exports. Empty
synthetic history lists are fixtures, not evidence a native buffer is empty.
Geometry dimensions and constitutive eligibility detection remain separate checks.

Within an episode, damage and maximum-opening history cannot decrease. Without
eligible local loading, and during the supported withdrawal/reclosure protocol,
those histories must remain exact. This helper does not compute the constitutive
law or make arbitrary D/kappa increases physically acceptable. Native adapters
must enforce the existing law, real contact eligibility, stable patch identity
and work audits. Across episodes, only an explicit reset can restore the chosen
baseline; expected_reset requires a new identity and the same captured seed.
A different random seed requires its own separately generated baseline rather
than relabelling random state. Reset to an interrupted baseline is distinguishable
from a fresh undamaged tomato and is not a splice into forward history.

Next priority P2: map existing conforming surface/design and patch-energy
registries into candidate backend assets and contact pair classes. Reuse existing
geometry; preserve true blade dimensions and cut-face adjacency. Then prepare
P5 dedicated guard and source-only P6 native coupons, with execution disabled.
