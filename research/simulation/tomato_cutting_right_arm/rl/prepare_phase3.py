"""Separate physical-task layer: original shapes, explicit provisional dynamics, self collisions."""
import json
from pathlib import Path
import numpy as np
from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics, UsdShade
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
import trimesh

ROOT = Path(__file__).resolve().parents[1]


def main():
    target = ROOT/'rl/scene/phase3.usda'
    s = Usd.Stage.CreateNew(str(target)) if not target.exists() else Usd.Stage.Open(str(target))
    s.GetRootLayer().Clear()
    s.GetRootLayer().subLayerPaths = [str(ROOT/'rl/scene/minimal_benchmark.usda')]
    meta = json.loads((ROOT/'rl/scene/manifest.json').read_text())
    root = s.GetPrimAtPath('/dual_ar5_o6')
    root.GetAttribute('physxArticulation:enabledSelfCollisions').Set(True)
    home=meta['home_rad'].copy()
    # Offline convex intersection search found the former shoulder posture intersecting the torso.
    home['right_AR5_5_07R_W4C4A2_joint_2']+=.3
    UsdPhysics.DriveAPI(s.GetPrimAtPath('/dual_ar5_o6/Physics/right_AR5_5_07R_W4C4A2_joint_2'),'angular').CreateTargetPositionAttr(float(np.rad2deg(home['right_AR5_5_07R_W4C4A2_joint_2'])))
    # Only physically connected joint neighbours are excluded. All other pairs remain enabled.
    neighbours=[]; joints=[]
    for p in Usd.PrimRange(root):
        if p.IsA(UsdPhysics.Joint):
            j=UsdPhysics.Joint(p); j.CreateCollisionEnabledAttr(False)
            pair=[str(x) for rel in [j.GetBody0Rel(),j.GetBody1Rel()] for x in rel.GetTargets()]
            if len(pair)==2:
                neighbours.append(pair)
                joints.append((pair,p.IsA(UsdPhysics.FixedJoint)))
        if p.HasAPI(UsdPhysics.RigidBodyAPI):
            p.AddAppliedSchema('PhysxContactReportAPI')
            p.CreateAttribute('physxContactReport:threshold',Sdf.ValueTypeNames.Float).Set(0.)
        if p.IsA(UsdGeom.Mesh) and p.HasAPI(UsdPhysics.CollisionAPI) and '/right_rh_' not in str(p.GetPath()) and '/left_lh_' not in str(p.GetPath()):
            # A single convex hull fills wrist and shoulder clearances. Keep source surfaces and decompose.
            UsdPhysics.MeshCollisionAPI.Apply(p).CreateApproximationAttr('convexDecomposition')
            p.AddAppliedSchema('PhysxConvexDecompositionCollisionAPI')
            p.CreateAttribute('physxConvexDecompositionCollision:maxConvexHulls',Sdf.ValueTypeNames.Int).Set(32)
            p.CreateAttribute('physxConvexDecompositionCollision:hullVertexLimit',Sdf.ValueTypeNames.Int).Set(64)
    # Fixed TCP/adapter/base links can separate two collision bodies in the USD tree.
    # Expand the standard adjacent-joint exclusion through welded assemblies only.
    parent={x:x for pair,fixed in joints for x in pair}
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]];x=parent[x]
        return x
    for pair,fixed in joints:
        if fixed:parent[find(pair[1])]=find(pair[0])
    adjacent={frozenset((find(a),find(b))) for (a,b),fixed in joints if not fixed}
    rigid=[str(p.GetPath()) for p in Usd.PrimRange(root) if p.HasAPI(UsdPhysics.RigidBodyAPI)]
    filtered=[]
    for i,a in enumerate(rigid):
        for b in rigid[i+1:]:
            ca,cb=find(a),find(b)
            if ca==cb or frozenset((ca,cb)) in adjacent:
                UsdPhysics.FilteredPairsAPI.Apply(s.GetPrimAtPath(a)).CreateFilteredPairsRel().AddTarget(b)
                filtered.append({'a':a,'b':b,'reason':'same welded assembly' if ca==cb else 'adjacent movable joint after welding fixed links'})
    mat=UsdShade.Material.Define(s,'/Phase3ContactMaterial')
    pm=UsdPhysics.MaterialAPI.Apply(mat.GetPrim())
    pm.CreateStaticFrictionAttr(.8); pm.CreateDynamicFrictionAttr(.6); pm.CreateRestitutionAttr(0.)
    for p in s.Traverse():
        if p.HasAPI(UsdPhysics.CollisionAPI) and UsdPhysics.CollisionAPI(p).GetCollisionEnabledAttr().Get():
            UsdShade.MaterialBindingAPI.Apply(p).Bind(mat,UsdShade.Tokens.weakerThanDescendants,'physics')
            p.AddAppliedSchema('PhysxCollisionAPI')
            p.CreateAttribute('physxCollision:contactOffset',Sdf.ValueTypeNames.Float).Set(.002)
            p.CreateAttribute('physxCollision:restOffset',Sdf.ValueTypeNames.Float).Set(0.)
    knife=s.GetPrimAtPath(meta['knife_path']); cache=UsdGeom.XformCache()
    matrix=np.array(cache.GetLocalToWorldTransform(knife)).T
    scale=float(np.linalg.norm(matrix[:3,0]))
    assert np.allclose(np.linalg.norm(matrix[:3,:3],axis=0),scale)
    # Bake uniform scale into a derived knife copy so mass/COM/inertia have unambiguous metre units.
    for p in Usd.PrimRange(knife):
        if p.IsA(UsdGeom.Mesh):
            m=UsdGeom.Mesh(p); v=np.array(m.GetPointsAttr().Get())*scale
            m.GetPointsAttr().Set(v.tolist())
            m.GetExtentAttr().Set([Gf.Vec3f(*v.min(0).tolist()),Gf.Vec3f(*v.max(0).tolist())])
    matrix[:3,:3]/=scale
    x=UsdGeom.Xformable(knife);x.ClearXformOpOrder();x.AddTransformOp(opSuffix='phase3').Set(Gf.Matrix4d(matrix.T.tolist()))
    components=[]
    for name,mass in [('Handle',.10),('Blade',.15)]:
        pts=np.array(UsdGeom.Mesh(s.GetPrimAtPath(str(knife.GetPath())+'/Collision'+name)).GetPointsAttr().Get())
        hull=trimesh.convex.convex_hull(pts); hull.density=mass/hull.volume
        components.append((mass,hull.center_mass,hull.moment_inertia))
    com=sum(m*c for m,c,i in components)/.25
    inertia=sum(i+m*((d@d)*np.eye(3)-np.outer(d,d)) for m,c,i in components for d in [c-com])
    eig,axes=np.linalg.eigh(inertia)
    if np.linalg.det(axes)<0:axes[:,0]*=-1
    quat=Rotation.from_matrix(axes).as_quat()
    ma=UsdPhysics.MassAPI.Apply(knife);ma.CreateMassAttr(.25)
    ma.CreateCenterOfMassAttr(Gf.Vec3f(*com));ma.CreateDiagonalInertiaAttr(Gf.Vec3f(*eig))
    ma.CreatePrincipalAxesAttr(Gf.Quatf(float(quat[3]),Gf.Vec3f(*quat[:3])))
    knife.AddAppliedSchema('PhysxRigidBodyAPI')
    knife.CreateAttribute('physxRigidBody:enableCCD',Sdf.ValueTypeNames.Bool).Set(True)
    knife.CreateAttribute('physxRigidBody:sleepThreshold',Sdf.ValueTypeNames.Float).Set(0.)
    knife.AddAppliedSchema('PhysxContactReportAPI')
    knife.CreateAttribute('physxContactReport:threshold',Sdf.ValueTypeNames.Float).Set(0.)
    s.GetRootLayer().Save()
    points=np.array(UsdGeom.Mesh(knife).GetPointsAttr().Get())
    report={'scene':str(target),'knife_mass_kg':.25,'mass_assumption':'provisional: 0.10 kg handle, 0.15 kg blade; not measured hardware',
        'knife_dimensions_local_m':np.ptp(points,axis=0).tolist(),'knife_com_local_m':com.tolist(),
        'knife_inertia_kg_m2':inertia.tolist(),'principal_inertia_kg_m2':eig.tolist(),
        'inertia_positive_and_triangle_inequality':bool(min(eig)>0 and max(eig)<=sum(eig)-max(eig)),
        'friction':{'static':.8,'dynamic':.6,'restitution':0.,'calibrated':False},
        'self_collision_enabled':True,'connected_neighbour_pairs':neighbours,
        'fixed_assembly_and_adjacent_filtered_pairs':filtered,
        'home_rad':home,'ready_change':'Right shoulder joint 2 +0.3 rad, separate Phase 3 reset only; clears torso intersection',
        'knife_scale_baked':scale,'handle_centre_local_m':(np.array(meta['knife_handle_local'])*scale).tolist(),
        'knife_initial_pose_xyzw':[*matrix[:3,3],*Rotation.from_matrix(matrix[:3,:3]).as_quat()],
        'board_bounds_m':meta['board_world_bounds'],'source_assets_modified':False,
        'limitations':['No physical mass/friction/actuator calibration','Self-collision must still pass runtime tests','Mechanical flat pickup feasibility not established']}
    (ROOT/'docs/rl/phase3_physics.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='connected_neighbour_pairs'},indent=2))

if __name__=='__main__':main()
