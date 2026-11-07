from pathlib import Path
import sys,json,numpy as np,cProfile,pstats
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'));src=w/'robot_cut11';z=np.load(src/'checkpoints/step_001000.npz');pose=np.r_[z['blade_translation']+[-.0225,0,.0295],Rotation.from_matrix(z['blade_rotation']).as_quat()];com=np.array(json.loads((src/'coupling_scope.json').read_text())['tool_com_local']);plan=json.loads((w/'clear_entry_robot_plan_v8.json').read_text());F=np.array(plan['target_rotation']);placement=np.array(plan['target_translation']);row=json.loads((src/'robot_intervals/step_001001.json').read_text());actual=np.array(row['after']['tool_pose']);goal=np.r_[F.T@(actual[:3]-placement),Rotation.from_matrix(F.T@Rotation.from_quat(actual[3:]).as_matrix()).as_quat()]
from tomato_master_slice_engine import subcycled_engine
g=subcycled_engine(pose,com,checkpoint=src/'checkpoints/step_001000.npz',padding_m=.001);next(g)
p=cProfile.Profile();p.enable();state=g.send(dict(pose=goal,dt=1/2400));p.disable();p.dump_stats(str(w/'master_step_profile.pstats'))
with (w/'master_step_profile.txt').open('w') as f:pstats.Stats(p,stream=f).sort_stats('cumtime').print_stats(40)
print((w/'master_step_profile.txt').read_text())
