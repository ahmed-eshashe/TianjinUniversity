from pathlib import Path
import sys,json,hashlib
import numpy as np
from pxr import Usd,UsdGeom,UsdPhysics,UsdShade,Gf,Vt
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parent
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm')
sys.path.insert(0,str(R/'scripts'))
from reach_kinematics import ArmKinematics,PALM_OFFSET
p=json.loads((R/'work/backward_elbow_20261105/plan.json').read_text())
scene=W/'robot_kitchen_straight_blade_v02.usda'
if scene.exists():raise FileExistsError(scene)
s=Usd.Stage.CreateNew(str(scene));s.GetRootLayer().subLayerPaths=[p['scene']]
UsdGeom.SetStageUpAxis(s,'Z');UsdGeom.SetStageMetersPerUnit(s,1.)
root=s.GetPrimAtPath(p['tool_path']);mesh=UsdGeom.Mesh(root)
old_faces=np.array(mesh.GetFaceVertexIndicesAttr().Get()).reshape(-1,3)
keep=np.array(UsdGeom.Subset(s.GetPrimAtPath(p['tool_path']+'/Section2')).GetIndicesAttr().Get())
mesh.GetFaceVertexIndicesAttr().Set(old_faces[keep].ravel().tolist());mesh.GetFaceVertexCountsAttr().Set([3]*len(keep))
if mesh.GetNormalsAttr().HasAuthoredValueOpinion():
 n=np.array(mesh.GetNormalsAttr().Get())
 if mesh.GetNormalsInterpolation()=='faceVarying':mesh.GetNormalsAttr().Set(Vt.Vec3fArray.FromNumpy(n.reshape(-1,3,3)[keep].reshape(-1,3)))
for pv in UsdGeom.PrimvarsAPI(root).GetPrimvars():
 if pv.GetInterpolation()=='faceVarying':
  if pv.IsIndexed():
   a=np.array(pv.GetIndices());pv.SetIndices(a.reshape(-1,3)[keep].ravel().tolist())
  else:
   a=np.array(pv.Get());pv.Set(a.reshape(len(old_faces),3,-1)[keep].reshape(-1,a.shape[-1]).tolist())
for section in ['Section0','Section1']:s.GetPrimAtPath(p['tool_path']+'/'+section).SetActive(False)
UsdGeom.Subset(s.GetPrimAtPath(p['tool_path']+'/Section2')).GetIndicesAttr().Set(list(range(len(keep))))
# The original handle and fingers are preserved. This tested triangular prism is
# visibly substituted for the curved blade, with its heel at the handle junction.
L=np.array([[0,0,-1],[0,1,0],[1,0,0]],float);C=np.array([-.232,-.02597565,.0012])
local=np.array([[0,0,-.06],[.0005,.03,-.06],[-.0005,.03,-.06],[0,0,.06],[.0005,.03,.06],[-.0005,.03,.06]])
faces=np.array([[0,2,1],[3,4,5],[0,1,4],[0,4,3],[1,2,5],[1,5,4],[2,0,3],[2,3,5]])
points=local@L.T+C
blade=UsdGeom.Mesh.Define(s,p['tool_path']+'/StraightBlade');blade.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(points.astype(np.float32)));blade.CreateFaceVertexCountsAttr([3]*8);blade.CreateFaceVertexIndicesAttr(faces.ravel().tolist());blade.CreateSubdivisionSchemeAttr('none');blade.CreateDoubleSidedAttr(True)
steel=UsdShade.Material(s.GetPrimAtPath('/PresentationLooks/MountedKnife_Section0'));UsdShade.MaterialBindingAPI.Apply(blade.GetPrim()).Bind(steel)
collision=UsdGeom.Mesh(s.GetPrimAtPath(p['tool_path']+'/CollisionBlade'));collision.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(points.astype(np.float32)));collision.GetFaceVertexCountsAttr().Set([3]*8);collision.GetFaceVertexIndicesAttr().Set(faces.ravel().tolist());collision.GetNormalsAttr().Block();collision.GetExtentAttr().Set([Gf.Vec3f(*points.min(0)),Gf.Vec3f(*points.max(0))]);UsdPhysics.MeshCollisionAPI(collision).GetApproximationAttr().Set('convexHull')
UsdGeom.Imageable(s.GetPrimAtPath('/CuttingTargetVisual')).MakeInvisible()
old_q=np.array(p['approach_routes'][-1][-1]);kin=ArmKinematics(s);mount=np.array(p['mount_hand_from_knife']);end=kin.transforms(old_q)[kin.hand_path]@mount
# Keep the established horizontal knife orientation; straighten minute IK noise.
heading=np.arctan2(end[1,0],end[0,0]);rk=np.array([[np.cos(heading),0,np.sin(heading)],[np.sin(heading),0,-np.cos(heading)],[0,1,0]])
Q=rk@L;anchor=np.array([.04,.04,0.])
def solve_tool(proxy,q):
 tool_origin=anchor+Q@proxy-rk@C
 desired=np.eye(4);desired[:3,:3]=rk;desired[:3,3]=tool_origin;hand=desired@np.linalg.inv(mount)
 q,pe,re=kin.solve(hand[:3,3]+hand[:3,:3]@PALM_OFFSET,hand[:3,:3],q)
 if pe>1e-4 or re>1e-3:raise ValueError(('IK error',proxy,pe,re))
 return q,tool_origin,pe,re
entry=[];q=old_q.copy();edge_start=end[:3,3]+end[:3,:3]@C;proxy_start=Q.T@(edge_start-anchor);proxy_above=np.array([.00175,.06075,0.])
for u in np.linspace(0,1,201):
 f=u*u*u*(10-15*u+6*u*u);proxy=(1-f)*proxy_start+f*proxy_above;proxy[1]+=.025*np.sin(np.pi*f)**2
 q,origin,pe,re=solve_tool(proxy,q);entry.append({'time':u*6,'q':q.tolist(),'proxy':proxy.tolist(),'origin':origin.tolist(),'error_m':pe,'error_rad':re})
# A geometric route table, not a substitute for measured knife movement.
sys.path.insert(0,str(W.parent/'tomato_motion_comparison_20261113_v30'))
from compare import command,CASES
motion=CASES['smooth_sync_2x'];proxy=proxy_above.copy();route=[]
for k in range(1800):
 action,phase=command(motion,k,proxy,1,0)
 proxy+=action[:3]*.02
 q,origin,pe,re=solve_tool(proxy,q)
 route.append({'time':(k+1)*.02,'q':q.tolist(),'proxy':proxy.tolist(),'origin':origin.tolist(),'error_m':pe,'error_rad':re})
 if proxy[1]<=.00340001:break
withdraw=[];start=proxy.copy()
for u in np.linspace(0,1,161):
 f=u*u*u*(10-15*u+6*u*u);position=start+[0,0,-.12*f];q,origin,pe,re=solve_tool(position,q);withdraw.append({'time':u*4,'q':q.tolist(),'proxy':position.tolist(),'origin':origin.tolist(),'error_m':pe,'error_rad':re})
start=position.copy();bodyward=np.array(p['robot_root_world_matrix'])[:3,3]-anchor;bodyward[2]=0;bodyward/=np.linalg.norm(bodyward);direction=Q.T@bodyward
for u in np.linspace(0,1,121)[1:]:
 f=u*u*u*(10-15*u+6*u*u);position=start+.06*f*direction;q,origin,pe,re=solve_tool(position,q);withdraw.append({'time':4+u*3,'q':q.tolist(),'proxy':position.tolist(),'origin':origin.tolist(),'error_m':pe,'error_rad':re})
s.GetRootLayer().Save()
config={'source_plan':str(R/'work/backward_elbow_20261105/plan.json'),'scene':str(scene),'proxy_to_knife_rotation':L.tolist(),'proxy_origin_in_knife_m':C.tolist(),'material_to_world_rotation':Q.tolist(),'material_origin_world_m':anchor.tolist(),'knife_rotation_world':rk.tolist(),'blade_vertices_knife':points.tolist(),'blade_faces':faces.tolist(),'entry':entry,'cut':route,'withdraw':withdraw,'knife_inertial_parameters':'Original authored 0.25kg mass, COM and inertia retained as an explicit controlled tool approximation; not a new mass measurement.','fixed_mount':True,'blade_change_authorized':'Keep original handle and grip, visibly use the tested straight blade','original_handle_faces_preserved':len(keep)}
(W/'scene_plan.json').write_text(json.dumps(config,indent=2));print(json.dumps({'scene':str(scene),'entry_points':len(entry),'cut_points':len(route),'withdraw_points':len(withdraw),'maximum_IK_position_error_m':max(r['error_m']for r in entry+route+withdraw),'minimum_joint_margin_rad':float(min(np.min(np.array([r['q']for r in entry+route+withdraw])-kin.lower),np.min(kin.upper-np.array([r['q']for r in entry+route+withdraw]))))},indent=2))
