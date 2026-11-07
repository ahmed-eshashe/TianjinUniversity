from pathlib import Path
import json,hashlib,shutil,math
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');run=root/'runs/native/bent_sequence_20261101_01'
sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'bent_sequence_partial.json').read_text());failure=json.loads((run/'worker_failure.json').read_text());assert not sup['passed'] and sup['child_exit_code']==1 and not sup['remaining_live_group_members']
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256'];assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
prev=json.loads((root/'runs/native/bent_contact_20261101_01/source_integrity.json').read_text())['sha256'];installed={n:h for n,h in prev.items() if not n.startswith(str(root))};assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_bent_sequence_worker.py','tomato_two_joint_sequence_reference.py','tomato_half_step_reaction.py','tomato_offset_contact_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_bent_sequence_reference.py','tests/test_tomato_bent_contact_reference.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
errors={}
for c in m['cases']:
 s=c['steps'][-1];mp=c['particle_mass_kg'];imp=[sum(x['force_n'][j]/2400 for x in c['steps']) for j in range(3)]
 errors[c['id']]=math.dist([mp*(s['particle_velocity_after'][j]-c['initial']['vp'][j]) for j in range(3)],imp)
name='newton-physx-bent-chain-repeated-contact-20261101'
report=dict(passed=False,status='stopped_on_existing_particle_impulse_gate',supervisor=sup,partial_measurements=m,failure=failure,latest_cumulative_particle_impulse_error_ns=errors,particle_impulse_gate_ns=2e-7,focused_host_tests_passed=16,source_sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True)
(out/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
s='''Repeated bent-chain contact — 1 November 2026

NOT PASSED. The protected run stopped after five shared PhysX intervals when the identity fixture's cumulative particle impulse error exceeded the existing 2e-7 N s gate. This result does not qualify repeated bent-chain contact or natural separation. No tolerance was changed and no replacement passing run was claimed.

The requested diagnostic reused the isolated passive two-joint near-origin fixture, now initialized at joint angles (30,-60) degrees. Identity and 90-degree world-yaw orientations were run together, with a 32-interval cap. Each link has mass 0.02 kg, length 0.02 m, halfway COM and COM diagonal inertia 0.0001 kg m². Gravity, actuators, stiffness, damping and friction are absent. CPU PhysX owns the articulated links; CUDA Newton represents the end link as an externally owned kinematic box. A 0.01 kg zero-radius particle starts at end-link local (0.004,0.004,0), penetrating the +Y face by 0.001 m. Actual fixed contact penalty is 1750 N/m, SolverVBD uses 16 iterations and dt=1/2400 s.

The worker checks initial bent forward kinematics and native coupled mass matrix, regenerates contact records each interval, compares force/point/torque against the independent implicit-particle reference, sends the actual reaction to the end link, and echoes the measured end-link state into both actual Newton State buffers. Its planar reference uses the evolving full mass matrix, analytic Jacobian and Coriolis bias, with interval-start acceleration and the established TGS position factor. Both local and independently propagated trajectory checks remain active.

At the fifth interval, the identity case had cumulative particle impulse error 2.1478593348971286e-7 N s (0.214786 microN s), above the unchanged 2e-7 N s limit (0.200000 microN s). The error is computed from particle mass times velocity change versus the accumulated native contact-force impulse. The yaw-rotated case's Newton-side measurement at the same interval gives 1.215922446109806e-7 N s; its fifth post-PhysX assessment was not completed because the identity assessment raised first. This must not be presented as a fully assessed fifth interval for both cases.

The identity fifth-interval local joint errors were 5.343893105802522e-8 rad and 2.7246903333555395e-7 rad/s, below the existing 1e-6 rad and 2e-5 rad/s limits. Its accumulated trajectory joint errors were 1.1231753349605356e-7 rad and 3.179244297768502e-6 rad/s. Particle trajectory velocity error was 1.999294284619523e-5 m/s, also just within its 2e-5 m/s gate. Local particle position and velocity errors were 2.5973986893535632e-9 m and 6.233756850258426e-6 m/s. Interval generalized impulse error was 6.182010412343055e-11 N m s and whole-chain/particle angular balance error 1.533406481421507e-9 N m s, below their 2e-8 N m s gates. These passing partial checks do not override the failed cumulative particle impulse gate.

The cause is not established. Numerical effects in the particle update and the analytical reference require a focused audit before deciding whether a fixture change or implementation correction is warranted. No evidence here establishes a general contact-transfer defect, and no evidence justifies loosening the gate. The earlier single-exchange bent-chain pass remains limited to its own scope.

'''
s+=f'''Exactly five shared PhysX steps and ten Newton solver steps ran before the stop; eleven actual-state echoes completed. Natural separation was not reached. Seven bent-reference/contract host tests and nine supervisor tests passed; they do not substitute for the failed native test. The supervisor recorded child exit 1 after {sup['elapsed_wall_s']:.2f} seconds, no owned live processes, no resource warnings and no monitor errors. Available RAM stayed at least {sup['min_available_ram_bytes']/1e9:.2f} GB and GPU free memory at least {sup['min_free_vram_bytes']/1e9:.2f} GB. Frozen original production inputs and previously pinned installed dependencies remain unchanged. Source snapshots, partial measurements and the original failure are preserved at {run}.

Next bounded step: audit particle numerical precision and impulse accumulation for this exact failed fixture, retaining the original result and unchanged gate. Full coupling, repeated bent-chain contact, real robot, real blade collision generation and cutting material remain open.
'''
(out/(name+'.txt')).write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());d['updated']='2026-11-01';i=next(x for x in d['items'] if x['id']==15);i['progress']='Repeated bent-chain check stopped at interval 5: cumulative particle impulse error 0.215 µN·s exceeds the unchanged 0.200 µN·s gate. Joint response checks still pass at the stop. Next: particle precision audit; repeated bent contact and full coupling remain open.';i['evidence']=name+'.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\n1 November 2026 — repeated bent-chain native check NOT PASSED: stopped at interval 5 on cumulative particle impulse error (0.215 vs 0.200 µN·s gate). Next: particle precision audit. Original failure retained; no tolerance relaxed. Evidence: '+name+'.txt\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Repeat contact with the bent chain','Audit bent-chain particle precision').replace('Bent-chain contact transfer passes in both orientations. Next: repeat contact and check evolving joint motion and natural separation.','Repeated bent-chain contact stopped on the particle impulse limit at interval 5. Next: audit numerical precision before continuing.');p.write_text(s)
print(json.dumps(errors,indent=2))
