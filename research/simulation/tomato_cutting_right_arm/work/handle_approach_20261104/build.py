from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation,Slerp
from pxr import Usd,UsdGeom,UsdPhysics,Gf
r=Path(__file__).resolve().parents[2];w=Path(__file__).resolve().parent;sys.path[:0]=[str(r/'scripts'),str(r/'rl')]
from reach_kinematics import ArmKinematics,PALM_OFFSET
from tomato_fixed_mount_scene import matrix
p=json.loads((r/'work/pickup_demo_20261104/pickup_plan_v02.json').read_text());f=json.loads((w/'grip_fit.json').read_text());m=np.array(f['mount']);s0=Usd.Stage.Open(p['scene']);k=ArmKinematics(s0);rk=np.array(p['knife_rotation']);rh=rk@m[:3,:3].T;o=np.array(p['knife_origin_route_m'][0]);seed=np.array([p['closed_home_rad'][n]for n in k.names]);seed,e,a=k.solve(o-rh@m[:3,3]+rh@PALM_OFFSET,rh,seed);assert e<2e-5 and a<2e-4,('Initial IK',e,a)
closed=p['closed_home_rad'].copy();closed.update(dict(zip(k.names,seed)))
for finger,angle in f['flex'].items():closed['right_rh_'+finger+'_mcp_pitch']=np.deg2rad(angle);closed['right_rh_'+finger+'_dip']=np.deg2rad(angle*.89)
left=ArmKinematics(s0,side='left');left.lower[0]=-.8;left.upper[0]=.8;left.lower[5]=-.65;left.upper[5]=.65;lb=next(t[:3,3]for n,t in left.transforms(np.zeros(7)).items()if n.endswith('_link2'));rng=np.random.default_rng(86)
def residual(q):
 tf=left.transforms(q);h=tf[left.hand_path];el=next(t[:3,3]for n,t in tf.items()if n.endswith('_link4'))
 return np.r_[3*(h[:3,3]-(lb+[.15,-.04,-.52])),.4*(h[:3,2]-[0,0,-1]),.3*(el-(lb+[.10,-.04,-.26])),.025*q]
best=None
for z in [np.clip([closed[n]for n in left.names],left.lower,left.upper)]+[rng.uniform(left.lower,left.upper)for _ in range(12)]:
 sol=least_squares(residual,z,bounds=(left.lower,left.upper),max_nfev=220)
 if best is None or np.linalg.norm(sol.fun)<np.linalg.norm(best.fun):best=sol
closed.update(dict(zip(left.names,best.x)))
for finger in ['index','middle','ring','pinky']:closed['left_lh_'+finger+'_mcp_pitch']=np.deg2rad(22);closed['left_lh_'+finger+'_dip']=np.deg2rad(22*.89)
closed['left_lh_thumb_cmc_yaw']=.86;closed['left_lh_thumb_cmc_pitch']=.14;closed['left_lh_thumb_ip']=.14*1.86
closed['right_rh_thumb_cmc_yaw']=f['thumb_yaw'];closed['right_rh_thumb_cmc_pitch']=f['thumb_pitch'];closed['right_rh_thumb_ip']=f['thumb_pitch']*1.86
initial=closed.copy()
for name in initial:
 if 'right_rh_'in name:initial[name]=p['home_rad'][name]
scene=w/'handle_approach_scene_v03.usda';s=Usd.Stage.CreateNew(str(scene));s.GetRootLayer().subLayerPaths=[p['scene']];UsdGeom.SetStageUpAxis(s,'Z');UsdGeom.SetStageMetersPerUnit(s,1.)
j=UsdPhysics.FixedJoint(s.GetPrimAtPath('/dual_ar5_o6/Physics/cutting_tool_mount'));j.CreateLocalPos0Attr(Gf.Vec3f(*m[:3,3]));quat=Rotation.from_matrix(m[:3,:3]).as_quat();j.CreateLocalRot0Attr(Gf.Quatf(float(quat[3]),Gf.Vec3f(*quat[:3])))
k=ArmKinematics(s);tf={'/dual_ar5_o6':k.root}
def tr(path):
 if path in tf:return tf[path]
 parent,child,a,b,axis,name=k.by_child[path];rot=np.eye(4)
 if axis is not None:rot[:3,:3]=Rotation.from_rotvec(axis*initial.get(name,0)).as_matrix()
 tf[path]=tr(parent)@a@rot@b;return tf[path]
for path in sorted(k.by_child,key=lambda x:x.count('/')):
 prim=s.GetPrimAtPath(path);parent=np.array(UsdGeom.XformCache().GetLocalToWorldTransform(prim.GetParent())).T;matrix(UsdGeom.Xformable(prim),np.linalg.inv(parent)@tr(path))
for name,v in initial.items():
 prim=s.GetPrimAtPath('/dual_ar5_o6/Physics/'+name)
 if prim:UsdPhysics.DriveAPI.Apply(prim,'angular').CreateTargetPositionAttr(float(np.rad2deg(v)))
# All motion follows Cartesian waypoints with a noncontact approach above the tomato.
blade=np.array(json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())['vertices']);target=np.load(r/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz')['x'];center=(target.min(0)+target.max(0))/2
lift=o+[0,0,.065];routes=[];origins=[];gaps=[];route=[]
for i in range(241):
 u=i/240;b=u*u*u*(10+u*(-15+6*u));origin=o+[0,0,.065*b];seed,e,a=k.solve(origin-rh@m[:3,3]+rh@PALM_OFFSET,rh,seed)
 if e>2e-5 or a>2e-4:raise ValueError(('lift IK',i,e,a))
 route.append(seed.tolist())
routes.append(route);origins.append([o.tolist(),lift.tolist()]);candidates=json.loads((w/'endpoints.json').read_text());chosen=None
sys.path.insert(0,str(r/'work/pickup_demo_20261104'));from clearance import check
for candidate in candidates:
 endq=np.array(candidate['q']);test=[];bad=False
 if abs(endq[5])>.82:continue
 for u in np.linspace(0,1,61):
  blend=u*u*u*(10+u*(-15+6*u));q=seed+(endq-seed)*blend;tool=k.transforms(q)[k.hand_path]@m;verts=blade@tool[:3,:3].T+tool[:3,3];gap=float(np.maximum(target.min(0)-verts.max(0),verts.min(0)-target.max(0)).max());test.append(gap)
  if gap<.025 or verts[:,2].min()<.025:bad=True;break
 if bad:continue
 for u in np.linspace(0,1,9):
  q=seed+(endq-seed)*(u*u*u*(10+u*(-15+6*u)))
  if check(q,left_zero=True,root_matrix=p['robot_root_world_matrix'],hand_values={n:v for n,v in closed.items()if 'right_rh_'in n}):bad=True;break
 if not bad:chosen=candidate;gaps=test;break
if chosen is None:raise ValueError('No screened joint-space approach')
route=[]
for u in np.linspace(0,1,601):route.append((seed+(np.array(chosen['q'])-seed)*(u*u*u*(10+u*(-15+6*u)))).tolist())
routes.append(route);origins.append([lift.tolist(),chosen['origin']]);end=np.array(chosen['origin']);(w/'selected_endpoint.json').write_text(json.dumps(chosen,indent=2))
s.GetRootLayer().Save();p.update(scene=str(scene),home_rad=initial,closed_home_rad=closed,mount_hand_from_knife=m.tolist(),lift_route=routes[0],approach_routes=routes[1:],motion_origins=origins,planned_minimum_target_gap_m=min(gaps),sequence=['supported open','close on handle','attach','lift','approach above tomato','stop clear']);(w/'plan.json').write_text(json.dumps(p,indent=2));print('left',best.x,'end',end,'gap',min(gaps))
