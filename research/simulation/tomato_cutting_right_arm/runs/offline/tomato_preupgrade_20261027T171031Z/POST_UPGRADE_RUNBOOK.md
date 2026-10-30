# Post-upgrade sequence — working preparation runbook

Updated 2026-10-27 21:03 UTC. This is a working runbook, not a readiness certificate.
Approval remains 2026-10-27 17:10:31 UTC, preparation ends 2026-10-28 08:10:31 UTC.
No native run or training is authorized by this document. The preparation scope
can finish before runtime validation, but a 32 GB upgrade alone does not make
cutting simulation or training ready.

## What is available

Separately authored offline contracts and tests cover SI load samples, work
accounting, declared history/reset, geometry registries, disabled launch and
checkpoint contracts, diagnostic native builder/step/observer source, staged
evaluation, artifact integrity, actor masks/history and residual bounds. Each
session test report names the exact tested source hashes and limitations.

Single-blade and two-piece source factories have not been constructed or compiled
with Newton/Warp. Synthetic solids are not the accepted tomato. The private
solver-derived reaction helper is not an independent physical audit. No source
or synthetic-data test counts as a native pass.

## Current integration status — 21:03 UTC refresh

The immutable detailed snapshot is `integration_gaps_2102.json`; the older
`integration_gaps.json` is historical. Completed offline work includes the exact
hard-disabled command preview, stdlib supervision fixtures, original-law force,
evolution and assembly comparisons, complete lossless 47-patch registry export,
COM/interval metadata, journal prefix verification and independent unsigned
point/facet geometry references. Original-tolerance dependency regressions pass.

The highest-impact unfinished implementation is the native-specific supervisory
route: current fixture resource/checkpoint supervision is not wired to a real
native worker. Prepare and test a disabled integration contract before any later
runtime enablement. Exact native state/checkpoint acknowledgments and actual OS
signal/resource behavior still need runtime evidence.

Native cohesion remains a separate design blocker. Reference mechanics match
original law arithmetic; no supported arbitrary implicit cohesive energy/Hessian
callback has been demonstrated in inspected VBD source. Force injection through
particle_f prediction is not equivalent. Softening tangent/stability requires a
reviewed implementation and physical evidence; no replacement law is authorized.

Endpoint reaction metadata is wired but is not step-average load. Diagnostic
work estimates cannot pass the step-average work ledger. Native buffer/history
completeness, SDF signed values/normals/contact-force completeness, independent
release, real robot endpoint, frozen grasp and throughput remain unverified.

## Gate 1: after installation, read-only hardware and dependency inventory

In `/home/omen/teamwork_projects/tomato_cutting_right_arm`:

```sh
date -u +%Y-%m-%dT%H:%M:%SZ
cat /proc/meminfo
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader,nounits
```

These commands do not import the simulator. Record the actual installed host
memory, available memory, GPU/VRAM, driver and dependency/source versions. Retain
at least 10,000,000,000 available RAM bytes and 4 GiB free VRAM for startup.
Capacity is not availability; the laptop GPU remains separate from host RAM.

Codex must obtain a fresh actual quota reading before a session and before/after
each computational batch. Any reported usage >=45% stops preparation and pauses
the schedule. Missing quota windows remain unknown. Shell commands are not a
substitute for the account usage tool.

## Gate 2: reviewed guarded native startup and coupons

Only after explicit runtime authorization, run one headless environment with a
60-second worker wall budget including imports/JIT/SDF cooking/setup. The final
executable native command is **not yet available**: it must be produced by the
completed guard integration and recorded verbatim in its launch manifest.
Do not use the existing robot guard as an undocumented substitute.

Preserve shared locks, one thread, host warning 3,000,000 KiB and hard stop
2,000,000 KiB; VRAM warning 1.5 GiB and hard stop 1 GiB; three monitor failures
stop; checkpoint and process-tree cleanup evidence required. Twelve mechanical
calls per bounded segment remain the preparation contract; unfinished stages
must be reported as unfinished. Offline 512 MiB protection does not imply a
native engine fits within 512 MiB.

Start with the real authored blade export and separately disclosed synthetic
nonfracturing coupon. Measure SDF signed-distance/normal error and cooking cost,
contact vertex/interior/edge cases and candidate/retained/per-body capacities.
The 434 saved surface probes provide zero-distance reference queries. Grid
estimates at resolution128 are about 2 mm/cell under zero-padding assumptions;
this is neither an SDF error bound nor a successful thin-edge test. Do not change
physical blade thickness or collision radii to force a pass.

Then test two-piece closure, slide, rim, reopening, touching rest and off-plane
negative controls. The challenge registry is disabled and unexecuted. Independent
force/work observations must agree in named SI frames/origins and step intervals.

## Gate 3: preserved mechanics, damage, reset and independent release

Compare the isolated native constitutive adapter against the preserved law under
intact/partial/full diagnostic states and loading/unloading. Retain the original
1% constitutive energy audits; draft native contact budgets require justification
before experiments. Never treat a penalty solver as equivalent to the old
quasistatic 1 nm feasibility gate.

Run rest, nonfracturing indentation, draw/down, stop, withdrawal and release.
No-contact and off-plane controls must not damage untouched material. Timeouts
are inconclusive, incomplete cuts stay attached. Graph disconnection and all
patches failed require independent motion after blade withdrawal, no fixture
bridge and at least one continuously recorded simulated second of observation.
Retain negative results and every source/trace/audit hash. Hash integrity alone
cannot authenticate runtime or establish algorithmic independence.

Compare half timestep and refined geometry/contact settings. Prior plans propose
<10% peak load/work change and <1 mm slice-thickness change, not validated native
tolerances. Exact reset needs every real history buffer, not merely the declared
reference schema. Diagnostic journals currently cannot resume native state.

## Gates 4–5: robot baseline, then separately authorized learning

Validate two-way robot coupling and existing frozen grasp criteria under actual
cutting force and moment. Verify sensor axes/frame/timing; all actor wrist
channels remain disabled. Confirm joint, velocity, acceleration and effort limits
before sending any action reference. Compare drawing and downward baselines with
the same evaluator, held-out physical cases and measured throughput.

Only then request a bounded learning smoke-test budget. No training command is
included: reward calibration, sensing, runtime mechanics and sample cost do not
yet support a training-ready claim. Camera perception, left-hand stabilization,
repeated slices and arbitrary fracture remain later milestones.

## Preserved physical checkpoint

`runs/offline/tomato_curvature_search_01/insertion292_20261027_h1644/attempt005`
at 9.638916015625 mm is preserved. It is not full cut or release. The historical
depth continuation session stays stopped and is never resumed by preparation.

## 19:13 UTC addition — exact disabled worker preview

The following now validates the saved source-bound configuration and prints its
exact command without native imports or subprocess launch. It remains a preview
only; real monitored native execution is still unavailable.

```sh
/home/omen/teamwork_projects/tomato_cutting_right_arm/.venv-native/bin/python /home/omen/teamwork_projects/tomato_cutting_right_arm/rl/tomato_native_worker.py --root /home/omen/teamwork_projects/tomato_cutting_right_arm --config /home/omen/teamwork_projects/tomato_cutting_right_arm/runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config.json --output /home/omen/teamwork_projects/tomato_cutting_right_arm/runs/offline/tomato_preupgrade_20261027T171031Z/FUTURE_NATIVE_OUTPUT_NOT_CREATED
```

This command refuses stale source hashes or reused output directories. It does
not establish runtime authorization or supersede the remaining watchdog gate.

## 19:48 UTC configuration update

The earlier 19:13 snapshot is preserved and intentionally refuses updated source
hashes. The current tested disabled worker configuration is
`single_blade_disabled_worker_config_1947.json`; its exact preview is saved in
`session1947_exact_preview.json`. Substitute that configuration and its unused
output path when previewing. Native execution stays hard-disabled.

## 19:53 UTC source correction and current preview

Prepared kinematic source now prescribes interval-end pose and fixed-orientation
secant velocity, consistent with inspected VBD history finalization. Native
behavior remains untested. The current immutable disabled config is
`single_blade_disabled_worker_config_1952.json`, with exact command in
`session1952_exact_preview.json`; 1947 and earlier snapshots remain historical
and refuse current source hashes. Stationary first interval is mandatory.

## Current disabled preview — 21:03 UTC

Current configuration: `single_blade_disabled_worker_config_2102.json`; tested
exact command: `session2102_exact_preview.json`. All earlier config snapshots
are historical, and may refuse changed source hashes. The command remains
preview-only and execution is hard-disabled even if an authorization flag is
passed to the source function. Future output directory is unused.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /home/omen/teamwork_projects/tomato_cutting_right_arm/.venv-native/bin/python /home/omen/teamwork_projects/tomato_cutting_right_arm/rl/tomato_native_worker.py --root /home/omen/teamwork_projects/tomato_cutting_right_arm --config /home/omen/teamwork_projects/tomato_cutting_right_arm/runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2102.json --output /home/omen/teamwork_projects/tomato_cutting_right_arm/runs/offline/tomato_preupgrade_20261027T171031Z/FUTURE_NATIVE_OUTPUT_2102_NOT_CREATED
```

This validates files and prints a command; it does not launch native packages,
complete a physical stage, or provide a training command.

## Completion review — 21:24 UTC

`requirement_completion_review_2122.json` is the current exit-condition review.
Preparation is not yet complete. Remaining offline items are actual external OS
signal/owned-child cleanup tests, final bindings/affected regressions and final
handoff. Current worker is initial-rest-only:12 steps at1/1200s cover0.01s,
while prescribed coupon trajectory lasts1.2s. Diagnostic checkpoints cannot
resume. Full motion needs reviewed native live-state/chunk or complete-state
continuation; no timestep or12-call-cap loosening is authorized. This limitation
applies even after RAM upgrade until the implementation/runtime gate is resolved.
