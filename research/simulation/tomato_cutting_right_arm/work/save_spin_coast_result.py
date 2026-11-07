from pathlib import Path
import json,hashlib,shutil
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm')
out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
run=root/'runs/native/spin_coast_20261031_01'
sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'spin_partial.json').read_text());assert not sup['passed']
pinned=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256']
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in pinned.items())
previous=json.loads((root/'runs/native/anisotropic_contact_20261031_01/source_integrity.json').read_text())['source_sha256'] if False else json.loads((root/'runs/native/anisotropic_contact_20261031_01/source_integrity.json').read_text())['sha256']
installed={n:h for n,h in previous.items() if not n.startswith(str(root))}
assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_spin_coast_worker.py','tomato_spin_reference.py','tomato_turning_sequence_reference.py','tomato_offset_contact_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_spin_reference.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
keys=('angular_velocity_error_rad_s','rotation_error_rad','relative_angular_momentum_drift','relative_energy_drift','linear_velocity_error_m_s','com_position_error_m')
enabled=[s for c in m['cases'] if c['gyro_enabled'] for s in c['steps']]
metrics={key:max(s[key] for s in enabled) for key in keys}
report=dict(passed=False,supervisor=sup,partial_measurements=m,max_enabled_partial_errors=metrics,source_sha256=pins,
 failure=json.loads((run/'worker_failure.json').read_text()),focused_tests_passed=14,
 original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True,
 cause_status='COM accuracy gate exceeded; floating-point accumulation and time-step effects are hypotheses, not established causes.')
(out/'physx-spin-coast-accuracy-check-20261031.json').write_text(json.dumps(report,indent=2)+'\n')
s='''CPU PhysX unequal-inertia spin/coast accuracy check — 31 October 2026

FAIL at the preset COM position accuracy gate. The intended 16-step test stopped after nine PhysX steps. General free-spin/gyroscopic accuracy is not qualified by this run. No tolerances were changed and no rerun was used to hide the failure.

Three isolated 0.02 kg CPU PhysX bodies used synthetic unequal principal moments (0.0001, 0.0002, 0.00025) kg m². One had identity orientation/zero COM offset; the other two had the earlier 60-degree oblique orientation and local COM (0.002, -0.001, 0.0005) m. Gyroscopic forces were enabled for the first two and disabled for the third as a control. Each began with body-frame angular velocity (1,2,3) rad/s and world COM linear velocity (0.02,-0.01,0.03) m/s. Gravity, damping, collisions and force queues were disabled/empty. No input wrench was submitted on any step.

The independent reference integrates continuous torque-free Euler equations and quaternion orientation with RK4 and 16 reference substeps per physical step. Host tests verify angular momentum/energy invariants, refinement, principal-axis spin and rotational covariance. CPU PhysX used dt=1/1200 s, TGS with 16 position iterations and zero velocity iterations. Numerical integration is allowed bounded error against the continuous solution; these newly declared sustained-spin gates are separate from the prior initially-resting impulse test.

Preset gates, saved before launch: angular velocity error 0.0002 rad/s; rotation error 0.00002 rad; relative angular-momentum drift 0.0002; relative energy drift 0.0002; linear velocity drift 0.000002 m/s; COM position error 0.0000001 m. The disabled-gyro control was intended to distinguish the full trajectory by at least 0.001 rad/s after 16 steps. That final control gate was not reached.

The identity body completed nine measured samples, the oblique gyro-enabled body nine, and the disabled-gyro control eight. At the ninth oblique-body sample, computed world COM position error was 1.041460411e-7 m (0.104146 micrometres), above the 1e-7 m limit. Linear COM velocity error was zero. Its angular velocity error was 6.68964e-5 rad/s, orientation error 1.20323e-5 rad, relative angular-momentum drift 1.70012e-5 and relative energy drift 5.34260e-6, all within their gates at that sample. These are partial results, not a 16-step pass. The disabled control already differed from continuous Euler angular velocity by about 0.0255 rad/s at sample eight; the complete control comparison is still unvalidated.

Maximum errors in the available enabled-body samples:
'''
for key,value in metrics.items():s+=f'  {key}: {value:.9g}\n'
s+=f'''
All 26 available measured CPU state packets copied exactly into actual CUDA Newton State body arrays. Newton did not run a solver step and no Newton contacts were present: this was a PhysX free-spin/transfer accuracy diagnostic, not a contact-feedback test.

Five focused independent-reference/guard-contract tests and nine supervisor tests passed. The native worker reported failure and exited with code 1; the supervisor correctly rejected it. It stopped in {sup['elapsed_wall_s']:.2f} seconds, retaining at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. No resource warning/monitor error occurred and no owned live processes remained. Source snapshots/hashes and the failed partial data were saved. Original frozen production inputs and pinned installed dependencies remain unchanged.

Next bounded step: compare smaller physical time steps over the same elapsed time, read the engine's direct world COM state alongside the reconstructed link-pose-plus-local-COM value, and investigate float32 position accumulation. These are hypotheses to test, not established explanations. Preserve the failed gate. No new accuracy tolerance should be adopted without an explicit error budget. Checklist item 15 is now an open issue; item 12 remains open. All earlier passed fixture-specific results remain valid within their stated scope.
'''
(out/'physx-spin-coast-accuracy-check-20261031.txt').write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());i=next(i for i in d['items'] if i['id']==15)
i['status']='open';i['progress']='Spin/coast accuracy check stopped at step 9: COM position drift 0.104 µm exceeded the 0.100 µm gate. Available spin/momentum checks stayed within limits. Next: time-step and direct-COM comparison. Full coupling validation remains open.'
i['evidence']='physx-spin-coast-accuracy-check-20261031.txt'
d['counts']={s:sum(i['status']==s for i in d['items']) for s in ('done','open','todo')};p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\nOPEN ACCURACY ISSUE — item 15: physx-spin-coast-accuracy-check-20261031.txt\nSpin/coast stopped at step 9: COM drift 0.104 µm > 0.100 µm. Next: smaller-time-step and direct-COM comparison. Current totals: 13 completed, 2 open issues, 17 upcoming.\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Check spinning and coasting','Investigate small position drift').replace('Unequal turning resistance passes the initial contact check. Next: check how the body spins and coasts with no applied force.','Spin test stopped at step 9: centre-of-mass drift exceeded its accuracy limit. Next: compare smaller time steps and direct centre-of-mass readings.');p.write_text(s)
print(json.dumps(dict(passed=False,partial_errors=metrics,counts=d['counts']),indent=2))
