"""Bounded material-only comparison. Never authorizes coupled adoption."""
from pathlib import Path
import sys,json,time,gc,hashlib,numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
from tomato_master_remap_slice_engine import subcycled_engine as baseline
from tomato_master_remap_slice_engine_exploratory_v2 import subcycled_engine as half
from tomato_master_remap_slice_engine_exploratory_v3 import subcycled_engine as quarter
from tomato_native_full_model import registry
cp=w/'robot_cut17/checkpoints/step_006400.npz';z=np.load(cp);scope=json.loads((cp.parent.parent/'coupling_scope.json').read_text());route=json.loads((w/'bodyward_withdrawal_plan_v1.json').read_text());direction=np.array(route['target_rotation']).T@np.array(route['direction_world']);pose=np.r_[z['blade_translation']+[-.0225,0,.0295],Rotation.from_matrix(z['blade_rotation']).as_quat()];fixed=np.array(registry()['design']['fixture']['node_ids'])
out=w/'bodyward_timestep_comparison';out.mkdir(exist_ok=False);report={'scope':__doc__,'checkpoint':str(cp),'sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'coupled_adoption_authorized':False,'limits':{'position_m':1e-4,'force_relative':.05},'cases':[]};references={}
for label,engine,stride in [('original',baseline,1),('dt1200',half,2),('dt600',quarter,4)]:
 g=engine(pose,scope['tool_com_local'],checkpoint=cp,padding_m=.001);next(g);start=time.monotonic();rows=[];previous=z['history'].copy()
 for i in range(stride,9,stride):
  goal=pose.copy();goal[:3]+=direction*.02*i/2400;s=g.send(dict(pose=goal,dt=stride/2400));values={k:s[k].copy() for k in ['x','v','history','wrench','eligible']};np.savez(out/f'{label}_{i:02d}.npz',**values)
  if stride==1:references[i]=values
  else:
   b=references[i];dx=float(np.linalg.norm(s['x']-b['x'],axis=1).max());df=float(np.linalg.norm(s['wrench'][:3]-b['wrench'][:3]))/max(float(np.linalg.norm(b['wrench'][:3])),1e-5);sep=bool(np.array_equal(s['history'][:,1]>=1,b['history'][:,1]>=1));fixture=bool(np.array_equal(s['x'][fixed],z['x'][fixed]+[-.0225,0,.0295]));eligible=bool(np.array_equal(s['eligible'],b['eligible']));monotone=bool(np.all(s['history']>=previous-1e-14));rows.append(dict(step=i,position_difference_m=dx,force_difference_relative=df,separation_identical=sep,fixture_exact=fixture,eligibility_identical=eligible,history_monotone=monotone,passed=bool(dx<=1e-4 and df<=.05 and sep and fixture and eligible and monotone)))
  previous=s['history'].copy();print(label,i,round(time.monotonic()-start,2),rows[-1] if rows else '',flush=True)
 report['cases'].append(dict(candidate=label,wall_s=time.monotonic()-start,comparisons=rows,passed=bool(rows) and all(x['passed'] for x in rows)));(out/'report.json').write_text(json.dumps(report,indent=2));g.close();del g;gc.collect()
