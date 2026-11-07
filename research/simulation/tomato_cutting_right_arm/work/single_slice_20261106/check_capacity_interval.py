from pathlib import Path
import sys,json,time,traceback
import numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'));out=w/'capacity_check02';out.mkdir(exist_ok=True);source=w/'robot_cut06';checkpoint=source/'material_before_failed_microstep.npz';z=np.load(checkpoint);meta=json.loads(checkpoint.with_suffix('.json').read_text());com=np.array(json.loads((source/'coupling_scope.json').read_text())['tool_com_local']);start=time.monotonic()
try:
 from tomato_capacity_slice_engine import subcycled_engine
 pose=np.r_[z['blade_translation']+[-.0225,0,.0295],Rotation.from_matrix(z['blade_rotation']).as_quat()];g=subcycled_engine(pose,com,checkpoint=checkpoint,padding_m=.001,diagnostic_directory=out);before=next(g)
 state=g.send(dict(pose=meta['goal_pose'],dt=meta['outer_interval']-meta['completed_interval']));state['checkpoint_writer'](out/'accepted_checkpoint.npz')
 result=dict(passed=True,scope='Exact previously rejected material interval only; not coupled robot success',elapsed=state['elapsed'],maximum_damage=float(state['history'][:,1].max()),history_monotone=bool(np.all(state['history']>=before['history'])),wall_s=time.monotonic()-start)
except BaseException as e:result=dict(passed=False,error=repr(e),traceback=traceback.format_exc(),wall_s=time.monotonic()-start)
(out/'result.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
