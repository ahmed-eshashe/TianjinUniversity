# Smallest future coupling and grasp-under-load gate

Source inspection only, 2026-10-27 20:24 UTC. Execution disabled. No controller,
backend, frozen criterion, material or robot scene was changed.

## Supported-source boundary

`rl/native_env.py` configures Isaac Lab PhysX on CPU at dt=1/240. The inspected
Newton `SolverCoupled` requires solver instances implementing `CouplingInterface`
and constructs Newton ModelView/State ownership mappings. No adapter from this
existing CPU PhysX robot endpoint to those Newton views/hooks was identified in
the inspected project code. This is an unresolved integration prerequisite;
RAM does not supply it.

Installed Newton XPBD/VBD and MuJoCo/VBD examples use the **experimental**
`SolverCoupledProxy`, not a PhysX bridge. The XPBD/VBD example is particles/cloth;
the MuJoCo/VBD example offers MuJoCo or Kamino rigid solvers. Source presence is
not execution evidence and those examples cannot validate our robot. They are
source leads for an isolated native load-transfer diagnostic only. Do not run the
full examples: they include capture/viewer paths outside the bounded worker.
Do not migrate the robot to MuJoCo/Kamino/XPBD under this preparation approval.

## Diagnostic A: native-only load transfer, separate from the hand

After separate runtime authorization and a reviewed supported-endpoint decision:
use one rigid proxy and the small nonfracturing deformable coupon, one environment,
no robot, no learner, no camera and a 60-second total worker budget. Start with
zero contact and gravity accounted explicitly. Run disclosed prescribed contact
and compare a responsive free rigid body with a clearly labelled kinematic
control. Retain body/proxy/particle local-to-global identity maps and source hashes.

Record both directions: contact force/moment on the rigid body and separately
observed deformable response; rigid pre/post COM momentum and angular momentum;
known applied actuator/fixture/gravity impulses; synchronized positions, twists,
contact candidates and retained records. Do not count a helper that reconstructs
the same solver contact list as independent validation. Momentum response must
change when transfer is disabled in the negative control. A computed equal-and-
opposite pair alone does not establish coupling.

The proxy example harvests response across coupled steps. Record that latency
and sample intervals explicitly; do not compare one engine's current load with
the other's next-step response as if simultaneous. Track energy transfer and
separate N and N m residuals with justified scoped tolerances. First/reset and
interrupted histories need real native rebaseline evidence. The diagnostic only
qualifies its own chosen solver pair and model; it proves no PhysX hand endpoint.

No numeric load envelope or new acceptance threshold is selected here. Loads must
come from validated contact mechanics or a disclosed diagnostic input with its
own justification. Existing SI/origin/time/work contracts provide bookkeeping,
not proof the transfer hooks work.

## Diagnostic B: existing robot grasp under actual cutting loads

First identify a supported two-way endpoint for the actual robot. Until that is
resolved, this diagnostic is blocked. Merely displaying both engines together,
replaying a prescribed blade trajectory, or applying a recorded wrench one way
cannot establish closed-loop two-way cutting interaction.

Preserve `docs/rl/phase3_grasp_criteria.json` and `rl/grasp_metrics.py` exactly.
The frozen gate retains 0.05 m lift, 3 s continuous unsupported hold, <=0.01 m
relative slip, palm support, opposed thumb, >=3 wrapping fingers and >=2 inner
finger contacts. The exact file additionally fixes contact/support thresholds,
clearance, curl and opposition/enclosure predicates. Blade contact, attachment,
unsafe events, joint limits or full contact buffers invalidate the episode.

Earlier reports explicitly state no full central-grasp attempt satisfied this
gate; a successful pickup or cutting-load hold must not be assumed. Supporting
knife gravity is insufficient for cutting forces/moments. Add angular drift as a
separate diagnostic without changing the frozen slip definition. Any supported
or near-wrap reset must stay separate from valid flat-start pickup success.

Only after the unmodified oracle agrees with physical/visual contact evidence,
unsupported hold and cutting reactions may the baseline cutting task be tested.
Sensor axes, wrist measurement provenance, bandwidth/latency and actuator limits
remain hardware gates; actor wrist force/torque channels stay off. No training
follows automatically from either diagnostic.

## Required later decision

Choose and authorize a supported robot/physics integration route based on actual
endpoint evidence. This preparation does not infer permission for migration or a
new co-simulation framework. Until the route and frozen grasp checks pass, the
readiness statement is: isolated mechanics preparation exists; robot cutting and
training are not validated.
