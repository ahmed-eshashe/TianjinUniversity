# Coupon motion and blade topology

Seven analytic tests pass for closed-surface auditing and prescribed rest,
indent/hold/withdraw/clear-hold motion. Actual authored blade has74vertices,
144triangles,216edges; every undirected edge appears twice with opposite
winding and signed enclosed volume is4.577378124134871e-05m3. No self-intersection
or native signed-distance accuracy test was performed. Topology alone cannot
establish a valid collision representation.

Trajectory uses a right-handed cyclic rotation: blade-local z(thickness)->worldx,
x(length)->worldy,y(width)->worldz. Initial translated bounding box has2mm
vertical clearance above the coupon; prescribed lowest bounds move at most
0.25mm below undeformed coupon apex. Cubic smoothstep gives zero velocity at
stage boundaries, then exact return to initial pose. dt proposal1/1200s;
rest.05s,indent.5s,hold.1s,withdraw.5s,clearhold.05s. This1.2s motion is a contact
coupon, not the1s independent-release observation required for a completed cut.
AABB overlap at indentation is not contact/nonpenetration proof. No path has
been run, accepted by a solver or shown to fit60seconds including JIT/SDF setup.

Next native soft-reaction source lead: SolverVBD has no inspected general public
soft-reaction collector. Its rigid collector does not cover blade-vs-deformable.
The proxy harvest invokes _eval_soft_ef_contact in
newton/_src/solvers/vbd/rigid_vbd_kernels.py:2067–2088, through
vbd_coupling_kernels.py:134–234. It takes current/previous particle/body pose,
contact parameters, barycentrics, shape/body maps and dt, returning force on
particle plus a contact point. Reaction on body is the negative and torque is
about worldCOM. It must use the same per-body adjacency as the solve.

Implement a separately versioned READ-ONLY observer kernel factory in source,
not proxy-flag hacks. Hash the private installed helper and declare the version
dependency; imports/decorators only inside disabled native execution factory.
Before aggregation refuse/trap truncated per-body adjacency, total soft contact
capacity saturation or missing arrays; independently assess broad-phase candidate
completeness. Balanced forces alone cannot prove completeness. Keep observation
separate from physical acceptance: using the solver's own helper is useful
reaction logging, not an independent constitutive/geometry audit.

The observer's runtime evaluation remains prohibited in this window. Test its
pure layout/count validation and AST/import refusal paths offline, then bind
actual stepping/pose history and dedicated guard. Need SDF surface error/buffer
and two-piece native case before a first contact-pass claim.
