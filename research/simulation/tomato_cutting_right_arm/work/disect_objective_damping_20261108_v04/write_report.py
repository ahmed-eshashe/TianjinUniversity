from pathlib import Path
import json,hashlib,shutil,datetime
from zoneinfo import ZoneInfo
w=Path(__file__).resolve().parent;diag=w.parent/'disect_stability_20261108_v03';a=json.loads((diag/'initial_analysis.json').read_text());c=json.loads((w/'controls_result.json').read_text());s=json.loads((w/'settle_result.json').read_text());f=json.loads((w/'affine_control.json').read_text());long=json.loads((w/'long_settle_result.json').read_text()) if (w/'long_settle_result.json').exists() else None
report='''DiSECt stability diagnosis and relative-velocity correction — 8 November 2026

DECISION AND SCOPE
The initial NaN failure had an explicit timestep far beyond the independently estimated viscous limit. Merely reducing the timestep did not make the original implementation usable: a separate hydrostatic damping frame error produced nonphysical internal forces under common translation. A separate corrected candidate fixes that term without reducing damping, stiffness, mass or gravity.
The corrected candidate passes the independent translation/resolved-deformation controls and the short 20ms gravity stability test. This is an intact bulk FEM component result, not a cutting-model or robot-contact qualification. Original production checkpoint 6925 and all previous failed states/verdicts remain preserved. No contact, fracture or training was attempted.

INITIAL-STATE AND EXPLICIT-STEP DIAGNOSIS
All captured initial positions, velocities, masses, inverse masses, rest poses, material constants and rest forces are finite. Physical mass 121.671g, minimum free nodal mass 6.53e-8kg. Max rest deformation-gradient error 4.13e-5; max zero-velocity rest force 1.13e-6 model N; max free rest acceleration 2.70m/s2. These rounding effects are recorded; the initial state was not itself NaN.
An independently assembled rest-linearized viscous operator has largest eigenvalue 5.31e6/s in the original implementation. Its damping-only scalar explicit limit is about 3.77e-7s; the old 1e-5s step is about 26.6 times larger. A seeded velocity-field kernel check agrees with this operator to 0.0144% in global force norm. Combined row-scale estimate ~2.70e-7s. These are diagnostic linearized estimates, not a theorem of nonlinear/contact stability.
A same-parameter run at 2e-7s remains finite but fails the declared volume gate at 16.2ms (ratio .04374). It remains FAILED. No failed result was re-labelled as passing.

SOURCE CORRECTION
In dflex/sim.py eval_tetrahedra, hydrostatic damping used dot(dJdx1,v1)+dot(dJdx2,v2)+dot(dJdx3,v3). The candidate uses v1-v0, v2-v0 and v3-v0. These are the relative velocities associated with the deformation Jacobian. Coefficient=10 remains unchanged. This fixes common-translation invariance of that term; it is NOT a claim of full rotational objectivity of every damping term or a reproduction of the original executable's physics.
The old rest-linearized operator predicts global force norm .1787 model N under uniform [0,-.1,0]m/s translation even though strain rate is zero. Forces sum near zero but are nonzero internally. This is an independently identified formulation defect. The causal share of every term in the original nonlinear collapse is not isolated by this finding alone.
All modifications are in v04. Prior vendor copies, production source and controller were not replaced. relative_damping.patch and newly compiled kernel/source hashes identify the candidate.

INDEPENDENT CONTROLS
At identical initial geometry:
- Uniform translation: added corrected GPU force norm ~1.28e-12 model N, below the prospective absolute 1e-7 diagnostic tolerance.
- Seeded deformation field: corrected kernel versus independent viscous operator differs by 0.0135% global force norm; damping power is negative.
- Adding common translation to that field changes forces by 0.00241%, below 0.1%.
- Low-signal affine strain rate .01/s FAILS the 0.1% relative target: observed .312%. This failed check is preserved; no low-force precision qualification follows.
- A prospectively documented 1/s affine field, 100x stronger, passes at .00310% relative error, absolute norm error 3.42e-7 model N with reference norm .01102 model N, and negative damping power. Similar absolute error at the smaller signal is consistent with a float32 subtraction/rounding floor but does not identify every rounding source. The threshold was not widened. The larger-field result establishes a resolved-signal check only, not a retroactive pass for the smaller field.
An offline four-node rigid free-fall control showed up to 2.38% transient volume drift from float32 position accumulation at tiny steps, versus nearly exact float64 translation. Its final ratio returned near 1; precision alone did not reproduce the full failed-FEM collapse. Finite-precision limitations remain relevant.

CORRECTED SHORT GRAVITY CHECK
Independent corrected damping spectrum ~6.41e6/s; combined row-scale estimate ~2.37e-7s. Selected timestep 1.5e-7s, rounded down from 75% of that scale before dynamics. Same mesh/material/damping/support/ground constants; only relative-velocity bug fix and timestep differ from the earlier failed setup.
133334 intervals / .0200001s complete normally: all saved states finite, minimum sampled volume ratio .85594, sampled board penetration zero and supports exact. Not settled: late maximum speed .2139m/s. Stepping takes 12.257 wall seconds (~612.8 wall seconds per simulated second). Snapshot GPU process memory 124MiB during the later long run is not a peak measurement. This headless bulk-only cost excludes fracture/contact interface work and cannot be advertised as full-cut throughput.

SUSTAINED ONE-SECOND CHECK
'''
if long:
 report+=f"Outcome: {'PASS for declared intact-bulk settling component' if long['passed'] else 'FAIL for complete settling gate'}. Process result and detailed histories: long_settle_result.json. Simulated {long['simulated_s']:.9f}s, stepping wall {long['stepping_wall_s']:.3f}s, cost {long['wall_s_per_sim_s']:.1f} wall seconds per simulated second. Stop={long['stop']}. Minimum sampled volume ratio {long['minimum_sampled_volume_ratio']:.6g}; maximum sampled board penetration {long['maximum_sampled_board_penetration_m']:.6g}m; last-0.1s maximum speed {long['late_max_speed_m_s']}m/s. The original 1mm/s final-speed limit is unchanged.\n"
else:report+='Running under a 1200s cap, sized from measured throughput. No sustained-settling pass has been recorded yet.\n'
precision=json.loads((w/'position_precision_check.json').read_text()) if (w/'position_precision_check.json').exists() else None
if precision:
 report+=f"\nFinal kinematic representability check: {precision['such_components_rounded_to_zero_position_increment']} of {precision['free_velocity_components_over_1mm_s']} free velocity components above 1mm/s round to zero position increments at dt=1.5e-7s in float32. Maximum reported nodal speed {precision['max_reported_node_speed_m_s']:.6g}m/s. This is a direct final-state one-update calculation, not an observed complete position history or proof of all error sources. It identifies a position/velocity consistency blocker; it does not justify lowering the settling criterion.\n"
report+='''
INTERPRETATION AND NEXT ACTION
The fast prism example used a different mesh and timestep. Our 5762-node / 28727-tet tomato representation at unchanged damping requires a much smaller explicit step. Compare models/resolutions explicitly; no equal-accuracy speedup is claimed against the original custom solver's 9200–9600 wall seconds/simulated second loaded sample. One bulk hold is also not a full slicing episode.
This candidate is useful for isolated numerical investigation; it is not yet a practical learning backend. Do not start contact/cutting if the settling gate fails. Before another expensive physical cohort, choose a supported numerical route that avoids the explicit damping bottleneck, or justify a new material/mesh approximation with declared limits. Do not silently lower viscosity or coarsen geometry until a slice appears.
Before any cut: original blade triangles do not automatically replace the hardcoded five-parameter analytic SDF contact shape. Exact original-blade contact needs a checked adapter or an explicitly scoped proxy. Cutting-spring damage is updated per invocation without explicit dt normalization; naive timestep refinement changes damage rate. No fracture-law mapping, skin equivalence, original finite-board qualification, coupled robot force/work or experimental validation is established here.

FILES
result.json; relative_damping.patch; controls_result.json; affine_low_signal_failure.json; affine_control.json; contract.json and long_gravity_contract.json; settle_result.json and long_settle_result.json when available; source/kernel/mesh/checkpoint hashes in integrity.json; gravity/long_gravity/controls logs; stability_diagnosis.png/.pdf. Initial diagnosis and failed same-law gravity traces are in ../disect_stability_20261108_v03. No failed state artifact is an accepted checkpoint.
'''
(w/'REPORT.txt').write_text(report)
print('Report written; sustained state:', 'complete' if long else 'running')
