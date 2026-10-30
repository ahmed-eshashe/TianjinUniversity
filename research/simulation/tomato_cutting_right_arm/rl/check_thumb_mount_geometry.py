"""Read-only original triangle-mesh overlap diagnostic; no collision exclusions or simulation."""
import json,sys
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom,UsdPhysics
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from reach_kinematics import ArmKinematics
s=Usd.Stage.Open(str(ROOT/'rl/scene/phase3_grasp.usda'));k=ArmKinematics(s);xc=UsdGeom.XformCache();meshes={}
for p in Usd.PrimRange(s.GetPrimAtPath(k.hand_path)):
 if not p.IsA(UsdGeom.Mesh):continue
 body=p
 while body and not body.HasAPI(UsdPhysics.RigidBodyAPI):body=body.GetParent()
 if not body or body.GetName() not in ['right_rh_hand_base_link','right_rh_thumb_metacarpals']:continue
 m=UsdGeom.Mesh(p);v=np.array(m.GetPointsAttr().Get());ids=np.array(m.GetFaceVertexIndicesAttr().Get());counts=np.array(m.GetFaceVertexCountsAttr().Get());off=np.r_[0,np.cumsum(counts)]
 faces=[]
 for i,n in enumerate(counts):
  ix=ids[off[i]:off[i+1]]
  faces.extend([[ix[0],ix[j],ix[j+1]] for j in range(1,n-1)])
 matrix=np.linalg.inv(np.array(xc.GetLocalToWorldTransform(body)).T)@np.array(xc.GetLocalToWorldTransform(p)).T
 meshes[body.GetName()]=(str(body.GetPath()),trimesh.Trimesh(v@matrix[:3,:3].T+matrix[:3,3],faces,process=True))
palm=meshes['right_rh_hand_base_link'][1];path,thumb=meshes['right_rh_thumb_metacarpals'];results=[]
for yaw,pitch in [(0.,0.),(.86,.14),(.86,.30),(.87,.49)]:
 values={'right_rh_thumb_cmc_yaw':yaw,'right_rh_thumb_cmc_pitch':pitch}
 transforms={k.hand_path:np.eye(4)}
 def tr(path):
  if path in transforms:return transforms[path]
  parent,child,a,b,axis,name=k.by_child[path];rot=np.eye(4)
  if axis is not None:rot[:3,:3]=Rotation.from_rotvec(axis*values.get(name,0.)).as_matrix()
  transforms[path]=tr(parent)@a@rot@b;return transforms[path]
 t=tr(path);v=thumb.vertices@t[:3,:3].T+t[:3,3];subset=v[::max(1,len(v)//500)]
 inside=palm.contains(subset)
 # Signed-distance interpretation is conditional on a watertight mesh.
 distance=trimesh.proximity.signed_distance(palm,subset)
 results.append({'yaw_rad':yaw,'pitch_rad':pitch,'sampled_thumb_vertices':len(subset),
  'thumb_vertices_inside_palm':int(inside.sum()),'max_positive_signed_distance_m':float(distance.max())})
report={'scope':'Original triangle-mesh samples in palm coordinates; no authored geometry or filters changed',
 'palm_watertight':bool(palm.is_watertight),'thumb_watertight':bool(thumb.is_watertight),
 'palm_faces':len(palm.faces),'thumb_faces':len(thumb.faces),'postures':results,
 'interpretation':'Sampled vertex inclusion is evidence of geometric interference only for closed valid meshes; it does not establish the complete collision-free joint range or hardware geometry.'}
(ROOT/'docs/rl/thumb_mount_geometry_check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
