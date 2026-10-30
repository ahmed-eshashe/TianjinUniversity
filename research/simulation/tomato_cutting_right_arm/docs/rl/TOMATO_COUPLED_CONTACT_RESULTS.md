# Coupled deformable normal-contact solver: indentation and reclosure

Built a full-node **offline nonlinear quasistatic normal-contact solver** for the refined tomato. It couples both deformable bodies, the existing same-side spring/volume mechanics, the original interface forces and unilateral contact in one equilibrium solve. **68 accepted checkpoints pass**, along with **24 tests**. Small indentation and guided normal reclosure pass their declared numerical/contact checks.

This is a restricted normal-contact coupon solver, not a general 3D collision backend. No full cut, evolving fracture, free-slice release, simulator, native Newton integration, training or installation was attempted. Original assets, controllers, material/damage implementations, runtime safeguards and frozen grasp criteria are unchanged.

## Mechanics and contact

Use the accepted refined 5 mm reference: 4,032 mechanical nodes / 12,096 coordinate DOFs, with 2.5 mm added slice sampling. All nodes participate in the existing nonlinear finite-spring and volume-barrier energy. This is no longer the earlier rigid-shape or independent supported-patch approximation.

Intact/partial interface forces use the actual 403 original finite-length bonds and unchanged area-scaled patch stiffness recipe. Diagnostic damage is frozen at D=0, 0.5 or 1. At D=1 those bonds are omitted exactly, without a small residual stiffness. No damage is advanced by tool depth or time in these tests. Damping/inertia are absent from this quasistatic solver.

Contact is an inequality constraint with nonnegative compressive multipliers; no penalty contact stiffness is fitted. An active-set Newton method couples exact material derivatives and contact. Active normal constraints are eliminated exactly. A memory-bounded SSOR-preconditioned conjugate-gradient solve handles the reduced equations; it adds no physical diagonal stiffness. Intermediate Newton guesses are uncommitted optimization states, not physical frames that are allowed to cross and then get repaired.

The first exploratory direct sparse factorization failed inside the unchanged address-space cap (`Can't expand MemType 0`). It is excluded from accepted results. The iterative replacement completed all final cases without relaxing the memory/time limits. Final linear solves needed at most 132 iterations.

## Explicit coupon supports and geometric scope

The original remainder fixture is retained. Both cut faces additionally have their y/z coordinates supported as **normal-contact coupon guides**. This keeps their matching finite triangulations in the same projection, while their normal coordinates are solved. Other material and exterior nodes retain their free coordinates.

Indentation has 10,993 free coordinate DOFs. Reclosure additionally drives the x coordinates of 193 slice back-cap surface nodes selected from a 1.5 mm-deep rest cap, leaving 10,800 free DOFs. Those supports apply the compression/reopening load; they do not prescribe the full slice shape. They are explicit diagnostic supports, not the fixture configuration for an independent released slice. The original fixture registry and slicing/grasp criteria were not changed.

For indentation, the tool is a finite planar blade-face surrogate, 265 by 50 mm, pressing the curved outer cap along x. It is not the original knife's verified cutting edge/bevel. Every potentially contacting tomato triangle must remain fully inside this facet's footprint, and every such vertex must belong to the constraint stencil. Otherwise the run is rejected as an unsupported finite-edge case. This gives complete planar triangle coverage in the tested central-contact region; it is not a particle-radius approximation.

For reclosure, 257 matched cut-vertex normal gaps constrain both sets of 448 finite cut triangles. With their common fixed y/z projection and matching triangulations, the gap at every interior point is the barycentric interpolation of its vertex gaps. Nonnegative vertex gaps therefore prevent the whole paired finite face from crossing. Reported contact reactions are x components under these guides. Normal contact remains eligible before and after diagnostic rupture, and inactive contact supplies no tensile bridge.

The guides exclude arbitrary tangential slip/rotation. Exterior surfaces also undergo proper-intersection screens at each endpoint and midpoint. Those screens permit coplanar touching and are **not general continuous vertex-face/edge-edge collision detection**. This implementation must not be used to claim arbitrary released-slice collision safety.

## Test sequences

| Sequence | Checkpoints | Loading |
| --- | ---: | --- |
| Intact indentation, coarse | 7 | Approach, 25/50 micrometre indentation, withdraw |
| Intact indentation, fine | 13 | Same cycle with 12.5 micrometre loaded increments |
| Fully broken reclosure, coarse | 13 | Start 0.1 mm open, close, drive back cap 50 micrometres beyond rest, reopen |
| Fully broken reclosure, fine | 25 | Same cycle with half increments |
| Intact reclosure | 5 | Rest, 25/50 micrometre back-cap compression, unload |
| Partial-damage reclosure | 5 | Same compression/unload with D=0.5 frozen |

At peak indentation the blade reaction is **0.666 mN**. After subtracting best-fit rigid motion, peak deformation is 48.71 micrometres in the slice and 0.777 micrometres in the remainder. At peak fully broken reclosure, contact reaction is **17.25 mN** and best-fit-rigid-motion-removed deformation is 18.13 and 20.25 micrometres respectively. Thus both bodies deform in the coupled solution; neither is being replaced by a moved rigid slice.

Those forces belong to a synthetic material and these supported, small-displacement coupons. They are not predictions of real knife-cutting forces or hardware load limits. The authoritative rigid-motion-removed measures are in the final audit; the per-worker `max_nonrigid_displacement_m` field removes translation only and should not be interpreted as a best-fit-rigid residual.

## Acceptance and numerical evidence

Every accepted endpoint requires converged coupled force equilibrium, feasible gaps, non-attractive contact within numerical tolerance, no local collapse, positive constrained tangent and the stated geometry/work checks. The existing 1e-6 relative force gate is retained for these tests, with an explicitly declared 1e-10 N absolute allowance for effectively unloaded states (relative scale floor 1e-4 N). This does not modify previous material/grasp acceptance files.

| Check | Observed result |
| --- | --- |
| Maximum force residual fraction | 7.24e-8 |
| Minimum local J, including cubic swept-volume certificate | 0.73793, above unchanged 0.1 floor |
| Minimum scaled tangent eigenvalue | 0.0012104, above 1e-6 |
| Maximum normal penetration roundoff | 1.10e-15 m, below declared 1e-9 m tolerance |
| Proper opposing-surface intersections in midpoint/end screens | 0 |
| Minimum surface triangle area ratio | 0.99720; no flipped endpoint normals |
| Maximum force/moment balance fractions | 4.97e-8 / 2.30e-8 |
| Reopened fully broken contact reaction | Zero in the final separated checkpoints |
| Broken interface cohesive force/energy | Exactly zero |

An independent unilateral-stability audit checks all 68 endpoints while allowing weak/zero-force contacts to open. Only multipliers greater than 1e-9 N restrict its critical space; dropping weaker bindings is conservative. All pass with the same minimum eigenvalue quoted above. This avoids hiding an opening instability by treating a zero-force unilateral contact as a bilateral tie. Run this audit as well as the endpoint checks when evaluating future coupon sequences.

Supported normal gaps are affine along the declared linear path between equilibria, so their endpoint gaps certify that path's non-crossing. Signed cell volumes are cubic along that path; interior derivative roots are checked, not just endpoint J. These are certificates for the interpolation, not a dynamic time-stepping claim. General exterior swept CCD is still absent.

Support/tool work is accumulated separately and compared with elastic energy change. Every increment meets the declared 1% energy-work allowance plus a 1e-12 J near-zero allowance. Loading work changes by **0.1353% for indentation** and **0.01090% for reclosure** when increments are halved, both below the unchanged 10% comparison target. Matched nonzero reaction differences are below 3e-10 relative; unloaded-force differences are checked against their absolute tolerance. Load/unload cycle residuals are negligible relative to peak storage. This is load-increment convergence on one mesh, not contact-mesh or dynamic-timestep convergence.

## Compression-path issue exposed before cutting

The unchanged bundle law is bilateral before failure, so it also carries compression alongside cut-face contact. At the same 50 micrometre back-cap drive:

| Frozen damage | Back-cap actuator force | Cut-contact contribution | Cohesive compressive contribution |
| --- | ---: | ---: | ---: |
| D=0 | 18.54 mN | 9.54 mN | 9.00 mN |
| D=0.5 | 18.45 mN | 9.96 mN | 8.49 mN |
| D=1 | 17.25 mN | 17.25 mN | 0 |

The intact cohesive path carries about 48.6% of the compressive load, while total actuator force is about 7.5% higher than in the fully broken case. This does **not** mean the total load is doubled, but it exposes a significant parallel load path that must be explicitly reviewed/calibrated before cutting. The existing energy-validated law was not silently changed or retuned during this test. Its previously unsupported compression-plus-shear fracture branch remains outside the tested scope.

## Code, evidence and safeguards

New offline code:

- `rl/tomato_coupled_contact.py`: full-node assembly, exact normal constraints, iterative equilibrium and geometric screens.
- `rl/offline_tomato_coupled.py`: one capped, checkpointed equilibrium endpoint with provenance and numerical checks.
- `rl/audit_tomato_coupled.py`: input provenance, force/work/refinement/compression and surface audits.
- `rl/audit_tomato_coupled_stability.py`: independent unilateral stability audit.
- `rl/tests/test_tomato_coupled_contact.py`: eight new analytic/regression tests; combined with existing volume/contact tests, **24 tests pass**.

Evidence is in `runs/offline/tomato_coupled_01/`: manifest, six complete sequence directories with nodal states and contact multipliers, `summary.json`, `unilateral_stability.json`, test logs, input/source hashes and preservation records. Source snapshots preserve the tested code. Exploratory trial directories are excluded from the 68-checkpoint dataset. The model's geometry/assignment files match hashes recorded in the previous refinement study.

Successful endpoint workers ran serially for 216.02 s total. The slowest took 4.79 s; peak worker RSS was **180.99 MiB**. Every solver/audit worker retains the shared controller lock and 512 MiB address-space, 45 s CPU and 55 s wall caps, with one BLAS thread. No simulator or GPU runtime is imported. Simulator startup reserves, runtime warning/hard-stop thresholds and frozen grasp criteria remain unchanged.

## Stop point before a full cut

This completes the requested **supported normal indentation/reclosure stage**. Keep it offline. Before a full cut, extend and validate actual blade-edge geometry, current-normal finite-face/edge contact with free tangential motion, general swept collision handling, and committed mixed-mode damage coupling. Resolve the compression load-path interpretation while retaining the existing constitutive energy checks. Contact-mesh convergence, unconstrained release and a real one-second post-withdrawal observation remain later gates. No full-cut, simulator or training pass is claimed or authorized by these results.
