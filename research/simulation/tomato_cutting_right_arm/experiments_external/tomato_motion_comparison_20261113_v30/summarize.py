from pathlib import Path
import hashlib,json
import numpy as np
W=Path(__file__).resolve().parent
rows=[];comparisons=[]
for p in sorted((W/'runs').glob('*/result.json')):
    result=json.loads(p.read_text());result['run']=p.parent.name;rows.append(result)
for coarse in [r for r in rows if r['dt_s']==.0002]:
    fine=next((r for r in rows if r['case']==coarse['case'] and r['dt_s']==.0001),None)
    if fine is None:continue
    a=np.load(W/'runs'/coarse['run']/'state.npz');b=np.load(W/'runs'/fine['run']/'state.npz')
    common=np.intersect1d(a['snapshot_time'],b['snapshot_time'])
    errors=[]
    for t in common:
        pa=a['snapshots'][np.flatnonzero(a['snapshot_time']==t)[0]]
        pb=b['snapshots'][np.flatnonzero(b['snapshot_time']==t)[0]]
        errors.append(float(np.linalg.norm(pa-pb,axis=1).max()))
    comparisons.append({'case':coarse['case'],'same_success':coarse['success']==fine['success'],'same_broken_bonds':bool(np.array_equal(a['alive'],b['alive'])),'peak_load_relative_difference':abs(coarse['peak_sum_load_N']-fine['peak_sum_load_N'])/fine['peak_sum_load_N'],'max_position_difference_at_common_snapshot_times_mm':max(errors)*1000 if errors else None,'number_common_snapshot_times':len(common)})
contract=json.loads((W/'contract.json').read_text())
preserved=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in contract['source_hashes'].items())
report={'runs':rows,'timestep_comparisons':comparisons,'original_physics_sources_unchanged':preserved,'scope':'Motion comparison in the authorized approximate model. No material, blade, fracture, support or stop changes. No physical-tomato calibration. GPU viewer may run concurrently, so wall timings are not clean throughput measurements.'}
(W/'reports/final.json').write_text(json.dumps(report,indent=2))
lines=['TOMATO MOTION COMPARISON — 13 NOVEMBER 2026','','Changes: controller only. Original v28 model/solver/environment source hashes preserved: '+str(preserved),'All original force, penetration, board and numerical stops retained.','Time below is simulated episode time, including approach and withdrawal.','Load is the sum of local contact and fracture magnitudes; not a calibrated wrist measurement.','','Run | timestep ms | success | episode s | load N | penetration mm | pre-separation RMS deformation mm']
for r in rows:
    lines.append(f"{r['run']} | {r['dt_s']*1000:.2f} | {r['success']} | {r['duration_sim_s']:.2f} | {r['peak_sum_load_N']:.3f} | {r['peak_penetration_mm']:.4f} | {r['max_preseparation_deformation_rms_mm']:.3f}")
lines+=['','Unsuccessful runs are partial episodes; their duration and deformation are not directly comparable to completed cuts.','RMS deformation removes center-of-mass translation relative to the state after initial settling. It includes cut opening before final separation, not only bulk compression.','All complete cases must retain the full fracture work budget and show an exact reset.','','Timestep sensitivity:']
for r in comparisons:lines.append(json.dumps(r))
lines+=['','Interpretation: slower motion is prescribed by the baseline controller. Speed can improve without changing material resistance, but faster feeding may increase force. Constant downward feeding during sliding reversals produced force spikes in the smooth trial.','The separate synchronized smooth trial therefore pauses downward motion smoothly at each reversal, while retaining the same average feed.','These screens do not establish real-tomato realism or unrestricted learned-policy safety. Larger timestep-dependent force changes must not be called a precise force prediction.']
(W/'REPORT.txt').write_text('\n'.join(lines)+'\n')
print(json.dumps({'rows':len(rows),'physics_preserved':preserved,'timestep_comparisons':comparisons},indent=2))
