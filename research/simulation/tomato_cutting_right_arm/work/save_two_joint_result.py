from pathlib import Path
import json,hashlib,shutil
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');run=root/'runs/native/two_joint_interface_20261101_01'
sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'hinge_interface_measurements.json').read_text());assert sup['passed'] and sup['child_exit_code']==0 and not sup['remaining_live_group_members']
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256'];assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
prev=json.loads((root/'runs/native/hinge_replay_20261101_01/source_integrity.json').read_text())['sha256'];installed={n:h for n,h in prev.items() if not n.startswith(str(root))};assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_two_joint_interface_worker.py','tomato_two_joint_reference.py','tomato_isaac_startup_guard.py','tests/test_tomato_two_joint_reference.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
metrics={k:max(c['pulse_check'][k] for c in m['cases']) for k in m['cases'][0]['pulse_check']}
report=dict(passed=True,supervisor=sup,measurements=m,max_errors=metrics,focused_tests_passed=13,source_sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True)
name='physx-two-joint-force-interface-20261101'
(out/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
s='''Two-joint force distribution — 1 November 2026

PASS in identity and 90-degree yaw orientations. This isolated prescribed-wrench check uses CPU PhysX and two passive joints. No actual Newton contact was connected. Full coupling checklist item 15 remains open.

Each locally authored chain has a fixed base and two Z-axis revolute joints, no drives, no stiffness, damping, friction, gravity or collisions. Both moving links have mass 0.02 kg, length 0.02 m, COM halfway along the link and COM diagonal inertia 0.0001 kg m². Both start straight and at rest, near the origin. World force 3 N perpendicular to the chain and world COM torque 0.0012 N m are applied only to the second link. The second fixture rotates both the chain and force by 90 degrees. Joint order and fixed-base topology are checked explicitly; fixed-base Jacobian rows omit the root.

Independent planar mechanics gives initial mass matrix [[0.000220,0.000106],[0.000106,0.000102]] kg m². The end-COM Jacobian has local linear columns (0,0.03,0) and (0,0.01,0), with Z angular columns for both joints. J-transpose times wrench gives joint efforts (0.0912,0.0312) N m. Solving the full 2x2 system predicts joint velocities (0.2229560871,-0.1042484827) rad/s after dt=1/2400 s. The negative second-joint response is a consequence of the off-diagonal inertia. A diagonal-only approximation is explicitly rejected by a host test. Position uses the previously established 16-substep TGS pulse schedule, factor 17/32. This is a short initial-rest reference, not a general trajectory integrator.

The native mass matrix, end-COM world Jacobian, joint position and velocity pass independently fixed gates: 1e-8 kg m², 1e-6 Jacobian components, 1e-6 rad and 2e-5 rad/s respectively. Both instantaneous and permanent force queues were inactive after submission. A second step submitted no force; both measured joint velocities were unchanged at stored precision, within the 2e-6 rad/s clearing gate. Constant joint velocities are specific to this short, nearly straight fixture; they are not assumed for arbitrary unforced articulated dynamics.

Four end-link pose/world-COM-velocity packets copied exactly from CPU to CUDA Warp buffers. This is a format/transport echo, not an actual Newton State or contact solver test. Exactly two shared PhysX steps and zero Newton steps ran.

Maximum reference errors:
'''
for k,v in metrics.items():s+=f'  {k}: {v:.12g}\n'
for c in m['cases']:s+=f"\n{c['id']}: joint velocities {c['after_pulse']['joint_velocity']}; coast velocity change {c['coast_joint_velocity_change_rad_s']} rad/s.\n"
s+=f'''\nFour focused reference/contract tests and nine supervisor tests passed. No acceptance gate was relaxed. The guarded run exited successfully after {sup['elapsed_wall_s']:.2f} seconds, with at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. No resource warning, monitor error or owned live process remained. Frozen original production files and previously pinned installed dependencies remain unchanged; the new modules and additive guard mode are isolated diagnostics. Run evidence: {run}

Next bounded step: actual Newton particle contact on the end link, checking its reaction against the coupled joint response. Real robot, real blade collision generation, cutting material, broad joint configurations and long trajectories remain unvalidated.
'''
(out/(name+'.txt')).write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());d['updated']='2026-11-01';i=next(x for x in d['items'] if x['id']==15);i['progress']='Two-joint prescribed-force check passes in two orientations: coupled mass matrix, world Jacobian, both joint responses and force clearing. Next: actual Newton contact on the end link. Full coupling remains open.';i['evidence']=name+'.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\n1 November 2026 — two-joint force distribution passes in two orientations. Next: actual Newton contact on the end link. Item 15 remains open. Evidence: '+name+'.txt\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Check force transfer across two joints','Connect contact to the two-joint chain').replace('Jointed reset and replay match exactly, including reset during contact. Next: check how one link force moves two connected joints.','Both joints respond correctly to an end-link force in two orientations. Next: apply actual Newton particle contact to the chain.');p.write_text(s)
print(json.dumps(metrics))
