"""Read-only evidence/observability audit. No simulator, no gate changes."""
from pathlib import Path
import hashlib
import json
import numpy as np

R = Path(__file__).resolve().parents[2]
out = Path(__file__).parent / 'measurements.json'
if out.exists():
    raise RuntimeError('Preserve existing audit; use a new version')
previous = json.loads((R/'work/astra_effort_resolution_20261102/verification01/measurements.json').read_text())
for name, sha in previous['raw_sha256'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == sha, name

# Independent kinematic work estimators, not interchangeable physical truths.
run = R/'runs/native/moving_contact_c1_down_20261102_01'
cases = []
for label in ['no_feedback', 'feedback', 'replay']:
    rows = json.loads((run/f'{label}_robot_audit.json').read_text())
    w_mid = w_displacement = velocity_rounding_budget = 0.
    for i, row in enumerate(rows):
        z = np.load(run/f'{label}_robot_interval{i}.npz')
        dt = float(z['dt'].item())
        tau = np.asarray(row['robot_audit']['commanded_effort_nm'])
        v0, v1 = [np.asarray(row[k]) for k in ['qd_before', 'qd_after']]
        q0, q1 = [np.asarray(row[k]) for k in ['q_before', 'q_after']]
        w_mid += float(tau @ ((v0+v1)*.5) * dt)
        w_displacement += float(tau @ (q1-q0))
        # Conditional storage-rounding envelope ONLY, not a total error bound.
        # Check JSON values really preserve float32 endpoints before using ULPs.
        for v in [v0, v1]:
            assert np.array_equal(v, v.astype(np.float32).astype(float))
        ulp0 = np.abs(np.spacing(v0.astype(np.float32)).astype(float))
        ulp1 = np.abs(np.spacing(v1.astype(np.float32)).astype(float))
        velocity_rounding_budget += float(np.abs(tau) @ (.25*(ulp0+ulp1))*dt)
    cases.append(dict(case=label, intervals=len(rows), known_input_midpoint_work_j=w_mid,
        known_input_displacement_work_j=w_displacement,
        displacement_minus_midpoint_j=w_displacement-w_mid,
        conditional_velocity_storage_rounding_envelope_j=velocity_rounding_budget))

# Exact analytic counterexample to recovering work from mean torque and endpoint
# states. v=v0+b*sin(2*pi*t/T) has identical endpoint velocities and displacement;
# tau=a +/- c*sin(2*pi*t/T) has identical interval mean. Work differs by T*b*c.
# This proves insufficiency of a generic readout contract, NOT actual PhysX error.
T, a, v0, b, c = 1/240, 1., .001, .001, .01
baseline = T*a*v0
plus, minus = baseline + T*b*c/2, baseline - T*b*c/2
assert np.isclose(plus-minus, T*b*c, rtol=1e-12, atol=0)

result = dict(status='audit_complete_no_physical_gate_closed',
    preserved_evidence_hashes_checked=len(previous['raw_sha256']),
    saved_known_input_estimator_comparisons=cases,
    observability_counterexample=dict(interval_s=T, same_mean_torque_nm=a,
        same_endpoint_velocity_rad_s=v0, same_displacement_rad=T*v0,
        work_plus_j=plus, work_minus_j=minus, difference_j=plus-minus,
        scope='Analytic information counterexample, not a measured simulator trajectory'),
    implication='Endpoint states plus interval-average total load do not uniquely determine motor work without a justified discrete identity or within-step drive impulse/velocity information.',
    native_runs=0, physics_changed=False, thresholds_changed=False,
    full_motor_work_gate_closed=False)
out.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
