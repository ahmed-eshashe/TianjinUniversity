"""Screen the planned pickup and wrist turn against the parked arm and torso."""
import argparse,json,numpy as np
from pathlib import Path
from scipy.spatial.transform import Rotation
from pxr import Usd
from reach_kinematics import ArmKinematics
from check_reach_clearance import check
ROOT=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--seed',default='work/grasp_stance_cooking_tucked.json');p.add_argument('--prethumb-pitch',type=float,default=33);p.add_argument('--prethumb-yaw',type=float,default=0);a=p.parse_args()
s=json.load(open(ROOT/a.seed));k=ArmKinematics(Usd.Stage.Open(str(ROOT/'work/kitchen_reach.usda')));k.root[:2,3]+=s['root_offset_xy'];k.root[:3,:3]=Rotation.from_euler('z',s['root_yaw_deg'],degrees=True).as_matrix();q=np.array(s['ready_rad']);poses=s['planned_poses'];previous_p=np.array(poses[0]['position']);previous_r=np.array(poses[0]['orientation']);samples=[]
for segment,pose in enumerate(poses[1:]):
 point=np.array(pose['position']);r=np.array(pose['orientation']);delta=Rotation.from_matrix(r@previous_r.T).as_rotvec()
 for t in np.linspace(0,1,11)[1:]:
  rr=Rotation.from_rotvec(delta*t).as_matrix()@previous_r;q,e,ang=k.solve(previous_p+(point-previous_p)*t,rr,q)
  closed=segment>=(4 if s.get('seat_center_xyz') else 2);seating=bool(s.get('seat_center_xyz') and segment in [2,3])
  pitch=33 if closed else a.prethumb_pitch
  values={'right_rh_thumb_cmc_yaw':np.deg2rad(60 if closed else a.prethumb_yaw),'right_rh_thumb_cmc_pitch':np.deg2rad(pitch),'right_rh_thumb_ip':np.deg2rad(pitch*1.86)}
  for f in ['index','middle','ring','pinky']:
   values['right_rh_'+f+'_mcp_pitch']=np.deg2rad(80 if closed else 50 if seating else 0);values['right_rh_'+f+'_dip']=.89*values['right_rh_'+f+'_mcp_pitch']
  samples.append({'segment':segment,'e':e,'angle':ang,'overlaps':check(q,True,k.root,values)})
 previous_p,previous_r=point,r
out={'passed':all(x['e']<.004 and x['angle']<.04 and not x['overlaps'] for x in samples),'samples':samples,'limitations':'Parked left arm/torso convex-hull screen; sampled path with nominal open/closed finger poses; kitchen contact and memory guards still required; self-collision disabled.'}
(ROOT/'logs/cooking_arm_clearance.json').write_text(json.dumps(out,indent=2));print('PASS',out['passed'],'FAILURES',[x for x in samples if x['overlaps'] or x['e']>=.004 or x['angle']>=.04]);raise SystemExit(0 if out['passed'] else 1)
