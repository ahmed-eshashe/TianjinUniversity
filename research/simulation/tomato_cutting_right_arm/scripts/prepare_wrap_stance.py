"""Fit a common robot stance to all waypoints of the experimental end-on grasp."""
import argparse,json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
from pxr import Usd
from reach_kinematics import ArmKinematics
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--seed',default='work/grasp_stance_wrap15.json')
parser.add_argument('--output',default='work/grasp_stance_wrap15.json')
parser.add_argument('--roll-deg',type=float,default=0.)
parser.add_argument('--palm-height',type=float,default=.028)
parser.add_argument('--finger-offset',type=float,default=.012)
parser.add_argument('--handle-offset',type=float,default=.05)
parser.add_argument('--approach-distance',type=float,default=.08)
parser.add_argument('--approach-clearance',type=float,default=.06)
args=parser.parse_args()
k=ArmKinematics(Usd.Stage.Open(str(ROOT/'work/kitchen_reach.usda')));base=k.root.copy();seed=json.loads((ROOT/args.seed).read_text());r=np.array(seed['orientation'])@Rotation.from_euler('x',args.roll_deg,degrees=True).as_matrix()
h=np.array([-2.2627178722644663,-1.7618141868696735,.871988845153742]);p=h-r@np.array([args.palm_height,-args.handle_offset,args.finger_offset]);outside=p+r[:,1]*args.approach_distance
points=[p+[0,0,.15],outside+[0,0,args.approach_clearance],outside,p,p+[0,0,.03]]
k.root[:2,3]+=seed['root_offset_xy'];k.root[:3,:3]=Rotation.from_euler('z',seed['root_yaw_deg'],degrees=True).as_matrix()
q=np.array(seed['ready_rad']);qs=[]
for point in points:
 q,_,_=k.solve(point,r,q);qs.append(q.copy())
n=len(points);lo=np.r_[np.tile(k.lower,n),[-.22,-.22,-np.pi/4]];hi=np.r_[np.tile(k.upper,n),[.22,.22,np.pi/4]]
def residual(v):
 k.root=base.copy();k.root[:2,3]+=v[-3:-1];k.root[:3,:3]=Rotation.from_euler('z',v[-1]).as_matrix()
 out=[]
 for i,point in enumerate(points):
  pp,rr=k.pose(v[i*7:(i+1)*7]);out.extend(pp-point);out.extend(.15*Rotation.from_matrix(r@rr.T).as_rotvec())
 return np.r_[out,.00001*v[:-3],.0002*v[-3:]]
fit=least_squares(residual,np.r_[np.concatenate(qs),[*seed['root_offset_xy'],np.deg2rad(seed['root_yaw_deg'])]],bounds=(lo,hi),max_nfev=800,ftol=1e-10,xtol=1e-10,gtol=1e-10)
v=fit.x;err=np.max(np.abs(residual(v)[:n*6]));print('endpoint error',err,flush=True)
if err>.0002:raise RuntimeError('No common stance found')
q=v[:7];start=points[0];maximum=0.
for target in points[1:]:
 for a in np.linspace(0,1,61)[1:]:
  previous=q.copy();q,e,ang=k.solve(start+(target-start)*a,r,q);maximum=max(maximum,float(np.max(np.abs(q-previous))))
  if e>.004 or ang>.035 or np.max(np.abs(q-previous))>.15:raise RuntimeError(f'Route failed {e}, {ang}, jump={maximum}')
 start=target
out={**seed,'root_yaw_deg':float(np.rad2deg(v[-1])),'root_offset_xy':v[-3:-1].tolist(),'ready_rad':v[:7].tolist(),'ready_position':points[0].tolist(),'grasp_rad':v[21:28].tolist(),'orientation':r.tolist(),'roll_deg':float(seed.get('roll_deg',0)+args.roll_deg),'center_xyz':[args.palm_height,-args.handle_offset,args.finger_offset+.065],'approach_distance_m':args.approach_distance,'approach_clearance_m':args.approach_clearance,'max_waypoint_joint_step_rad':maximum}
(ROOT/args.output).write_text(json.dumps(out,indent=2));print('stance saved',out['root_offset_xy'],out['root_yaw_deg'],maximum,flush=True)
