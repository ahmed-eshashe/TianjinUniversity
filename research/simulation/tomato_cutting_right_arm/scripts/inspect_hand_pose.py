from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom,UsdPhysics
from reach_kinematics import ArmKinematics
r=Path(__file__).resolve().parents[1];s=Usd.Stage.Open(str(r/'work/kitchen_reach.usda'));k=ArmKinematics(s);xc=UsdGeom.XformCache()
def bounds(values):
 tf={k.hand_path:np.eye(4)}
 def tr(path):
  if path in tf:return tf[path]
  parent,child,a,b,axis,name=k.by_child[path];rot=np.eye(4)
  if axis is not None:rot[:3,:3]=Rotation.from_rotvec(axis*np.deg2rad(values.get(name,0))).as_matrix()
  tf[path]=tr(parent)@a@rot@b;return tf[path]
 for p in Usd.PrimRange(s.GetPrimAtPath(k.hand_path)):
  if not p.IsA(UsdGeom.Mesh):continue
  body=p
  while not body.HasAPI(UsdPhysics.RigidBodyAPI):body=body.GetParent()
  rel=np.linalg.inv(np.array(xc.GetLocalToWorldTransform(body)).T)@np.array(xc.GetLocalToWorldTransform(p)).T
  mat=tr(str(body.GetPath()))@rel;v=np.array(UsdGeom.Mesh(p).GetPointsAttr().Get())@mat[:3,:3].T+mat[:3,3]
  if 'distal' in body.GetName() or 'hand_base' in body.GetName():print(body.GetName(),v.min(0).round(3),v.max(0).round(3))
for angle in [0,60,85]:
 vals={n:angle for n in k.home if n.startswith('right_rh_')};vals.update({'right_rh_thumb_cmc_yaw':60,'right_rh_thumb_cmc_pitch':30,'right_rh_thumb_ip':50})
 print('ANGLES',angle);bounds(vals)
