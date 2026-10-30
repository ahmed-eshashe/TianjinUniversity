"""Screen the experimental fixed hand preshape against existing kitchen collision hulls."""
import argparse,json,itertools
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import linprog
from search_wrap_grasp import geometry,s,xc,meta,ROOT
from pxr import UsdGeom
from reach_kinematics import PALM_OFFSET
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--seed',default='work/grasp_stance_wrap15.json');parser.add_argument('--palm-height',type=float,default=.028);parser.add_argument('--finger-offset',type=float,default=.012);parser.add_argument('--handle-offset',type=float,default=.05);parser.add_argument('--preclose-deg',type=float,default=75);parser.add_argument('--top-down',action='store_true');parser.add_argument('--clearance',type=float,default=.06);args=parser.parse_args()
seed=json.loads((ROOT/args.seed).read_text());r=np.array(seed['orientation']);h=np.array([-2.2627178722644663,-1.7618141868696735,.871988845153742]);grasp=h-r@np.array([args.palm_height,-args.handle_offset,args.finger_offset]);ready=np.array(seed['ready_position'])
# Match the controller's session-only board placement for this wrist orientation.
board=s.GetPrimAtPath('/Indoor/RZ/SM_kitchen_Board');bm=np.array(xc.GetLocalToWorldTransform(board)).T
knife_matrix=np.array(xc.GetLocalToWorldTransform(s.GetPrimAtPath(meta['knife_path']))).T
authored_handle=knife_matrix[:3,:3]@np.array(meta['knife_handle_local'])+knife_matrix[:3,3]
direction=r[:,1].copy();direction[2]=0;direction/=np.linalg.norm(direction)
board_points=np.array(UsdGeom.Mesh(board).GetPointsAttr().Get());bi=np.linalg.inv(bm)
hl=bi[:3,:3]@authored_handle+bi[:3,3];dl=bi[:3,:3]@direction
edge=min((board_points.max(0)[i]-hl[i])/dl[i] if dl[i]>0 else (board_points.min(0)[i]-hl[i])/dl[i] for i in [0,1] if abs(dl[i])>1e-6)
board_shift=-direction*max(0.,edge-(-.035))
obstacles=[]
for path in meta['active_kitchen_colliders']:
 if path==meta['knife_path']:continue
 p=s.GetPrimAtPath(path)
 if not p.IsA(UsdGeom.Mesh):continue
 m=np.array(xc.GetLocalToWorldTransform(p)).T
 if path.endswith('SM_kitchen_Board'):m[:3,3]+=board_shift
 v=np.array(UsdGeom.Mesh(p).GetPointsAttr().Get())@m[:3,:3].T+m[:3,3];eq=ConvexHull(v).equations
 obstacles.append((path,v.min(0),v.max(0),eq))
results=[]
for distance,yaw,pitch in itertools.product([0] if args.top_down else [.08,.095,.10],[0,20,40,60,77],[0,10,20,30,33]):
 outside=grasp+r[:,1]*distance;start=ready;points=[]
 for target in [outside+[0,0,args.clearance],outside,grasp]:
  points.extend(start+(target-start)*a for a in np.linspace(0,1,13)[1:]);start=target
 collisions=[]
 for name,v in geometry(args.preclose_deg,yaw,pitch):
  vv=v@r.T;eq=ConvexHull(vv).equations;lo=vv.min(0);hi=vv.max(0)
  for i,point in enumerate(points):
   origin=point-r@PALM_OFFSET;low=lo+origin;high=hi+origin
   for path,ol,oh,oe in obstacles:
    if np.any(high<ol) or np.any(oh<low):continue
    he=eq.copy();he[:,3]-=eq[:,:3]@origin
    both=np.r_[he,oe]
    fit=linprog([0,0,0,-1],A_ub=np.c_[both[:,:3],np.ones(len(both))],b_ub=-both[:,3],bounds=[(None,None)]*4,method='highs')
    if fit.success and fit.x[3]>.0005:collisions.append({'body':name,'object':path,'sample':i,'depth_m':float(fit.x[3])})
 result={'distance':distance,'yaw':yaw,'pitch':pitch,'collisions':collisions,'max_penetration_m':max((x['depth_m'] for x in collisions),default=0.)};results.append(result)
 print(distance,yaw,pitch,'max penetration',result['max_penetration_m'],'objects',sorted(set(x['object'] for x in collisions)),flush=True)
(ROOT/'work/wrap_approach_screen.json').write_text(json.dumps(results,indent=2))
