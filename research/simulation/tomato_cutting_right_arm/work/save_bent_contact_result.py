from pathlib import Path
import json,hashlib,shutil
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');run=root/'runs/native/bent_contact_20261101_01'
sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'bent_contact_measurements.json').read_text());assert sup['passed'] and sup['child_exit_code']==0 and not sup['remaining_live_group_members']
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256'];assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
prev=json.loads((root/'runs/native/two_joint_replay_20261101_01/source_integrity.json').read_text())['sha256'];installed={n:h for n,h in prev.items() if not n.startswith(str(root))};assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_bent_contact_worker.py','tomato_bent_contact_reference.py','tomato_two_joint_sequence_reference.py','tomato_two_joint_contact_worker.py','tomato_two_joint_contact_reference.py','tomato_two_joint_reference.py','tomato_hinge_contact_reference.py','tomato_half_step_reaction.py','tomato_offset_contact_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_bent_contact_reference.py','tests/test_tomato_two_joint_contact_reference.py','tests/test_tomato_two_joint_reference.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
metrics={k:max(c['pulse_check'][k] for c in m['cases']) for k in m['cases'][0]['pulse_check']}
for key in ('force_error_n','point_error_m','torque_error_nm','coast_joint_velocity_reference_error_rad_s'):metrics[key]=max(c[key] for c in m['cases'])
for key in m['cases'][0]['balance_checks']:metrics[key]=max(c['balance_checks'][key] for c in m['cases'])
name='newton-physx-bent-chain-contact-20261101'
report=dict(passed=True,supervisor=sup,measurements=m,max_errors=metrics,focused_tests_passed=13,source_sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True)
(out/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
s='''Bent-chain contact transfer — 1 November 2026

PASS for one actual Newton contact exchange and explicit clearing control with two passive joints starting at (30,-60) degrees, in identity and 90-degree world-yaw orientations. Full coupling item 15 remains open.

The isolated near-origin chain has a fixed base and two 0.02 kg links, each 0.02 m long with COM halfway along the link and diagonal COM inertia 0.0001 kg m². Both joints start at rest. Gravity, actuators, stiffness, damping and friction are absent. The requested joint angles and independently derived end-link forward kinematics are checked before contact. PhysX owns the articulated motion. CUDA Newton represents the end link as an externally owned kinematic box with half sizes (0.01,0.005,0.002) m. A 0.01 kg zero-radius particle starts at end-link local (0.004,0.004,0), penetrating the +Y face by 0.001 m. SolverVBD runs with 16 iterations, fixed actual penalty 1750 N/m, zero damping/friction, and dt=1/2400 s. Both the chain and contact rotate together for the second fixture.

The analytic mass matrix at this bend is [[0.000216,0.000104],[0.000104,0.000102]] kg m², rather than the straight-chain matrix. The analytic world end-COM Jacobian uses the two different link angles. Both quantities are compared independently with native PhysX values. The independent implicit-particle reference predicts contact force, point and COM torque, then J-transpose maps that predicted reaction into generalized joint effort. Solving the full coupled system predicts both joint velocity increments. Joint position is referenced to the nonzero initial angles with the established 16-substep TGS factor 17/32. This is an initial-rest short-step fixture, not a general trajectory qualification.

Actual native contact reaction is submitted only to the end link through the world-wrench interface. Newton must not move its externally owned proxy. The measured PhysX link pose and world COM velocity are copied exactly into both actual Newton State buffers. Particle linear impulse and position are checked independently. Whole-chain angular momentum about the fixed base uses the first row of the analytic mass matrix evaluated at the measured post-pulse joint angles, multiplied by both joint velocities, balanced against particle angular momentum.

The clearing interval explicitly moves the particle outside the link and resets its velocity. Regenerated contact count must be zero and no new wrench is submitted; both composers remain inactive. Coast joint velocity is compared with the analytic unforced bent-chain dynamics, including Coriolis terms, rather than assumed constant. This explicit control does not test natural separation in a bent configuration.

Unchanged gates: mass matrix 1e-8 kg m²; Jacobian components 1e-6; joint position 1e-6 rad; joint velocity 2e-5 rad/s; native contact force 2e-5 N; contact point and particle position 1e-7 m; contact torque 2e-7 N m; particle impulse 2e-7 N s; total angular balance 2e-8 N m s; coast joint velocity reference error 2e-6 rad/s. Forward kinematics gate 1e-6 over the pose packet. Exactly two shared PhysX steps, four Newton steps, six exact actual-state echoes and two clearing controls passed. No gate was relaxed.

Maximum errors:
'''
for k,v in metrics.items():s+=f'  {k}: {v:.12g}\n'
for c in m['cases']:s+=f"\n{c['id']}: initial joints {c['before']['joint_position']}; predicted joint velocities {c['expected']['velocity']}; measured {c['after_pulse']['joint_velocity']}; predicted coast {c['coast_velocity_reference']}; measured coast {c['after_coast']['joint_velocity']}.\n"
s+=f'''\nFour focused reference/guard-contract tests and nine supervisor tests passed, including rotated response, rejection of a straight-chain mass matrix and nonconstant unforced bent-chain speed. The protected run exited successfully in {sup['elapsed_wall_s']:.2f} seconds with at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. There were no resource warnings, monitor errors or remaining owned live processes. Frozen original production inputs and previously pinned installed dependencies remain unchanged. Source hashes and snapshots are preserved. Run evidence: {run}

Next bounded step: repeated contact from this bent initial configuration, checking evolving dynamics and natural separation. Broader configurations, large motion, robot drives, real robot reset, contact work/energy, real blade collision generation and cutting material remain unvalidated.
'''
(out/(name+'.txt')).write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());d['updated']='2026-11-01';i=next(x for x in d['items'] if x['id']==15);i['progress']='Bent-chain Newton contact passes at initial joints 30°/-60° in two orientations: changed mass matrix/Jacobian, joint response, impulse balance, state feedback and explicit clearing. Next: repeated bent-chain contact and natural separation. Full coupling remains open.';i['evidence']=name+'.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\n1 November 2026 — bent-chain contact passes at initial joints 30°/-60° in two orientations. Next: repeated bent-chain contact and natural separation. Item 15 remains open. Evidence: '+name+'.txt\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Check contact with a bent chain','Repeat contact with the bent chain').replace('Two-joint reset and replay match exactly, including reset during contact. Next: check force transfer with the chain starting bent.','Bent-chain contact transfer passes in both orientations. Next: repeat contact and check evolving joint motion and natural separation.');p.write_text(s)
print(json.dumps(metrics,indent=2))
