from pathlib import Path
import json,sys,hashlib
import numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom,UsdPhysics,UsdShade,Gf,Vt
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm')
p=json.loads((R/'work/backward_elbow_20261105/plan.json').read_text())
s=Usd.Stage.CreateNew(str(W/'head_vision_pickup_v02.usda'));s.GetRootLayer().subLayerPaths=[p['scene']]
UsdGeom.SetStageUpAxis(s,'Z');UsdGeom.SetStageMetersPerUnit(s,1.)
xc=UsdGeom.XformCache();bb=UsdGeom.BBoxCache(Usd.TimeCode.Default(),['default','render'])
torso='/dual_ar5_o6/Geometry/world/torso_base_link';body=s.GetPrimAtPath(torso+'/lm0310_body/lm0310_body');M=np.array(xc.GetLocalToWorldTransform(body)).T;v=np.array(UsdGeom.Mesh(body).GetPointsAttr().Get())@M[:3,:3].T+M[:3,3];centre=(v.min(0)+v.max(0))/2
heading=np.arctan2(p['robot_root_world_matrix'][1][0],p['robot_root_world_matrix'][0][0]);forward=-np.array([np.cos(heading),np.sin(heading),0.]);lateral=np.array([-forward[1],forward[0],0.]);board_centre=np.array([-.1,0.,0.]);board_centre[1]=centre[1]+(board_centre[0]-centre[0])*forward[1]/forward[0]
board=s.GetPrimAtPath(p['board_path']);world=np.array(xc.GetLocalToWorldTransform(board)).T;world[:2,3]=board_centre[:2];parent=np.array(xc.GetLocalToWorldTransform(board.GetParent())).T;xf=UsdGeom.Xformable(board);xf.ClearXformOpOrder();xf.AddTransformOp(opSuffix='headVisionBoard').Set(Gf.Matrix4d((np.linalg.inv(parent)@world).T.tolist()));xc.Clear();bb.Clear()
board_bbox=bb.ComputeWorldBound(board).ComputeAlignedRange();lo=np.array(board_bbox.GetMin());hi=np.array(board_bbox.GetMax())
# Verify a dense footprint against actual near-horizontal counter triangles,
# including sink/edge holes rather than merely its axis-aligned bounding box.
cp=s.GetPrimAtPath(p['counter_path']);cm=UsdGeom.Mesh(cp);T=np.array(xc.GetLocalToWorldTransform(cp)).T;pts=np.array(cm.GetPointsAttr().Get())@T[:3,:3].T+T[:3,3];counts=np.array(cm.GetFaceVertexCountsAttr().Get());ind=np.array(cm.GetFaceVertexIndicesAttr().Get());tri=[];start=0
for n in counts:
 face=ind[start:start+n];start+=n
 for j in range(1,n-1):tri.append([face[0],face[j],face[j+1]])
tri=pts[np.array(tri)];top=pts[:,2].max();tri=tri[np.all(abs(tri[:,:,2]-top)<.0005,axis=1)];a=tri[:,0,:2];e1=tri[:,1,:2]-a;e2=tri[:,2,:2]-a;det=e1[:,0]*e2[:,1]-e1[:,1]*e2[:,0];valid=abs(det)>1e-12;a,e1,e2,det=a[valid],e1[valid],e2[valid],det[valid]
unsupported=[]
for x in np.linspace(lo[0]+.003,hi[0]-.003,15):
 for y in np.linspace(lo[1]+.003,hi[1]-.003,21):
  d=np.array([x,y])-a;u=(d[:,0]*e2[:,1]-d[:,1]*e2[:,0])/det;vv=(e1[:,0]*d[:,1]-e1[:,1]*d[:,0])/det
  if not np.any((u>=-1e-7)&(vv>=-1e-7)&(u+vv<=1+1e-7)):unsupported.append([float(x),float(y)])
# Remove former mounted-demo supports and joints in this layer only.
for path in ['/PickupFixture','/dual_ar5_o6/Physics/cutting_tool_mount','/CuttingTargetVisual']:
 prim=s.GetPrimAtPath(path)
 if prim:prim.SetActive(False)
knife=s.GetPrimAtPath(p['tool_path']);cleared=[]
for prim in s.Traverse():
 if prim.HasAPI(UsdPhysics.FilteredPairsAPI):
  rel=UsdPhysics.FilteredPairsAPI(prim).GetFilteredPairsRel();targets=rel.GetTargets();keep=[t for t in targets if str(t)!=p['tool_path']]
  if prim==knife:keep=[]
  if list(targets)!=keep:rel.SetTargets(keep);cleared.append(str(prim.GetPath()))
# A flat, supported original knife along the board's long axis. Spawn height is
# a geometry-derived 2mm gap; settling is mandatory before any pickup attempt.
mesh=UsdGeom.Mesh(knife);verts=np.array(mesh.GetPointsAttr().Get());rot=Rotation.from_euler('z',90,degrees=True).as_matrix();q=verts@rot.T;translation=np.array([*board_centre[:2],hi[2]+.002-q[:,2].min()])-(np.r_[(q[:,:2].min(0)+q[:,:2].max(0))/2,0.]);K=np.eye(4);K[:3,:3]=rot;K[:3,3]=translation;parent=np.array(xc.GetLocalToWorldTransform(knife.GetParent())).T;xf=UsdGeom.Xformable(knife);xf.ClearXformOpOrder();xf.SetResetXformStack(True);xf.AddTransformOp(opSuffix='freeKnife').Set(Gf.Matrix4d(K.T.tolist()));rb=UsdPhysics.RigidBodyAPI(knife);rb.GetRigidBodyEnabledAttr().Set(True);rb.CreateKinematicEnabledAttr(False)
# Camera centre at the head face, with its lens aimed down toward the board.
head=v[(v[:,2]>.45)&(v[:,2]<.54)];delta=head-centre;mask=abs(delta@lateral)<.025;front=float(np.max(delta[mask]@forward));eye=centre+forward*(front+.004);eye[2]=.495;target=board_centre.copy();target[2]=.01
f=(target-eye);f/=np.linalg.norm(f);right=np.cross(f,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,f);C=np.eye(4);C[:3,:3]=np.column_stack([right,up,-f]);C[:3,3]=eye;parent=np.array(xc.GetLocalToWorldTransform(s.GetPrimAtPath(torso))).T;local=np.linalg.inv(parent)@C
camera_path=torso+'/HeadRGBD';cam=UsdGeom.Camera.Define(s,camera_path);cam.AddTransformOp().Set(Gf.Matrix4d(local.T.tolist()));cam.CreateFocalLengthAttr(13.5);cam.CreateHorizontalApertureAttr(20.955);cam.CreateVerticalApertureAttr(15.71625);cam.CreateClippingRangeAttr(Gf.Vec2f(.03,3.))
# Lens-marker geometry is intentionally omitted: it must not occlude the sensor.
s.GetRootLayer().Save()
config=dict(source_plan=str(R/'work/backward_elbow_20261105/plan.json'),scene=str(W/'head_vision_pickup_v02.usda'),robot_root_world_matrix=p['robot_root_world_matrix'],board_path=p['board_path'],counter_path=p['counter_path'],knife_path=p['tool_path'],camera_path=camera_path,camera_world_matrix=C.tolist(),camera_eye_world_m=eye.tolist(),board_centre_world_m=board_centre.tolist(),board_world_bounds=[lo.tolist(),hi.tolist()],abdomen_centre_world_m=centre.tolist(),body_forward_world=forward.tolist(),board_lateral_offset_m=float((board_centre-centre)@lateral),unsupported_board_samples=unsupported,filter_overrides=cleared,knife_pose_xyzw=translation.tolist()+Rotation.from_matrix(rot).as_quat().tolist(),home_rad=p['home_rad'],closed_home_rad=p['closed_home_rad'],head_camera=dict(width=320,height=240,data_types=['rgb','distance_to_image_plane']),no_attachment=True)
(W/'scene_config.json').write_text(json.dumps(config,indent=2));print(json.dumps({k:config[k] for k in ['board_centre_world_m','board_lateral_offset_m','camera_eye_world_m','unsupported_board_samples','filter_overrides']},indent=2))
originals=[R/'work/backward_elbow_20261105/plan.json',Path(p['scene']),R/'rl/grasp_metrics.py',R/'docs/rl/phase3_grasp_criteria.json'];(W/'preserved_sources.json').write_text(json.dumps({str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in originals},indent=2))
