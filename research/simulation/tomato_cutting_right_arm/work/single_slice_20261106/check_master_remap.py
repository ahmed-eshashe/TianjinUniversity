from pathlib import Path
import sys,json,time,numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'));out=w/'master_remap_probe01';out.mkdir(exist_ok=True);src=w/'robot_cut11';checkpoint=src/'material_before_failed_microstep.npz';z=np.load(checkpoint);m=json.loads(checkpoint.with_suffix('.json').read_text());com=np.array(json.loads((src/'coupling_scope.json').read_text())['tool_com_local']);pose=np.r_[z['blade_translation']+[-.0225,0,.0295],Rotation.from_matrix(z['blade_rotation']).as_quat()];start=time.monotonic()
from tomato_master_remap_slice_engine import subcycled_engine
from tomato_native_full_model import registry
try:
 g=subcycled_engine(pose,com,checkpoint=checkpoint,padding_m=.001,diagnostic_directory=out);state=next(g);state=g.send(dict(pose=m['trial_pose'],dt=m['micro_interval']));state['checkpoint_writer'](out/'accepted.npz');error=None
except Exception as e:error=repr(e)
result=dict(error=error,wall_s=time.monotonic()-start);(out/'result.json').write_text(json.dumps(result,indent=2));print(result)
