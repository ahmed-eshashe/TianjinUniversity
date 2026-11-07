"""Conservative convex-hull overlap check for right arm versus left arm and torso."""
from pathlib import Path
import json
import numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from scipy.optimize import linprog
from pxr import Usd,UsdGeom,UsdPhysics
from reach_kinematics import ArmKinematics
ROOT=Path(__file__).resolve().parents[2]
def check(qright,left_zero=False,root_matrix=None,hand_values=None):
 s=Usd.Stage.Open(str(ROOT/'work/kitchen_reach.usda'));kin=ArmKinematics(s);meta=json.loads((ROOT/'work/kitchen_reach_metadata.json').read_text());values=meta['home_rad'].copy();values.update(zip(kin.names,qright))
 for n in values:
  if n.startswith('right_rh_') or (left_zero and n.startswith('left_')):values[n]=0.
 if hand_values:values.update(hand_values)
 if root_matrix is not None:kin.root=np.array(root_matrix)
 transforms={'/dual_ar5_o6':kin.root}
 def trans(path):
  if path in transforms:return transforms[path]
  parent,child,a,b,axis,name=kin.by_child[path];rot=np.eye(4)
  if axis is not None:rot[:3,:3]=Rotation.from_rotvec(axis*values[name]).as_matrix()
  transforms[path]=trans(parent)@a@rot@b;return transforms[path]
 xc=UsdGeom.XformCache();points={}
 for p in s.Traverse():
  if not str(p.GetPath()).startswith('/dual_ar5_o6'):continue
  if p.IsA(UsdGeom.Mesh):v=np.array(UsdGeom.Mesh(p).GetPointsAttr().Get())
  elif p.IsA(UsdGeom.Cube):
   size=UsdGeom.Cube(p).GetSizeAttr().Get()/2;v=np.array([[x,y,z] for x in [-size,size] for y in [-size,size] for z in [-size,size]])
  else:continue
  body=p
  while body and not body.HasAPI(UsdPhysics.RigidBodyAPI):body=body.GetParent()
  if not body:continue
  name=str(body.GetPath())
  if name not in kin.by_child:continue
  rel=np.linalg.inv(np.array(xc.GetLocalToWorldTransform(body)).T)@np.array(xc.GetLocalToWorldTransform(p)).T
  m=trans(name)@rel;world=v@m[:3,:3].T+m[:3,3];points.setdefault(name,[]).append(world)
 hulls={}
 for n,ps in points.items():
  v=np.concatenate(ps);h=ConvexHull(v);hulls[n]=(v.min(0),v.max(0),h.equations)
 overlaps=[]
 for n,(lo,hi,eq) in hulls.items():
  if not n.split('/')[-1].startswith('right_'):continue
  for other,(ol,oh,oe) in hulls.items():
   if not (other.split('/')[-1].startswith('left_') or other.split('/')[-1]=='torso_base_link'):continue
   if 'torso' in other.split('/')[-1] and any(n.endswith(x) for x in ['_base','_link1']):continue
   if np.any(hi<ol) or np.any(oh<lo):continue
   # Maximum inscribed ball radius: positive radius means hull volume overlap.
   e=np.concatenate([eq,oe]);a=np.c_[e[:,:3],np.ones(len(e))]
   res=linprog([0,0,0,-1],A_ub=a,b_ub=-e[:,3],bounds=[(None,None)]*3+[(None,None)],method='highs')
   if res.success and res.x[3]>.002:overlaps.append((n.split('/')[-1],other.split('/')[-1],float(res.x[3])))
 return overlaps
if __name__=='__main__':
 s=Usd.Stage.Open(str(ROOT/'work/kitchen_reach.usda'));kin=ArmKinematics(s);seed=json.loads((ROOT/'work/reach_seed.json').read_text());report=json.loads((ROOT/'logs/kitchen_reach_report.json').read_text())
 q,e,a=kin.solve(np.array(report['palm_target_m']),np.array(seed['orientation']),np.array(seed['ready_rad']))
 print('AUTHORED_LEFT',check(q));print('ZERO_LEFT',check(q,True))
