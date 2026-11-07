from pathlib import Path
import sys,json
import numpy as np
import warp as wp
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
from tomato_local_plane_partition import candidate_faces
from tomato_fast_exact_cad import fast_query
wp.init();wp.set_device('cuda:0');source=w/'robot_cut08';z=np.load(source/'material_before_failed_microstep.npz');meta=json.loads((source/'material_before_failed_microstep.json').read_text());blade=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());ids=np.unique(z['packet_indices'],axis=0);origin=np.array([-.0225,0,.0295]);pose=np.array(meta['trial_pose']);rng=np.random.default_rng(2984);bary=np.vstack([rng.dirichlet([1,1,1],size=64),np.eye(3),[[.5,.5,0],[.5,0,.5],[0,.5,.5],[1/3]*3]])
rows=[]
for name,x,R,t in [('current',z['x'],z['blade_rotation'],z['blade_translation']),('lookahead',z['x']+z['v']*meta['micro_interval'],Rotation.from_quat(pose[3:]).as_matrix(),pose[:3]-origin)]:
 local=(x[ids]-t)@R;mask,details=candidate_faces(blade,local);points=np.einsum('qi,tij->tqj',bary,local).reshape(-1,3);n=len(points);outputs=[wp.zeros(n,dtype=d)for d in [wp.float64,wp.vec3d,wp.vec3d,int,wp.float64]];wp.launch(fast_query,dim=n,inputs=[wp.array(blade['vertices'],dtype=wp.vec3d),wp.array(blade['triangles'],dtype=wp.vec3i),wp.array(points,dtype=wp.vec3d)],outputs=outputs,block_dim=64);chosen=outputs[3].numpy().reshape(len(ids),-1);missing=~np.take_along_axis(mask,chosen,axis=1)
 rows.append(dict(geometry=name,points=n,material_triangles=len(ids),omitted_actual_nearest_faces=int(missing.sum()),minimum_candidates=int(mask.sum(1).min()),maximum_candidates=int(mask.sum(1).max())))
result=dict(passed=all(q['omitted_actual_nearest_faces']==0 for q in rows),proof='Distance-to-face is 1-Lipschitz; center distance beyond nearest center distance plus twice enclosing radius cannot be nearest inside triangle; 1e-10m roundoff expansion',rows=rows)
(w/'local_feature_bound_check.json').write_text(json.dumps(result,indent=2));print(result)
