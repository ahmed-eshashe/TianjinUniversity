from pathlib import Path
import json,sys,numpy as np
from scipy.spatial.transform import Rotation
from scipy.spatial import ConvexHull
from pxr import Usd,UsdGeom
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path[:0]=[str(R/'scripts'),str(R/'rl')]
from plan_contact_seating import HandGeometry
c=json.loads((W/'scene_config.json').read_text());g=json.loads((W/'reports/pinch_geometry02.json').read_text());rows=[]
for case in ['datasets/v13_teacher_matrix/train_short_face0_00','datasets/v13_teacher01/opposite','datasets/v13_teacher_matrix/train_wide_face0_00','datasets/v13_teacher_matrix/train_wide_face180_00','datasets/v13_teacher01/medium','datasets/v22_cross_probe/train_medium_face180_00']:
 p=W/case;cfg=json.loads((p/'configuration.json').read_text());s=Usd.Stage.Open(cfg['args']['scene']);m=HandGeometry(s);handle=np.array(UsdGeom.Mesh(s.GetPrimAtPath(c['knife_path']+'/CollisionHandle')).GetPointsAttr().Get());hh=ConvexHull(handle);handle=handle[hh.vertices]
 traj=json.loads((p/'trajectory.json').read_text());pose=[x for x in traj if x['phase']=='settle'][-1]['knife_pose'];K=np.eye(4);K[:3,:3]=Rotation.from_quat(pose[3:]).as_matrix();K[:3,3]=pose[:3];H=np.array(json.loads((p/'teacher_target_override.json').read_text())['hand_target_world'])
 if 'v22_cross' in case:H[:3,3]+=K[:3,1]*.0015
 A=np.linalg.inv(K)@H;values=[]
 for qi in np.linspace(.73,.9347,83):
  q=np.array(g['hand_joint_rad']);q[1]-=.07;q[2:]-=.1;q[2]=qi;B=A@m.transforms(q)['right_rh_index_distal'];v,eq=m.meshes['right_rh_index_distal'];vk=v@B[:3,:3].T+B[:3,3];ov=(handle-B[:3,3])@B[:3,:3];gap=max(float((ov@eq[:,:3].T+eq[:,3]).min(0).max()),float((vk@hh.equations[:,:3].T+hh.equations[:,3]).min(0).max()));values.append(dict(q=qi,gap_m=gap))
 row=dict(case=case,minimum=min(values,key=lambda x:x['gap_m']));rows.append(row);print(row,flush=True)
(W/'reports/all_index_static_reach.json').write_text(json.dumps(rows,indent=2))
