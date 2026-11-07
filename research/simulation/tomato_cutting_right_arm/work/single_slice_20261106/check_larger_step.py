from pathlib import Path
import sys,json,time,numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'));src=w/'robot_cut12';out=w/'larger_step01';out.mkdir(exist_ok=True)
criteria=dict(position_m=5e-6,velocity_m_s=.001,damage=1e-4,opening_m=1e-6,force_relative=.01,force_absolute_N=1e-5,scope='Exploratory loaded-window screen, not full trajectory convergence')
(out/'criteria.json').write_text(json.dumps(criteria,indent=2))
p=r/'rl/tomato_master_remap_slice_engine.py';s=p.read_text().replace('1/2400','1/800');target=r/'rl/tomato_larger_step_diagnostic_engine.py';target.write_text(s)
from tomato_larger_step_diagnostic_engine import subcycled_engine
checkpoint=src/'checkpoints/step_001600.npz';z=dict(np.load(checkpoint));z['adaptive_dt_cap']=np.array(1/800);np.savez(out/'start.npz',**z);pose=np.r_[z['blade_translation']+[-.0225,0,.0295],Rotation.from_matrix(z['blade_rotation']).as_quat()];com=np.array(json.loads((src/'coupling_scope.json').read_text())['tool_com_local']);plan=json.loads((w/'clear_entry_robot_plan_v8.json').read_text());F=np.array(plan['target_rotation']);placement=np.array(plan['target_translation']);start=time.monotonic()
try:
 g=subcycled_engine(pose,com,checkpoint=out/'start.npz',padding_m=.001,diagnostic_directory=out);next(g)
 for k in range(1603,1676,3):
  row=json.loads((src/'robot_intervals'/f'step_{k:06d}.json').read_text());actual=np.array(row['after']['tool_pose']);goal=np.r_[F.T@(actual[:3]-placement),Rotation.from_matrix(F.T@Rotation.from_quat(actual[3:]).as_matrix()).as_quat()];state=g.send(dict(pose=goal,dt=1/800))
  with (out/'progress.jsonl').open('a') as f:f.write(json.dumps(dict(step=k,wall_s=time.monotonic()-start))+'\n')
 ref=np.load(src/'checkpoints/step_001675.npz');meta=json.loads((src/'checkpoints/step_001675.json').read_text());dx=state['x']-(ref['x']+[-.0225,0,.0295]);dh=state['history']-ref['history'];reaction=np.array(meta['reaction']);result=dict(position_m=float(np.linalg.norm(dx,axis=1).max()),velocity_m_s=float(np.linalg.norm(state['v']-ref['v'],axis=1).max()),damage=float(abs(dh[:,1]).max()),opening_m=float(abs(dh[:,0]).max()),force_error_N=float(np.linalg.norm(state['wrench'][:3]-reaction[:3])),reference_force_N=float(np.linalg.norm(reaction[:3])),wall_s=time.monotonic()-start)
 result['passed']=all(result[k]<=criteria[k]for k in ['position_m','velocity_m_s','damage','opening_m']) and result['force_error_N']<=criteria['force_absolute_N']+criteria['force_relative']*result['reference_force_N']
except Exception as e:result=dict(passed=False,error=repr(e),wall_s=time.monotonic()-start)
(out/'result.json').write_text(json.dumps(result,indent=2));print(result)
