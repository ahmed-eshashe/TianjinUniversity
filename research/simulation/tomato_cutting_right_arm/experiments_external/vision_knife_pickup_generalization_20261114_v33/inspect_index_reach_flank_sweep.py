from pathlib import Path
import json,sys,numpy as np
from scipy.spatial.transform import Rotation
from scipy.spatial import ConvexHull
from pxr import Usd,UsdGeom
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path[:0]=[str(R/'scripts'),str(R/'rl')]
from plan_contact_seating import HandGeometry
s=Usd.Stage.Open(str(W/'medium_original_handle_v01.usda'));m=HandGeometry(s);c=json.loads((W/'scene_config.json').read_text());handle=np.array(UsdGeom.Mesh(s.GetPrimAtPath(c['knife_path']+'/CollisionHandle')).GetPointsAttr().Get());hh=ConvexHull(handle);handle=handle[hh.vertices];blade=np.array(UsdGeom.Mesh(s.GetPrimAtPath(c['knife_path']+'/CollisionBlade')).GetPointsAttr().Get());bh=ConvexHull(blade);blade=blade[bh.vertices]
g=json.loads((W/'reports/pinch_geometry02.json').read_text());rows=[]
for cross in [0.,.001,.002,.003,.004]:
 case='datasets/v22_cross_probe/train_medium_face180_00'
 p=W/case;traj=json.loads((p/'trajectory.json').read_text());initial=[x for x in traj if x['phase']=='settle'][-1];pose=initial['knife_pose'];K=np.eye(4);K[:3,:3]=Rotation.from_quat(pose[3:]).as_matrix();K[:3,3]=pose[:3];H=np.array(json.loads((p/'teacher_target_override.json').read_text())['hand_target_world']);H[:3,3]+=K[:3,0]*.011+K[:3,1]*(cross-.0015);A=np.linalg.inv(K)@H
 values=[]
 for qi in np.linspace(.73,1.1,75):
  q=np.array(g['hand_joint_rad']);q[1]-=.07;q[2:]-=.1;q[2]=qi;T=m.transforms(q)['right_rh_index_distal'];B=A@T;v,eq=m.meshes['right_rh_index_distal'];vk=v@B[:3,:3].T+B[:3,3];vw=vk@K[:3,:3].T+K[:3,3]
  def gap(other,oh):
   ov=(other-B[:3,3])@B[:3,:3];return max(float((ov@eq[:,:3].T+eq[:,3]).min(0).max()),float((vk@oh.equations[:,:3].T+oh.equations[:,3]).min(0).max()))
  values.append(dict(q=qi,handle_gap_m=gap(handle,hh),blade_gap_m=gap(blade,bh),board_gap_m=float(vw[:,2].min())))
 good=[x for x in values if x['handle_gap_m']<.0007 and x['blade_gap_m']>.002 and x['board_gap_m']>.0005]
 rows.append(dict(cross=cross,case=case,values=values,first_contact=good[0] if good else None));print(cross,min(values,key=lambda x:x['handle_gap_m']),flush=True)
(W/'reports/index_static_reach_flank_sweep.json').write_text(json.dumps(rows,indent=2))
