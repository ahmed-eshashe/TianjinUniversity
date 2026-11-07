from pathlib import Path
import hashlib,json,shutil
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm')
out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
run=root/'runs/native/feedback_sequence_20261031_01'
sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'feedback_sequence_measurements.json').read_text());assert sup['passed']
pinned=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256']
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in pinned.items())
previous=json.loads((root/'runs/native/contact_feedback_20261031_02/source_integrity.json').read_text())['sha256']
installed={n:h for n,h in previous.items() if not n.startswith(str(root))}
assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_feedback_sequence_worker.py','tomato_feedback_sequence_reference.py','tomato_contact_feedback_worker.py','tomato_isaac_startup_guard.py','tests/test_tomato_feedback_sequence_reference.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,installed_dependencies_unchanged=True),indent=2)+'\n')
steps=[s for c in m['cases'] for s in c['steps']]
metrics={key:max(s['assessment'][key] for s in steps) for key in ('position_error_m','velocity_error_m_s','force_error_n','momentum_increment_error_kg_m_s','impulse_error_kg_m_s','work_identity_error_j','energy_identity_error_j')}
metrics.update({key:max(s[key] for s in steps) for key in ('trajectory_position_error_m','trajectory_velocity_error_m_s','cumulative_impulse_error_kg_m_s')})
contact=m['cases'][0];forces=[s['soft_force_n'][2] for s in contact['steps']]
report=dict(supervisor=sup,measurements=m,max_errors=metrics,source_sha256=pins,focused_tests_passed=14,
 original_frozen_sources_unchanged=True,installed_dependencies_unchanged=True)
(out/'newton-physx-repeated-feedback-check-20261031.json').write_text(json.dumps(report,indent=2)+'\n')
summary=f'''Newton–CPU PhysX repeated contact feedback — 31 October 2026

PASS for 16 consecutive partitioned intervals in two persistent synthetic fixtures. Full checklist item 15 remains unfinished.

The same particle/body states, Newton solver, contact pipeline and contact buffers were reused throughout each fixture. Contacts were regenerated before every Newton step. The contact fixture began with 1 mm penetration and separated naturally; the second fixture began clear and stayed still. No reset, teleport, impulse kick or forced separation was used. Each interval copied actual CPU PhysX pose and COM velocity exactly into both CUDA Newton body states, solved the soft particle with its proxy frozen, collected the actual native contact reaction, applied it once to PhysX, advanced PhysX, and copied the resulting rigid state back before swapping the Newton states.

Exactly 32 Newton steps (two fixtures x 16 intervals) and 16 shared PhysX steps ran. dt=1/1200 s, total simulated duration=0.0133333 s per fixture. Particle/box masses were 0.01/0.02 kg; native contact stiffness was 1750 N/m, with zero radius/margin, gravity, damping and friction. Each Newton step used 16 iterations. CPU PhysX used TGS, explicitly specified/read-back 16 position substeps and zero velocity iterations, with force applied per substep. Local COM offsets and contact torque were zero.

Four active contacts were generated in the contact fixture. Measured forces (N) were {', '.join(f'{f:.8f}' for f in forces[:4])}. Contact count then changed from one to zero for all remaining 12 intervals. No new wrench was submitted on those clear intervals: the instantaneous and permanent composers were inactive and write_data_to_sim had to clear the previous backend force. Measured coast velocities and positions matched zero force. The simultaneous clear control had zero contact, zero force and zero motion throughout. No unexpected contact reappearance or transverse motion occurred.

The independent reference includes nonzero incoming particle and rigid velocities, a unilateral soft contact solve against the frozen pose, and 16 constant-force PhysX substeps. It checks each measured increment and separately advances a full reference trajectory from the initial state. Momentum/impulse are checked per interval and against the accumulated delivered contact impulse. Work is compared against measured kinetic-energy change with the particle and TGS numerical losses accounted separately. The unilateral-potential correction also covers the interval that exits penetration; frozen-proxy splitting work is explicitly reported. Energy conservation is not expected from this stepping scheme.

Maximum errors over both fixtures:
'''
for k,v in metrics.items():summary+=f'  {k}: {v:.9g}\n'
summary+=f'''
Gates were unchanged from the one-interval test: position and accumulated trajectory 1e-7 m; velocity and accumulated velocity 2e-5 m/s; force 2e-5 N; per-interval/accumulated impulse and momentum 2e-7 kg m/s; work/energy identities 2e-8 J. Five sequence reference/guard-contract tests plus nine existing supervisor tests passed. Host controls reject a stale force on a clear interval and invalid inputs.

Protected run duration was {sup['elapsed_wall_s']:.2f} s, retaining at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. It exited normally with no live owned processes, no memory warning and no monitor errors. Source snapshots/hashes were saved; original frozen production inputs and the previously pinned installed dependencies remain unchanged.

Scope: only a short head-on particle/analytic-box sequence. This does not validate long-run stability, rotated/nonzero-COM contact torque, articulated robot feedback, reset/history restoration, time-step sensitivity or the real blade's collision-generated full-surface path.

Next bounded step: validate an off-centre contact reaction, including world torque about the COM and rotated/offset rigid frames. Keep item 15 in progress and item 12 open.
'''
(out/'newton-physx-repeated-feedback-check-20261031.txt').write_text(summary)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());i=next(i for i in d['items'] if i['id']==15)
i['progress']='16 repeated exchanges pass with reused solver/buffers and fresh contacts: four contact steps, then 12 zero-input coast steps. State echo, accumulated impulse and work checks pass. Next: off-centre contact torque and rotated/offset frames. Full coupling validation remains open.'
i['evidence']='newton-physx-repeated-feedback-check-20261031.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\nRepeated feedback: newton-physx-repeated-feedback-check-20261031.txt\nItem 15: 16 exchanges pass, including 12 cleared-contact coast steps. Next: off-centre torque and rotated/offset frames.\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Repeat the contact exchange','Check off-centre contact forces').replace('One contact-force exchange passes, including recoil, momentum and work checks. Next: repeat the exchange and verify contact clearing.','16 contact exchanges pass; forces clear when contact ends. Next: verify off-centre forces, torque and rotated body frames.');p.write_text(s)
print(json.dumps(metrics,indent=2))
