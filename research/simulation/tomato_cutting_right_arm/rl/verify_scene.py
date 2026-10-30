"""Check source preservation, minimal-scene provenance and collision structure offline."""
import hashlib
import json
from pathlib import Path
import numpy as np
from pxr import Usd, UsdGeom, UsdPhysics

ROOT = Path(__file__).resolve().parents[1]


def main():
    audit = json.loads((ROOT/'docs/rl/phase1_inventory.json').read_text())
    manifest = json.loads((ROOT/'rl/scene/manifest.json').read_text())
    stage = Usd.Stage.Open(str(ROOT/'rl/scene/minimal_benchmark.usda'))
    source = Usd.Stage.Open(str(ROOT/'work/kitchen_reach.usda'))
    checks = {}
    checks['source_asset_unchanged'] = hashlib.sha256(Path(audit['source']).read_bytes()).hexdigest() == audit['source_sha256']
    checks['accepted_baselines_unchanged'] = all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == sha for p, sha in audit['baseline_sha256'].items())
    checks['metres_and_z_up'] = UsdGeom.GetStageMetersPerUnit(stage) == 1. and UsdGeom.GetStageUpAxis(stage) == 'Z'
    checks['no_composition_errors'] = not stage.GetCompositionErrors()
    paths = [x['path'] for x in manifest['provenance']]
    checks['copied_geometry_matches_source'] = all(np.array_equal(stage.GetPrimAtPath(p).GetAttribute(attr).Get(), source.GetPrimAtPath(p).GetAttribute(attr).Get())
        for p in paths for attr in ['points', 'faceVertexCounts', 'faceVertexIndices'])
    knife_bodies = [str(p.GetPath()) for p in stage.Traverse() if 'knife' in str(p.GetPath()).lower() and p.HasAPI(UsdPhysics.RigidBodyAPI)]
    checks['one_original_named_knife_body'] = knife_bodies == [manifest['knife_path']]
    checks['separate_handle_blade_hulls'] = all(stage.GetPrimAtPath(manifest['knife_path']+'/Collision'+n).HasAPI(UsdPhysics.CollisionAPI) for n in ['Handle', 'Blade'])
    checks['no_knife_attachment'] = all(not any('knife' in str(x).lower() for x in UsdPhysics.Joint(p).GetBody0Rel().GetTargets()+UsdPhysics.Joint(p).GetBody1Rel().GetTargets()) for p in stage.Traverse() if p.IsA(UsdPhysics.Joint))
    checks['parked_left_arm_present'] = any(p.GetName().startswith('left_AR5') and p.HasAPI(UsdPhysics.RigidBodyAPI) for p in stage.Traverse())
    indoor_meshes = [str(p.GetPath()) for p in stage.Traverse() if str(p.GetPath()).startswith('/Indoor') and p.IsA(UsdGeom.Mesh)]
    checks['only_required_kitchen_geometry'] = set(indoor_meshes) == set(paths+[manifest['knife_path']+'/CollisionHandle', manifest['knife_path']+'/CollisionBlade'])
    checks['board_parallel'] = manifest['board_alignment_error_deg'] < .1
    xc = UsdGeom.XformCache(); body = stage.GetPrimAtPath(manifest['knife_path']); mesh = UsdGeom.Mesh(body)
    matrix = np.array(xc.GetLocalToWorldTransform(body)).T
    vertices = np.array(mesh.GetPointsAttr().Get())@matrix[:3,:3].T+matrix[:3,3]
    lo, hi = np.array(manifest['board_world_bounds'])
    centre = (vertices.min(0)+vertices.max(0))/2
    checks['knife_centre_over_board_centre'] = bool(np.linalg.norm(centre[:2]-(lo[:2]+hi[:2])/2)<.001)
    checks['knife_above_board_at_reset'] = bool(0 <= vertices[:,2].min()-hi[2] <= .005)
    checks['knife_initial_extent_inside_board_xy'] = bool(np.all(vertices[:,:2].min(0)>=lo[:2]) and np.all(vertices[:,:2].max(0)<=hi[:2]))
    dimensions = {}
    bbox = UsdGeom.BBoxCache(0, ['default','render'])
    for prim in stage.Traverse():
        if prim.GetName() in ['right_rh_hand_base_link','right_rh_index_proximal','right_rh_index_distal']:
            bound = bbox.ComputeWorldBound(prim).ComputeAlignedRange()
            dimensions[prim.GetName()] = {'world_aabb_extent_m': (np.array(bound.GetMax())-np.array(bound.GetMin())).tolist(), 'note': 'world-axis visual bounds, not calibrated physical link dimensions'}
    report = {'passed': all(checks.values()), 'checks': checks, 'knife_bodies': knife_bodies,
              'kitchen_meshes': indoor_meshes, 'prim_count': len(list(stage.Traverse())), 'visual_dimensions': dimensions,
              'limitations': ['Offline structure/provenance checks, not physical grasp validation', 'Self-collision disabled']}
    (ROOT/'docs/rl/minimal_scene_checks.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
