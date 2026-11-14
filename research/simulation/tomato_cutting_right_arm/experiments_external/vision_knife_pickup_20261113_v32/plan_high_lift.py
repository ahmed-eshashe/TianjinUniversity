from pathlib import Path
import json,sys,numpy as np
from pxr import Usd
from scipy.spatial.transform import Rotation,Slerp
from scipy.optimize import least_squares
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path.insert(0,str(R/'scripts'));from reach_kinematics import ArmKinematics,PALM_OFFSET
c=json.load(open(W/'scene_config.json'));g=json.load(open(W/'reports/pinch_geometry02.json'));kin=ArmKinematics(Usd.Stage.Open(c['scene']));p=np.array(json.load(open(W/'runs/camera01/result.json'))['knife_pose']);K=np.eye(4);K[:3,:3]=Rotation.from_quat(p[3:]).as_matrix();K[:3,3]=p[:3];H=K@np.array(g['hand_from_knife']);desired=H[:3,3]+[0,0,.35];seed=np.array(json.load(open(W/'reports/high_lift_reach.json'))['final_q'])
def f(q):
 T=kin.transforms(q)[kin.hand_path];return np.r_[T[:3,3]-desired,.005*Rotation.from_matrix(H[:3,:3]@T[:3,:3].T).as_rotvec(),.00001*(q-seed)]
s=least_squares(f,seed,bounds=(kin.lower,kin.upper),max_nfev=500,ftol=1e-12,gtol=1e-12,xtol=1e-12);T=kin.transforms(s.x)[kin.hand_path];goal=T.copy();goal[:3,3]=desired;rot=Slerp([0,1],Rotation.from_matrix([H[:3,:3],goal[:3,:3]]));q=g['q'];rows=[]
for u in np.linspace(0,1,81):
 r=rot(u).as_matrix();pt=H[:3,3]*(1-u)+goal[:3,3]*u;q,pe,re=kin.solve(pt+r@PALM_OFFSET,r,q);rows.append([float(u),pe,re])
out=dict(start_hand_world=H.tolist(),end_hand_world=goal.tolist(),max_position_error_m=float(np.max(np.array(rows)[:,1])),max_orientation_error_rad=float(np.max(np.array(rows)[:,2])),wrist_adjustment_deg=float(np.rad2deg(Rotation.from_matrix(goal[:3,:3]@H[:3,:3].T).magnitude())),samples=rows)
(W/'reports/high_lift_route.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k not in ['samples','start_hand_world','end_hand_world']})
