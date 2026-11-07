from pathlib import Path
import sys,json,time,numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'));out=w/'failure_probe01';out.mkdir(exist_ok=True);src=w/'robot_cut10';checkpoint=src/'material_before_failed_microstep.npz';z=np.load(checkpoint);m=json.loads(checkpoint.with_suffix('.json').read_text());com=np.array(json.loads((src/'coupling_scope.json').read_text())['tool_com_local']);pose=np.r_[z['blade_translation']+[-.0225,0,.0295],Rotation.from_matrix(z['blade_rotation']).as_quat()];start=time.monotonic()
from tomato_failure_probe_engine import subcycled_engine
from tomato_native_full_model import registry
try:
 g=subcycled_engine(pose,com,checkpoint=checkpoint,padding_m=.001,diagnostic_directory=out);state=next(g);state=g.send(dict(pose=m['trial_pose'],dt=m['micro_interval']));error=None
except Exception as e:error=repr(e)
data=registry();f=np.load(w/'element_frame_definition.npz');rows=[]
for label,path in [('before',checkpoint),('failed_iterate',out/'nonlinear_iterate.npz')]:
 if not path.exists():continue
 a=np.load(path);x=a['x'];mid=x[f['pairs']].mean(2);uv=np.einsum('pji,pjk->pik',f['coefficients'],mid);areas=np.linalg.norm(np.cross(uv[:,0],uv[:,1]),axis=1);J=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes']);i=int(areas.argmin());rows.append(dict(label=label,min_J=float(J.min()),min_frame_area_ratio=float(areas.min()),frame_patch=i,frame_history=a['history'][i].tolist(),max_coordinate_m=float(abs(x).max()),worst_rhs_node=int(np.linalg.norm(a['rhs'],axis=1).argmax())if 'rhs'in a else None))
result=dict(error=error,states=rows,wall_s=time.monotonic()-start);(out/'result.json').write_text(json.dumps(result,indent=2));print(result)
