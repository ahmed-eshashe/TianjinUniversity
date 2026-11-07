"""Prospective local comparison; no full-cut accuracy qualification."""
from pathlib import Path
import sys,json,time,gc,numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
from tomato_master_remap_slice_engine import subcycled_engine as baseline
from tomato_master_remap_slice_engine_exploratory_v1 import subcycled_engine as candidate
report={'scope':__doc__,'limits':{'position_m':1e-4,'force_relative':.05,'force_floor_N':1e-5},'candidate':'compiled exact geometry; velocity defect budget 1e-4; dt unchanged 1/2400','cases':[],'passed':False}
out=w/'exploratory_comparison_v1';out.mkdir(exist_ok=True)
for run,step,direction in [('robot_cut14',5400,1),('robot_cut13',5375,-1)]:
 cp=w/run/'checkpoints'/f'step_{step:06d}.npz';z=np.load(cp);scope=json.loads((w/run/'coupling_scope.json').read_text());pose=np.r_[z['blade_translation']+[-.0225,0,.0295],Rotation.from_matrix(z['blade_rotation']).as_quat()];reference=[];case={'checkpoint':str(cp),'direction':direction,'steps':8,'dt':1/2400,'comparisons':[]};times={}
 for label,engine in [('baseline',baseline),('candidate',candidate)]:
  g=engine(pose,np.array(scope['tool_com_local']),checkpoint=cp,padding_m=.001);initial=next(g);fixed=np.flatnonzero(np.linalg.norm(initial['v'],axis=1)==0);start=time.monotonic();previous=z['history'].copy()
  for i in range(8):
   goal=pose.copy();goal[2]+=direction*.02/2400*(i+1);s=g.send({'pose':goal,'dt':1/2400});vals={k:s[k].copy() for k in ['x','v','history','wrench','eligible']};vals['separation']=s['separation'];np.savez(out/f'{run}_{label}_{i+1:02d}.npz',**{k:v for k,v in vals.items() if k!='separation'})
   if label=='baseline':reference.append(vals)
   else:
    b=reference[i];dx=float(np.linalg.norm(vals['x']-b['x'],axis=1).max());df=float(np.linalg.norm(vals['wrench'][:3]-b['wrench'][:3]));relative=df/max(float(np.linalg.norm(b['wrench'][:3])),1e-5);sep=all(vals['separation'][k]==b['separation'][k] for k in ['topological_separation','component_count','failed_patches']);same_eligible=bool(np.array_equal(vals['eligible'],b['eligible']));monotone=bool(np.all(vals['history']>=previous-1e-14));case['comparisons'].append(dict(step=i+1,position_difference_m=dx,force_difference_relative=relative,separation_identical=sep,eligibility_identical=same_eligible,history_monotone=monotone,passed=bool(dx<=1e-4 and relative<=.05 and sep and same_eligible and monotone)))
   previous=vals['history'];print(run,label,i+1,'seconds',round(time.monotonic()-start,2),flush=True)
  times[label]=time.monotonic()-start;g.close();del g;gc.collect()
 case['wall_s']=times;case['passed']=all(c['passed'] for c in case['comparisons']);report['cases'].append(case);(w/'exploratory_comparison_v1.json').write_text(json.dumps(report,indent=2))
report['passed']=all(c['passed'] for c in report['cases']);(w/'exploratory_comparison_v1.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
