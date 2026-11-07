from pathlib import Path
import sys,json,time,gc,numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
from tomato_master_remap_slice_engine_exploratory_v2 import subcycled_engine
from tomato_native_full_model import registry
fixed=np.array(registry()['design']['fixture']['node_ids']);report={'scope':'Local held-out loaded windows only; timestep 1/1200 vs original 1/2400, not full-cut qualification','cases':[],'passed':False};out=w/'exploratory_comparison_v2';out.mkdir(exist_ok=True)
for run,step,direction in [('robot_cut14',5400,1),('robot_cut13',5375,-1)]:
 cp=w/run/'checkpoints'/f'step_{step:06d}.npz';z=np.load(cp);scope=json.loads((w/run/'coupling_scope.json').read_text());pose=np.r_[z['blade_translation']+[-.0225,0,.0295],Rotation.from_matrix(z['blade_rotation']).as_quat()];g=subcycled_engine(pose,np.array(scope['tool_com_local']),checkpoint=cp,padding_m=.001);next(g);start=time.monotonic();rows=[];previous=z['history'].copy()
 for i in [2,4,6,8]:
  goal=pose.copy();goal[2]+=direction*.02/2400*i;s=g.send({'pose':goal,'dt':1/1200});b=np.load(w/'exploratory_comparison_v1'/f'{run}_baseline_{i:02d}.npz');dx=float(np.linalg.norm(s['x']-b['x'],axis=1).max());df=float(np.linalg.norm(s['wrench'][:3]-b['wrench'][:3]))/max(float(np.linalg.norm(b['wrench'][:3])),1e-5);sep=bool(np.array_equal(s['history'][:,1]>=1,b['history'][:,1]>=1));fixture=bool(np.array_equal(s['x'][fixed],z['x'][fixed]+[-.0225,0,.0295]));eligible=bool(np.array_equal(s['eligible'],b['eligible']));monotone=bool(np.all(s['history']>=previous-1e-14));passed=bool(dx<=1e-4 and df<=.05 and sep and fixture and eligible and monotone);rows.append(dict(step=i,position_difference_m=dx,force_difference_relative=df,separation_identical=sep,fixture_exact=fixture,eligibility_identical=eligible,history_monotone=monotone,passed=passed));previous=s['history'].copy();np.savez(out/f'{run}_{i:02d}.npz',**{k:s[k] for k in ['x','v','history','wrench','eligible']});print(run,rows[-1],flush=True)
 report['cases'].append(dict(checkpoint=str(cp),wall_s=time.monotonic()-start,comparisons=rows,passed=all(x['passed'] for x in rows)));g.close();del g;gc.collect();(w/'exploratory_comparison_v2.json').write_text(json.dumps(report,indent=2))
report['passed']=all(c['passed'] for c in report['cases']);(w/'exploratory_comparison_v2.json').write_text(json.dumps(report,indent=2));print('PASSED',report['passed'],flush=True)
