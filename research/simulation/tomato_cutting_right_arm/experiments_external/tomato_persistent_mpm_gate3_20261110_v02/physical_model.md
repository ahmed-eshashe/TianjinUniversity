# Gate 3 isolated physical candidate — formulation and limits

10 November 2026. **Under test, not adopted in the project.** The existing Isaac/DiSECt setup and Gate 0–2 evidence are unchanged. This is an independent paper-informed prototype, not official CRESSim or BladeMaster code. No tomato calibration or learned policy is claimed.

## Bulk and persistent history

The inherited total-Lagrangian MPM update uses fixed quadratic reference-grid weights, pure FLIP particle velocity increments, a modified-update-stress-last velocity remap, and antisymmetric momentum exchange only among compatible persistent ternary cut codes. Density is 1000 kg/m³, E = 100 kPa, Poisson ratio = 0.4. These are provisional block-test parameters, not tomato measurements. The energy density is W(F) = μ/2 [tr(FᵀF) − 3] − μ ln J + λ/2 (ln J)², and P = μF + (λ ln J − μ)F⁻ᵀ. No material viscosity, plasticity, strain clipping or position projection is added. J must remain strictly between 0.1 and 10; finite state alone is not a pass.

Mass and reference volume stay attached to particles when history changes. A code change does not reset position, velocity or deformation. The Gate 2 geometry-only sweeps qualify transfer topology, not physical fracture. Geometry cannot authorize a new physical cut in this Gate 3 candidate.

## Declared material boundary and blade

The exact saved watertight CAD blade has 74 vertices and 144 triangles. Its copied asset is hash-preserved. The component fixture uses a documented rigid rotation/translation; it does not alter the robot grip or scene transforms. Frozen triangle groups distinguish lower cutting edge, broad face, spine and tip. Tip contact is collision-only in this first envelope; tip cutting is unqualified.

For contact, the material is explicitly reconstructed as a union of closed trilinear cells, one initial 1.5 mm cube per particle. Cell corners are affine-exact local linear combinations Cx of compatible material particles. Exterior and newly exposed incompatible faces carry midpoint quadrature with spacing at most 0.25 mm. Surface point positions q = Qx and forces f_particle = Qᵀ f_surface use the same map, conserving resultant, moment and instantaneous work under that reconstruction. This reconstruction is a new approximation to the boundary, not a proof of the exact continuum or a measured tomato surface. Arbitrarily distorted/partially split cells require further qualification.

Signed distances come from the watertight CAD, with a separately implemented double-precision point/triangle and winding query as a control. A conservative check covers the entire declared volume: each trilinear subcell is contained in the convex hull of its eight corners. Signed distance is 1-Lipschitz, so distance at the hull center minus its covering radius, a full endpoint-relative-motion bound, and 2 μm query allowance bounds the whole subcell. Unproved subcells subdivide; unresolved/capacity failures reject the step. The 0.1 mm limit is never replaced by a particle-center check. This is a bound for the declared reconstruction, not for an unspecified true material surface.

## Blade contact and friction

For each surface sample with reference area A and signed distance φ, δ = max(−φ,0), U_contact = ½ K A δ², and F_normal = K A δ n. K = 10⁹ N/m³ is a provisional penalty parameter, independent of timestep. Tangential force is −μ_f F_normal tanh(|v_t|/v_s) v_t/|v_t|, with μ_f = 0.2 and v_s = 0.001 m/s. Its nonnegative dissipation is −F_t·v_relative. No extra contact dashpot is hidden in this law. Both resultant reaction magnitude and summed contact-force magnitudes must remain below 2 N.

Reaction on the tool is the negative of the applied material force, in newtons. Tool moment uses the instantaneous tool reference origin T and surface lever arms q−T. Step impulse is F Δt, in N·s. The continuous contact tests log end-state forces at shared physical timestamps; step impulses use the interval force, not an end-time value relabeled as an interval average. Support impulses are separately recorded and included in momentum balance. Tool input work uses the force on material dotted with tool displacement.

## Fragment recontact

A two-fragment component fixture reconstructs closed material surfaces with persistent incompatible codes. One new surface is tested against the other. Equal/opposite normal forces act through closest-point interpolation. Friction acts at a shared midpoint using an affine-exact correction of both interpolation maps; this prevents an artificial frictional torque from using two slightly different application points. Force and moment cancel internally. A bound on bilinear-face/triangle deviation is added to the whole-volume certificate. Separation removes contact forces, not history. The pre-separated fixture is an initial condition for recontact testing, not evidence that this physical law created the split.

## New cutting-work candidate

The candidate uses ideal rate-independent cutting resistance, with Gc = 80 J/m² per single reference interface area (not twice for its two faces). This value is from the project's **synthetic** reference toughness, not a measured tomato experiment. This law is different from the old bilinear cohesive law; no DiSECt qualification transfers to it.

A finite current edge sweep intersects an explicit material-area patch. Only actual sharp-edge contact and positive material-relative advance are eligible. Required irreversible work is Gc times newly covered area. The union of previously paid area prevents double charging on re-entry. Area is partitioned, not assigned in full to every particle or band. Unit tests cover subdivisions, half timesteps, pause, reversal, re-entry, rejected trials, repeated queries, checkpoint restore and duplicate/stale commits.

The first coupled pilot is deliberately restricted to one straight initial patch on a small supported coupon. A frozen affine material marker at first CAD edge contact gives a work-conjugate contact velocity. Backward-Euler cutting resistance sticks below yield and slides at Gc times the patch width. For normal direction d, u = d·(v_tool − Q_marker v_free), effective mass m_eff = m / Σ Q_marker² on free particles, and J_cut = min(Gc width Δt, m_eff max(u,0)). Applied material impulse is Q_markerᵀ J_cut d. Plastic relative travel at yield earns cutting work; the distinct backward-Euler numerical loss is J_cut²/(2m_eff). Contact friction, fracture/cutting work and this numerical loss must be recorded separately.

This pilot uses projected area along a frozen material direction (a small-strain straight-front approximation), not a general finite-deformation crack-coordinate algorithm. It cannot establish unrestricted path freedom. A full front-row area must be paid before any particle code changes; a fraction of that work must not release the whole row. That restriction deliberately tests whether the discrete topology and strict penetration limit are compatible. If not, this formulation fails; no face disappears early to create a visually successful cut.

All candidate history stays transactional until work, volume, force and full-volume/new-surface checks pass. A failed step restores positions, velocities, deformation, codes, simulation time and history. Logging and previews do not mutate the ledger. A paid patch is only a component result; a complete persistent slice remains a later gate.

## Energy and acceptance

Record elastic and kinetic energy, recoverable contact potential, tool work, support work, physical cutting work, friction loss, and any identified numerical loss separately. Residual energy is a measured error, never relabeled fracture energy. Compare positions, force, impulse and work at shared physical times with Δt = 12.5 μs and 6.25 μs. Screens are 0.1 mm and 5%, with frozen floors 10⁻⁴ N, 10⁻⁷ N·s and 10⁻⁸ J. The same physical onset/separation classification and admissible volumes are required. These are numerical checks, not experimental validation.

Scope remains block/coupon qualification. Tomato shape generation, complete slices, robot integration and RL throughput are pending. In particular, Gc = 80 J/m² over a 60 mm engaged edge implies 4.8 N ideal cutting resistance before other loads, above the retained 2 N limit. The later tomato gate must not ignore this incompatibility or silently soften the material.

## Gate 3 outcome and additional volume check

The coupled v02 candidate **failed qualification**. The original stored-F volume check did not detect collapse/inversion of the reconstructed material geometry. `volume_guard.py` now bounds every reconstructed trilinear cell's Jacobian: derivative entries are bilinear, their extrema are bounded at cell corners, and interval determinant bounds are refined by subdivision when needed. Observed J outside (0.1, 10), an unresolved interval or capacity exhaustion rejects the step. Identity, rotation, affine compression, collapse and inversion controls pass. This is an additional physical guard, not a repair of the material update.

The bounded retest used 62.5 μm quadrature on loaded top/new cut faces and retained 250 μm elsewhere, with exactly conserved face areas and unchanged physical parameters. It stopped on reconstructed volume at 0.029175 s, before any physical topology event. The null-mode diagnostic proves a particle-motion mode invisible to stored strain in the current transfer. Consequently, passing shallow-contact force refinement or work-ledger unit tests does not qualify the coupled cutting model.

The smallest-step recontact run completed at 0.5 μs, but its matched 0.25 μs run was deliberately not launched after the structural failure was established. Recontact refinement remains unresolved. Tip/spine loaded qualification, physical newly exposed blade-contact faces and a positive work-gated crack remain pending. Refer to `contact_fracture_controls.json` for the final per-check status and `RECOVERY_PROPOSAL.md` for the proposed scope review.
