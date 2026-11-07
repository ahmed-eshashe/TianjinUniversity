from pathlib import Path
import hashlib,json,shutil,math,sys
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path.insert(0,str(root/'rl'))
from tomato_float32_coast_replay import replay
out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
run=root/'runs/native/spin_near_origin_2400_20261031_01';baseline=root/'runs/native/spin_accuracy_2400_20261031_01'
sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'spin_accuracy_measurements.json').read_text());old=json.loads((baseline/'spin_accuracy_measurements.json').read_text())
assert sup['passed'] and m['physical_accuracy_passed'] and not old['physical_accuracy_passed']
assert m['limits']==old['limits'] and m['dt_s']==old['dt_s'] and m['physx_steps']==old['physx_steps']
pinned=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256']
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in pinned.items())
prev=json.loads((baseline/'source_integrity.json').read_text())['sha256'];installed={n:h for n,h in prev.items() if not n.startswith(str(root))}
assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_spin_near_origin_worker.py','tomato_spin_accuracy_audit.py','tomato_spin_reference.py','tomato_float32_coast_replay.py','tomato_turning_sequence_reference.py','tomato_offset_contact_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_near_origin_spin_guard.py')]+[Path(n) for n in installed]
pins={}
for i,p in enumerate(files):
 target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
rows=[]
for near,far in zip(m['cases'],old['cases']):
 assert near['id']==far['id'] and near['gyro_enabled']==far['gyro_enabled']
 assert near['com_local']==far['com_local'] and near['principal']==far['principal']
 assert near['initial']['velocity']==far['initial']['velocity'] and near['initial']['pose'][3:]==far['initial']['pose'][3:]
 assert near['initial']['pose'][:3]==[0.,0.,0.]
 fields=('com_position_error_m','api_com_error_m','api_vs_host_com_difference_m','angular_velocity_error_rad_s','rotation_error_rad','relative_angular_momentum_drift','relative_energy_drift')
 maxima={field:max(s[field] for s in near['steps']) for field in fields}
 old_com=max(s['com_position_error_m'] for s in far['steps'])
 angular_difference=max(math.dist(a['measured']['velocity'][3:],b['measured']['velocity'][3:]) for a,b in zip(near['steps'],far['steps']))
 quaternion_difference=max(math.dist(a['measured']['pose'][3:],b['measured']['pose'][3:]) for a,b in zip(near['steps'],far['steps']))
 predicted=replay(near['initial_com_api_world'],near['initial']['velocity'][:3],m['dt_s'],m['physx_steps'])
 rows.append(dict(id=near['id'],gyro_enabled=near['gyro_enabled'],old_actor_position=far['initial']['pose'][:3],
  new_actor_position=near['initial']['pose'][:3],old_com_position_error_m=old_com,new_max_errors=maxima,
  com_error_reduction_factor=old_com/maxima['com_position_error_m'],angular_velocity_change_from_translation_rad_s=angular_difference,
  quaternion_change_from_translation=quaternion_difference,max_float32_replay_api_residual_m=max(math.dist(p,s['api_com_world']) for p,s in zip(predicted,near['steps']))))
report=dict(passed=True,scope='Near-origin half-step free-spin only; original far-origin failures preserved.',supervisor=sup,measurements=m,
 comparison=rows,source_sha256=pins,baseline_measurements_sha256=hashlib.sha256((baseline/'spin_accuracy_measurements.json').read_bytes()).hexdigest(),
 original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True,focused_tests_passed=10)
(out/'physx-spin-near-origin-check-20261031.json').write_text(json.dumps(report,indent=2)+'\n')
s='''CPU PhysX spin near-origin comparison — 31 October 2026

PASS within the original free-spin accuracy limits for the isolated near-origin setup at dt=1/2400 s. This does not reverse or delete the failed original/far-origin results, or qualify arbitrary world coordinates. Checklist item 15 remains open for complete coupling validation.

The half-step baseline was repeated for the same 0.0133333 seconds: 32 PhysX steps, three fixtures, 96 exact CPU-to-CUDA Newton State echoes, no Newton solver/contact steps. Only initial actor translations changed: the identity body stayed at (0,0,0), while the two oblique/offset-COM bodies moved from (0,0.05,0) and (0,0.10,0) to (0,0,0) m. They can overlap in this isolated test because all collisions are disabled and there are no constraints between the bodies. Rotations, body-local COM, principal inertia, gyro settings, initial COM velocities, time step, duration, reference algorithm and limits were unchanged. Actual starting readbacks were checked for exact matching of all non-translation fields.

Both gyro-enabled bodies satisfied every original gate over all 32 intervals: COM position 1e-7 m, COM velocity 2e-6 m/s, continuous-reference angular velocity 2e-4 rad/s, rotation 2e-5 rad, relative angular-momentum drift 2e-4 and relative energy drift 2e-4. The disabled-gyro control satisfied the translation gates while remaining clearly different from the torque-free Euler angular solution, as expected. All force queues remained inactive. The original-step orientation issue is not solved by translation; the already-tested half-step setting is retained.

Comparison by fixture:
'''
for r in rows:
 e=r['new_max_errors']
 s+=f"\n{r['id']}:\n  COM error before: {r['old_com_position_error_m']*1e6:.6f} µm; near origin: {e['com_position_error_m']*1e6:.6f} µm; reduction factor {r['com_error_reduction_factor']:.3f}.\n  COM API error: {e['api_com_error_m']:.9g} m.\n  Angular velocity error: {e['angular_velocity_error_rad_s']:.9g} rad/s; rotation error: {e['rotation_error_rad']:.9g} rad.\n  Relative angular-momentum/energy drift: {e['relative_angular_momentum_drift']:.9g} / {e['relative_energy_drift']:.9g}.\n  Angular velocity difference from translated baseline: {r['angular_velocity_change_from_translation_rad_s']:.9g} rad/s; quaternion difference: {r['quaternion_change_from_translation']:.9g}.\n  Maximum COM API residual against explicit binary32 substep replay: {r['max_float32_replay_api_residual_m']:.9g} m.\n"
s+='''
The oblique-body translational drift falls by over 20 times while angular traces are unchanged. Together with the earlier explicit binary32 substep replay, this supports accumulated position-rounding as the cause of the far-origin accuracy failure in these fixtures. It is a tested numerical mitigation, not an exposed hidden engine accumulator or a proof that any arbitrary scene can meet a 100 nm position requirement. The COM API remains a float32 reconstruction of link pose plus local offset, not independent native COM telemetry.

The new guard mode requires actual physical_accuracy_passed=True, all 32 steps, all 96 exact state echoes, correct refinement, all three cases and a distinguished gyro control. A guard-contract test rejects data-collection-only success, failed accuracy and wrong counts; nine existing supervisor tests also pass. No tolerances were relaxed and no production scene coordinates were changed.

'''
s+=f'''The protected worker completed in {sup['elapsed_wall_s']:.2f} seconds, retaining at least {sup['min_available_ram_bytes']/1e9:.2f} GB available RAM and {sup['min_free_vram_bytes']/1e9:.2f} GB free GPU memory. No resource warning or monitor error occurred, and no owned live processes remained. Source snapshots/hashes and baseline evidence hashes were saved. Frozen production inputs and installed dependencies remain unchanged.

Next bounded step: combine the validated near-origin/half-step setting with repeated unequal-inertia Newton contact feedback, checking updated world COM torque, angular response and clearing. Any later adoption of scene-local coordinates for real robot links needs its own frame mapping and error budget. Articulated-link dynamics, general contact work/energy, material cutting, broad coordinate precision, long-run stability and the real blade contact backend remain unvalidated.
'''
(out/'physx-spin-near-origin-check-20261031.txt').write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());i=next(i for i in d['items'] if i['id']==15)
i['progress']='Near-origin half-step spin passes unchanged accuracy gates; rotated-body COM drift falls from 0.183 to 0.009 µm with identical angular traces. Far-origin failures preserved. Next: repeated unequal-inertia contact in this validated setting.'
i['evidence']='physx-spin-near-origin-check-20261031.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\nNear-origin spin check: physx-spin-near-origin-check-20261031.txt\nValidated near-origin/half-step free-spin setup passes original gates. Far-origin failures remain preserved; item 15 stays open for broader coupling. Next: repeated unequal-inertia contact.\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Check position rounding near the origin','Combine spinning with contact').replace('Smaller time steps improve turning accuracy; position drift matches accumulated rounding. Next: repeat near the origin with the same accuracy limits.','Near-origin spin passes the unchanged accuracy limits. Next: repeat contact with unequal turning resistance in this tested setup.');p.write_text(s)
print(json.dumps(rows,indent=2))
