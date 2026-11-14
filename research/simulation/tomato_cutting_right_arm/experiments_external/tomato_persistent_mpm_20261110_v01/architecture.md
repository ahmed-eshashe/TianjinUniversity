# Candidate architecture — Gates 0–2 only

This is a new, independent total-Lagrangian MPM prototype implemented in Warp CUDA with an independent NumPy reference. The installed Warp compiler is reused with a task-local cache. It does not alter or wrap the live Isaac/DiSECt setup. CRESSim's existing build is reused only for diagnostic controls; its public solver is not the candidate backend. This is paper-informed research code, not official BladeMaster code or a reproduction claim.

## Mechanics and transfer

Reference particle positions X, mass m and volume V0 stay fixed. Current x, v, F evolve. Quadratic tensor-product B-spline weights N and reference gradients G are precomputed once. Each particle owns exactly one persistent ternary code (four digits maximum). P2G scatters m*N, m*N*v and -dt*V0*P*G into its code's logical grid. Every particle's weights sum to one and gradients sum to zero. No material mass is copied when codes change.

For occupied logical states a,b at a node, compatible states exchange momentum by (m_a*p_b - m_b*p_a)/M_total and likewise exchange internal impulse. Opposite nonzero digits in any cut are incompatible. The exchange is evaluated from the original states simultaneously, not in-place sequentially. Its pair antisymmetry conserves total momentum. An all-zero code couples to both sides ahead of a partial incision, preserving an intact bridge; this is not a connected-component split of the whole body. After a complete sweep assigns all material within overlapping stencils, opposite sides cannot share velocity or stress through the grid. The same rule applies to MUSL remapping.

Use pure FLIP: v_p += sum N*(v_grid_updated - v_grid_uncoupled_old). Advance particle position with its updated velocity. Remap updated momenta using the same compatibility, then F += dt*sum(v_remap outer G). Positive occupied grid masses are normalized; there is no dimensionful mass cutoff that leaves momentum in a velocity field. Stress is the derivative of the declared compressible neo-Hookean energy. This differs explicitly from BladeMaster's fixed-corotated example and CRESSim's co-rotational model. No hidden damping, viscosity, plasticity or toughness.

## Current finite tool motion and persistent history

An action supplies only the current finite edge's previous and current pose, cut ID, and advance direction. A swept segment labels reached material behind the advancing edge, limited by the actual finite edge length and a declared six-grid-cell normal band. No future path is supplied. Existing nonzero digits never change, even after tool removal. An unused slot represents a new incision; maximum four cuts, overflow rejected before any state mutation. Small rotation segments will require conservative subdivision; initial fixtures restrict within-step angular motion to zero and test several fixed orientations. Curved/turning cuts are NOT qualified by those fixtures.

History is attached to particles and fixed reference stencils. Translating/rotating a separated fragment cannot restore incompatible transfers. No permanent world-space barrier is stored. Geometry-triggered codes here test topology only: they do not claim physically resisted fracture. A separate physical cutting law must be defined and pass Gate 3 before a tomato cutting claim.

## Recontact and the remaining modules

Independent logical grids do not supply contact. Gate 2 uses receding, resolved-gap/no-support probes, with no cutter present during independence measurement. Gate 3 must add current-configuration contact, with equal/opposite impulses, and verify recontact without changing nonzero cut digits. The architecture admits contact impulses between incompatible states; it must never average their velocities unconditionally. A future independent surface check must bound whole-material penetration. No Gate 2 contact or force qualification is implied.

Modules: (1) energy/stress, (2) fixed reference stencil, (3) persistent swept-tool history, (4) compatible transfer/MUSL, (5) later tool and fragment contact, (6) later tomato sampler, (7) state snapshot/reset, (8) later measured-blade/wrench bridge, (9) bounded benchmark runner. Gates 3–8 remain unimplemented. No kitchen, arm or controller file changes.

## Evidence and decision

Gate 0 reproduces CRESSim held/absent/wide-gap controls including rotated and translated configurations. Gate 1 audits the suspected low-grid-mass bug by measuring its effect and one isolated corrective patch, then independently verifies the chosen TL backend. Gate 2 compares CPU/GPU transfer and current-step cut history, then untouched/partial/full/parallel/intersecting/moving-fragment fixtures and half-step verdicts. The opening of actual sweep-generated fragments uses applied normal velocities and forward integration, never a fabricated empty initial gap. Separate manufactured discontinuities may test algebra but are labeled fixtures.

For each run, persist configuration, traces, final fields/codes, result, timings and memory. Mass and positive admissible volume are checked; failure aborts. First 8-hour decision scope ends at Gate 2, whether successful or blocked. A useful block topology result does not complete the tomato or establish RL throughput.

References: https://arxiv.org/html/2609.27342v1 equations 1–9 and 13; local prior CRESSim evidence at ../cressim_20261110/REPORT.txt. The selected position update, pure-FLIP choice, neo-Hookean material and finite test envelope are our explicit implementation choices.
