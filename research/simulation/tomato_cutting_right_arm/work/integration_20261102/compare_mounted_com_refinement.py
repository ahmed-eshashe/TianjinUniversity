"""Compare identical physical COM-reporting fixtures at every common interval."""
from pathlib import Path
import argparse, gzip, hashlib, json
import numpy as np

p = argparse.ArgumentParser()
p.add_argument('--coarse', type=int, default=64)
p.add_argument('--fine', type=int, default=128)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--fine-run', type=Path)
a = p.parse_args()
root = Path(__file__).resolve().parents[2]
out = a.output.resolve()
out.mkdir(exist_ok=False)
plan_path = root/'runs/offline/preload_contact_work_plan_20261102_01/plan.json'
plan = json.loads(plan_path.read_text())
pins = {}
def pin(path):
    pins[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return path
pin(plan_path); pin(Path(__file__).resolve())
runs = {}
for factor in (a.coarse, a.fine):
    run = a.fine_run.resolve() if factor==a.fine and a.fine_run else root/f'runs/native/mounted_target_com_r{factor}_20261102_01'
    result = json.loads(pin(run/'supervisor_result.json').read_text())
    manifest = json.loads(pin(run/'input_manifest.json').read_text())
    closure = json.loads(pin(run/'source_closure.json').read_text())['source_sha256']
    assert result['passed'] and result['worker']['mounted_target_com_component_passed']
    assert manifest['refinement'] == factor
    assert result['worker']['controlled_steps'] == 32*factor
    runs[factor] = dict(run=run, manifest=manifest, closure=closure)
left, right = runs[a.coarse], runs[a.fine]
assert left['closure'] == right['closure'], 'A common frozen source/input closure is required'
assert left['manifest']['duration_s'] == right['manifest']['duration_s']
assert left['manifest']['contact_refresh_clock_s'] == right['manifest']['contact_refresh_clock_s']
assert a.fine % a.coarse == 0
ratio = a.fine//a.coarse
records = []
for label in left['manifest']['cases']:
    rows = []
    for data in (left, right):
        path = pin(data['run']/(label+'_audit.jsonl.gz'))
        with gzip.open(path, 'rt') as f:
            rows.append([json.loads(line) for line in f])
    lr, rr = rows
    assert len(lr) == 8*a.coarse and len(rr) == 8*a.fine
    dx = dv = ferr = fscale = qerr = qderr = 0.
    for i in range(len(lr)):
        j = (i+1)*ratio-1
        assert abs(lr[i]['time_s']-rr[j]['time_s']) < 1e-16
        with np.load(pin(left['run']/f'{label}_interval{i}.npz')) as x, np.load(pin(right['run']/f'{label}_interval{j}.npz')) as y:
            assert np.isfinite(x['x_after']).all() and np.isfinite(y['x_after']).all()
            assert np.isfinite(x['v']).all() and np.isfinite(y['v']).all()
            dx = max(dx, float(abs(x['x_after']-y['x_after']).max()))
            dv = max(dv, float(abs(x['v']-y['v']).max()))
        f0 = np.array(lr[i]['accepted_pressure_wrench_at_actual_tool_com'][:3])
        f1 = np.array(rr[j]['accepted_pressure_wrench_at_actual_tool_com'][:3])
        ferr = max(ferr, float(np.linalg.norm(f0-f1)))
        fscale = max(fscale, float(np.linalg.norm(f0)), float(np.linalg.norm(f1)))
        qerr = max(qerr, float(abs(np.array(lr[i]['q_after'])-rr[j]['q_after']).max()))
        qderr = max(qderr, float(abs(np.array(lr[i]['qd_after'])-rr[j]['qd_after']).max()))
    impulses = [np.array([r['accepted_pressure_wrench_at_actual_tool_com'][:3] for r in rs]).sum(0)*data['manifest']['dt_s'] for data, rs in zip((left,right), rows)]
    ierr = float(np.linalg.norm(impulses[0]-impulses[1]))
    iscale = max(float(np.linalg.norm(v)) for v in impulses)
    criteria = dict(position=dx <= plan['position_finest_pair_budget_m'], velocity=dv <= plan['velocity_finest_pair_budget_m_s'], force=ferr <= plan['force_absolute_budget_n']+plan['force_relative_budget']*fscale, force_impulse=ierr <= plan['impulse_absolute_budget_ns']+plan['impulse_relative_budget']*iscale)
    records.append(dict(case=label, common_physical_clocks=len(lr), maximum_position_component_error_m=dx, maximum_velocity_component_error_m_s=dv, maximum_force_error_n=ferr, force_scale_n=fscale, force_impulse_error_ns=ierr, force_impulse_scale_ns=iscale, maximum_robot_q_error_rad=qerr, maximum_robot_qd_error_rad_s=qderr, criteria=criteria))
report = dict(refinement_passed=all(all(r['criteria'].values()) for r in records), factors=[a.coarse,a.fine], comparisons=records, source_sha256=pins, qualification_scope='Only the identical assigned, nonfracturing 0.8333ms preload fixture at all coarse physical timestamps. No executed route, moving-blade work, fracture, release or training qualification.')
(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='source_sha256'},indent=2))
