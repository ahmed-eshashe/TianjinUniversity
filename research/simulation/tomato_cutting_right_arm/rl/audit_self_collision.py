"""Offline convex intersection audit at the native reset posture; never moves a simulator."""
import json
from pathlib import Path
import sys
import numpy as np
from pxr import Usd, UsdGeom, UsdPhysics
from scipy.optimize import linprog
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from reach_kinematics import ArmKinematics


def main():
    stage=Usd.Stage.Open(str(ROOT/'rl/scene/phase3.usda'))
    k=ArmKinematics(stage); cache=UsdGeom.XformCache()
    home=json.loads((ROOT/'rl/scene/manifest.json').read_text())['home_rad']
    transforms={'/dual_ar5_o6':k.root}
    def transform(path):
        if path in transforms:return transforms[path]
        if path in k.by_child:
            parent,child,a,b,axis,name=k.by_child[path]
            rot=np.eye(4)
            if axis is not None:rot[:3,:3]=Rotation.from_rotvec(axis*home.get(name,0.)).as_matrix()
            transforms[path]=transform(parent)@a@rot@b
        else:
            p=stage.GetPrimAtPath(path); parent=str(p.GetParent().GetPath())
            authored=np.array(cache.GetLocalToWorldTransform(p)).T
            ap=np.array(cache.GetLocalToWorldTransform(p.GetParent())).T
            transforms[path]=transform(parent)@np.linalg.inv(ap)@authored
        return transforms[path]
    geometry=[]
    for p in Usd.PrimRange(stage.GetPrimAtPath('/dual_ar5_o6')):
        if not p.IsA(UsdGeom.Mesh) or not p.HasAPI(UsdPhysics.CollisionAPI):continue
        if not UsdPhysics.CollisionAPI(p).GetCollisionEnabledAttr().Get():continue
        body=p
        while not body.HasAPI(UsdPhysics.RigidBodyAPI):body=body.GetParent()
        path=str(body.GetPath())
        rel=np.linalg.inv(np.array(cache.GetLocalToWorldTransform(body)).T)@np.array(cache.GetLocalToWorldTransform(p)).T
        mat=transform(path)@rel
        vertices=np.array(UsdGeom.Mesh(p).GetPointsAttr().Get())@mat[:3,:3].T+mat[:3,3]
        geometry.append((path,vertices,ConvexHull(vertices).equations))
    neighbours={frozenset((j[0],j[1])) for j in k.joints.values() if j[0]}
    overlaps=[]
    for i,(pa,a,ea) in enumerate(geometry):
        for pb,b,eb in geometry[i+1:]:
            if pa==pb or frozenset((pa,pb)) in neighbours:continue
            if np.any(a.max(0)<b.min(0)) or np.any(b.max(0)<a.min(0)):continue
            eq=np.r_[ea,eb]
            fit=linprog([0,0,0,-1],A_ub=np.c_[eq[:,:3],np.ones(len(eq))],b_ub=-eq[:,3],
                        bounds=[(None,None)]*3+[(0,None)],method='highs')
            if fit.success and fit.x[3]>.0005:
                overlaps.append({'body_a':pa,'body_b':pb,'intersection_inscribed_radius_m':float(fit.x[3]),'point_world_m':fit.x[:3].tolist()})
    result={'posture':'Phase 2 ready / left parked zero','nonadjacent_overlap_count':len(overlaps),
            'overlaps':overlaps,'collision_mesh_count':len(geometry),
            'method':'Convex mesh intersection LP; adjacent joints excluded; not a runtime contact force',
            'passed':not overlaps}
    (ROOT/'docs/rl/phase3_self_collision_geometry.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
