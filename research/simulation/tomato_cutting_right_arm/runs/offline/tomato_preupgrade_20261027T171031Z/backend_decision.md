# Source-grounded coupon route and load-sample boundary

Status: offline preparation completed for the initial route decision; native
runtime and robot adoption remain unverified. All exact source hashes are in
coupling_sources.json. The selected candidate is an isolated Newton VBD contact
coupon with its real full-surface contact prerequisites, not whole-robot migration.

## Inspected findings

- solver_vbd.py:1271–1376 implements coupling_harvest_proxy_wrenches. Rigid and
  body-particle contacts take different paths; collect_rigid_contact_forces alone
  cannot provide the deformable blade reaction. The soft harvest at 1340 uses
  the same truncated per-body adjacency list as the solver. Reported reaction
  agreement alone therefore cannot prove contact completeness.
- vbd_coupling_kernels.py:128–130 shifts rigid contact torque about world COM
  using (contact_point - COM) cross force and writes spatial_vector(force,torque).
  Lines188–234 apply the same world-COM convention to body-particle harvest.
  Do not confuse this with an angular-first spatial convention or a joint-anchor
  sensor moment. Flags and mappings in these paths concern proxy bodies; do not
  treat them as a generic prescribed-body collector without verifying preconditions.
- solver_vbd.py:3639–3691 documents the RIGID-contact collector: world contact
  points in metres and force ON body1 in N, after step with the same contact buffer
  and correct previous-pose snapshot. Iterate only to active count; sentinel/zero
  output can mean missing/undersized state, not an absence-of-contact proof.
- coupled/interface.py defines Newton coupling hooks. solver_coupled.py:226–229
  requires CouplingInterface and entries construct Newton SolverBase objects from
  ModelView. This is no evidence that existing Isaac CPU PhysX is a supported
  endpoint. Whole-hand integration remains BLOCKED pending a supported route.
- Full-surface VBD rigid SDF contacts and finite cut-face self-contact require the
  independent completeness/exclusion tests from the contact plan.

## Implementation completed this session

rl/tomato_load_samples.py adds explicit body/interaction, step and time interval,
SI load versus impulse conventions, declared component ordering and common-origin
normalization using the preserved wrench reference. It rejects stale/mismatched
pairs, missing or duplicate steps, trace gaps, undeclared units and nonfinite data.
Ten analytic tests pass under original caps and shared locks. These fixtures
validate data handling, not native contact or force extraction. Impulse division
returns step-average load; it must not be mislabeled as instantaneous force.

## Next exact work

Implement a separate integrated-work ledger and explicit reset/history registry,
reusing the new samples and existing material functions. Test missing samples,
sampling convention, changing reference points, energy signs, no healing and
incomplete resets with tiny synthetic fixtures. In parallel scope (serial work),
inspect installed VBD examples for a supported isolated soft-reaction collector
and real knife/SDF setup. If no suitable collection path is exposed, preserve the
blocker and prepare the smallest coupon that can establish it after the upgrade.
Do not implement a speculative PhysX/Newton bridge or call proxy hooks without
their required owner, flags and model mappings.
