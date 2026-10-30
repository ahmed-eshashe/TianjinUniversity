# Minimal Newton tomato prototype plan

Status: offline design only, 19 October 2026. No model, solver code, asset or training environment is implemented by this plan. The existing controller, memory safeguard, parameter specification and grasp criteria remain authoritative and unchanged.

## Objective and scope

Demonstrate one mechanically driven end cut in a small tomato model: a prescribed blade deforms a spring network, progressively damages bonds near its cutting edge, and leaves a genuinely independent slice. Use Newton 1.6.0 building blocks already identified in `TOMATO_CAPABILITY_AUDIT.md`. This is a mechanics experiment, not a grasp demonstration or a validated real-tomato simulation.

The scene has one tomato, a board, a disclosed fixture holding only the remainder, and a prescribed knife trajectory. No robot, camera, kitchen or learner is needed. The eventual robot integration remains a separate gate because Newton's simple solver does not preserve all the hand's mimic and actuator-limit behaviour.

## 1 Geometry and spring layout

Use the proposed 65 by 65 by 55 mm ellipsoid, with board z up, x pointing inward from the exposed tomato end, and y the drawing direction. A proposed cut plane lies 10 mm inward from the leftmost extent. Dimensions and material properties are synthetic until measured.

Start with approximately 5 mm lattice spacing, adjusted locally to place the cut between two node layers and to resolve the thin end cap. Target approximately 1,000 to 2,500 nodes and fewer than 30,000 unique bonds as a design budget, not a measured count or memory guarantee. Count actual boundary nodes and bonds offline before any run. A finer comparison is a later serial experiment, not a parallel environment.

Connect axial, face-diagonal and selected body-diagonal neighbours to resist extension and shear. Compute rest lengths from the undeformed geometry; assign positive lumped mass using represented cell volumes. Remove duplicate bonds and isolated boundary nodes, and inspect anisotropy. Record per-cell signed volumes for diagnostics even if the first model has no FEM elements. A spring network is not automatically volume preserving: compression, shear and volume-collapse checks determine whether it is adequate. If not, add a documented volume constraint or compare coarse FEM; do not hide collapse by increasing all spring stiffnesses.

Classify every bond as within the slice, within the remainder, or crossing the intended interface. Only the last group is damageable in this restricted prototype. Give each interface patch a physical area, a flesh/skin label and a list of crossing bonds. Include all diagonals and any effective surface reinforcement in this registry. There must be no unregistered connection across the cut.

Use finite rest-length interface bonds. The installed spring kernel divides by current length, so coincident duplicate-node springs are invalid. A future implementation must reject degenerate rest lengths and stop before any current bond collapses toward the singularity; never silently clamp an invalid geometry and report success.

Surface patches near the exterior may use a distinct effective skin rupture law. This is not an explicit thin skin or a detailed tomato interior. Bulk springs remain intact in version one; failure away from the planned interface is outside its model scope.

Three representations share the same material coordinates: a smooth visual exterior, the mechanical network, and a collision sampling surface. No visual mesh is allowed to continue stretching across a completed cut. The final visual split should follow the damage state and should not drive it.

## 2 Blade contact and local damage eligibility

Derive a test blade from the existing knife geometry and identify its edge, faces, orientation and physical dimensions. Treat its prescribed pose as external actuation and account for the work it injects. Do not scale blade thickness to the grid spacing or replace its edge with a large collision margin to force success.

The blade needs both contact response and damage eligibility:

- Contact resists penetration and supplies particle forces plus a reaction wrench on the prescribed tool. Contact remains active before and after fracture.
- Eligibility identifies which interface patches have actually been reached by the cutting edge. Use the swept edge over each physics substep in the current deformed configuration, with a tolerance tied to contact resolution. Verify nearby blade contact or explicitly reconstructed blade/material intersection. Proximity, blade centre position, elapsed time and final depth alone are insufficient.
- Only a patch with present local blade interaction can accumulate new damage in the initial contact-gated model. Do not permanently mark an entire row as cuttable just because the knife once passed nearby. Existing damage remains irreversible. Fracture driven solely by stored energy after the blade leaves is deliberately excluded from version one.

Use a blade contact coupon to verify that the chosen native particle-to-shape contact resolves the real thin edge. A sparse lattice can let the blade pass between particles even with a swept eligibility test. Therefore swept edge geometry cannot compensate for missing mechanical contact. If finer sampling or supported surface contacts are required, select them explicitly and retest. A custom surface/blade contact path is a possible extra implementation cost, not a source-confirmed ready-made feature.

## 3 Bond damage law

Store per-patch damage D in [0,1], maximum effective opening/shear history, area, material label, damage dissipation and active bond IDs. Initial D is zero. Broken means D equals one exactly and all associated cohesive force paths are removed.

The proposed starting law is displacement-driven cohesive softening. Define a local interface frame from the deformed patch, remove rigid motion, and measure positive opening and tangential separation between its two material sides. Compression alone does not initiate fracture. An effective separation combines positive opening and shear with a documented mode weight. All kinematic measures must return zero under a common rigid motion.

For a one-spring tensile coupon, use a bilinear traction law as the reference:

- Initial stiffness K is in N/m; patch area A is in m²; peak traction t0 is in Pa; fracture energy Gc is in J/m².
- Peak force F0 = t0 A; onset opening delta0 = F0/K.
- Final opening deltaf = 2 Gc A/F0, requiring deltaf > delta0 > 0.
- With eligible local contact, update kappa as the maximum opening reached. D = 0 below delta0; between onset and failure, D = deltaf (kappa - delta0) / [kappa (deltaf - delta0)]; D = 1 at or above deltaf. Unloading uses the degraded stiffness without healing.

This reference provides a clear energy target for a scalar tensile bond. It is not automatically an exact law for an oblique multi-spring patch under mixed-mode loading. For a real patch bundle, allocate initial stiffness by bond geometry, define the common effective separation and mode weights, and validate total force and dissipated work against coupon targets. Do not give every diagonal the full patch fracture energy. Across the interface, patch areas must partition the cut area; refinement must not multiply resistance.

For the first Newton spring implementation proposal, use the same patch D to set each registered interface bond's stiffness to (1-D) times its initial value. Degrade its damping consistently to zero; do not leave damping linking the detached slice. Newton's ordinary springs are bilateral, so this also weakens their compressive stiffness. Separate compressive contact must prevent the two sides interpenetrating after damage. This approximation needs explicit compression and shear coupons and may require a custom cohesive element if it cannot meet them.

Advance damage before force evaluation for the substep using committed geometry, then apply the selected stiffness/damping consistently. Log the fixed-geometry drop in stored spring energy from each damage update separately from viscous/contact dissipation and prescribed tool work. If one-substep lag produces overshoot or false fracture, reduce timestep or use a documented predictor/corrector. Never delete a whole interface on a single global force threshold.

Material constants remain unset. Synthetic engineering values may be selected in a later implementation configuration only if labelled uncalibrated and accompanied by stability/energy checks. They cannot establish real tomato cutting forces.

## 4 How the slice becomes independent

Node identity is separate across the cut from the start; intact interface bonds hold the body together mechanically. A progressing blade weakens only the patches it physically loads. The final connection may be a skin patch near the lower edge, so blade depth alone never declares completion.

At each diagnostic checkpoint, build connectivity from all mechanically active bonds and constraints. Include fixture attachments and any surface/volume elements that could bridge the interface. Separation requires distinct slice and remainder components and zero residual cross-cut cohesive stiffness/damping. A tiny positive stiffness is still a connection; do not use a loose graph threshold to manufacture success.

The slice retains its original particles, velocities, masses and internal bonds. Do not spawn a replacement rigid slice, move it, reset velocities or attach it to the blade. After blade withdrawal it must move independently under gravity and contact. At-rest touching is allowed. Observe at least one simulated second after release; if friction prevents visible motion, a bounded probe may confirm independence, but must not finish tearing residual bonds.

## 5 Contact across the interface

Contact is a key unresolved implementation gate. A set of spring links supplies cohesion but not closed cut-face collision. The plan requires a supported contact representation for both sides that works before and after failure.

Preferred design: pre-author separate surface samples or faces for the slice and remainder, with compatible local compression contact available throughout. While intact, the interface bonds provide tensile/shear coupling and compressive contact provides nonpenetration. After damage, cohesive coupling vanishes but compression/friction contact remains. Prevent double-counting initial compression resistance and avoid overlapping collision radii that preload the intact tomato.

Do not disable all self-contact, remove all blade contact after rupture, or keep one convex envelope covering both pieces. Check face normals, exposed-face contact, particle radius and spacing, contact exclusions and neighbouring-node collision. Native particle contacts may be too coarse to close the surface; surface sampling/filtering support and its cost must be verified before selecting this design. If supported contact cannot meet these requirements, stop at the contact gate and revise the representation.

## 6 Fixture and blade trajectory

Constrain a small, explicitly identified region of the remainder away from the cut. The fixture must never constrain slice nodes or provide a hidden bridge. Record imposed degrees of freedom and reactions. A stationary fixture can supply large forces without doing work, so report its force as well as its energy contribution.

Proposed motion stages: settle at rest, lightly indent without fracture, draw and descend through the target plane, stop above unsafe board penetration, withdraw along a checked clearance path, then observe released pieces. The bottom skin must actually rupture before success; if the blade/board geometry prevents it, record an incomplete cut rather than snapping the last bonds. Define stage durations and speeds after numerical/contact checks; no assumed motion duration is a damage parameter.

## 7 Thickness definition correction to resolve before freezing

An end cap from an ellipsoid has a curved outer surface and varying local thickness. A 10 mm offset of the cut plane therefore does not make every point of that cap 10 mm thick. The existing draft multi-point thickness criterion needs clarification before acceptance is frozen; this plan does not edit that file.

For the first cap experiment, report central cut depth and compare local thickness samples against the known undeformed cap profile, with deformation and taper recorded separately. It must be labelled an end-cap cut. To demonstrate a uniformly thick slice, use two parallel cuts or a disclosed pre-trimmed specimen with an initial flat face. Do not quietly grade a curved cap against a uniform-thickness target.

## 8 Future implementation sequence and success checks

Implement only after a later user instruction, in this order:

| Stage | Smallest future check | Exit condition |
| --- | --- | --- |
| Offline topology | Generate node/bond registry and fixture map without advancing physics | Positive rest lengths/masses, unique bonds, correct area partition, no unregistered cross-cut path; actual counts within declared budget. |
| Scalar coupon | One finite-length bond patch | Onset, complete failure, unloading and no healing follow the stated law; patch dissipation matches its target within a predeclared numerical tolerance. |
| Bundle coupons | Opening, shear, compression and common rigid motion | No fracture from pure compression/rigid motion; correct sign and total area-based resistance; zero residual coupling after full failure. |
| Contact coupon | Thin moving blade and a small spring solid | Blade cannot tunnel through unresolved gaps; contact reactions and work balance have correct signs; no damage without actual contact. |
| Two-piece contact | Intact and fully released interface | No initial collision preload explosion, no invisible barrier, no piece interpenetration or lingering viscous bridge. |
| Tomato mechanics | Rest, indentation, one draw cut, withdrawal and release | Stable geometry, local progressive failure, full connectivity separation and independent motion, measured fixture loads and numerical validity. |
| Robustness | No-contact, off-plane, partial cut, stop/withdraw and reset controls | No timer/depth-triggered fracture, no off-plane magical release, partial cut stays attached and reset restores every state. |
| Resolution | Half timestep and refined interface/network | Existing proposed convergence checks hold with consistent physical stiffness/area scaling; otherwise narrow claims or revise model. |

Add energy and allowable volume-change tolerances to the future model-specific contract before any acceptance run. For partial failure, always record which patches remain connected and why. No screenshot or normal process exit substitutes for these checks.

## 9 Resource limits and handoff

Retain the common lock and unchanged memory watchdog: at least 10,000,000,000 available host bytes and 4 GiB free VRAM at startup, plus the existing runtime warning/hard-stop behaviour. Use one worker at a time, bounded diagnostics and the proposed 60-second worker limit; report incomplete stages as inconclusive. Include JIT/startup and contact/mesh setup in wall-time accounting. The guard currently has no tomato worker mode, so guarded integration is future work rather than a command to run now.

Future logs should include node/bond counts, intact/damaged/broken patch counts, actual cut area, component IDs, per-patch opening/damage/work, blade pose and reaction, fixture reactions, total mass, energy ledger, volume diagnostics, contact penetration, stage completion, peak process-tree RAM, global VRAM and step-time distribution. Avoid saving every array every step; use capped traces and summaries.

Recommended next authorized deliverable is the offline topology and scalar/bundle coupon design, followed by a separately reviewed implementation. Do not add robot dynamics, camera rendering or RL until mechanics/contact gates pass. Full robot adoption still requires a supported solver/coupling path for the same hand, unchanged grasp checks, and sensor/load calibration.

## Source and draft references

- `TOMATO_CAPABILITY_AUDIT.md` and `tomato_capability_audit.json`: installed source findings, hashes and solver limitations.
- `tomato_parameter_schema.json`: provisional dimensions, unset material parameters and sensor assumptions.
- `slicing_criteria.json`: draft acceptance, not modified or frozen here.
- Installed Newton `ModelBuilder.add_spring`, semi-implicit spring/contact kernels and rigid–soft example: primitives only. The cohesive law, patch mapping and cut-contact design above are proposals requiring implementation and validation.
