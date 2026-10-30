"""Create a lightweight, referenced kitchen scene; preserve the kitchen's own knife."""
from pathlib import Path
import json
import numpy as np
from pxr import Usd,UsdGeom,UsdShade,UsdPhysics,Gf,Sdf
from reach_kinematics import ArmKinematics
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/robots/Collected_whole_robot_updated/Collected_whole_robot/whole_robot_2.usd'
KNIFE='/Indoor/RZ/SM_kitchen_knife_02'
out=ROOT/'work/kitchen_reach.usda'
s=Usd.Stage.CreateNew(str(out)) if not out.exists() else Usd.Stage.Open(str(out))
s.GetRootLayer().Clear()
UsdGeom.SetStageMetersPerUnit(s,1);UsdGeom.SetStageUpAxis(s,'Z')
for path in ['/dual_ar5_o6','/Indoor']:
    s.DefinePrim(path,'Xform').GetReferences().AddReference(str(SOURCE),path)
while True:
    inst=[p for p in s.Traverse() if p.IsInstance()]
    if not inst:break
    for p in inst:p.SetInstanceable(False)
kin=ArmKinematics(s)
home={n:float(np.clip(q,*kin.limits[n])) for n,q in kin.home.items()}
# Simple local materials avoid the kitchen's broken MDL shaders and large textures.
def material(name,color,metal=0):
    m=UsdShade.Material.Define(s,'/ReachLooks/'+name);sh=UsdShade.Shader.Define(s,str(m.GetPath())+'/Surface')
    sh.CreateIdAttr('UsdPreviewSurface');sh.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color));sh.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(.6);sh.CreateInput('metallic',Sdf.ValueTypeNames.Float).Set(float(metal));m.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(),'surface');return m
mats={'neutral':material('neutral',(.65,.65,.62)),'wood':material('wood',(.38,.18,.07)), 'metal':material('metal',(.55,.58,.62),.8),'handle':material('handle',(.035,.025,.02)),'white':material('white',(.82,.82,.8))}
for p in list(Usd.PrimRange(s.GetPrimAtPath('/Indoor'))):
    if p.IsValid() and p.IsA(UsdShade.Material):p.SetActive(False)
cache=UsdGeom.BBoxCache(0,['default','render'])
active_colliders=[]
for p in list(s.Traverse()):
    path=str(p.GetPath())
    if path.startswith('/Indoor'):
        if p.IsA(UsdPhysics.Joint):UsdPhysics.Joint(p).CreateJointEnabledAttr(False)
        if p.IsA(UsdGeom.Mesh) and p.HasAPI(UsdPhysics.MeshCollisionAPI):UsdPhysics.MeshCollisionAPI(p).CreateApproximationAttr('none')
        if p.HasAPI(UsdPhysics.RigidBodyAPI):
            b=UsdPhysics.RigidBodyAPI(p);b.CreateRigidBodyEnabledAttr(path==KNIFE);b.CreateVelocityAttr(Gf.Vec3f(0));b.CreateAngularVelocityAttr(Gf.Vec3f(0))
        if p.HasAPI(UsdPhysics.CollisionAPI):UsdPhysics.CollisionAPI(p).CreateCollisionEnabledAttr(False)
        if p.IsA(UsdGeom.Mesh):
            bound=cache.ComputeWorldBound(p).ComputeAlignedRange();lo=np.array(bound.GetMin());hi=np.array(bound.GetMax())
            near=np.all(hi>[-3.05,-2.3,.5]) and np.all(lo<[-1.0,-.8,1.8]) and np.max(hi-lo)<3.1
            if near:
                UsdPhysics.CollisionAPI.Apply(p).CreateCollisionEnabledAttr(True)
                UsdPhysics.MeshCollisionAPI.Apply(p).CreateApproximationAttr('convexHull' if path==KNIFE else 'none')
                active_colliders.append(path)
            key='wood' if 'Board' in path else 'metal' if ('knife' in path or 'Salt' in path) else 'white' if ('appliance' in path or 'CF_' in path) else 'neutral'
            UsdShade.MaterialBindingAPI.Apply(p).Bind(mats[key])
            for subset in p.GetChildren():
                if subset.IsA(UsdGeom.Subset):
                    subkey='handle' if 'knife' in path and subset.GetName()=='Section2' else key
                    UsdShade.MaterialBindingAPI.Apply(subset).Bind(mats[subkey])
    elif path.startswith('/dual_ar5_o6'):
        if p.IsA(UsdPhysics.CollisionGroup):
            p.GetAttribute('collection:colliders:includeRoot').Set(False)
            p.GetRelationship('collection:colliders:excludes').SetTargets([])
        if p.HasAPI(UsdPhysics.RigidBodyAPI):
            UsdPhysics.RigidBodyAPI(p).CreateVelocityAttr(Gf.Vec3f(0));UsdPhysics.RigidBodyAPI(p).CreateAngularVelocityAttr(Gf.Vec3f(0))
        if p.HasAPI(UsdPhysics.CollisionAPI) and p.IsA(UsdGeom.Mesh):UsdPhysics.MeshCollisionAPI.Apply(p).CreateApproximationAttr('convexHull')
        if p.IsA(UsdPhysics.RevoluteJoint):
            d=UsdPhysics.DriveAPI.Apply(p,'angular');arm='_AR5_' in p.GetName()
            d.CreateStiffnessAttr(2500 if arm else 50);d.CreateDampingAttr(150 if arm else 2);d.CreateTargetVelocityAttr(0);d.CreateTargetPositionAttr(float(np.rad2deg(home[p.GetName()])))
art=s.GetPrimAtPath('/dual_ar5_o6')
art.CreateAttribute('physxArticulation:enabledSelfCollisions',Sdf.ValueTypeNames.Bool).Set(False)
art.CreateAttribute('physxArticulation:solverPositionIterationCount',Sdf.ValueTypeNames.Int).Set(16)
art.CreateAttribute('physxArticulation:solverVelocityIterationCount',Sdf.ValueTypeNames.Int).Set(4)
knife=s.GetPrimAtPath(KNIFE)
UsdPhysics.MassAPI.Apply(knife).CreateMassAttr(.25)
UsdPhysics.RigidBodyAPI(knife).CreateKinematicEnabledAttr(False)
# Derive the handle centre from the existing knife's handle geometry subset.
mesh=UsdGeom.Mesh(knife);pts=np.array(mesh.GetPointsAttr().Get());ix=np.array(mesh.GetFaceVertexIndicesAttr().Get());cnt=np.array(mesh.GetFaceVertexCountsAttr().Get());offset=np.r_[0,np.cumsum(cnt)]
faces=UsdGeom.Subset(s.GetPrimAtPath(KNIFE+'/Section2')).GetIndicesAttr().Get();v=pts[np.unique(np.concatenate([ix[offset[f]:offset[f+1]] for f in faces]))]
handle=(v.min(0)+v.max(0))/2
sources=[{'layer':x.layer.identifier,'prim':str(x.path)} for x in knife.GetPrimStack()]
assert any(x['prim']=='/Root/RZ/SM_kitchen_knife_02' and x['layer'].endswith('/Indoor.usd') for x in sources)
meta={'knife_path':KNIFE,'knife_source_stack':sources,'knife_handle_local':handle.tolist(),'home_rad':home,'right_joint_names':kin.names,'hand_path':kin.hand_path,'active_kitchen_colliders':active_colliders,'simplified_kitchen_materials':True,'self_collision':False}
(ROOT/'work/kitchen_reach_metadata.json').write_text(json.dumps(meta,indent=2));s.GetRootLayer().Save()
print(json.dumps({'knife_path':KNIFE,'handle_local':handle.tolist(),'active_colliders':active_colliders,'home_right_deg':np.rad2deg([home[n] for n in kin.names]).tolist(),'palm_home':kin.pose(np.array([home[n] for n in kin.names]))[0].tolist()},indent=2))
