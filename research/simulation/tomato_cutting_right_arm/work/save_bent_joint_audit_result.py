from pathlib import Path
import json,hashlib,shutil,runpy
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');run=root/'runs/native/bent_origin_20261101_01';audit_dir=root/'runs/offline/bent_joint_precision_20261101_01';audit_dir.mkdir(parents=True,exist_ok=False)
api=runpy.run_path(str(root/'work/audit_bent_joint_precision.py'));a=api['audit']()
assert [c['assessed_intervals'] for c in a['cases']]==[11,10]
for c in a['cases']:
 for mode in ('fused','separate'):
  assert all(r['variants'][mode]['local_error_rad']==0 and r['variants'][mode]['accumulated_error_rad']==0 for r in c['rows'])
assert a['cases'][0]['rows'][-1]['measured_velocity_conditioned_double_accumulated_error_rad']>1e-6
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256'];assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
previous=json.loads((run/'source_integrity.json').read_text())['sha256'];assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in previous.items())
files=[run/'bent_origin_partial.json',run/'worker_failure.json',run/'supervisor_result.json',run/'synthetic_hinges.usda',run/'source_integrity.json',root/'work/audit_bent_joint_precision.py',root/'rl/tomato_two_joint_sequence_reference.py',Path('/home/omen/IsaacLab/source/isaaclab_physx/isaaclab_physx/assets/articulation/articulation_data.py')]
pins={}
for i,p in enumerate(files):
 t=audit_dir/'source_snapshot'/str(i)/p.name;t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,t);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(audit_dir/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,all_native_run_pinned_sources_unchanged=True),indent=2)+'\n')
name='bent-chain-joint-angle-precision-audit-20261101'
report=dict(audit_checks_passed=True,original_native_test_passed=False,native_joint_trajectory_gate_rad=1e-6,audit=a,source_sha256=pins,
 scope='Read-only host audit conditioned on saved endpoint velocities. No native solver run or independent force validation.',
 next_step='Encode the bent rest pose in local joint frames, keeping the same physical link geometry while joint coordinates start near zero; repeat with existing limits.')
(audit_dir/'audit_result.json').write_text(json.dumps(report,indent=2)+'\n');(out/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
s='''Bent-chain joint-angle precision audit — 1 November 2026

AUDIT CHECKS PASS. Both original native failures remain FAILED. In particular, the translated bent-chain test still fails the unchanged 1e-6 rad trajectory joint-position limit at interval 11. No native solver was launched, no installed source was edited and no gate was relaxed.

The read-only audit uses the preserved translated fixture's before/after joint positions and endpoint joint velocities. Identity has eleven complete saved post-PhysX packets, including the failing assessment; yaw has ten. Yaw's eleventh post-PhysX packet is absent because the identity assessment raised first, so it is excluded. This gives 21 recorded joint-state transitions and 42 scalar joint position updates.

Evidence from authored configuration: the simulation uses TGS, articulation position iterations 16 and velocity iterations zero. Installed articulation_data.py line 1697 stores joint position in a wp.float32 TimestampedBuffer. The closed native PhysX solver's internal joint substep telemetry is not present in the saved run. We therefore test a specific integration hypothesis against the endpoints rather than claiming to have directly observed each native arithmetic operation.

Replay hypothesis: divide dt=1/2400 s into sixteen equal substeps. Within each interval linearly interpolate velocity from its saved input to its saved output, using substep endpoint velocities. At every substep, add velocity*dt/16 to joint position and round to IEEE binary32. Evaluate both a fused multiply-add form and a separately rounded multiply/add form. This is explicitly CONDITIONED ON MEASURED ENDPOINT VELOCITIES; it is not an independent dynamics or contact-force reference.

Both arithmetic forms reproduce every saved joint position EXACTLY in both fixtures. They match per interval starting from the saved input position, and also across the whole available history starting from only the initial joint positions, without injecting subsequent measured positions. The maximum local and accumulated position difference is zero for all 42 scalar updates.

For comparison, use the same measured endpoint velocities with an unrounded double-precision integration schedule: q_next = q + dt*v_before + dt*(v_after-v_before)*17/32. This isolates the position accumulation effect from discrepancies in predicted force or joint acceleration. The identity accumulated difference reaches 1.2968965648063602e-6 rad, whereas the original independently propagated mechanical reference differs by 1.3003888819085319e-6 rad. Their difference is approximately 3.49e-9 rad. Thus the measured-velocity-conditioned rounding model accounts for almost all of the observed failing discrepancy; the remaining independent-reference discrepancy is much smaller for this recorded history. The yaw accumulated unrounded difference reaches 8.96640121816894e-7 rad at its tenth saved transition.

At q1 approximately 0.5236 rad, a binary32 spacing is about 5.96e-8 rad. At q2 approximately -1.0472 rad it is about 1.19e-7 rad. Repeatedly adding small substep displacements to these nonzero angles can accumulate a position discrepancy even while endpoint joint velocities remain close to the mechanical reference. This is consistent with the two clear-contact intervals: unforced velocity agreement remains good while accumulated position error grows.

'''
for c in a['cases']:
 s+=f"{c['id']}: {c['assessed_intervals']} complete saved transitions\n"
 for mode in ('fused','separate'):
  s+=f"  {mode}: max local replay error {max(r['variants'][mode]['local_error_rad'] for r in c['rows']):.12g} rad; max accumulated replay error {max(r['variants'][mode]['accumulated_error_rad'] for r in c['rows']):.12g} rad\n"
 s+=f"  measured-velocity-conditioned unrounded accumulated error {max(r['measured_velocity_conditioned_double_accumulated_error_rad'] for r in c['rows']):.12g} rad\n\n"
s+='''Interpretation: the exact endpoint match provides strong evidence that binary32 substep joint-angle accumulation drives the discrepancy in this fixture. Since endpoint velocities are supplied and internal solver substep states are unavailable, this does not independently validate torque integration, uniquely identify compiler arithmetic, or qualify other motions and configurations. The native pass/fail result is unchanged.

All audit assertions pass: expected 11/10 complete transition coverage, exact local and accumulated matches for both arithmetic forms, and the double-precision control exceeding the same 1e-6 rad limit in identity. Original production sources and all source/dependency hashes pinned in the failed translated run remain unchanged. The offline audit preserves code, input snapshots and source hashes.

Next bounded step: express the same physical bent rest configuration through the two local joint frames so the simulated joint coordinates start near zero, retain the whole-fixture translation near the contact origin, and repeat the native 32-interval check with unchanged physics and limits. The independent reference must convert the rebased joint coordinates back to physical link angles. This comparison tests coordinate representation; it must preserve the original failures and does not qualify general joint offsets or real robot motion. Full coupling remains open.
'''
(out/(name+'.txt')).write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());d['updated']='2026-11-01';i=next(x for x in d['items'] if x['id']==15);i['progress']='Joint-angle audit reproduces all 42 saved scalar position updates exactly with 16 binary32 substeps using measured velocities. Unrounded integration explains ~1.297 of the 1.300 µrad drift. Next: encode the same bent pose with joint coordinates near zero and repeat unchanged limits. Original failures remain; full coupling open.';i['evidence']=name+'.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\n1 November 2026 — joint precision audit: 42 scalar positions match exactly under a measured-velocity-conditioned 16-substep binary32 replay. Original native failures remain. Next: rebase joint coordinates while preserving physical bent pose, then repeat unchanged limits. Evidence: '+name+'.txt\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Audit joint-angle precision','Compare joint coordinates near zero').replace('Moving contact near zero reduces particle error. A joint-position limit now stops the test at interval 11. Next: audit joint-angle integration.','Joint-position rounding replay matches all saved updates exactly. Next: keep the bent physical pose while starting joint coordinates near zero.');p.write_text(s)
print('Audit saved: 42 scalar updates reproduce exactly; native failures and limits unchanged.')
