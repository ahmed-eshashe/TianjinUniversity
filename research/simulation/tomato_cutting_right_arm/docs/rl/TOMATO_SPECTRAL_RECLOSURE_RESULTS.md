# Supported reclosure after the two-failed-patch cut

26 October 2026, 04:38 UTC. Local NumPy/SciPy quasistatic diagnostics only.

**The interrupted-cut withdrawal and blade-cleared supported reclosure gates now pass from the actual two-failed-patch state.** This is not a full cut or an independently released slice: two of 47 cohesive patches are completely failed, 45 remain active, and the material graph has one component.

## What was tested

The withdrawal follows the independently accepted forward checkpoint at 8.84375 mm insertion. Its complete predecessor chain contains 388 accepted states, including the initial same-position hold. The blade returns to zero depth without any change in all 47 damage/history records. The zero-depth trial initially cycled numerically; a new target-specific numerical guess recovered convergence, then the original physical worker and independent auditor accepted the endpoint. The guess itself was never accepted as a physical state.

Zero insertion still places the edge at the cut apex. A separate clearance step then moves the blade to 1 mm above the whole tomato's rest maximum height, engages the disclosed slice back-cap support at zero drive, and independently checks support engagement displacement, negligible old edge load, swept contact, energy and physical stability. This is a supported diagnostic, not free slice motion or robot control.

Ten accepted phases use support drive 0, +0.025, +0.05, +0.025, 0, -0.025, -0.05, -0.025, 0, 0 mm. Positive drive compresses the interface; negative drive reopens it. Every endpoint passes a physical worker, independent recomputation and saved source/state/history qualification.

| Check | Result |
|---|---:|
| Compression at +0.05 mm: fixture reaction | 0.0172473469743 N |
| Compression: cut-face contact force | 0.0172473469859 N |
| Compression: maximum face gap | 0 m |
| Reopening at -0.05 mm: maximum gap | 11.5567291 micrometres |
| Final maximum face gap | 8.75688410673e-15 m |
| Worst swept gap over cycle | -9.41260958065e-14 m, within original 1 nm allowance |
| Minimum measured blade clearance | 0.997369643 mm, above original 0.5 mm gate |
| Blade contact load | Exactly zero in every accepted phase |
| Maximum reclosure work residual fraction | 0.000290116888952, below original 1% gate |
| Peak worker resident memory | 214564864 bytes |
| Damage/history | Exactly unchanged for all 47 patches |
| Final stored elastic energy | 2.24269611938e-26 J; returns within original 1e-12 J check |

## What changed in the software

Original qualified workers, physical laws, collision geometry, material parameters, controller, grasp criteria and safeguards remain unchanged. Separate spectral-source-compatible reclosure worker/auditor copies add the current backend identifiers and strict source/state transition provenance. The worker uses the already qualified spectral numerical solver; the independent auditor retains the original physical expressions. Exact history equality is an additional diagnostic stop. Thirteen source/provenance tests pass, including negative cases and exact comparison proving the allowed numerical/provenance edits account for all changes to the original physical worker/auditor.

The first return-to-zero reclosure attempt (phase08_cycle) repeats an uncommitted optimizer state and remains unaccepted. A bounded frozen-history numerical guess improves the residual from 2.26344e-7 to 1.12079e-8, with lower energy, in 1.81 seconds and 207003648 bytes peak resident memory. phase08_seeded then passes the unchanged physical worker and independent auditor; phase09_hold also passes. The first recovery helper stopped before numerical work because it referenced the old tests filename; its source/log are retained. A separately archived v2 corrects only that reference. Separate seed provenance qualification passes.

A positive-infinity minimum polygon gap is permitted only for the independently empty blade clipping query, with zero blade contact load and measured blade clearance; all mechanical state values remain finite. This is the existing cleared-blade sentinel convention, not a relaxed contact threshold.

## Limits and next step

The model remains a guided, frictionless, synthetic quasistatic spring/cohesive model, not a native Newton/Isaac simulation or a calibrated real tomato. No gravity, board-contact dynamics, robot integration, native simulator imports or training are demonstrated. The support intentionally constrains the slice during this diagnostic.

All original per-worker limits remain: 512 MiB address space, 45 CPU seconds, 55-second alarm, 60-second parent timeout, one numerical thread, common nonblocking locks and at most 12 calls per endpoint. RAM/VRAM startup safeguards and frozen grasp criteria remain unchanged. Actual account quota is checked before/after each endpoint; latest reported window is 10% used / 90% remaining, missing secondary unknown. Hard stop remains 04:54:40 UTC.

Resume deeper insertion only from the original forward checkpoint, not from this fixture-controlled reclosure state. That trial and a 0.015625 mm interval were subsequently rejected for swept contact. The 0.0078125 mm trial remains an uncommitted candidate. See OVERNIGHT_FINAL_HANDOFF.md for exact state and next test. On contact/work failure halve the interval from the accepted predecessor; on unresolved physical instability stop. Full cut still requires all patches failed, a two-component material graph and independent motion/contact checks; depth alone never proves release.

Evidence: runs/offline/tomato_spectral_reclosure_01/qualification.json and seed_qualification.json. Last accepted reclosure: runs/offline/tomato_spectral_reclosure_01/phase09_hold/attempt000. Original forward checkpoint: runs/offline/tomato_curvature_search_01/insertion26_small_global/attempt004.

Overnight work stopped before the hard deadline; heartbeat PAUSED. Fullcut and release remain unvalidated.
