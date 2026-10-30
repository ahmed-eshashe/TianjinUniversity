# Soft reaction observer preparation

Eight offline tests pass for retained stream/per-body adjacency consistency,
count/shape validation, saturation refusal, reference-count mismatches, default
factory refusal and source syntax. No Warp module import, decorator execution,
compilation or kernel launch took place. Factory/kernel source is UNEXECUTED.

The planned observer uses version-pinned _eval_soft_ef_contact from installed
rigid_vbd_kernels.py. Its signature was read directly. Corners are -1-padded
particle/edge/face indices, barycentrics define the soft contact point and the
helper returns force-on-particle and the world rigid contact point. Observer
sums negative force-on-particle and moment about each body's world COM, reading
only solver/contact state. It does not mutate contact/material/physical state.
The private helper hash must match before runtime import; dedicated native launch
must also verify the full source/config manifest.

Metadata checks conservatively refuse a full buffer (>=capacity) even if actual
overflow is not observable. Per-body list must contain exactly its retained soft
records without duplicates. Independent reference counts can be supplied but
this is NOT broad-phase completeness proof: matching counts can hide different
candidates and filters may have omitted contacts before the retained stream.
Independent geometry/candidate identity and known small-coupon expectations are
still required. Output invalid flags must make a future runtime inconclusive.

Native arguments remain to be bound and checked for lengths, finite material
values, barycentric validity and matching step/contact identities. Do not treat
Python syntax success as Warp compatibility. Integration still needs full current
and effective previous pose histories, one snapshot/collision/solve/observe cadence,
zeroed bounded outputs and explicit sample metadata. SolverVBD body_q_prev is
advanced by the step; first/reset worlds rebaseline it. Source lines3658–3663
warn to snapshot effective previous poses before step, correcting reset rows.
Particle history and body/kinematic pose paths must be traced independently.
Never simply read the overwritten history after the solve.

Next: P6e source-only step/pose observer binding and two-piece contact construction.
Keep CLI/native execution disabled. Review VBD _predict_particle_inertia,
step ordering, _update_rigid_history and state/history updates around lines
3025,3136–3143,3797–3821. Build finite diagnostic two-piece surfaces with explicit
separate identities and contact filtering/capacity; do not report prescribed D=1
as a cutting success. Native guard still needs real monitoring/checkpoint path.
