"""Fit one base placement and continuous arm path for pickup and an edge-down wrist turn."""
import argparse,json,numpy as np
from pathlib import Path
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix
from pxr import Usd
from reach_kinematics import ArmKinematics
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--root-x-max',type=float,default=.3);p.add_argument('--seating-roll-deg',type=float,default=0.);p.add_argument('--seating-grasp-report');p.add_argument('--clearance-height',type=float,default=.035);p.add_argument('--closed-center-xyz',type=float,nargs=3);p.add_argument('--keep-root',action='store_true',help='Retain a previously screened base pose and solve the new path with the same strict checks');p.add_argument('--scene-log',help='Use the actual settled handle and knife axis from a scene probe');p.add_argument('--roll-deg',type=float,default=-75);p.add_argument('--seed',default='work/grasp_stance_cooking_120.json');p.add_argument('--center-xyz',type=float,nargs=3,default=[.04,0,.085]);p.add_argument('--seat-center-xyz',type=float,nargs=3);p.add_argument('--output',default='work/grasp_stance_cooking_final.json');p.add_argument('--use-cached-fit',action='store_true');p.add_argument('--refine-cached-fit',action='store_true');p.add_argument('--root-x-min',type=float,default=-.3);p.add_argument('--root-y-min',type=float,default=-.3);a=p.parse_args()
s=json.load(open(ROOT/a.seed));k=ArmKinematics(Usd.Stage.Open(str(ROOT/'work/kitchen_reach.usda')));base=k.root.copy();r=np.array(s['orientation']);h=np.array([-2.26269,-1.76180,.87195]);offset=np.array(a.center_xyz)-[0,0,.065];lift=.06
line=next(x for x in (ROOT/(a.scene_log or 'logs/cooking_trial1.log')).read_text().splitlines() if x.startswith('SETTLED_SCENE '));scene=json.loads(line.removeprefix('SETTLED_SCENE '));axis=np.array(scene['knife_rotation_world'])[:,0]
if a.scene_log:h=np.array(scene['handle'])
poses=[(h-r@offset+[0,0,.15],r),(h-r@offset+[0,0,.08],r),(h-r@offset,r)]
if a.seat_center_xyz:
 seated=np.array(a.seat_center_xyz)-[0,0,.065]
 side=offset.copy();side[2]=seated[2];poses.extend([(h-r@side,r),(h-r@seated,r)]);offset=seated
if a.seating_roll_deg:
 if not a.seating_grasp_report:raise ValueError('A measured contact grip is required for planning the seating tilt')
 measured=json.load(open(ROOT/a.seating_grasp_report));relative=np.array(measured['handle_in_palm_frame_m']);seating_axis=np.array(measured['knife_rotation_world'])[:,0]
 clear=h-r@offset+[0,0,a.clearance_height];pivot=clear+r@relative;tilted=Rotation.from_rotvec(seating_axis*np.deg2rad(a.seating_roll_deg)).as_matrix()@r
 poses.extend([(clear,r),(pivot-tilted@relative,tilted),(clear,r)])
end_palm=h-r@offset+[0,0,lift];poses.append((end_palm,r))
roll_offset=np.array(a.closed_center_xyz)-[0,0,.065] if a.closed_center_xyz else offset
roll_pivot=end_palm+r@roll_offset
for roll in [a.roll_deg/3,2*a.roll_deg/3,a.roll_deg]:
 rr=Rotation.from_rotvec(axis*np.deg2rad(roll)).as_matrix()@r;poses.append((roll_pivot-rr@roll_offset,rr))
k.root[:2,3]+=s['root_offset_xy'];k.root[:3,:3]=Rotation.from_euler('z',s['root_yaw_deg'],degrees=True).as_matrix();q=np.array(s['ready_rad']);qs=[]
for point,rr in poses:q,e,ang=k.solve(point,rr,q);qs.append(q.copy())
n=len(poses)
def residual(v):
 k.root=base.copy();k.root[:2,3]+=v[-3:-1];k.root[:3,:3]=Rotation.from_euler('z',v[-1]).as_matrix();out=[]
 for i,(point,rr) in enumerate(poses):
  pp,actual=k.pose(v[7*i:7*i+7]);out.extend(pp-point);out.extend(.15*Rotation.from_matrix(rr@actual.T).as_rotvec())
 return np.r_[out,.00001*v[:-3],.0002*v[-3:]]
lo=np.r_[np.tile(k.lower,n),[a.root_x_min,a.root_y_min,-np.pi/3]];hi=np.r_[np.tile(k.upper,n),[a.root_x_max,.3,np.pi/3]]
initial=np.r_[np.concatenate(qs),[*s['root_offset_xy'],np.deg2rad(s['root_yaw_deg'])]]
initial=np.clip(initial,lo+1e-8,hi-1e-8)
# Dense differentiation is inexpensive for seven poses and avoids sparse solver stagnation near joint limits.
cache=(ROOT/a.output).with_suffix('.fit.json')
if a.use_cached_fit:
 saved=json.loads(cache.read_text())
 if saved['center_xyz']!=a.center_xyz or saved['roll_deg']!=a.roll_deg:raise ValueError('Cached fit parameters do not match')
 v=np.array(saved['v'])
else:
 if a.refine_cached_fit:initial=np.clip(np.array(json.loads(cache.read_text())['v']),lo+1e-8,hi-1e-8)
 if a.keep_root:v=initial
 else:
  fit=least_squares(residual,initial,bounds=(lo,hi),max_nfev=700,ftol=1e-10,xtol=1e-10,gtol=1e-10);v=fit.x
 cache.write_text(json.dumps({'v':v.tolist(),'center_xyz':a.center_xyz,'roll_deg':a.roll_deg},indent=2))
err=np.max(np.abs(residual(v)[:6*n]));print('ENDPOINT_ERROR',err,flush=True)
if err>.0002:raise RuntimeError('No common pickup and cutting stance')
k.root=base.copy();k.root[:2,3]+=v[-3:-1];k.root[:3,:3]=Rotation.from_euler('z',v[-1]).as_matrix();q=v[:7];previous_p,previous_r=poses[0];maximum=0
for point,rr in poses[1:]:
 delta=Rotation.from_matrix(rr@previous_r.T).as_rotvec()
 for t in np.linspace(0,1,161)[1:]:
  target=previous_p+(point-previous_p)*t;orientation=Rotation.from_rotvec(delta*t).as_matrix()@previous_r
  prior=q.copy();q,e,ang=k.solve(target,orientation,q);maximum=max(maximum,float(np.max(np.abs(q-prior))))
  if e>.004 or ang>.04 or maximum>.15:raise RuntimeError(f'Discontinuous/unreachable route {e}, {ang}, {maximum}, target={point}, t={t}')
 previous_p,previous_r=point,rr
out={**s,'root_offset_xy':v[-3:-1].tolist(),'root_yaw_deg':float(np.rad2deg(v[-1])),'ready_rad':v[:7].tolist(),'ready_position':poses[0][0].tolist(),'center_xyz':a.center_xyz,'seat_center_xyz':a.seat_center_xyz,'post_lift_roll_deg':a.roll_deg,'lift_height':lift,'max_waypoint_joint_step_rad':maximum,'planned_handle_world':h.tolist(),'source_scene_log':a.scene_log,'planned_poses':[{'position':pos.tolist(),'orientation':rr.tolist()} for pos,rr in poses]}
(ROOT/a.output).write_text(json.dumps(out,indent=2));print('SAVED',a.output,out['root_offset_xy'],out['root_yaw_deg'],maximum,flush=True)
