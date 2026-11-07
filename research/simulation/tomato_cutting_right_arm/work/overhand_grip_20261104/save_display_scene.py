from pathlib import Path
import sys,json,numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom
r=Path(__file__).resolve().parents[2];w=Path(__file__).resolve().parent;sys.path[:0]=[str(r/'scripts'),str(r/'rl')]
from reach_kinematics import ArmKinematics
from tomato_fixed_mount_scene import matrix
p=json.loads((w/'overhand_plan_v06.json').read_text());k=ArmKinematics(Usd.Stage.Open(p['scene']));tf={'/dual_ar5_o6':k.root};home=p['home_rad']
def tr(path):
 if path in tf:return tf[path]
 parent,child,a,b,axis,name=k.by_child[path];rot=np.eye(4)
 if axis is not None:rot[:3,:3]=Rotation.from_rotvec(axis*home.get(name,0)).as_matrix()
 tf[path]=tr(parent)@a@rot@b;return tf[path]
scene=w/'overhand_ready.usda';s=Usd.Stage.CreateNew(str(scene));s.GetRootLayer().subLayerPaths=[p['scene']];UsdGeom.SetStageUpAxis(s,UsdGeom.Tokens.z);UsdGeom.SetStageMetersPerUnit(s,1.0)
for path in sorted(k.by_child,key=lambda x:x.count('/')):
 prim=s.GetPrimAtPath(path);parent=np.array(UsdGeom.XformCache().GetLocalToWorldTransform(prim.GetParent())).T;matrix(UsdGeom.Xformable(prim),np.linalg.inv(parent)@tr(path))
s.GetRootLayer().Save();p['scene']=str(scene);(w/'overhand_ready_plan.json').write_text(json.dumps(p,indent=2));print(scene)
