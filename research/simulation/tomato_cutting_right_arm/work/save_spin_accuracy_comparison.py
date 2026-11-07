from pathlib import Path
import hashlib,json,shutil,math,sys
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path.insert(0,str(root/'rl'))
from tomato_float32_coast_replay import replay
out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
pinned=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256']
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in pinned.items())
prev=json.loads((root/'runs/native/anisotropic_contact_20261031_01/source_integrity.json').read_text())['sha256']
installed={n:h for n,h in prev.items() if not n.startswith(str(root))}
assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in installed.items())
files=[root/'rl'/n for n in ('tomato_spin_accuracy_worker.py','tomato_spin_accuracy_audit.py','tomato_spin_reference.py','tomato_float32_coast_replay.py','tomato_turning_sequence_reference.py','tomato_offset_contact_reference.py','tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py','tests/test_tomato_spin_accuracy_audit.py','tests/test_tomato_float32_coast_replay.py')]+[Path(n) for n in installed]
files.append(Path('/home/omen/IsaacLab/source/isaaclab_physx/isaaclab_physx/assets/rigid_object/rigid_object_data.py'))
pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
results=[];rows=[]
fields=('com_position_error_m','api_com_error_m','api_vs_host_com_difference_m','angular_velocity_error_rad_s','rotation_error_rad','relative_angular_momentum_drift','relative_energy_drift')
for denom in (1200,2400,4800):
 run=root/f'runs/native/spin_accuracy_{denom}_20261031_01';sup=json.loads((run/'supervisor_result.json').read_text());m=json.loads((run/'spin_accuracy_measurements.json').read_text());assert sup['passed']
 assert not m['physical_accuracy_passed']
 for i,p in enumerate(files):
  target=run/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 (run/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,previously_pinned_dependencies_unchanged=True),indent=2)+'\n')
 for c in m['cases']:
  trace=replay(c['initial_com_api_world'],c['initial']['velocity'][:3],m['dt_s'],m['physx_steps'])
  one=replay(c['initial_com_api_world'],c['initial']['velocity'][:3],m['dt_s'],m['physx_steps'],substeps=1)
  comparison=dict(max_16_substep_api_residual_m=max(math.dist(p,s['api_com_world']) for p,s in zip(trace,c['steps'])),
   max_1_step_api_residual_m=max(math.dist(p,s['api_com_world']) for p,s in zip(one,c['steps'])),
   final_predicted_com_world=trace[-1],final_api_com_world=c['steps'][-1]['api_com_world'])
  c['float32_substep_replay']=comparison
  row=dict(denominator=denom,id=c['id'],gyro_enabled=c['gyro_enabled'],steps=len(c['steps']),
    accuracy_violations=sorted({v for s in c['steps'] for v in s['accuracy_violations']}),
    **{f:max(s[f] for s in c['steps']) for f in fields},**comparison)
  rows.append(row)
 results.append(dict(supervisor=sup,measurements=m))
report=dict(audit_collection_completed=True,physical_accuracy_passed=False,results=results,summary=rows,
 source_sha256=pins,focused_tests_passed=17,original_frozen_sources_unchanged=True,
 previously_pinned_dependencies_unchanged=True,
 com_api_independent=False,float32_replay_scope='Explicit separate-rounded binary32 add/multiply model seeded with COM API initial state. Strong numerical attribution, not inspection of hidden engine accumulators.')
(out/'physx-spin-time-step-comparison-20261031.json').write_text(json.dumps(report,indent=2)+'\n')
s='''CPU PhysX spin time-step and COM readout comparison — 31 October 2026

MEASUREMENT AUDIT COMPLETE. Original physical accuracy gate remains FAILED at every tested time step. A successful audit supervisor result only means all bounded finite measurements were collected; it does not mean physical qualification passed. The original fail-fast run and its limits remain unchanged.

Three separate guarded runs compared dt=1/1200, 1/2400 and 1/4800 s over the same 0.0133333 s elapsed time, taking 16, 32 and 64 PhysX steps. Each retained the same three original free-spin fixture definitions, initial poses, COM offsets, velocities, unequal principal inertias and gyro settings. No forces were submitted. The same continuous Euler/RK4 reference and accuracy limits were used. All 112 controlled PhysX steps and 336 CUDA Newton body-state echoes completed. No Newton contact solve or mechanical step ran.

COM API provenance: inspection of installed RigidObjectData.root_com_pose_w shows it calls get_root_com_pose_from_root_link_pose on the link pose plus body-local COM. It is therefore a float32 reconstructed COM, not independent telemetry from a hidden engine COM accumulator. The host path reconstructs COM in double precision from the same measured inputs with a normalized quaternion. Both paths were logged. Their small difference is insufficient to explain the coast drift.

Maximum error for the oblique, offset-COM, gyro-enabled fixture:
  dt             COM host (µm)   COM API (µm)   rotation (rad)   angular velocity (rad/s)
'''
for row in rows:
 if row['id']=='oblique_offset_gyro':s+=f"  1/{row['denominator']:<10} {row['com_position_error_m']*1e6:>12.6f} {row['api_com_error_m']*1e6:>14.6f} {row['rotation_error_rad']:>16.9g} {row['angular_velocity_error_rad_s']:>24.9g}\n"
s+='''
The gyro-enabled rotation error approximately halves with each time-step halving. Half/quarter-step rotation passes the original 2e-5 rad limit; the original-step full-duration run slightly exceeds it. Angular-velocity error, relative angular-momentum drift and relative energy drift remain within their original gates for the gyro-enabled fixtures. The disabled-gyro control is clearly distinguishable at all three resolutions. COM velocity remains unchanged, while COM position still exceeds 1e-7 m for offset fixtures. Smaller steps do not monotonically improve that position error; the gyro-disabled control at quarter step accumulates about 3.64 µm.

Offline binary32 replay: the independently coded replay advances constant COM velocity with 16 position increments per physical step, explicitly rounding the substep duration, multiply and addition to binary32. It is seeded only with each fixture's initial COM API position and measured initial constant linear velocity. There is no fitted coefficient, step-dependent correction or tolerance change. A one-increment-per-frame model is retained as a contrast.

Maximum API residuals against the 16-substep binary32 model:
'''
for row in rows:s+=f"  1/{row['denominator']} {row['id']}: {row['max_16_substep_api_residual_m']:.9g} m (one-increment model: {row['max_1_step_api_residual_m']:.9g} m)\n"
s+='''
The identity-origin trajectory matches the 16-substep binary32 positions exactly at every frame. The offset/rotated cases agree within COM reconstruction rounding. This strongly attributes the translational discrepancy to accumulated finite-precision substep additions rather than the continuous rigid-body trajectory or a change in linear velocity. It is numerical evidence, not direct inspection of hidden PhysX state. No general error budget has yet been adopted.

Original limits remain: COM position 1e-7 m, COM linear velocity 2e-6 m/s, continuous spin angular velocity 2e-4 rad/s, rotation 2e-5 rad, relative angular momentum/energy 2e-4. Per-sample violations are preserved rather than stopping collection early. Existing initially-resting impulse and isotropic-contact checks retain their original references and scope.

Four focused audit-classification tests, four binary32-replay tests and nine supervisor tests passed. Controls preserve the historical COM failure and distinguish measurement completion from physical qualification. Native resource protection remained active for every run.

'''
for result in results:
 sup=result['supervisor'];m=result['measurements']
 s+=f"1/{round(1/m['dt_s'])}: {sup['elapsed_wall_s']:.2f} s wall time, minimum RAM {sup['min_available_ram_bytes']/1e9:.2f} GB, free GPU memory {sup['min_free_vram_bytes']/1e9:.2f} GB; exit {sup['child_exit_code']}; no owned live processes.\n"
s+='''
No memory warning or resource-monitor error occurred. Source snapshots/hashes include the COM getter and independent arithmetic model. Original frozen project inputs and previously pinned installed dependencies remain unchanged.

Next bounded step: translate the same isolated fixtures nearer the origin and repeat the fixed-duration check, preserving local geometry/COM/inertia and original gates. This tests the prediction that smaller absolute coordinates reduce accumulation error before considering any error-budget change. Do not claim the general blade/robot pipeline is qualified; checklist items 12 and 15 remain open.
'''
(out/'physx-spin-time-step-comparison-20261031.txt').write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());i=next(i for i in d['items'] if i['id']==15)
i['progress']='Time-step audit complete: smaller steps improve spin rotation, but COM drift still fails. Binary32 substep replay closely reproduces position drift; COM getter is also reconstructed. Next: near-origin comparison with unchanged limits.'
i['evidence']='physx-spin-time-step-comparison-20261031.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\nSpin time-step/COM comparison: physx-spin-time-step-comparison-20261031.txt\nItem 15 stays OPEN. Position drift closely reproduced by binary32 substep accumulation. Next: near-origin test; original limits unchanged.\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Investigate small position drift','Check position rounding near the origin').replace('Spin test stopped at step 9: centre-of-mass drift exceeded its accuracy limit. Next: compare smaller time steps and direct centre-of-mass readings.','Smaller time steps improve turning accuracy; position drift matches accumulated rounding. Next: repeat near the origin with the same accuracy limits.');p.write_text(s)
print(json.dumps([r for r in rows if r['id']=='oblique_offset_gyro'],indent=2))
