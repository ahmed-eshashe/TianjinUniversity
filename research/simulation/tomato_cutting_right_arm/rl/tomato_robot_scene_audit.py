"""Audit SI scene frames and prepare a disposable local-origin cutting scene.

This does not attach the knife, command a robot, or qualify a grasp.
"""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from pxr import Gf, Usd, UsdGeom, UsdPhysics

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from reach_kinematics import ArmKinematics


def prepare(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    original = ROOT / 'rl/scene/phase3.usda'
    stage = Usd.Stage.Open(str(original))
    manifest = json.loads((ROOT / 'rl/scene/manifest.json').read_text())
    physics = json.loads((ROOT / 'docs/rl/phase3_physics.json').read_text())
    blade = json.loads((ROOT / 'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())
    source_paths = [original, ROOT / 'rl/scene/minimal_benchmark.usda',
                    Path(manifest['source']), ROOT / 'docs/rl/phase3_physics.json',
                    ROOT / 'rl/scene/manifest.json',
                    ROOT / 'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json']
    pins = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    points = np.asarray(UsdGeom.Mesh(stage.GetPrimAtPath(manifest['knife_path'] + '/CollisionBlade')).GetPointsAttr().Get())
    faces = np.asarray(UsdGeom.Mesh(stage.GetPrimAtPath(manifest['knife_path'] + '/CollisionBlade')).GetFaceVertexIndicesAttr().Get()).reshape(-1, 3)
    lo, hi = np.asarray(manifest['board_world_bounds'])
    origin = (lo + hi) / 2
    origin[2] = hi[2]
    root_matrix = np.asarray(UsdGeom.XformCache().GetLocalToWorldTransform(stage.GetPrimAtPath('/dual_ar5_o6'))).T
    scene_path = output / 'local_cutting_scene.usda'
    derived = Usd.Stage.CreateNew(str(scene_path)) if not scene_path.exists() else Usd.Stage.Open(str(scene_path))
    derived.GetRootLayer().Clear()
    derived.GetRootLayer().subLayerPaths = [str(original)]
    UsdGeom.SetStageMetersPerUnit(derived, 1.)
    UsdGeom.SetStageUpAxis(derived, 'Z')
    new_root = root_matrix.copy()
    new_root[:3, 3] -= origin
    xform = UsdGeom.Xformable(derived.GetPrimAtPath('/dual_ar5_o6'))
    xform.ClearXformOpOrder()
    xform.AddTransformOp(opSuffix='cuttingLocal').Set(Gf.Matrix4d(new_root.T.tolist()))
    derived.OverridePrim('/Indoor').SetTypeName('Xform')
    xform = UsdGeom.Xformable(derived.GetPrimAtPath('/Indoor'))
    if xform.GetOrderedXformOps():
        raise ValueError('Indoor parent must be an identity frame before rebasing')
    xform.AddTranslateOp(opSuffix='cuttingLocal').Set(Gf.Vec3d(*(-origin)))
    # Newton owns the deformable target. This mesh is a labelled visual only.
    design = json.loads((ROOT / 'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text())
    positions = np.asarray([n['position_m'] for n in design['nodes']]) + [0., 0., .002]
    triangles = np.asarray([tri for piece in design['pieces'] for tri in piece['triangles']])
    target = UsdGeom.Mesh.Define(derived, '/CuttingTargetVisual')
    target.CreatePointsAttr(positions.tolist())
    target.CreateFaceVertexCountsAttr([3] * len(triangles))
    target.CreateFaceVertexIndicesAttr(triangles.ravel().tolist())
    target.CreateDisplayColorAttr([Gf.Vec3f(.75, .05, .025)])
    target.CreateSubdivisionSchemeAttr('none')
    target.GetPrim().SetCustomDataByKey('simulationOwner', 'Newton; visual mesh has no PhysX collider')
    fixture_ids = design['fixture']['node_ids']
    fixture_positions = positions[fixture_ids]
    target_margin = np.minimum(positions[:, :2].min(0) - (lo-origin)[:2], (hi-origin)[:2] - positions[:, :2].max(0))
    cache = UsdGeom.XformCache()
    errors = []
    for path in ['/dual_ar5_o6', manifest['knife_path'], manifest['board_path'], manifest['counter_path']]:
        old = np.asarray(UsdGeom.XformCache().GetLocalToWorldTransform(stage.GetPrimAtPath(path))).T
        new = np.asarray(cache.GetLocalToWorldTransform(derived.GetPrimAtPath(path))).T
        errors.append(float(np.max(np.abs(new[:3, 3] - (old[:3, 3] - origin)))))
        errors.append(float(np.max(np.abs(new[:3, :3] - old[:3, :3]))))
    k = ArmKinematics(derived)
    home = np.asarray([physics['home_rad'][n] for n in k.names])
    palm, orientation = k.pose(home)
    checks = dict(metres_and_z_up=UsdGeom.GetStageMetersPerUnit(derived) == 1. and UsdGeom.GetStageUpAxis(derived) == 'Z',
                  no_composition_errors=not derived.GetCompositionErrors(),
                  robot_rigid_unit_scale=bool(np.allclose(new_root[:3, :3].T @ new_root[:3, :3], np.eye(3), atol=1e-12)),
                  blade_vertices_exact=bool(np.array_equal(points, np.asarray(blade['vertices'], dtype=np.float32))),
                  blade_triangles_exact=bool(np.array_equal(faces, np.asarray(blade['triangles']))),
                  common_origin_preserves_relative_frames=max(errors) < 1e-12,
                  target_inside_board=bool(np.all(target_margin > .02)),
                  visual_target_has_no_duplicate_collider=not target.GetPrim().HasAPI(UsdPhysics.CollisionAPI),
                  fixture_on_bulk_side=bool(np.all(positions[fixture_ids, 0] > design['cut_x_m'])),
                  self_collision_enabled=derived.GetPrimAtPath('/dual_ar5_o6').GetAttribute('physxArticulation:enabledSelfCollisions').Get() is True,
                  no_knife_attachment=not any(any('knife' in str(t).lower() for t in UsdPhysics.Joint(p).GetBody0Rel().GetTargets()+UsdPhysics.Joint(p).GetBody1Rel().GetTargets()) for p in derived.Traverse() if p.IsA(UsdPhysics.Joint)))
    derived.GetRootLayer().Save()
    result = dict(passed=all(checks.values()), checks=checks, scene=str(output / 'local_cutting_scene.usda'),
                  source_sha256=pins, world_to_local_translation_m=(-origin).tolist(),
                  board_local_bounds_m=(np.asarray([lo,hi])-origin).tolist(),
                  target_origin_local_m=[0.,0.,.002], target_support='planned fixed bulk-side nodes from authored fixture; not a left-hand grasp',
                  fixture_node_ids=fixture_ids, fixture_bounds_m=[fixture_positions.min(0).tolist(),fixture_positions.max(0).tolist()],
                  target_minimum_board_edge_margin_m=float(target_margin.min()),
                  blade_float64_export_to_usd_max_error_m=float(np.max(np.abs(points-np.asarray(blade['vertices'])))),
                  maximum_rebase_error_m=max(errors),
                  blade_dimensions_m=np.ptp(points,axis=0).tolist(),
                  ready_palm_local_m=palm.tolist(), ready_palm_rotation=orientation.tolist(),
                  home_rad=physics['home_rad'], robot_root_world_matrix=new_root.tolist(),
                  knife_path=manifest['knife_path'], board_path=manifest['board_path'],counter_path=manifest['counter_path'],
                  limitations=['Offline audit only; native robot motion, fixture and scene reset are not yet qualified.',
                               'Knife mounting method awaits user choice; no attachment or new grasp introduced.',
                               'Existing provisional mass, friction, actuator and collision approximations remain uncalibrated.'])
    result['source_files_unchanged']=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pins.items())
    result['passed'] &= result['source_files_unchanged']
    (output / 'scene_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__ == '__main__':
    result=prepare(ROOT/'runs/offline/robot_scene_20261101_01')
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['passed'] else 1)
