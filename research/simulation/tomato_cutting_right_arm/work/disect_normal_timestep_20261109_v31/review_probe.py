from pathlib import Path
import json,numpy as np
W=Path(__file__).resolve().parent;V=W.parent/'disect_normal_contact_20261109_v30'
a=json.loads((W/'moving_probe_result.json').read_text())['runs'][0]
b=json.loads((V/'moving_probe_result.json').read_text())['runs'][0]
assert a['dt_s']==2*b['dt_s']
aa={round(r['sim_s'],12):r for r in a['rows']};bb={round(r['sim_s'],12):r for r in b['rows']};times=sorted(set(aa)&set(bb))
force_error=max(abs(aa[t]['force_N']-bb[t]['force_N'])/max(bb[t]['force_N'],1e-6) for t in times)
q=np.load(W/'moving_probe_coarse_final.npz');ref=np.load(V/'moving_probe_coarse_final.npz')
position=float(np.max(np.linalg.norm(q['x']-ref['x'],axis=1)))
velocity=float(np.max(np.linalg.norm(q['v']-ref['v'],axis=1)))
reaction=float(np.linalg.norm(q['force'].sum(0)-ref['force'].sum(0))/max(np.linalg.norm(ref['force'].sum(0)),1e-6))
# Total wrench difference around a fixed world origin; also check net reaction.
# Fixed lever arm changes do not hide torque error. The original CAD COM is
# recovered independently from its source orientation and prescribed end pose.
R=W.parents[1];src=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz')
A=np.array([[1,0,0],[0,0,-1],[0,1,0]],float);rotation=A.T@src['rotation']
plan=json.loads((V/'correction_plan.json').read_text());T=np.array(plan['selected']['translation_m'])+[0,-42e-6,0]
com=src['com_local']@rotation.T+T
moments=[np.cross(z['x']-com,z['force']).sum(0) for z in [q,ref]]
moment=float(np.linalg.norm(moments[0]-moments[1])/max(np.linalg.norm(moments[1]),1e-8))
physical=all(r['stop']=='completed' and all(row['passed'] and row['damage_max']==0 for row in r['rows']) for r in [a,b])
passed=physical and position<=1e-4 and velocity<=.005 and force_error<=.05 and reaction<=.05 and moment<=.05
out={'scope':'One 6.25/3.125 us fresh contact component comparison; loaded prefix and actual damage still unqualified','coarse_dt_s':a['dt_s'],'fine_dt_s':b['dt_s'],'shared_samples':len(times),'maximum_shared_force_norm_relative':force_error,'final_position_m':position,'final_velocity_m_s':velocity,'final_reaction_relative':reaction,'final_moment_relative':moment,'physical_checks_passed':physical,'passed':passed,'gate_b_passed':False}
(W/'fresh_probe_review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if passed:
 (W/'candidate_controls_gate.json').write_text(json.dumps({'passed':True,'scope':'Shared v30 physical operator controls and one coarser fresh nonfracturing probe only; candidate not adopted before loaded-prefix comparison','physical_operator_controls_source':str(V/'controls_result.json'),'gate_b_passed':False},indent=2)+'\n')
assert passed
