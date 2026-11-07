from pathlib import Path
import json,hashlib,shutil,math
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');run=root/'runs/native/bent_origin_20261101_01'
sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'bent_origin_partial.json').read_text());failure=json.loads((run/'worker_failure.json').read_text());assert not sup['passed'] and sup['child_exit_code']==1 and not sup['remaining_live_group_members']
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256'];assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
prev=json.loads((root/'runs/native/bent_sequence_20261101_01/source_integrity.json').read_text())['sha256'];installed={n:h for n,h in prev.items() if not n.startswith(str(root))};assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_bent_origin_worker.py','tomato_bent_origin_reference.py','tomato_bent_sequence_worker.py','tomato_two_joint_sequence_reference.py','tomato_half_step_reaction.py','tomato_offset_contact_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_bent_origin_reference.py','tests/test_tomato_bent_sequence_reference.py','tests/test_tomato_bent_contact_reference.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
def impulse_trace(case):
 mp=case['particle_mass_kg'];initial=case['initial']['vp'];total=[0.]*3;values=[]
 for s in case['steps']:
  for j in range(3):total[j]+=s['force_n'][j]/2400
  values.append(math.dist([mp*(s['particle_velocity_after'][j]-initial[j]) for j in range(3)],total))
 return values
old_run=root/'runs/native/bent_sequence_20261101_01';old=json.loads((old_run/'bent_sequence_partial.json').read_text());comparison=[]
for a,b in zip(old['cases'],m['cases']):
 x=impulse_trace(a);y=impulse_trace(b)
 comparison.append(dict(id=b['id'],origin_world_m=b['origin_world_m'],initial_particle_position_world_m=b['initial']['p'],
  original_fifth_impulse_error_ns=x[4],translated_fifth_impulse_error_ns=y[4],translated_peak_saved_impulse_error_ns=max(y),
  translated_latest_impulse_error_ns=y[-1],fifth_error_reduction_factor=x[4]/y[4],generated_contact_intervals=b['contact_steps'],generated_coast_intervals=b['coast_steps']))
name='newton-physx-bent-chain-origin-comparison-20261101'
report=dict(passed=False,particle_precision_comparison_improved=True,status='stopped_on_existing_joint_trajectory_position_gate',
 supervisor=sup,partial_measurements=m,failure=failure,comparison=comparison,focused_host_tests_passed=19,source_sha256=pins,
 original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True)
(out/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
s='''Bent-chain contact-origin comparison — 1 November 2026

FULL SEQUENCE NOT PASSED. Translating the entire fixture near the particle/contact origin sharply reduces the particle impulse error, supporting the position-resolution explanation for the earlier failure. The comparison run stops at shared interval 11 on a DIFFERENT unchanged gate: identity joint trajectory position error 1.3003888819085319e-6 rad exceeds 1e-6 rad. The original interval-5 particle impulse failure is preserved. No tolerance was relaxed.

Only a whole-fixture translation was introduced. The original two-link chain, fixed anchor and particle move together, using the negative analytic initial particle position as the translation. Joint angles remain (30,-60) degrees. Both world orientations (identity and 90-degree yaw), masses, dimensions, inertia, stiffness, damping, friction, gravity, time step, solver iterations, contact material and error limits remain as before. Each moving link is 0.02 kg and 0.02 m long, with halfway COM and diagonal COM inertia 0.0001 kg m². A 0.01 kg zero-radius particle contacts the kinematic Newton end-link box, with actual fixed penalty 1750 N/m and dt=1/2400 s. Both engines retain their previous ownership: PhysX advances the joints, Newton advances the particle, and the actual contact reaction drives the end link.

The root transform, fixed anchor world position and articulation initial root position receive the same translation. Native joint defaults, analytic translated forward kinematics and coupled initial mass matrix are checked. A translation-aware wrapper subtracts the anchor offset before calling the unchanged independent planar reference, then restores world particle/contact positions. Forces, COM torques, Jacobian joint effort and dynamics remain translation-invariant. Angular momentum is correctly referenced to the translated fixed anchor, not the world origin. Host tests verify equivalent force, torque, joint response and particle motion under the translation.

Native initial particle positions are within about 8.2 nm of zero in the identity fixture and 0.6 nm in yaw (including the saved small out-of-plane numerical component). The intended contact geometry is the same up to floating-point representation, not bit-identical world coordinates. This comparison changes absolute position resolution while preserving intended mechanics; it does not establish arbitrary-coordinate accuracy.

Saved Newton-side particle impulse comparisons:
'''
for c in comparison:
 s+=f"\n{c['id']}:\n  whole-fixture translation {c['origin_world_m']} m\n  initial particle position {c['initial_particle_position_world_m']} m\n  original interval-5 error {c['original_fifth_impulse_error_ns']:.12g} N s\n  translated interval-5 error {c['translated_fifth_impulse_error_ns']:.12g} N s\n  reduction factor {c['fifth_error_reduction_factor']:.4g}\n  largest translated saved particle impulse error {c['translated_peak_saved_impulse_error_ns']:.12g} N s\n  latest translated error {c['translated_latest_impulse_error_ns']:.12g} N s\n  generated phases: {c['generated_contact_intervals']} contact intervals, {c['generated_coast_intervals']} clear intervals\n"
s+='''
The translated particle errors stay below the unchanged 2e-7 N s gate in all saved Newton updates, with peaks below 2.6e-9 N s. At the original failure interval the reduction is over 800-fold for identity and over 190-fold for yaw. This strengthens the numerical-position-precision explanation; it does not identify all underlying floating-point operations or repair the installed solver.

At identity interval 11, joint local position and velocity errors are 3.969478575838181e-7 rad and 1.2552111072761107e-8 rad/s. Joint trajectory position error is 1.3003888819085319e-6 rad (FAIL), while trajectory velocity error is 6.88943667337405e-7 rad/s (PASS). Particle trajectory position and velocity errors are 4.5180632509067726e-9 m and 9.307869443719734e-7 m/s (PASS). Generalized impulse error is 2.7615866861470902e-12 N m s and angular balance error 1.813363287788772e-10 N m s (PASS). The pattern motivates a joint-angle integration/precision audit; it does not yet establish the cause of this second discrepancy.

Each fixture generated nine contact intervals and then two clear intervals without particle repositioning or reset. The run did not reach the required three coast intervals or finish 32 exchanges. The identity interval-11 assessment raised before yaw's interval-11 post-PhysX assessment; yaw's latest saved Newton particle update is available, but a fully assessed eleventh articulated interval for both cases is not claimed. No full natural-separation qualification is awarded.

'''
s+=f'''Exactly 11 shared PhysX steps, 22 Newton steps and 23 exact state-feedback echoes completed before the stop. Ten bent-reference/contract host tests and nine supervisor tests passed. The supervisor recorded exit 1 after {sup['elapsed_wall_s']:.2f} seconds, with no resource warnings, monitor errors or owned live processes. Available RAM stayed at least {sup['min_available_ram_bytes']/1e9:.2f} GB and free GPU memory at least {sup['min_free_vram_bytes']/1e9:.2f} GB. Frozen original production inputs and previously pinned installed dependencies remain unchanged. Source snapshots, authored translated USD, partial measurements and the original failure are preserved at {run}.

Next bounded step: audit native joint-angle integration and binary32 accumulation against the reference using the saved interval history and installed articulation solver settings. Preserve both failed native runs and all existing limits. Repeated bent-chain qualification, broad coordinate/configuration accuracy, full robot coupling, real blade collision generation and cutting material remain open.
'''
(out/(name+'.txt')).write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());d['updated']='2026-11-01';i=next(x for x in d['items'] if x['id']==15);i['progress']='Contact-origin translation cuts particle impulse error below the unchanged limit (peak <0.0026 µN·s). Run stops at interval 11 on joint trajectory position error: 1.30 µrad vs 1.00 µrad. Next: joint-angle precision audit. Both failed runs preserved; full coupling remains open.';i['evidence']=name+'.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\n1 November 2026 — translated bent-chain comparison: particle impulse error improves by >800x at original identity failure interval, but full test stops at interval 11 on joint trajectory position (1.30 vs 1.00 µrad). Next: joint-angle integration audit; all gates unchanged. Evidence: '+name+'.txt\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Compare contact near the numerical origin','Audit joint-angle precision').replace('Saved particle velocities reproduce exactly from rounded positions. Next: translate the whole fixture near the contact origin and repeat with the same limits.','Moving contact near zero reduces particle error. A joint-position limit now stops the test at interval 11. Next: audit joint-angle integration.');p.write_text(s)
print(json.dumps(comparison,indent=2))
