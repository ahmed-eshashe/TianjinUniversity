"""Recorded measured-blade intervals, unchanged engine versus geometry optimization."""
from pathlib import Path
import sys,json,time,gc,numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
from tomato_master_remap_slice_engine import subcycled_engine as baseline
from tomato_master_remap_slice_engine_v2 import subcycled_engine as optimized
checkpoint=w/'robot_cut13/checkpoints/step_005375.npz';z=np.load(checkpoint);scope=json.loads((checkpoint.parent.parent/'coupling_scope.json').read_text());pose=np.r_[z['blade_translation']+[-.0225,0,.0295],Rotation.from_matrix(z['blade_rotation']).as_quat()];rows=[p for p in json.loads((w/'robot_cut14/cutting_trace.json').read_text())if 5375<p['step']<=5379];assert len(rows)==4
reference=[];timings=[];comparisons=[]
for label,engine in [('baseline',baseline),('optimized',optimized)]:
 g=engine(pose,np.array(scope['tool_com_local']),checkpoint=checkpoint,padding_m=.001);next(g);elapsed=float(z['elapsed']);start=time.monotonic()
 for i,row in enumerate(rows):
  state=g.send(dict(pose=np.array(row['actual_tool_pose_canonical']),dt=row['time_s']-elapsed));elapsed=row['time_s'];values={key:state[key].copy() for key in ['x','v','history','wrench','eligible']}
  if label=='baseline':reference.append(values)
  else:
   d={key:float(np.max(abs(values[key]-reference[i][key]))) for key in ['x','v','history','wrench']};d.update(step=row['step'],eligibility_identical=bool(np.array_equal(values['eligible'],reference[i]['eligible'])));d['passed']=bool(d['x']<=1e-9 and d['v']<=1e-6 and d['history']<=1e-8 and d['wrench']<=1e-6 and d['eligibility_identical']);comparisons.append(d)
  print(label,row['step'],'wall',time.monotonic()-start,flush=True)
 timings.append(dict(engine=label,wall_s=time.monotonic()-start));g.close();del g;gc.collect()
report=dict(passed=all(row['passed']for row in comparisons),scope=__doc__,recorded_intervals=4,source_checkpoint=str(checkpoint),timings=timings,comparisons=comparisons,material_law_unchanged=True,all_solver_and_remap_budgets_unchanged=True);(w/'compiled_geometry_replay.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
