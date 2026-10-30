"""Check a contact-preserving wrist roll above the board before physics."""
import json,numpy as np
from pathlib import Path
from scipy.spatial.transform import Rotation
from pxr import Usd
from reach_kinematics import ArmKinematics
ROOT=Path(__file__).resolve().parents[1];s=json.load(open(ROOT/'work/grasp_stance_cooking_120.json'));k=ArmKinematics(Usd.Stage.Open(str(ROOT/'work/kitchen_reach.usda')))
k.root[:2,3]+=s['root_offset_xy'];k.root[:3,:3]=Rotation.from_euler('z',s['root_yaw_deg'],degrees=True).as_matrix();r=np.array(s['orientation']);h=np.array([-2.26269,-1.76180,.87195]);q=np.array(s['ready_rad'])
line=next(x for x in (ROOT/'logs/wrap_trial16.log').read_text().splitlines() if x.startswith('SETTLED_SCENE '));kr=Rotation.from_euler('z',120,degrees=True).as_matrix()@np.array(json.loads(line.removeprefix('SETTLED_SCENE '))['knife_rotation_world'])
axis=kr[:,0];offset=np.array([.035,-.015,.020]);results=[]
for p in [h-r@offset,h+[0,0,.05]-r@offset]:q,e,a=k.solve(p,r,q)
for roll in np.arange(0,91,5):
 rr=Rotation.from_rotvec(axis*np.deg2rad(roll)).as_matrix()@r;p=h+[0,0,.05]-rr@offset;q,e,a=k.solve(p,rr,q)
 row={'roll_deg':int(roll),'position_error_m':e,'rotation_error_rad':a,'q':q.tolist()};results.append(row);print('ROLL',roll,'e',round(e,5),'a',round(a,4),flush=True)
(ROOT/'work/cooking_roll_screen.json').write_text(json.dumps(results,indent=2))
