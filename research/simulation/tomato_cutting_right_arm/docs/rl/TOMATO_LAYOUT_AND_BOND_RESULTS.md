# Offline tomato layout and bond test results

Date: 19 October 2026. Status: node/bond layout and synthetic constitutive checks completed; multi-spring fracture-energy gate failed. No Newton, Warp, Isaac, Torch or USD module was imported by the bounded runner. No dynamics, blade contact, simulator, camera or training was executed.

## Outcome

The 5 mm topology is suitable for further offline design, but the simple scalar-to-bundle damage mapping is not ready for contact experiments. The scalar reference dissipates the intended fracture energy. The five-spring bundle does not: opening work is 13.60% high and shear work is 64.20% low relative to the same target. These failures were retained, not hidden by a passing unit-test count or exit code. Actual interface bundles in the tomato have varying directions and need their own constitutive mapping.

Recommended next step is an offline energy-consistent mixed-mode patch law or an explicit regularized cohesive element. Preserve the scalar coupon as the reference. Do not merely increase fracture energy globally or give every spring a full patch energy budget. No simulator run is needed to address this mismatch.

## Layout generated

| Quantity | Value |
| --- | --- |
| Synthetic dimensions | 65 by 65 by 55 mm |
| Node spacing | 5 mm |
| Nodes | 979, including 64 in the end cap and 915 in the remainder |
| Unique springs | 10,510 |
| Registered cross-cut bonds | 403 |
| Interface area patches | 47 |
| Proposed remainder fixture nodes | 25; no slice nodes constrained |
| Diagnostic full lattice cells | 648; no force or volume constraints attached |
| Analytic cut area | 1462.049 mm² |
| Analytic ellipsoid volume | 121.671 cm³ |
| Synthetic total mass | 121.671 g, from explicitly assumed density 1000 kg/m³ |

Every bond has finite positive rest length and a unique pair of node IDs. Each cross-cut axial or diagonal bond is registered exactly once to a patch. Initially the bond graph is connected. Removing all 403 interface bonds produces exactly two internally connected components. Leaving even one interface bond connects them. This is a graph test, not blade-driven physical separation.

The lattice is an interior point approximation of the ellipsoid. Positive boundary-cell volume estimates are globally normalized to analytic volume; total mass agreement therefore checks accounting, not geometric convergence. Before normalization the sampled boundary estimate differs by -5.39%. No collision or render mesh was generated. Point extents do not establish board contact or a closed cut face.

Patch areas partition the analytic cut ellipse using nearest-anchor equal-area disk quadrature. Doubling radial and angular resolution changes the patch-area distribution by 3.03% in normalized L1 distance, while total area remains analytic. This is not a mechanically refined mesh test. The effective skin annulus is synthetic, not measured tomato skin. The equal-unit-stiffness directional network probe has max/min ratio 1.0121; this is only a topology bias screen, not continuum elasticity, compressibility or dynamic stability validation.

## Bond checks

The synthetic scalar coupon explicitly uses K=1000 N/m, area=25 mm², peak traction=40 kPa, Gc=80 J/m² and damping=0.2 N s/m. These are engineering test values and do not populate the provisional tomato material registry.

The independently expected tensile triangle work is 0.002 J, onset is 1 mm and failure is 4 mm. Monotonic numerical work agrees to rounding precision; discrete damage energy loss differs by 0.0154%. Unloading does not heal. Explicitly ineligible updates do not accumulate damage. Pure compression does not initiate damage. A completely broken bond has exactly zero cohesive stiffness and damping.

The eligibility Boolean is supplied by a test, not detected from a blade. The shear history test only verifies the proposed scalar effective-separation update. It does not validate a physical mixed-mode fracture criterion.

| Mode | Integrated work | Difference from scalar target | Gate |
| --- | --- | --- | --- |
| Scalar opening | 0.002000 J | approximately zero | Pass |
| Five-spring opening | 0.002272 J | +13.60% | Fail |
| Five-spring shear | 0.000716 J | −64.20% | Fail |

The bundle's small-displacement normal tangent is 1000 N/m, while the two shear tangents are approximately 333.33 N/m. Its finite geometric response explains why blindly reusing one scalar law cannot certify a common fracture-energy target. The report does not assume that real materials must have equal mode-I and mode-II fracture energy; rather, different targets and weights must be explicitly defined and verified, not produced accidentally by spring geometry.

Rotation tests preserve bond lengths and remove rigid rotation from local separation using supplied orthonormal frames. They do not implement deformed-frame reconstruction. Degenerate lengths are rejected, even for broken bonds. Both stiffness and damping vanish at full damage. Compression contact after bond failure remains unimplemented; zero cohesive force is not nonpenetration.

## Tests and bounded resources

All 20 focused standard-library tests pass: force/onset/failure reference, fracture work, damage dissipation, contact gating, compression, unloading, exact zero residuals, area subdivision, invalid inputs, bundle tangent response, rigid rotation, frame handling, degenerate springs, mixed history, graph integrity, partial connection, omitted diagonal detection, fixture isolation, mass/area accounting and coarse-grid resource restrictions. Unit-test success is distinct from the failed bundle energy gate above.

The final bounded runner used a 256 MiB address-space ceiling, 30-second CPU ceiling, 45-second wall deadline and the existing common controller lock. Runtime was 1.10 seconds; Linux process VmHWM was 47.10 MiB. These offline ceilings do not replace the simulator's unchanged 10 GB available-RAM and 4 GiB free-VRAM startup gates. No GPU memory was allocated by these standard-library checks.

The earlier `tomato_layout_01` result is superseded for memory reporting: its getrusage high-water value included inherited pre-exec history and should not be interpreted as this Python workload's peak. The final `tomato_layout_02` uses `/proc/self/status` VmHWM and archives matching source files. The second run also adds explicit specimen-size limits and records the unnormalized boundary-volume estimate; constitutive results are unchanged.

## Files and preservation

- `rl/tomato_layout.py`: bounded offline node, bond, patch, diagnostic-cell and fixture registry.
- `rl/tomato_bonds.py`: scalar reference, finite-length bundle response and supplied-frame separation; no simulator binding.
- `rl/offline_tomato_probe.py`: serial bounded layout/coupon report runner with fresh output directory and shared lock.
- `rl/tests/test_tomato_offline.py`: analytical and adversarial topology tests.
- `runs/offline/tomato_layout_02/`: layout, summary, test output, matching source snapshot and preservation hashes.

All 165 pre-existing non-cache files checked under `rl` and `docs/rl` retain their original hashes. Existing controller, scenes, memory safeguard, frozen grasp criteria and draft tomato specifications were not edited. No Newton solver configuration was created or activated. Contact, physical separation, hardware sensing and training remain unvalidated and unstarted.
