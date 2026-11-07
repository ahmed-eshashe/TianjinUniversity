from pathlib import Path
import sys,json,numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom,UsdPhysics,UsdShade,Gf,Vt
r=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');w=r/'work/single_slice_20261106';out=w/'cutting_playback';sys.path.insert(0,str(r/'scripts'))
from reach_kinematics import ArmKinematics
p=json.loads((r/'work/backward_elbow_20261105/plan.json').read_text());base=Usd.Stage.Open(p['scene']);k=ArmKinematics(base);route=json.loads((w/'clear_entry_robot_plan_v8.json').read_text());F=np.array(route['target_rotation']);placement=np.array(route['target_translation']);design=json.loads((r/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text());frames={}
for run in ['robot_cut11','robot_cut12','robot_cut13','robot_cut14','robot_cut15']:
 names=json.loads((w/run/'runtime_joint_limits.json').read_text())['names']
 for path in sorted((w/run/'checkpoints').glob('step_*.json')):
  m=json.loads(path.read_text())
  if 'robot_state' in m and path.with_suffix('.npz').exists():frames[round(m['clock'],8)]=(path,m,names)
scene=out/'recorded_incomplete_cut.usda';scene.unlink(missing_ok=True);s=Usd.Stage.CreateNew(str(scene));s.GetRootLayer().subLayerPaths=[p['scene']];UsdGeom.SetStageUpAxis(s,'Z');UsdGeom.SetStageMetersPerUnit(s,1);s.SetTimeCodesPerSecond(24)
for prim in s.Traverse():
 if prim.HasAPI(UsdPhysics.RigidBodyAPI):UsdPhysics.RigidBodyAPI(prim).CreateRigidBodyEnabledAttr(False)
 if prim.HasAPI(UsdPhysics.CollisionAPI):UsdPhysics.CollisionAPI(prim).CreateCollisionEnabledAttr(False)
 if prim.IsA(UsdPhysics.Joint):UsdPhysics.Joint(prim).CreateJointEnabledAttr(False)
old=s.GetPrimAtPath('/CuttingTargetVisual');material=UsdShade.MaterialBindingAPI(old).ComputeBoundMaterial()[0];UsdGeom.Imageable(old).MakeInvisible();meshes=[]
for piece in design['pieces']:
 mesh=UsdGeom.Mesh.Define(s,'/RecordedTomato/'+piece['side']);faces=np.array(piece['triangles']);mesh.CreateFaceVertexCountsAttr([3]*len(faces));mesh.CreateFaceVertexIndicesAttr(faces.ravel().tolist());mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateDoubleSidedAttr(True)
 if material:UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(material)
 meshes.append(mesh)
ops={}
for path in list(k.by_child)+[p['tool_path']]:
 if path in ops:continue
 xf=UsdGeom.Xformable(s.GetPrimAtPath(path));xf.ClearXformOpOrder();xf.SetResetXformStack(True);ops[path]=xf.AddTransformOp(opSuffix='recordedPlayback')
board=s.GetPrimAtPath(p['board_path']);xf=UsdGeom.Xformable(board);world=np.array(UsdGeom.XformCache().GetLocalToWorldTransform(board)).T;world[0,3]-=.05;xf.ClearXformOpOrder();xf.SetResetXformStack(True);xf.AddTransformOp(opSuffix='recordedBoard').Set(Gf.Matrix4d(world.T.tolist()))
start=min(frames);audit=[]
for clock,(path,m,names) in sorted(frames.items()):
 tc=(clock-start)*24*4;state=m['robot_state'];values=dict(zip(names,state['q']));tf={'/dual_ar5_o6':np.array(p['robot_root_world_matrix'])}
 def tr(path):
  if path in tf:return tf[path]
  parent,child,a,b,axis,name=k.by_child[path];rot=np.eye(4)
  if axis is not None:rot[:3,:3]=Rotation.from_rotvec(axis*values.get(name,k.home.get(name,0))).as_matrix()
  tf[path]=tr(parent)@a@rot@b;return tf[path]
 for child in k.by_child:
  if child!=p['tool_path']:ops[child].Set(Gf.Matrix4d(tr(child).T.tolist()),tc)
 pose=np.array(state['tool_pose']);T=np.eye(4);T[:3,:3]=Rotation.from_quat(pose[3:]).as_matrix();T[:3,3]=pose[:3];ops[p['tool_path']].Set(Gf.Matrix4d(T.T.tolist()),tc)
 z=np.load(path.with_suffix('.npz'));points=(z['x']+[-.0225,0,.0295])@F.T+placement
 for mesh in meshes:mesh.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(points.astype(np.float32)),tc)
 audit.append({'source':str(path),'time_code':tc})
s.SetStartTimeCode(0);s.SetEndTimeCode(tc);cam=UsdGeom.Camera.Define(s,'/ReplayCamera');cam.CreateFocalLengthAttr(22);cam.AddTransformOp().Set(Gf.Matrix4d().SetLookAt(Gf.Vec3d(1.05,.8,.8),Gf.Vec3d(.40,-.30,-.10),Gf.Vec3d(0,0,1)).GetInverse());s.GetRootLayer().Save();(out/'manifest.json').write_text(json.dumps({'scope':'Recorded accepted checkpoint playback; interpolated between saved frames; four times slower. No new physics, no full separation. Robot links reconstructed from measured joint positions; knife pose and tomato positions from saved states.','frames':audit,'duration_s':tc/24},indent=2));print(scene,len(audit),tc/24)
