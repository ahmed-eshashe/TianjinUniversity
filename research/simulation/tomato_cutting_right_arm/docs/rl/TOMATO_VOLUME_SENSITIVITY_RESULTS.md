# Tomato volume protection sensitivity results

Date: 19 October 2026. **All 40 selected mechanical paths and 240 load stages pass the unchanged deformation/stability checks**, but mesh independence is not established. A 6 mm bulk mesh changes the slice compression reaction by 12.58%, exceeding the predeclared 10% comparison target. The 4.5 mm versus 5 mm comparison stays within 8.53%; doubling angular surface resolution changes the selected reactions by at most 2.36%.

These are offline static tests of an inactive, uncalibrated hybrid spring/volume model. No simulator, time integration, blade contact or training was launched.

## Study design

Use a one-factor-at-a-time screen, not a full Cartesian parameter grid. Test two deliberately demanding paths for each piece: x compression through 30%, and negative xz simple shear through 50%. Both use the same six load levels and fully prescribed exterior surfaces as the prior study, with interior equilibrium and exact tangent checks. This does not repeat all 18 directions for every variant.

Compare bulk lattice spacing 4.5, 5 and 6 mm with fixed 64-segment exterior rings and fixed meridional resolution. Separately compare 32, 64 and 128 angular surface segments at fixed 5 mm bulk spacing. Regenerate same-side positive stiffness weights against the same synthetic E=30 kPa, Poisson ratio 0.25 and volume-lumping recipe; this is the unchanged discretization rule, not fitting to the sensitivity results. Geometry and per-piece volumes determine the uniform density while the total synthetic mass remains fixed.

At 5 mm, vary one protection parameter at a time: coefficient 2.5/10/40 kPa; activation J=0.35/0.5/0.65; floor J=0.05/0.1/0.2. Default is 10 kPa, activation 0.5, floor 0.1. A lower model floor never changes the independent near-collapse acceptance threshold J>=0.1.

The manifest was saved before mechanical sweeps. The unchanged acceptance checks require force residual below 1e-6, positive signed cell volumes, no local ratio below 0.1, no near-zero spring length and a positive local free-tangent screen. Matched mesh curves are compared at the same strain levels; the planned energy/reaction comparison target is 10%.

## Mesh preparation and exclusions

| Design | Bulk spacing | Angular segments | Total nodes | Preparation |
| --- | --- | --- | --- | --- |
| bulk4p5 | 4.5 mm | 64 | 4106 | Pass |
| bulk5 | 5 mm | 64 | 3735 | Pass |
| bulk6 | 6 mm | 64 | 3329 | Pass |
| surface32 | 5 mm | 32 | 2359 | Reject geometry |
| surface128 | 5 mm | 128 | 6487 | Pass |

The attempted 4 mm bulk grid is not usable with the present tether generator: a new surface node coincides with a material anchor. The generator rejects the zero-length connection. That failure is retained, not bypassed by perturbing nodes or changing rest geometry. A 4.5 mm grid supplies the valid finer comparison.

The 32-segment surface fails the original 1% closed-volume approximation gate and is therefore excluded from mechanical acceptance. Its masses and small-strain checks were still recorded, but a stiffness pass cannot override failed geometry. The 128-segment surface remains inside the existing bounded design caps with 6,487 nodes and 49,054 bonds. No cap or runtime memory reserve was loosened for these variants.

## Mesh response comparison

Compare mean energy density and strain-conjugate reaction density, normalized by each piece's actual closed volume. The reaction is the derivative of energy with respect to the imposed dimensionless strain, not a physical platen force in newtons. All matched stages are included; the table reports the largest absolute difference across both selected paths and both pieces.

| Comparison | Maximum energy-density change | Maximum reaction-density change | 10% target |
| --- | --- | --- | --- |
| bulk4p5 vs bulk5 | 7.74% | 8.53% | Met |
| bulk6 vs bulk5 | 10.82% | 12.58% | Not met |
| surface128 vs bulk5 | 1.69% | 2.36% | Met |

The largest bulk-mesh sensitivity occurs in slice x compression. For the remainder, selected changes are much smaller. The 4.5 mm result passing a two-mesh tolerance does not prove asymptotic convergence; a finer valid grid and/or improved tether-node reuse is still needed. The 64-to-128 comparison tests angular surface resolution only, not meridional, SDF or blade-contact resolution.

Static stability and mesh convergence are different gates. A model can resist inversion at every sampled endpoint while its reaction remains discretization-dependent. Keep 5 mm as the current reference for further comparisons; do not describe 6 mm as converged or select a production mesh from these tests alone.

## Protection parameter sensitivity

All seven settings complete the four selected 5 mm paths. The changes below are maximum absolute differences across matched strain levels relative to the default, not tolerance requirements for intentional material changes.

| Setting | Minimum local J | Maximum energy-density change | Maximum reaction-density change | Paths passed |
| --- | --- | --- | --- | --- |
| baseline | 0.2224 | 0.00% | 0.00% | 4/4 |
| modulus2500 | 0.1214 | 4.70% | 13.16% | 4/4 |
| modulus40000 | 0.3345 | 3.19% | 9.82% | 4/4 |
| activation035 | 0.1905 | 7.05% | 19.49% | 4/4 |
| activation065 | 0.2643 | 11.08% | 21.63% | 4/4 |
| floor005 | 0.2076 | 1.39% | 3.41% | 4/4 |
| floor020 | 0.3031 | 1.27% | 4.93% | 4/4 |

The weakest 2.5 kPa coefficient reaches J=0.1214, only a small margin above the unchanged 0.1 near-collapse threshold. The 40 kPa coefficient keeps a larger local-volume margin, but can stiffen the response and increase numerical work. Earlier activation and a higher floor also increase protection; they do not establish a better physical tomato model. A lower floor is admissible in this screen only because no tested state actually violates the independent threshold.

There is no evidence here to replace the default 10 kPa/0.5/0.1 with a calibrated optimum. Keep it as the comparison reference until measured compression/torque data and mesh convergence support a choice. Parameter interactions, temperature, ripeness, near-incompressibility and contact loads remain untested.

Across all selected cases, minimum J is 0.1214; minimum checked preconditioned tangent eigenvalue is 0.027437; maximum force residual is 9.49e-08. No endpoint is accepted merely because the minimizer returned normally. Local static minima do not establish dynamic stability, global uniqueness or actual cutting performance.

## Numerical evidence and resources

An independent finite-difference energy calculation validates the reported strain-conjugate reaction in all 28 parameter paths at their final states; maximum relative derivative error is below 1e-8. This verifies the new comparison metric rather than assuming its units/sign from a label. The core volume-energy, gradient and tangent code was unchanged.

Mechanical paths ran serially for 144.61 s in total; successful/recorded mesh preparations took 32.94 s. Maximum process VmHWM was 236.05 MiB. Every worker used the common lock, one BLAS thread, a 512 MiB offline address-space limit, a 45-second CPU limit and a 55-second wall limit. No simulator/GPU runtime was imported or allocated by these NumPy/SciPy checks.

All 190 existing non-cache files checked under `rl` and `docs/rl` retained their hashes. Only new sensitivity runner/preparation code and evidence were added; the controller, memory watchdog, grasp criteria, original material model, baseline data and acceptance thresholds remain unchanged. Historical preliminary output-path bookkeeping failures are preserved under `cases`; only complete final runs under `cases_final` enter this report.

Evidence: `runs/offline/tomato_sensitivity_01/case_manifest.json`, `summary.json`, `matched_case_comparisons.json`, `reaction_derivative_audit.json`, mesh preparations, complete case traces, source snapshots and baseline hashes. This task did not activate a runtime model or authorize simulator launch/training.

## Next useful offline work

Resolve the 4 mm coincident-node handling with explicit same-material node reuse or a reviewed surface attachment design, then repeat a finer bulk convergence check. Keep cut-side identities separate; do not weld opposite cut faces. Investigate the cap's compression sensitivity before further material calibration. Native volume-force and cut-face-contact integration remains a separate later task under the unchanged memory safeguard.
