from pathlib import Path
import json,hashlib,shutil,math,runpy
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');original=root/'runs/native/bent_sequence_20261101_01';audit_dir=root/'runs/offline/bent_particle_precision_20261101_01';audit_dir.mkdir(parents=True,exist_ok=False)
api=runpy.run_path(str(root/'work/audit_bent_particle_precision.py'));a=api['audit']()
for c in a['cases']:
 assert max(s['velocity_reconstruction_error_m_s'] for s in c['steps'])==0
 assert max(max(s['variants']['fused']['position_offset_in_binary32_ulps']) for s in c['steps'])<1
 assert max(s['variants']['fused']['decomposition_identity_error_ns'] for s in c['steps'])<1e-15
frozen=json.loads((root/'runs/offline/tomato_preupgrade_20261027T171031Z/single_blade_disabled_worker_config_2132.json').read_text())['source_sha256'];assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in frozen.items())
previous=json.loads((original/'source_integrity.json').read_text())['sha256'];assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in previous.items())
newton=Path('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/solvers/vbd')
files=[original/'bent_sequence_partial.json',original/'worker_failure.json',original/'supervisor_result.json',original/'source_integrity.json',root/'work/audit_bent_particle_precision.py',newton/'solver_vbd.py',newton/'particle_vbd_kernels.py']
pins={}
for i,p in enumerate(files):
 target=audit_dir/'source_snapshot'/str(i)/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(audit_dir/'source_integrity.json').write_text(json.dumps(dict(sha256=pins,original_frozen_sources_unchanged=True,all_failed_run_pinned_sources_unchanged=True),indent=2)+'\n')
name='bent-chain-particle-precision-audit-20261101'
report=dict(audit_checks_passed=True,original_native_test_passed=False,acceptance_gate_ns=2e-7,audit=a,source_sha256=pins,
 scope='Read-only host audit of saved five-interval evidence, not a new native solver run.',next_step='Translate the complete fixture near the contact origin and repeat without changing the physical setup or gate.')
(audit_dir/'audit_result.json').write_text(json.dumps(report,indent=2)+'\n');(out/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
s='''Bent-chain particle precision audit — 1 November 2026

AUDIT CHECKS PASS. The original repeated bent-chain native test remains FAILED at interval 5 on the unchanged 2e-7 N s cumulative particle impulse gate. No native solver was launched for this audit, no installed library or production file was changed, and no tolerance was relaxed.

Read-only evidence: saved before/after particle positions, velocities and native cached contact forces from both five-interval fixture traces. The identity fifth assessment failed before the yaw fixture's fifth post-PhysX assessment; both Newton particle updates are present. The audit uses only saved Newton-side data for the yaw fifth interval and does not claim that its articulated fifth interval was fully assessed.

Installed implementation inspected:
- particle_vbd_kernels.py forward_step stores previous position and constructs the inertial position prediction from current position plus velocity*dt (no gravity or external particle force here).
- update_velocity at lines 1504–1506 computes (position - previous_position)/dt using Warp vec3/float values.
- solver_vbd.py launches update_velocity at lines 3796–3797 after the position solve.
- The particle position solve balances mass*(inertial_position-position)/dt² with contact force. The audit checks its equilibrium using the collected final native contact force, rather than replacing that force with the independent plane reference.

A host emulation rounds arithmetic through IEEE binary32 using struct pack/unpack. Reconstructing velocity from the two saved positions and binary32 dt matches every stored particle velocity exactly in all ten available updates. A reciprocal-multiply variant also matches to at most 1.8e-15 m/s. This establishes the saved velocities' dependence on rounded absolute position differences in this fixture.

For each axis, the audit predicts the inertial position with both fused-add and separately rounded multiply/add variants, then forms the force-balance position x_equilibrium = x_inertia + dt32²*F_native/m. Every observed solved position lies less than one local binary32 position spacing from this prediction: maximum 0.848851 spacing for identity and 0.922891 for yaw. These are checks against stored force equilibrium, not a new simulation or an exact emulation of every Newton iteration. Force-kernel roundoff, convergence and position quantization cannot be uniquely separated by these endpoint data alone.

At an x coordinate around 0.0316 m, one binary32 spacing is 3.725290298e-9 m. Dividing by dt=1/2400 s corresponds to roughly 8.94e-6 m/s, or 8.94e-8 N s for a 0.01 kg particle. A sub-spacing force-balance residual can therefore be significant relative to a 2e-7 N s accumulated gate over several updates.

The audit decomposes each observed impulse residual exactly (within arithmetic rounding) into:
  m/dt * (x_inertia - x_previous - dt*v_before)
  + [m/dt * (x_after - x_inertia) - dt*F_native]
  + m * [v_after - (x_after-x_previous)/dt].
These respectively describe inertial prediction rounding, the position-solve force-balance residual and final velocity reconstruction rounding. This algebraic identity is an accounting check, not independent proof of a unique root cause. In this saved run the position-solve term dominates; the inertial predictor term is negligible. Combined with exact velocity reconstruction and sub-spacing equilibrium offsets, the evidence points to a binary32 position-resolution limitation contributing to the gate failure.

'''
for c in a['cases']:
 s+=f"{c['id']}:\n  cumulative particle impulse error {c['latest_cumulative_impulse_error_ns']:.12g} N s\n  maximum saved velocity reconstruction error {max(x['velocity_reconstruction_error_m_s'] for x in c['steps']):.12g} m/s\n  maximum position-equilibrium offset {max(max(x['variants']['fused']['position_offset_in_binary32_ulps']) for x in c['steps']):.9g} binary32 spacings\n"
 for key in ('forward_rounding_impulse_ns','stationarity_impulse_ns','velocity_rounding_impulse_ns'):
  total=[sum(x['variants']['fused'][key][j] for x in c['steps']) for j in range(3)];s+=f'  norm of accumulated {key}: {math.hypot(*total):.12g} N s\n'
 s+=f"  maximum residual-decomposition identity error {max(x['variants']['fused']['decomposition_identity_error_ns'] for x in c['steps']):.12g} N s\n\n"
s+='''The unchanged identity impulse failure remains 2.147859335e-7 N s versus the 2e-7 N s gate. The rotated case's saved particle error is 1.215922446e-7 N s. All three audit assertions pass for both cases: exact velocity reconstruction, position-equilibrium offsets below one spacing, and decomposition identity error below 1e-15 N s. Original frozen production sources and every source/dependency pinned by the failed native run remain unchanged. Evidence and code snapshots/hashes are saved with the offline audit.

Next bounded step: translate the entire chain, fixed anchor and particle together so contact occurs close to the numerical origin, then repeat the native 32-interval test with the same physical dimensions, orientations, time step, materials and acceptance gate. A whole-fixture translation preserves the intended mechanics but changes absolute position resolution. This comparison can test the coordinate-precision explanation. It does not justify replacing the original failed result or claiming arbitrary-coordinate accuracy. Full coupling and repeated bent-chain qualification remain open.
'''
(out/(name+'.txt')).write_text(s)
p=out/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());d['updated']='2026-11-01';i=next(x for x in d['items'] if x['id']==15);i['progress']='Particle audit reproduces every saved velocity exactly from binary32 position differences; force-balance position offsets are below one spacing. Original bent-chain impulse failure remains. Next: translate the whole fixture near the contact origin and repeat with unchanged limits. Full coupling remains open.';i['evidence']=name+'.txt';p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'isaac-sim-progress-checklist.txt';p.write_text(p.read_text()+'\n1 November 2026 — particle precision audit: saved velocities reproduce exactly from rounded position differences; solved positions lie within one spacing of native-force equilibrium. Original native failure remains. Next: whole-fixture translation comparison with unchanged gate. Evidence: '+name+'.txt\n')
p=Path('/home/omen/.codex/.chatgpt-projects/g-p-6ad3464570508191a7832df1cb22a988/work/build_progress_view.py');s=p.read_text().replace('Audit bent-chain particle precision','Compare contact near the numerical origin').replace('Repeated bent-chain contact stopped on the particle impulse limit at interval 5. Next: audit numerical precision before continuing.','Saved particle velocities reproduce exactly from rounded positions. Next: translate the whole fixture near the contact origin and repeat with the same limits.');p.write_text(s)
print('Offline audit saved; all consistency assertions passed; original native result remains failed.')
