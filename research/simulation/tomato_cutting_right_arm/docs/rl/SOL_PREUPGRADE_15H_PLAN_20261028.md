# Sol execution plan: 15-hour preparation before the 32 GB RAM upgrade

Prepared 28 October 2026, Asia/Shanghai. **Status: awaiting user approval.**
The user confirmed 32 GB total RAM after the upgrade and that the 15-hour
window begins when they approve this finished plan. Planning does not start
that clock. This document does not reactivate the paused automation.

## Objective and honest completion boundary

Complete the highest-value offline implementation, tests and launch preparation
for the first guarded tomato mechanics experiment. Prepare the subsequent robot
and learning interfaces. Deliver reproducible evidence and a clear decision on
what can run after the upgrade.

Do not promise a validated cutting simulator or training readiness from offline
tests. Runtime contact, separation, robot coupling, grasp retention and throughput
remain gates after the upgrade. A prepared command or passing mock is not runtime
evidence. If a capability is missing, deliver the smallest reproducible blocker
and a concrete alternative investigation, not a fake implementation.

## Current starting evidence

- Main forward checkpoint: `runs/offline/tomato_curvature_search_01/insertion292_20261027_h1644/attempt005`,
  accepted depth 9.638916015625 mm. Five of 47 patches fully failed, 11 damaged
  including those five; 42 active patches and one connected material component.
  Full cut and independent release are unvalidated.
- Next depth 9.642578125 mm and `insertion293_20261027_h1644/attempt001` are saved
  continuation information, not an accepted new state. Preserve both. Do not
  resume depth advancement as the default activity for this work window.
- Twelve analytic wrench reference tests and seven existing false-separation
  tests passed. Evidence is in `runs/offline/tomato_methods_20261028_01/`.
- Prior withdrawal/reclosure and refinement evidence must retain its original
  scope and branch history. Never splice it into the forward branch or describe
  supported quasistatic reclosure as dynamic free-slice release.
- Installed-source audit identifies possible Newton mechanics/contact paths,
  but no validated native cutting integration. The existing robot task uses
  CPU PhysX; a Newton solver is not a drop-in replacement for its hand constraints.
- The prior depth automation is paused and session status is
  `stopped_priority_change`.

Use these authoritative plans together, with this work order controlling priority:
`TOMATO_SLICING_IMPLEMENTATION_PLAN.md`, `NEWTON_TOMATO_PROTOTYPE_PLAN.md`,
`BLADE_CONTACT_AND_CUT_FACE_TEST_PLAN.md`, and
`TOMATO_METHODS_HANDOFF_20261028.md`. Reconcile other saved results before repeating
experiments. Treat older implementation prohibitions as superseded only for the
offline preparation explicitly approved here; runtime restrictions remain.

## Execution authorization and quota contract

On approval, record actual local UTC as T0 and an immutable deadline T0+15 hours
in a NEW preparation session directory. Record the corresponding Shanghai times.
The new authorization supersedes the earlier window only for this preparation
scope. Do not alter historical deadlines or reuse the insertion driver for a
different task. Update the existing automation through the app tool with the
new scope and deadline; do not create a duplicate or modify its TOML manually.

Use serial, bounded sessions, normally five-minute starts and at most 4.5 minutes
per session. Save resumable work frequently. No numerical worker may overlap
another, including manually launched workers. Reserve time for verification and
handoff; stop starting computational batches at deadline minus 20 minutes, and
use the remaining window to finalize and pause the automation. If preparation
finishes sooner, finalize early rather than inventing work to fill 15 hours.

Obtain actual app usage before each work session and before AND after each
computational batch. Bound each quota request to 20 seconds; never overlap quota
requests or replace a missing reading with an assumed value. Inspect every
reported usage window. Unreported windows remain unknown. At any reported usage
of 45% or more, stop new project work, preserve the current evidence, write the
minimal handoff and pause the automation. This preserves a buffer above the
user's 50%-remaining floor; shared account use cannot be reserved or guaranteed.
Do not buy credits, resets or additional usage.

If quota fails, persist `waiting_quota`, failure count and next probe time with
10/20/40/60-minute backoff. No computation until a fresh reliable reading permits
it. Early wakes launch nothing. A due wake gets one bounded probe. Reconcile
saved in-flight work and hashes before resuming; never rerun used output folders.
Wait time and downtime count against the fixed 15-hour window. Missing quota is
not quota exhaustion. Notify only meaningful milestones, failures or required
user input; keep unchanged scheduled states quiet.

Preserve the existing 512 MiB address-space, 45 s CPU, 55 s alarm, 60 s parent
timeout, one-thread and shared-lock limits for offline computational tests;
keep no more than 12 mechanical calls per batch. Use small fixtures and serial
subsets when a suite does not fit. Do not raise caps to force a pass.

No simulator launch or imports, GPU/JIT warmup, training, dependency installation,
production controller change, backend migration or threshold relaxation during
this window. Inspect installed sources as text. Implement new modules separately;
do not modify source-hashed physical workers or frozen grasp criteria. New
test/worker orchestration must itself have explicit caps, source hashes and the
new deadline; do not remove a historical runner's expired guard.

## Work blocks: 15-hour allocation, not a promise of runtime success

The hour allocations are ceilings and planning priorities, not requirements to
spend every minute. Each task needs code/data evidence and a brief result. Advance
when its exit condition is met; carry unused time into the next priority. Reserve
the final two hours for integration review and handoff.

| Elapsed time | Sol's task and deliverables | Exit condition / fallback |
| --- | --- | --- |
| 0–1 h | Inventory current sources, tests, artifacts, installed metadata and safeguards. Create a requirement/evidence matrix and preserve baseline hashes. | Every required capability marked source-inspected, offline-tested, runtime-unverified or blocked; no duplicate work. |
| 1–3 h | Resolve the candidate simulator route from installed source: supported contact, damage updates, cut-face handling, reaction extraction, hand constraints and force application. Write a backend decision with exact source references and remaining experiments. | A source-grounded mechanics coupon route with explicit unknowns. If robot coupling lacks a supported path, label it blocked and isolate mechanics; do not invent an API or silently change the robot solver. |
| 3–6 h | Implement backend-neutral data contracts and small deterministic checks: geometry/contact pair registry, damage/history, timestamps, force/impulse units, reaction frames, work ledger and reset completeness. Extend existing helpers instead of duplicating them. | Tests reject sign/unit/time errors, hidden cross-cut connections, stale contact, history healing and incomplete resets. Synthetic traces are labelled synthetic. |
| 6–9 h | Prepare isolated native contact-coupon and two-piece-contact worker source, bounded configuration and a dedicated guarded launch route. Keep simulator imports behind the future execution entry point. | Syntax/static checks and offline guard tests pass. Launch remains disabled pending upgrade and runtime authorization. Missing native support produces a specific blocked case, not a stub reported as complete. |
| 9–11 h | Prepare the integrated mechanics experiment's staged state machine and evaluator: rest, indentation, draw/down, stop, withdraw, release. Specify timestep/contact refinement and failure traces. | Timeouts and failed/inconclusive stages cannot advance or award cutting success; damaged/reset states and criteria are explicit. No depth-triggered separation. |
| 11–13 h | Prepare the robot/baseline and RL interface specification plus testable pure logic: observation masks, action bounds, evaluator/reward agreement, episode reset and held-out case manifest. | Tests catch hidden-state leakage, premature success and reset/reward inconsistencies. Existing controller remains unchanged; learning launch is gated and unexecuted. |
| 13–15 h | Integrate artifacts, run only justified capped regression subsets, inspect failures, verify source preservation, write post-upgrade runbook and final readiness report. | Each deliverable has location, test evidence, status and next command or blocker. Automation paused and no worker left running. |

## Backend decision must address these known risks

Read the actual installed code and refresh the old capability record without
importing simulator packages. The blade-contact plan identifies VBD full-surface
contact against rigid SDFs as a candidate; the simple semi-implicit solver does
not consume the same contact records. Verify compatibility of springs, damage
updates, surface collision, force logging and reset for the selected candidate.
Include SDF thin-edge error, cooking cost, contact buffer completeness, exclusion
maps and coincident cut-face behavior. Source presence is not a passing test.

Keep the real knife dimensions and a consistent mass/area/fracture-energy
registry. Never thicken the blade or inflate collision radii to manufacture
contact. Never prescribe full damage and report the resulting contact diagnostic
as a successful cut. Preserve separation between visual, collision and mechanical
geometry while ensuring all derive from the same material coordinates.

For robot integration, identify both directions of force transfer and the exact
supported interfaces. A prescribed blade provides a mechanics experiment; it
does not prove the hand withstands cutting loads. Displaying two engines in one
scene does not establish coupling. No speculative co-simulation framework in
this 15-hour window. If neither native route supports the required coupling,
make that the main readiness blocker and prepare its smallest future experiment.

## Required checks, with useful scope limits

1. Geometry and topology: positive volumes/rest lengths, area/mass accounting,
   correct winding, side labels, complete interface registry and no fixture,
   volume or surface path silently bridging a released interface.
2. Contact: blade vertex/triangle-interior/edge approaches; cut-face closure,
   slide, rim contact, reopening and exactly touching rest state; pair-filter
   completeness and bounded buffer-overflow handling. Offline geometry tests
   support these cases but cannot pass the native contact gate.
3. Constitutive state: no-contact/no-eligibility controls, irreversible damage,
   proper unloading, zero residual cohesive stiffness/damping at full damage,
   intact/partial/full diagnostic states and exact reset of all history fields.
4. Coupling contract: named bodies, declared SI units, frame/origin, timestamp,
   sample interval and force versus impulse convention. Integrate work with a
   declared sampling rule; keep gravity, fixture, actuator, elastic, fracture,
   contact and numerical residual terms distinguishable. Test duplicated/missing
   samples, sign errors and moment shifts. Do not add N and N m into one norm.
5. Evaluation: incomplete cut remains attached; all damage plus graph separation
   still requires independent motion/contact after withdrawal. Require the
   planned one simulated second of release observation; timeout is inconclusive.
6. Learning logic: actor gets only declared deployment-observable channels;
   damage/connectivity/material truth may support the evaluator or privileged
   critic, never silently the actor. Default physical wrist force channels off
   while hardware axes are unknown. Baseline and policy use the same evaluator.

Reuse established physical tolerances exactly. New native-specific tolerances
must be justified and recorded before experiments, with draft versus frozen
status explicit. Do not apply a quasistatic 1 nm gap gate to a different native
penalty solver without a justified contract; equally, do not weaken the old gate
or claim the two models are equivalent. Retain the existing constitutive energy
checks and the prior plans' provisional convergence targets with their scope.

## Resource and launch preparation for 32 GB

32 GB is expected installed host capacity, not measured available memory and not
additional VRAM. Record actual GPU model/VRAM through read-only inspection. After
the upgrade, remeasure resources and verify the runtime/driver environment.
Keep startup floors of at least 10,000,000,000 available RAM bytes and 4 GiB free
VRAM. Preserve runtime warning thresholds of 3,000,000 KiB RAM and 1.5 GiB VRAM,
and hard thresholds of 2,000,000 KiB RAM and 1 GiB VRAM, including monitor-error
shutdown and process-tree cleanup. Increase reserves if evidence requires it;
never lower them to permit a run.

Prepare a dedicated route for the new workload without changing the existing
robot guard/controller. Unit-test refusal, monitor failure, timeout, signal and
child cleanup using tiny dummy processes. A dry-run prints the exact intended
command and refuses simulator execution; it must not perform imports or launch
hidden subprocesses. The future native run is one headless environment with a
60-second worker budget, accounting for startup/JIT/cooking and reporting which
stages did not finish. It does not inherit the offline 512 MiB cap as a claim that
Isaac fits that limit; native protection uses the preserved host/VRAM watchdog.

## Post-upgrade gate sequence

1. Resource and dependency verification, followed by a guarded minimal native
   startup check after explicit runtime authorization.
2. Blade and cut-face coupons, including native reaction/work observations.
3. Nonfracturing indentation, then blade-driven damage and independent release,
   with negative controls, reset checks and resolution comparisons.
4. Robot/hand integration and existing frozen grasp checks under actual cutting
   reactions, then a repeatable conventional baseline and measured sample cost.
5. Only after these pass, request a bounded training budget and run an initial
   learning smoke test; full training remains separately authorized.

Do not skip failed gates to meet the calendar. If only the coupons are ready at
handoff, state that explicitly. Camera perception, left-hand stabilization,
repeated slices, arbitrary fracture and detailed tomato anatomy remain later
milestones from Astra's original plan.

## Completion package and continuation rules

Use a new `runs/offline/tomato_preupgrade_<approval timestamp>/` evidence root and
a preparation journal separate from the old insertion journal. Recommended
deliverables are a capability/decision record, machine-readable requirement
matrix, test reports and source manifest, dedicated worker/config/guard source,
learning-interface contract, exact post-upgrade runbook and final handoff.

Each result must state what was executed, what only received static inspection,
what failed, and what was not attempted. Preserve all failures. Mark placeholders
as incomplete. Do not declare work ready solely because tests on fake backends
passed. Include outstanding hardware sensor/load-calibration inputs without
blocking unrelated offline work or guessing physical safety limits.

At every restart check local UTC, deadline, actual quota, locks, source hashes,
active task and saved outputs. Reconcile before retrying. File edits should be
atomic where practical; never replace accepted evidence with candidates. Keep
the historical insertion driver and paused state preserved. At the final deadline
stop all project work; a later extension requires new user authorization.

No subagents or messages to another chat are implied by this plan. Sol may read
and execute it in this same chat after user approval; messaging a separate Sol
chat requires the user's explicit instruction identifying that destination.
