"""Separate grasp layer retaining palm/thumb cavities instead of filling them with convex hulls."""
import json
from pathlib import Path
from pxr import Usd,UsdGeom,UsdPhysics,Sdf
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'rl/scene/phase3_grasp.usda'
stage=Usd.Stage.CreateNew(str(path)) if not path.exists() else Usd.Stage.Open(str(path))
stage.GetRootLayer().Clear();stage.GetRootLayer().subLayerPaths=[str(ROOT/'rl/scene/phase3.usda')]
changed=[]
for p in stage.Traverse():
    if not p.IsA(UsdGeom.Mesh) or not p.HasAPI(UsdPhysics.CollisionAPI):continue
    body=p
    while body and not body.HasAPI(UsdPhysics.RigidBodyAPI):body=body.GetParent()
    if not body:continue
    if body.GetName() in [side+part for side in ['right_rh_','left_lh_'] for part in ['hand_base_link','thumb_metacarpals','thumb_metacarpals_base2']]:
        UsdPhysics.MeshCollisionAPI.Apply(p).CreateApproximationAttr('convexDecomposition')
        p.AddAppliedSchema('PhysxConvexDecompositionCollisionAPI')
        p.CreateAttribute('physxConvexDecompositionCollision:maxConvexHulls',Sdf.ValueTypeNames.Int).Set(32)
        p.CreateAttribute('physxConvexDecompositionCollision:hullVertexLimit',Sdf.ValueTypeNames.Int).Set(64)
        changed.append(str(p.GetPath()))
stage.GetRootLayer().Save()
(ROOT/'docs/rl/grasp_collision_refinement.json').write_text(json.dumps({'derived_layer':str(path),'changed_meshes':changed,
    'source_geometry_changed':False,'new_filtered_pairs':0,'force_limits_changed':False,
    'reason':'Single hull fills concave palm/thumb mounting clearances; preserve authored surface with decomposition',
    'runtime_validation_pending':True},indent=2))
print('Refined',len(changed),'mesh collision approximations')
