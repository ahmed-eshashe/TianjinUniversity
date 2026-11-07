from pathlib import Path
import json,hashlib,shutil
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');run=root/'runs/native/two_joint_contact_20261101_01'
sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'hinge_contact_measurements.json').read_text());assert sup['passed'] and sup['child_exit_code']==0 and not sup['remaining_live_group_members']
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256'];assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
prev=json.loads((root/'runs/native/two_joint_interface_20261101_01/source_integrity.json').read_text())['sha256'];installed={n:h for n,h in prev.items() if not n.startswith(str(root))};assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_two_joint_contact_worker.py','tomato_two_joint_contact_reference.py','tomato_two_joint_reference.py','tomato_hinge_contact_reference.py','tomato_half_step_reaction.py','tomato_offset_contact_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_two_joint_contact_reference.py','tests/test_tomato_two_joint_reference.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
metrics={k:max(c['pulse_check'][k] for c in m['cases']) for k in m['cases'][0]['pulse_check']}
for key in ('force_error_n','point_error_m','torque_error_nm','coast_joint_velocity_change_rad_s'):metrics[key]=max(c[key] for c in m['cases'])
for key in m['cases'][0]['balance_checks']:metrics[key]=max(c['balance_checks'][key] for c in m['cases'])
name='newton-physx-two-joint-contact-20261101'
report=dict(passed=True,supervisor=sup,measurements=m,max_errors=metrics,focused_tests_passed=17,source_sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True)
(out/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
s='''Actual Newton contact on two passive joints — 1 November 2026

PASS for one contact exchange and an explicit outside-particle clearing control in both identity and 90-degree yaw orientations. Full coupling checklist item 15 remains open.

Two locally authored CPU PhysX chains each have a fixed base, two Z revolute joints and two moving 0.02 kg links. Link lengths are 0.02 m, with COM halfway along each link and COM diagonal inertia 0.0001 kg m². The chains start straight, at rest and near the origin. No actuators, stiffness, damping, friction, gravity or PhysX collision shapes are enabled. Newton alone generates particle contact against a kinematic box proxy of the end link (half sizes 0.01,0.005,0.002 m). A 0.01 kg point particle starts at end-link local coordinates (0.004,0.004,0), penetrating the +Y side by 0.001 m. The whole fixture and contact rotate together in the second case.

The actual CUDA Newton collision pipeline generates exactly one unsaturated full-surface soft contact. SolverVBD runs with 16 iterations, fixed penalty, no damping/friction and externally owned rigid state. The actual cached penalty is 1750 N/m. An independent local-plane implicit-particle reference predicts force k*depth/(1+k*dt²/m), contact point, COM torque and particle motion, at dt=1/2400 s. The native cached contact evaluator reconstructs the particle force and opposite link reaction. The worker checks native force within 2e-5 N, point within 1e-7 m and COM torque within 2e-7 N m against the independent reference.

The independent initial planar chain mass matrix is [[0.000220,0.000106],[0.000106,0.000102]] kg m². The end-COM world Jacobian maps the independently predicted reaction to both joint efforts. The full 2x2 solve predicts both joint velocities; positions use the previously established 16-substep TGS factor 17/32. Thus the joint response reference uses the independently predicted contact wrench, rather than simply accepting the measured wrench. Native mass matrix and Jacobian are checked independently too. Gates remain 1e-8 kg m², 1e-6 Jacobian components, 1e-6 rad and 2e-5 rad/s. Whole-chain angular momentum about the fixed base uses the FIRST ROW of the coupled mass matrix times both joint velocities, balanced against particle angular impulse. This avoids treating the fixed-base chain as a free rigid body. Particle linear impulse and position are also checked (2e-7 N s, 1e-7 m); angular balance gate is 2e-8 N m s.

Only the end link receives the world COM reaction wrench via its instantaneous composer. Newton is checked not to move its externally owned rigid proxy. PhysX end-link pose and world COM velocity are copied back exactly into BOTH actual Newton State buffers. Six such state echoes pass. The second interval explicitly moves the particle outside the link and resets its velocity; regenerated contact count is zero and Newton leaves the particle velocity zero. No new link wrench is submitted. Joint velocity drift must stay below 2e-6 rad/s. This is an explicit clearing control, not evidence of natural separation. Near-zero coast drift here is specific to the short, nearly straight fixture.

Exactly two shared PhysX steps and four Newton solver steps ran across the two fixtures. Maximum errors:
'''
for k,v in metrics.items():s+=f'  {k}: {v:.12g}\n'
for c in m['cases']:s+=f"\n{c['id']}: predicted joint velocities {c['expected']['velocity']}; measured {c['after_pulse']['joint_velocity']}; native reaction {c['native_contact']['wrench'][0]}.\n"
s+=f'''\nEight two-joint reference/contract tests and nine supervisor tests passed, including incorrect reaction sign, rotated wrench, angular balance and count-contract rejection. No gate was relaxed. The protected run exited successfully in {sup['elapsed_wall_s']:.2f} seconds with at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. There were no resource warnings, monitor errors or remaining owned live processes. Frozen original production inputs and previously pinned installed dependencies remain unchanged. Source hashes and snapshots are preserved. Run evidence: {run}

Next bounded step: repeated Newton contact on the two-joint chain, updating the end-link proxy every interval and checking natural separation and force clearing. General configurations, longer articulated dynamics, real robot, real blade collision generation and cutting material remain unvalidated.
'''
(out/(name+'.txt')).write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());d['updated']='2026-11-01';i=next(x for x in d['items'] if x['id']==15);i['progress']='Actual Newton contact drives both joints correctly in two orientations: coupled response, particle/chain impulse and exact Newton state feedback pass. Explicit contact clearing passes. Next: repeated two-joint contact and natural separation. Full coupling remains open.';i['evidence']=name+'.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\n1 November 2026 — actual Newton contact on two joints passes in two orientations, including impulse balance and explicit clearing. Next: repeated contact and natural separation. Item 15 remains open. Evidence: '+name+'.txt\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Connect contact to the two-joint chain','Repeat contact on the two-joint chain').replace('Both joints respond correctly to an end-link force in two orientations. Next: apply actual Newton particle contact to the chain.','Actual Newton contact moves both joints as predicted in two orientations. Next: repeat contact and check natural separation.');p.write_text(s)
print(json.dumps(metrics,indent=2))
