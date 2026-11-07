"""Exact configured timestep and identical prospective poses; includes baseline repeat.
The earlier timestamp-difference replay is retained but can subdivide at rounded
clock differences. This control uses the actual configured 1/2400 s interval.
"""
from pathlib import Path
import sys,json,time,gc,numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
from tomato_master_remap_slice_engine import subcycled_engine as baseline
from tomato_master_remap_slice_engine_v2 import subcycled_engine as optimized
checkpoint=w/'robot_cut14/checkpoints/step_005400.npz';z=np.load(checkpoint);scope=json.loads((checkpoint.parent.parent/'coupling_scope.json').read_text());pose=np.r_[z['blade_translation']+[-.0225,0,.0295],Rotation.from_matrix(z['blade_rotation']).as_quat()];goals=[pose+np.array([0,0,.02/2400*j,0,0,0,0])for j in [1,2]];reference=[];reports=[]
for label,engine in [('baseline',baseline),('baseline_repeat',baseline),('optimized',optimized)]:
 g=engine(pose,np.array(scope['tool_com_local']),checkpoint=checkpoint,padding_m=.001);next(g);start=time.monotonic();comparisons=[]
 for i,goal in enumerate(goals):
  state=g.send(dict(pose=goal,dt=1/2400));values={key:state[key].copy() for key in ['x','v','history','wrench','eligible']}
  if label=='baseline':reference.append(values)
  else:
   d={key:float(np.max(abs(values[key]-reference[i][key])))for key in ['x','v','history','wrench']};d.update(interval=i+1,eligibility_identical=bool(np.array_equal(values['eligible'],reference[i]['eligible'])),interval_substeps=state['interval_substeps']);comparisons.append(d)
  print(label,i+1,time.monotonic()-start,flush=True)
 reports.append(dict(engine=label,wall_s=time.monotonic()-start,comparisons=comparisons));g.close();del g;gc.collect()
(w/'geometry_reproducibility_check.json').write_text(json.dumps(dict(scope=__doc__,dt_s=1/2400,source_checkpoint=str(checkpoint),reports=reports),indent=2));print(json.dumps(reports,indent=2))
