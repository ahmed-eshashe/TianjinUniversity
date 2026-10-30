"""Read-only scale, mass and inertia audit; never regenerates a USD layer."""
import json
from pathlib import Path
import numpy as np
from pxr import Usd,UsdGeom,UsdPhysics
from scipy.spatial.transform import Rotation
import trimesh
from offline_grasp_audit import ROOT


def main():
    folder=ROOT/'runs/offline/load_support_01'
    meta=json.loads((ROOT/'rl/scene/manifest.json').read_text())
    expected=json.loads((ROOT/'docs/rl/phase3_physics.json').read_text())
    stage=Usd.Stage.Open(str(ROOT/'rl/scene/phase3_grasp.usda'))
    # SimulationContext authors metres on its root before native_env appends
    # the scene layer. Reproduce only that USD composition, without simulation.
    runtime_composition=Usd.Stage.CreateInMemory()
    UsdGeom.SetStageMetersPerUnit(runtime_composition,1.)
    runtime_composition.GetRootLayer().subLayerPaths.append(str(ROOT/'rl/scene/phase3_grasp.usda'))
    minimal=Usd.Stage.Open(str(ROOT/'rl/scene/minimal_benchmark.usda'))
    path=meta['knife_path'];cache=UsdGeom.XformCache();knife=stage.GetPrimAtPath(path)
    matrix=np.array(cache.GetLocalToWorldTransform(knife)).T
    before_matrix=np.array(UsdGeom.XformCache().GetLocalToWorldTransform(minimal.GetPrimAtPath(path))).T
    vertices=np.array(UsdGeom.Mesh(knife).GetPointsAttr().Get())
    before_vertices=np.array(UsdGeom.Mesh(minimal.GetPrimAtPath(path)).GetPointsAttr().Get())
    world=vertices@matrix[:3,:3].T+matrix[:3,3]
    before_world=before_vertices@before_matrix[:3,:3].T+before_matrix[:3,3]
    assert world.shape==before_world.shape
    components=[]
    for name,mass in [('Handle',.10),('Blade',.15)]:
        p=stage.GetPrimAtPath(path+'/Collision'+name)
        rel=np.linalg.inv(matrix)@np.array(cache.GetLocalToWorldTransform(p)).T
        v=np.array(UsdGeom.Mesh(p).GetPointsAttr().Get());v=v@rel[:3,:3].T+rel[:3,3]
        hull=trimesh.convex.convex_hull(v);hull.density=mass/hull.volume
        components.append({'name':name,'assigned_mass_kg':mass,'bounds_local_m':[v.min(0).tolist(),v.max(0).tolist()],
            'convex_volume_m3':float(hull.volume),'implied_uniform_density_kg_m3':float(hull.density),
            'com_local_m':hull.center_mass.tolist(),'own_com_inertia_kg_m2':hull.moment_inertia.tolist()})
    mass=sum(c['assigned_mass_kg'] for c in components)
    com=sum(c['assigned_mass_kg']*np.array(c['com_local_m']) for c in components)/mass
    inertia=np.zeros((3,3))
    for c in components:
        d=np.array(c['com_local_m'])-com
        inertia+=np.array(c['own_com_inertia_kg_m2'])+c['assigned_mass_kg']*((d@d)*np.eye(3)-np.outer(d,d))
    api=UsdPhysics.MassAPI(knife);q=api.GetPrincipalAxesAttr().Get()
    r=Rotation.from_quat([*q.GetImaginary(),q.GetReal()]).as_matrix()
    authored=r@np.diag(np.array(api.GetDiagonalInertiaAttr().Get()))@r.T
    authored_com=np.array(api.GetCenterOfMassAttr().Get())
    result={'scope':'Asset and internal-assumption consistency only; no real hardware measurement',
        'stage_metres_per_unit':UsdGeom.GetStageMetersPerUnit(stage),
        'runtime_root_composition_metres_per_unit':UsdGeom.GetStageMetersPerUnit(runtime_composition),
        'unit_scope':'Bare derived layer uses USD fallback 0.01; native SimulationContext root explicitly uses 1.0; numerical geometry below interpreted in native-root metres',
        'current_transform_axis_scales':np.linalg.norm(matrix[:3,:3],axis=0).tolist(),
        'pre_bake_transform_axis_scales':np.linalg.norm(before_matrix[:3,:3],axis=0).tolist(),
        'visual_dimensions_local_m':np.ptp(vertices,axis=0).tolist(),
        'baked_vs_pre_bake_world_max_vertex_error_m':float(np.linalg.norm(world-before_world,axis=1).max()),
        'components':components,'recomputed_mass_kg':mass,'authored_mass_kg':float(api.GetMassAttr().Get()),
        'recomputed_com_local_m':com.tolist(),'authored_com_local_m':authored_com.tolist(),
        'com_error_m':float(np.linalg.norm(com-authored_com)),
        'recomputed_inertia_kg_m2':inertia.tolist(),'authored_inertia_kg_m2':authored.tolist(),
        'inertia_max_absolute_error_kg_m2':float(np.max(abs(inertia-authored))),
        'report_com_error_m':float(np.linalg.norm(com-np.array(expected['knife_com_local_m']))),
        'report_inertia_max_error_kg_m2':float(np.max(abs(inertia-np.array(expected['knife_inertia_kg_m2'])))),
        'eigenvalues_kg_m2':np.linalg.eigvalsh(inertia).tolist(),
        'assumption':'Uniform 0.10 kg handle and 0.15 kg blade convex volumes; uncalibrated; source asset is not a physical knife measurement',
        'geometry_changed':False,'mass_changed':False}
    result['internal_consistency_passed']=bool(result['runtime_root_composition_metres_per_unit']==1 and
        abs(result['authored_mass_kg']-mass)<1e-7 and result['com_error_m']<1e-7 and
        result['inertia_max_absolute_error_kg_m2']<1e-8 and result['baked_vs_pre_bake_world_max_vertex_error_m']<1e-6)
    (folder/'knife_mass_audit.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    print(json.dumps({k:result[k] for k in ['internal_consistency_passed','visual_dimensions_local_m','authored_mass_kg','authored_com_local_m','com_error_m','inertia_max_absolute_error_kg_m2','baked_vs_pre_bake_world_max_vertex_error_m']},indent=2))


if __name__=='__main__':main()
