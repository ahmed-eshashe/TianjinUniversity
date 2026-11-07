from pathlib import Path
import json,hashlib,shutil
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');run=root/'runs/native/two_joint_sequence_20261101_01'
sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'hinge_sequence_measurements.json').read_text());assert sup['passed'] and sup['child_exit_code']==0 and not sup['remaining_live_group_members']
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256'];assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
prev=json.loads((root/'runs/native/two_joint_contact_20261101_01/source_integrity.json').read_text())['sha256'];installed={n:h for n,h in prev.items() if not n.startswith(str(root))};assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_two_joint_sequence_worker.py','tomato_two_joint_sequence_reference.py','tomato_two_joint_contact_worker.py','tomato_two_joint_contact_reference.py','tomato_two_joint_reference.py','tomato_hinge_contact_reference.py','tomato_half_step_reaction.py','tomato_offset_contact_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_two_joint_sequence_reference.py','tests/test_tomato_two_joint_contact_reference.py','tests/test_tomato_two_joint_reference.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
metrics={k:max(s['checks'][k] for c in m['cases'] for s in c['steps']) for k in m['cases'][0]['steps'][0]['checks']}
for key in ('force_error_n','torque_error_nm','point_error_m'):metrics[key]=max(s[key] for c in m['cases'] for s in c['steps'])
name='newton-physx-two-joint-repeated-contact-20261101'
report=dict(passed=True,supervisor=sup,measurements=m,max_errors=metrics,focused_tests_passed=22,source_sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True)
(out/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
s='''Repeated Newton contact on two passive joints — 1 November 2026

PASS for 32 persistent exchanges in identity and 90-degree yaw orientations. Each case has nine contact intervals followed by 23 natural coast intervals. Neither particle is repositioned or reset during the sequence. Full coupling item 15 remains open.

The isolated near-origin fixture uses a fixed base and two passive Z joints, with two 0.02 kg links of 0.02 m length, COM halfway along each link, and explicit diagonal COM inertia 0.0001 kg m². Actuators, stiffness, damping, friction and gravity are absent. CPU PhysX owns articulated motion; a CUDA Newton kinematic box proxy represents only the end link. One 0.01 kg zero-radius particle starts at end-link local (0.004,0.004,0) against the box +Y face, penetrating 0.001 m. Box half sizes are (0.01,0.005,0.002) m. Contact uses SolverVBD with 16 iterations, externally owned rigid state, fixed actual penalty 1750 N/m, no damping or friction, and dt=1/2400 s. The second fixture rotates both particle and chain by 90 degrees.

Each interval regenerates collision records and checks the signed-depth contact count and updated world normal. The native cached contact evaluator's force, point and reaction COM torque are compared with an independent planar implicit-particle calculation. The actual collected reaction is sent to only the end link. PhysX advances both joints and sends the measured end-link pose and world COM velocity back to BOTH actual Newton State buffers, with exact equality. The same model, solver, pipeline and buffers persist for the complete sequence; Newton is checked not to advance its externally owned proxy.

An independent planar two-link reference uses changing joint geometry, the full coupled 2x2 mass matrix and velocity-dependent Coriolis terms. It maps the contact wrench through the analytic end-COM Jacobian and predicts joint acceleration. Position follows the established 16-substep TGS factor 17/32 for force increments. This is a short-step approximation, using interval-start acceleration; it is qualified only for this small-motion 32-interval fixture. Both a per-interval reference from measured input and a complete independently propagated trajectory are checked. Native mass matrix is independently checked at initialization. The reference is not a general-purpose long-trajectory or large-motion validation.

Generalized impulse is checked per interval using M*delta(qdot)+C*dt against joint effort impulse. It is not treated as conserved individual joint momentum. Whole-chain angular momentum about the fixed base uses the first row of M(q) times both joint velocities, balanced with particle angular momentum. Accumulated particle impulse is independently checked. Coast acceptance compares velocity with unforced coupled dynamics, allowing normal Coriolis evolution rather than assuming each joint speed must be constant.

Gates unchanged: per-step and trajectory joint position 1e-6 rad; joint velocity 2e-5 rad/s; particle position 1e-7 m; particle velocity 2e-5 m/s; generalized impulse and total angular balance 2e-8 N m s; accumulated particle impulse 2e-7 N s; coast joint velocity reference error 2e-6 rad/s. Contact gates are 2e-5 N force, 2e-7 N m torque and 1e-7 m point. Initial mass matrix gate is 1e-8 kg m². No limit was relaxed.

Natural separation is required after an active contact phase and no contact reappearance is allowed. All later intervals submit no new wrench, both force queues remain clear, and at least three coast intervals are required. Active normal change must exceed 1e-5. Actual changes are about 0.000985. Exactly 32 shared PhysX steps, 64 Newton steps and 66 exact actual-state feedback echoes passed.

Maximum errors:
'''
for k,v in metrics.items():s+=f'  {k}: {v:.12g}\n'
for c in m['cases']:s+=f"\n{c['id']}: {c['contact_steps']} contact intervals, {c['coast_steps']} natural coast intervals; active normal change {c['active_normal_change']:.9g}; final joint state {c['steps'][-1]['after']['q']}, {c['steps'][-1]['after']['qd']}.\n"
s+=f'''\nThirteen two-joint reference/contract tests and nine supervisor tests passed. They include a finite-difference kinematic Jacobian check, bent-chain unforced dynamics with nonzero Coriolis bias, initial contact response, natural separation and strict count contracts. The protected run exited successfully in {sup['elapsed_wall_s']:.2f} seconds, retaining at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. No resource warning, monitor error or owned live process remained. Frozen original production inputs and previously pinned installed libraries remain unchanged; source snapshots and hashes are preserved. Run evidence: {run}

Next bounded step: reset and replay this two-joint contact fixture, including reset while contact is active and clearing deliberately queued forces. Broader configurations, large motion, robot drives, long trajectories, contact work/energy, real blade collision generation and cutting material remain unvalidated.
'''
(out/(name+'.txt')).write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());d['updated']='2026-11-01';i=next(x for x in d['items'] if x['id']==15);i['progress']='Repeated two-joint Newton contact passes in both orientations: 9 contact + 23 natural coast intervals, coupled trajectory/impulse checks and exact state feedback. Next: reset/replay the two-joint fixture, including reset during contact. Full coupling remains open.';i['evidence']=name+'.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\n1 November 2026 — repeated two-joint contact passes: 9 contact + 23 natural coast intervals per orientation. Next: two-joint reset/replay. Item 15 remains open. Evidence: '+name+'.txt\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Repeat contact on the two-joint chain','Check two-joint reset and replay').replace('Actual Newton contact moves both joints as predicted in two orientations. Next: repeat contact and check natural separation.','Repeated two-joint contact and natural separation pass in both orientations. Next: check reliable reset and replay, including reset during contact.');p.write_text(s)
print(json.dumps(metrics,indent=2))
