# Source-only native step binding — UNEXECUTED

Read SolverVBD.step/reset, initialization and finalize paths and the particle
forward_step kernel as text. Added tomato_native_step.py binding for the isolated
single rigid blade body. It applies the fixed reviewed cyclic orientation,
clears forces, generates contacts, solves, observes and only then swaps states.
Previous body history is cloned before the step; first-step pose rebaselines
from input. Particle forward_step writes particle_q_prev from input positions,
while finalization computes velocity without advancing that history. This is
source-grounded reasoning, not validated native timing behavior.

Six new pure event-order/static/default-refusal tests plus eight observer layout
regressions pass (14 total). No native function called with authorization, no
Warp decorator/compiler/kernel executed, no simulator imported. Static syntax
cannot establish actual buffer dtypes/shapes, compilation or physical response.
The CLI execution route remains disabled. Existing robot/controller unchanged.

Binding supports exactly one rigid body and fixed orientation, isolates soft
contacts, checks retained stream/per-body adjacency and refuses saturation.
Observer outputs world force then world moment about COM. It still requires
shape/array/barycentric finite and size validation, source-pinned native smoke,
full body COM world coordinates and velocity/reference metadata in exported
records, independent geometry/contact/energy acceptance and resource integration.
Output native_physics_pass is alwaysFalse: logging alone cannot pass physics.
First/reset histories must be validated at runtime; reconstruct/reset explicitly
rather than toggling first_step mid-episode. Do not use rigid-only collector.

Next P6f: build two independent finite diagnostic blocks with explicit separate
node/triangle/spring registries, no cross-cut connections, outward cut faces and
physical gap. This is a prescribed separated-cohesion contact control, not a
successful cut. Include reclosure/opening/slide/rim cases and explicit pair
filters; own-side adjacency exclusions must not hide opposing cut faces.
Inspect actual VBD self-contact/collision initialization before native builder
source. Keep one-thread/512MiB tests and native execution disabled.

After the two-piece preparation, finish dedicated native guard monitoring/
checkpoint configuration and source/asset authorization manifests, then the
staged evaluator, baseline/RL pure logic and post-upgrade runbook. All remaining
runtime contact, constitutive transfer, independent release and robot-coupling
gates stay unverified. Do not substitute more tiny insertion progression.
