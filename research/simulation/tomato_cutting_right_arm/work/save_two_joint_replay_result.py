from pathlib import Path
import json,hashlib,shutil
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');run=root/'runs/native/two_joint_replay_20261101_01'
sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'two_joint_replay_measurements.json').read_text());assert sup['passed'] and sup['child_exit_code']==0 and not sup['remaining_live_group_members']
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256'];assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
prev=json.loads((root/'runs/native/two_joint_sequence_20261101_01/source_integrity.json').read_text())['sha256'];installed={n:h for n,h in prev.items() if not n.startswith(str(root))};assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_two_joint_replay_worker.py','tomato_two_joint_replay_reference.py','tomato_two_joint_sequence_worker.py','tomato_two_joint_sequence_reference.py','tomato_two_joint_contact_worker.py','tomato_two_joint_contact_reference.py','tomato_two_joint_reference.py','tomato_hinge_contact_reference.py','tomato_half_step_reaction.py','tomato_offset_contact_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_two_joint_replay_reference.py','tests/test_tomato_two_joint_sequence_reference.py','tests/test_tomato_two_joint_contact_reference.py','tests/test_tomato_two_joint_reference.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
metrics={k:max(c['assessment']['max_errors'][k] for c in m['comparisons']) for k in m['comparisons'][0]['assessment']['max_errors']}
assert all(v==0 for v in metrics.values())
assert [r['source_contact_count'] for r in m['reset_records']]==[0,0,1,1]
name='newton-physx-two-joint-reset-replay-20261101'
report=dict(passed=True,supervisor=sup,measurements=m,max_replay_errors=metrics,focused_tests_passed=26,source_sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True)
(out/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
s='''Two-joint reset and replay — 1 November 2026

PASS for reset after natural separation and reset during active contact, in identity and 90-degree yaw orientations. All compared replay differences are exactly zero at recorded precision. Full coupling checklist item 15 remains open.

This reuses the same near-origin passive two-joint fixture and coupled Newton/CPU PhysX reference as the preceding repeated-contact diagnostic. Each link has mass 0.02 kg, length 0.02 m, COM halfway along it, and COM diagonal inertia 0.0001 kg m². The base is fixed; gravity, actuators, damping, friction and stiffness are absent. A CUDA Newton kinematic box proxy of the end link contacts one 0.01 kg zero-radius particle. Fixed actual contact penalty is 1750 N/m and dt=1/2400 s. The independent planar reference accounts for changing coupled mass matrix, analytic Jacobian and Coriolis bias; its interval-start acceleration and 16-substep TGS position schedule are qualified only for this short, small-motion fixture.

Three episodes run: a 32-interval baseline, reset after coast followed by two replay intervals, then reset while contact is active followed by a full 32-interval replay. Both full episodes have nine contact intervals and 23 natural coast intervals per orientation. The contact stream before each reset is checked: zero after coast, one during active contact.

Before each reset, BOTH instantaneous and permanent wrench composers are deliberately populated with force (99,-55,33) N and COM torque (1,2,3) N m on the end link. These controls are never advanced into physics. Articulation reset must clear both queues, and both joint positions and velocities are restored to the authored initial values. Newton solver reset restores particle position and velocity in both persistent State buffers while explicitly preserving externally owned rigid state. Particle/body forces are cleared, contact matching is reset and the contact prefix invalidated. The measured reset link packet is then copied into both Newton State buffers. No model, solver, pipeline, body or state-buffer replacement is used.

Four comparisons cover the two-interval prefix and complete 32-interval replay in both orientations. They compare before/after positions and velocities of both joints and the particle, contact counts, force, COM torque, end-link pose/quaternion and linear/angular COM velocity. Replay acceptance uses the existing per-field limits; observed errors are all zero. Reset link packet errors are independently checked within 1e-7. Existing interval and full-trajectory mechanics, native contact, impulse balance, natural separation, force clearing and exact state-feedback checks also run for every episode. No gate is relaxed.

Maximum replay differences:
'''
for k,v in metrics.items():s+=f'  {k}: {v:.12g}\n'
for c in m['comparisons']:s+=f"\nEpisode {c['episode']}, {c['id']}: {c['assessment']['intervals_compared']} intervals compared.\n"
s+=f'''\nExactly 66 shared PhysX steps, 132 Newton steps, 138 exact actual-state feedback echoes, two reset cycles, four dirty-queue resets and four replay comparisons passed. Seventeen two-joint reference/contract tests and nine supervisor tests passed, including rejection of a stale second-joint velocity, incorrect force, contact count and link angular velocity. The protected run exited successfully after {sup['elapsed_wall_s']:.2f} seconds with at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. There were no resource warnings, monitor errors or remaining owned live processes. Frozen original production inputs and previously pinned installed dependencies remain unchanged. Hashes and source snapshots are preserved. Run evidence: {run}

Next bounded step: check contact transfer with the two joints starting in a bent configuration, extending coverage beyond the initially straight chain. Real robot reset, robot drives, broader motion/configurations, contact work/energy, real blade collision generation and cutting material remain unvalidated. Checklist item 22 (eventual real robot/scene reset) is not completed by this synthetic fixture.
'''
(out/(name+'.txt')).write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());d['updated']='2026-11-01';i=next(x for x in d['items'] if x['id']==15);i['progress']='Two-joint reset/replay passes after coast and during contact in both orientations: all compared joint, particle, force and link traces match exactly; dirty force queues clear. Next: contact transfer with a bent chain. Full coupling remains open.';i['evidence']=name+'.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\n1 November 2026 — two-joint reset/replay passes after coast and during contact; replay traces match exactly and dirty queues clear. Next: bent-chain contact transfer. Items 15 and real-robot reset remain open. Evidence: '+name+'.txt\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Check two-joint reset and replay','Check contact with a bent chain').replace('Repeated two-joint contact and natural separation pass in both orientations. Next: check reliable reset and replay, including reset during contact.','Two-joint reset and replay match exactly, including reset during contact. Next: check force transfer with the chain starting bent.');p.write_text(s)
print(json.dumps(metrics,indent=2))
