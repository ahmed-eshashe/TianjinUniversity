"""Compose a separate minimal USD using the original robot, knife and board geometry."""
import json
from pathlib import Path
import sys
import numpy as np
from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics, UsdShade

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from grasp_scene_geometry import align_board

SOURCE = ROOT / 'assets/robots/Collected_whole_robot_updated/Collected_whole_robot/whole_robot_2.usd'
OUTPUT = ROOT / 'rl/scene/minimal_benchmark.usda'


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    src = Usd.Stage.Open(str(ROOT / 'work/kitchen_reach.usda'))
    out = Usd.Stage.CreateNew(str(OUTPUT)) if not OUTPUT.exists() else Usd.Stage.Open(str(OUTPUT))
    out.GetRootLayer().Clear()
    UsdGeom.SetStageMetersPerUnit(out, 1.)
    UsdGeom.SetStageUpAxis(out, 'Z')
    root = out.DefinePrim('/dual_ar5_o6', 'Xform')
    root.GetReferences().AddReference(str(SOURCE), '/dual_ar5_o6')
    while True:
        instances = [p for p in Usd.PrimRange(root) if p.IsInstance()]
        if not instances:
            break
        for p in instances:
            p.SetInstanceable(False)
    def material(name, color):
        m = UsdShade.Material.Define(out, '/BenchmarkLooks/' + name)
        sh = UsdShade.Shader.Define(out, str(m.GetPath()) + '/Surface')
        sh.CreateIdAttr('UsdPreviewSurface')
        sh.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
        sh.CreateInput('roughness', Sdf.ValueTypeNames.Float).Set(.7)
        m.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(), 'surface')
        return m
    mats = {n: material(n, c) for n, c in {'robot': (.5, .53, .56), 'board': (.5, .26, .08),
             'counter': (.65, .65, .62), 'blade': (.65, .68, .7), 'handle': (.025, .02, .015)}.items()}
    meta = json.loads((ROOT / 'work/kitchen_reach_metadata.json').read_text())
    seed = json.loads((ROOT / 'work/grasp_stance_cooking_clear.json').read_text())
    home = meta['home_rad'].copy()
    for n, q in zip(meta['right_joint_names'], seed['ready_rad']):
        home[n] = q
    for n in home:
        if n.startswith('left_') or n.startswith('right_rh_'):
            home[n] = 0.
    rm = np.array(UsdGeom.XformCache().GetLocalToWorldTransform(src.GetPrimAtPath('/dual_ar5_o6'))).T
    from scipy.spatial.transform import Rotation
    rm[:2, 3] += seed['root_offset_xy']; rm[:3, :3] = Rotation.from_euler('z', seed['root_yaw_deg'], degrees=True).as_matrix()
    xr = UsdGeom.Xformable(root); xr.ClearXformOpOrder(); xr.AddTransformOp().Set(Gf.Matrix4d(rm.T.tolist()))
    for p in list(Usd.PrimRange(root)):
        if p.IsA(UsdPhysics.CollisionGroup):
            p.GetAttribute('collection:colliders:includeRoot').Set(False)
            p.GetRelationship('collection:colliders:excludes').SetTargets([])
        if p.HasAPI(UsdPhysics.RigidBodyAPI):
            UsdPhysics.RigidBodyAPI(p).CreateVelocityAttr(Gf.Vec3f(0)); UsdPhysics.RigidBodyAPI(p).CreateAngularVelocityAttr(Gf.Vec3f(0))
        if p.IsA(UsdGeom.Mesh):
            UsdShade.MaterialBindingAPI.Apply(p).Bind(mats['robot'])
            for subset in p.GetChildren():
                if subset.IsA(UsdGeom.Subset):
                    UsdShade.MaterialBindingAPI.Apply(subset).Bind(mats['robot'])
            if p.HasAPI(UsdPhysics.CollisionAPI):
                UsdPhysics.MeshCollisionAPI.Apply(p).CreateApproximationAttr('convexHull')
        if p.IsA(UsdPhysics.RevoluteJoint):
            follower = p.GetRelationship('newton:mimicJoint').HasAuthoredTargets()
            arm = '_AR5_' in p.GetName()
            d = UsdPhysics.DriveAPI.Apply(p, 'angular')
            d.CreateStiffnessAttr(2500. if arm else 0. if follower else 3.)
            d.CreateDampingAttr(150. if arm else 0. if follower else .15)
            d.CreateMaxForceAttr(80. if arm else 0. if follower else 1. if 'thumb' in p.GetName() else .3)
            d.CreateTargetPositionAttr(float(np.rad2deg(home[p.GetName()])))
            d.CreateTargetVelocityAttr(0.)
    # Author known attributes offline; PhysX schemas are loaded by Kit at runtime.
    root.CreateAttribute('physxArticulation:enabledSelfCollisions', Sdf.ValueTypeNames.Bool).Set(False)
    root.CreateAttribute('physxArticulation:solverPositionIterationCount', Sdf.ValueTypeNames.Int).Set(32)
    root.CreateAttribute('physxArticulation:solverVelocityIterationCount', Sdf.ValueTypeNames.Int).Set(8)
    cache = UsdGeom.XformCache()
    paths = ['/Indoor/RZ/SM_YZ_CF_10', '/Indoor/RZ/SM_kitchen_Board', meta['knife_path']]
    transforms = {p: np.array(cache.GetLocalToWorldTransform(src.GetPrimAtPath(p))).T for p in paths}
    boardp, tablep = paths[1], paths[0]
    transforms[boardp], error = align_board(np.array(UsdGeom.Mesh(src.GetPrimAtPath(boardp)).GetPointsAttr().Get()), transforms[boardp],
        np.array(UsdGeom.Mesh(src.GetPrimAtPath(tablep)).GetPointsAttr().Get()), transforms[tablep])
    # Centre the existing knife over the board, preserving its original scale and yaw.
    bp = np.array(UsdGeom.Mesh(src.GetPrimAtPath(boardp)).GetPointsAttr().Get())
    bw = bp @ transforms[boardp][:3, :3].T + transforms[boardp][:3, 3]
    knife_path = meta['knife_path']; kp = np.array(UsdGeom.Mesh(src.GetPrimAtPath(knife_path)).GetPointsAttr().Get())
    kw = kp @ transforms[knife_path][:3, :3].T + transforms[knife_path][:3, 3]
    transforms[knife_path][:2, 3] += (bw.min(0)[:2] + bw.max(0)[:2]) / 2 - (kw.min(0)[:2] + kw.max(0)[:2]) / 2
    transforms[knife_path][2, 3] += bw[:, 2].max() + .003 - kw[:, 2].min()
    provenance = []
    for path in paths:
        orig = UsdGeom.Mesh(src.GetPrimAtPath(path)); mesh = UsdGeom.Mesh.Define(out, path)
        for attr in ['points', 'faceVertexCounts', 'faceVertexIndices', 'normals', 'subdivisionScheme', 'extent']:
            a = orig.GetPrim().GetAttribute(attr)
            if a and a.Get() is not None:
                mesh.GetPrim().CreateAttribute(attr, a.GetTypeName()).Set(a.Get())
        mesh.SetNormalsInterpolation(orig.GetNormalsInterpolation())
        UsdGeom.Xformable(mesh).AddTransformOp().Set(Gf.Matrix4d(transforms[path].T.tolist()))
        UsdPhysics.CollisionAPI.Apply(mesh.GetPrim()).CreateCollisionEnabledAttr(path != knife_path)
        UsdPhysics.MeshCollisionAPI.Apply(mesh.GetPrim()).CreateApproximationAttr('none' if path != knife_path else 'convexHull')
        UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mats['blade' if path == knife_path else 'board' if path == boardp else 'counter'])
        for child in orig.GetPrim().GetChildren():
            if child.IsA(UsdGeom.Subset):
                subset = UsdGeom.Subset.Define(out, path + '/' + child.GetName())
                subset.CreateElementTypeAttr('face'); subset.CreateIndicesAttr(UsdGeom.Subset(child).GetIndicesAttr().Get())
                if path == knife_path:
                    UsdShade.MaterialBindingAPI.Apply(subset.GetPrim()).Bind(mats['handle' if child.GetName() == 'Section2' else 'blade'])
        provenance.append({'path': path, 'original_stack': [{'layer': x.layer.identifier, 'path': str(x.path)} for x in orig.GetPrim().GetPrimStack()], 'point_count': len(orig.GetPointsAttr().Get())})
    knife = out.GetPrimAtPath(knife_path)
    UsdPhysics.RigidBodyAPI.Apply(knife).CreateKinematicEnabledAttr(False)
    UsdPhysics.MassAPI.Apply(knife).CreateMassAttr(.25)
    pts = np.array(UsdGeom.Mesh(knife).GetPointsAttr().Get()); ids = np.array(UsdGeom.Mesh(knife).GetFaceVertexIndicesAttr().Get()); counts = np.array(UsdGeom.Mesh(knife).GetFaceVertexCountsAttr().Get()); offsets = np.r_[0, np.cumsum(counts)]
    for name, sections in [('Handle', ['Section2']), ('Blade', ['Section0', 'Section1'])]:
        faces = np.concatenate([np.array(UsdGeom.Subset(src.GetPrimAtPath(knife_path + '/' + n)).GetIndicesAttr().Get()) for n in sections])
        used, remap = np.unique(np.concatenate([ids[offsets[f]:offsets[f + 1]] for f in faces]), return_inverse=True)
        mesh = UsdGeom.Mesh.Define(out, knife_path + '/Collision' + name)
        mesh.CreatePointsAttr(pts[used].tolist()); mesh.CreateFaceVertexCountsAttr(counts[faces].tolist()); mesh.CreateFaceVertexIndicesAttr(remap.tolist()); mesh.CreateVisibilityAttr('invisible')
        UsdPhysics.CollisionAPI.Apply(mesh.GetPrim()); UsdPhysics.MeshCollisionAPI.Apply(mesh.GetPrim()).CreateApproximationAttr('convexHull')
    out.GetRootLayer().Save()
    manifest = {'source': str(SOURCE), 'derived_scene': str(OUTPUT), 'provenance': provenance, 'board_alignment_error_deg': error,
                'home_rad': home, 'knife_path': knife_path, 'board_path': boardp, 'counter_path': tablep,
                'knife_handle_local': meta['knife_handle_local'], 'board_world_bounds': [bw.min(0).tolist(), bw.max(0).tolist()],
                'knife_initial_world_matrix': transforms[knife_path].tolist(), 'robot_root_world_matrix': rm.tolist(),
                'source_assets_modified': False, 'knife_count': 1, 'knife_initially_over_board_centre': True,
                'self_collision': False, 'limitations': ['Self-collision disabled, resource benchmark only; Phase 3 must resolve it', 'Contact material and dynamics not hardware calibrated', 'Core World CPU PhysX harness, not a completed Isaac Lab RL task']}
    (ROOT / 'rl/scene/manifest.json').write_text(json.dumps(manifest, indent=2))
    print(json.dumps({'scene': str(OUTPUT), 'prim_count': len(list(out.Traverse())), 'board_error_deg': error, 'knife_count': 1}))


if __name__ == '__main__':
    main()
