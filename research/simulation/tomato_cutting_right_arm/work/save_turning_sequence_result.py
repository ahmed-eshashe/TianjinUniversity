from pathlib import Path
import json,hashlib,shutil
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm')
out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
run=root/'runs/native/turning_sequence_20261031_01'
sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'turning_sequence_measurements.json').read_text());assert sup['passed']
pinned=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256']
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in pinned.items())
previous=json.loads((root/'runs/native/contact_feedback_20261031_02/source_integrity.json').read_text())['sha256']
installed={n:h for n,h in previous.items() if not n.startswith(str(root))}
assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_turning_sequence_worker.py','tomato_turning_sequence_reference.py','tomato_contact_feedback_worker.py','tomato_offset_contact_reference.py','tomato_physx_proxy_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_turning_sequence_reference.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,installed_dependencies_unchanged=True),indent=2)+'\n')
steps=[s for c in m['cases'] for s in c['steps']]
metrics={key:max(s[key] for s in steps) for key in ('force_error_n','torque_error_nm','point_error_m')}
for section in ('pulse_check','motion_checks'):
 for name,value in steps[0][section].items():
  if isinstance(value,(int,float)) and 'error' in name:metrics[name]=max(s[section][name] for s in steps)
report=dict(supervisor=sup,measurements=m,max_errors=metrics,source_sha256=pins,focused_tests_passed=13,
 original_frozen_sources_unchanged=True,installed_dependencies_unchanged=True)
(out/'newton-physx-turning-sequence-check-20261031.json').write_text(json.dumps(report,indent=2)+'\n')
s='''Newton–CPU PhysX repeated turning contact — 31 October 2026

PASS for two persistent off-centre analytic fixtures over 16 exchanges each. Checklist item 15 remains in progress.

The identity-oriented fixture had zero local COM offset; the second began rotated 90 degrees about Y with local COM (0.002, -0.001, 0.0005) m. Both began at rest, with a particle at body-local (0.004, 0.003, 0.001) m inside a box whose top face was at local z=0.002 m. Newton owned each 0.01 kg soft particle and PhysX owned each 0.02 kg rigid body. Inertia was the same explicitly specified synthetic isotropic 0.0001 kg m² used in the previous test. Gravity, damping, friction, contact radius/margin and PhysX collisions were disabled. No robot or blade was loaded.

Exactly 32 Newton steps and 16 shared CPU PhysX steps were taken, dt=1/1200 s, for 0.0133333 seconds per fixture. The same solver, collision pipeline, contact buffers and pair of Newton states were reused. Each interval copied CPU PhysX link pose and world COM velocity into both Newton body states exactly, generated fresh contacts, froze the proxy during the soft solve, collected the native contact force with the actual solver caches, and sent the world force/torque about the updated COM once to PhysX with positions=None. Updated PhysX pose/twist copied back exactly before state swap. Newton used 16 particle iterations with fixed native stiffness 1750 N/m. PhysX TGS used 16 force substeps with zero velocity iterations, explicitly specified and read back.

Each fixture generated contacts for four intervals, then separated naturally and coasted for 12 intervals. No reset, teleport or artificial separation was used. No new wrench was submitted after contact cleared; the composer and backend had to discard the last reaction. Both linear and angular coast velocities stayed within the existing gates. Updated collision normals matched the current body orientation. Contact force, surface point and COM torque matched an independent moving-plane reference at every active interval.

The independent reference includes incoming particle velocity, the moving/rotating pose sampled at the start of each frozen-proxy soft solve, updated world COM/lever arm, constant-force isotropic TGS rigid substeps, and sequential quaternion increments. A separate full reference trajectory starts from each initial state. Particle and rigid linear impulses and rigid spin impulse are accumulated independently from the measured force/torque stream. Total angular-momentum increments include the finite-step orbital splitting term caused by the TGS body translation schedule; this is not a claim of exact physical conservation for the partitioned scheme. This test does not extend the earlier work/energy qualification to general rotating contacts.

'''
for c in m['cases']:
 s+=f"{c['id']}: active-contact normal change={c['active_contact_normal_change']:.9g}; coast steps={c['coast_steps']}; final angular velocity rad/s={c['steps'][-1]['after']['velocity'][3:]}\n"
s+='\nMaximum errors over all 32 fixture intervals:\n'
for name,value in metrics.items():s+=f'  {name}: {value:.9g}\n'
s+=f'''
Gates: force 2e-5 N; COM torque 2e-7 N m; point/particle/COM position and accumulated trajectory 1e-7 m; particle/COM velocity 2e-5 m/s; rigid angular velocity 2e-6 rad/s; per-step/full-trajectory orientation 1e-6 rad; accumulated linear impulse 2e-7 N s; angular impulse/balance 2e-8 N m s. Every fixture had to change its active-contact normal by at least 1e-5 and provide at least three cleared-contact coast steps. No tolerances were relaxed. Four focused host-reference/guard-contract tests and nine existing supervisor tests passed.

The protected run completed in {sup['elapsed_wall_s']:.2f} seconds, retaining at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. No memory warning or resource-monitor error occurred; no owned live processes remained. Source snapshots/hashes were saved. Original frozen project inputs and previously pinned installed dependencies remain unchanged.

Next bounded step: reset these isolated coupled fixtures and replay the same short trajectory, verifying particle/rigid state and contact/solver history do not leak between runs. Anisotropic inertia, robot articulations, general rotating-contact energy, time-step sensitivity, long-run stability, material cutting and the real blade collision backend remain unvalidated.
'''
(out/'newton-physx-turning-sequence-check-20261031.txt').write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());i=next(i for i in d['items'] if i['id']==15)
i['progress']='Repeated turning contact passes for identity and rotated/offset-COM bodies: updated normals/lever arms, accumulated linear/angular impulse and 12 coast steps each. Next: isolated reset and replay. Full coupling validation remains open.'
i['evidence']='newton-physx-turning-sequence-check-20261031.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\nRepeated turning contact: newton-physx-turning-sequence-check-20261031.txt\nItem 15: turning sequence and clearing pass for both fixtures. Next: isolated reset and replay.\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Repeat contact while turning','Check reset and replay').replace('Off-centre forces and turning effects pass, including a rotated body and shifted centre of mass. Next: repeat contact while the body turns.','Repeated turning contact passes; forces clear after separation. Next: reset the test and check that it repeats cleanly.');p.write_text(s)
print(json.dumps(metrics,indent=2))
