# Isolated v03 APIC repair

The approved repair replaces pure-FLIP updates on a fixed reference grid with current-spatial-grid APIC. Reference material coordinates and persistent cut history are retained. This numerical change is explicit; the prior fixed-reference-grid qualification is not inherited. The material law, synthetic Gc, CAD, fixed attachment in production, contact constants and physical limits remain unchanged. Production is untouched.

At particle positions x, quadratic B-spline weights w and spatial gradients g are recomputed. The APIC state is (x, v, C, F, mass, reference volume, persistent cut code, fragment ID). Let r_ip = x_i − x_p and D = h²I/4. P2G momentum is Σ m_p w_ip (v_p + C_p r_ip). The particle kinetic measure includes both ½m|v|² and ½m tr(C D Cᵀ); angular momentum includes x×mv plus mΣw r×Cr. These affine quantities are included in diagnostics and checkpoint/reset.

At a shared spatial grid node, only compatible material states exchange momentum, using the inherited symmetric antisymmetric pair rule. Since the exchange happens at the same physical point, its net linear and angular impulses vanish. It is a convex mass-weighted velocity mixing and its kinetic loss is recorded as numerical transfer dissipation. Forces are applied AFTER this momentum exchange, avoiding an unmatched contact-force mixing operator.

Neo-Hookean P is unchanged. The spatial grid force is −Σ V0 P Fᵀ g. Frame-objective stress gives zero total internal torque. External surface position q=Qx has velocity Q W v_grid, so its grid force is Wᵀ Qᵀ f. No direct post-transfer particle velocity kick is used. Fixed material points are imposed as W_fixed v_grid=0 through a mass-metric grid impulse projection; its reaction and numerical energy removal are recorded separately. A nonconverged support projection rejects the step.

G2P sets v=Σw v_grid, C=(Σw v_grid rᵀ)D⁻¹, x_new=x+dt v and F_new=(I+dt Σ v_grid gᵀ)F. Motion and strain therefore use the same current grid velocity. APIC filters unresolved velocity modes instead of letting them move positions while remaining invisible to strain. Local reconstruction differences still require explicit checks; this argument does not make arbitrary surface interpolation exact.

The implementation uses float64 and an allocated spatial grid whose overflow is a stop, not a clamp. Force integration is explicit symplectic Euler. Its energy error is measured by refinement. P2G, compatibility mixing, G2P filtering and support-projection losses are not fracture energy or material viscosity.

Persistent topology uses both local ternary cut-side codes and whole-fragment IDs derived from reference-material adjacency after committed cuts. Partial cuts retain a connected bridge and local incompatibility. After complete separation, outer material cannot start sharing grid momentum just because it moves near another piece. Fragment IDs do not derive from spatial proximity and therefore cannot heal on recontact. This adjacency construction is restricted to regular block fixtures; moving-fragment and intact-bridge requalification was not reached because mechanics failed.

The APIC transfer choice is motivated by [Jiang, Schroeder and Teran](https://arxiv.org/abs/1603.06188). Independent CPU algebra and GPU comparisons provide component evidence, not qualification of the modified history/support/contact coupling. This prototype is not the authors' software, CRESSim's official implementation or a calibrated tomato.

Existing trilinear reconstructed material geometry, exact CAD queries, conservative penetration/volume certificates, surface penalty potential, friction and transactional area/work ledger are retained from v02. They keep their declared approximation limits. A physical cut still needs a paid, admissible topology event. No geometry-only label is promoted to fracture, and no subcell work may open an unpaid whole row.

Final disposition: the null-mode and localized-strain controls pass, but mechanics timestep consistency fails. See REPORT.txt. The algorithm is implemented, not adopted or physically qualified.
