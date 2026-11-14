"""Kinematic feasibility for gravity-assisted handle pickup; tool motion is a target, not a drive."""
from pathlib import Path
import json,sys,numpy as np
from pxr import Usd,UsdGeom
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path[:0]=[str(R/'scripts'),str(R/'rl')];from reach_kinematics import ArmKinematics,PALM_OFFSET
from plan_contact_seating import HandGeometry
c=json.load(open(W/'scene_config.json'));g=json.load(open(W/'reports/pinch_geometry02.json'));kin=ArmKinematics(Usd.Stage.Open(c['scene']));s=kin.kin if False else Usd.Stage.Open(c['scene']);geom=HandGeometry(s);v=np.array(UsdGeom.Mesh(s.GetPrimAtPath(c['knife_path'])).GetPointsAttr().Get());p=np.array(json.load(open(W/'runs/camera01/result.json'))['knife_pose']);kr=Rotation.from_quat(p[3:]).as_matrix();rel=np.array(g['hand_from_knife']);anchor=np.array([-.145,.005,.005]);anchorworld=p[:3]+kr@anchor;lo0=(v@kr.T)[:,2].min();q=g['q'];tr=geom.transforms(g['hand_joint_rad']);handv=np.concatenate([vv@tr[n][:3,:3].T+tr[n][:3,3] for n,(vv,eq) in geom.meshes.items()]);rows=[]
for u in np.linspace(0,1,81):
 theta=-75*u;rk=kr@Rotation.from_euler('y',theta,degrees=True).as_matrix();trans=anchorworld-rk@anchor;trans[2]=p[2]+lo0-(v@rk.T)[:,2].min();T=np.eye(4);T[:3,:3]=rk@rel[:3,:3];T[:3,3]=trans+rk@rel[:3,3];q,pe,re=kin.solve(T[:3,3]+T[:3,:3]@PALM_OFFSET,T[:3,:3],q);mingap=float((handv@T[:3,:3].T+T[:3,3])[:,2].min());rows.append(dict(fraction=float(u),angle_deg=float(theta),hand_world=T.tolist(),q=q.tolist(),position_error_m=pe,angle_error_rad=re,min_hand_world_z_m=mingap))
print('maxerror',max(x['position_error_m'] for x in rows),max(x['angle_error_rad'] for x in rows),'minimumhandz',min(x['min_hand_world_z_m'] for x in rows));print('firstbad',next((x['fraction'] for x in rows if x['position_error_m']>.0003 or x['angle_error_rad']>.003),None));(W/'reports/supported_tilt_route.json').write_text(json.dumps(dict(scope='Unvalidated gravity-assisted pickup trajectory; board support allowed only before the final unsupported hold.',waypoints=rows),indent=2))
