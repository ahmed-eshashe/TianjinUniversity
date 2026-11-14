"""Prepare held-out geometric variants, preserving original assets and densities."""
from pathlib import Path
import json
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from pxr import Usd, UsdGeom, UsdPhysics, Gf

W = Path(__file__).resolve().parent
c = json.loads((W/'scene_config.json').read_text())
source = Usd.Stage.Open(c['scene'])
kp = c['knife_path']
suffixes = dict(visual='', handle='/CollisionHandle', blade='/CollisionBlade')
original = {name: np.array(UsdGeom.Mesh(source.GetPrimAtPath(kp+suffix)).GetPointsAttr().Get()) for name,suffix in suffixes.items()}
join = float(original['handle'][:,0].min())
rows = []
for name, ratio, width in [('compact_wide_handle', .35, 1.10), ('medium_original_handle', .65, 1.)]:
    destination = W / (name + '_v01.usda')
    assert not destination.exists(), 'Preserve prepared assets'
    stage = Usd.Stage.CreateNew(str(destination))
    stage.GetRootLayer().subLayerPaths = [c['scene']]
    transformed = {}
    for key,suffix in suffixes.items():
        v = original[key].copy()
        v[:,0] = np.where(v[:,0] < join, join + (v[:,0]-join)*ratio, v[:,0])
        # Smooth handle-only widening in the transverse dimension; blade unchanged.
        handle_weight = np.clip((v[:,0]-join)/.015, 0., 1.)
        middle_y = (original['handle'][:,1].min()+original['handle'][:,1].max())/2
        v[:,1] = middle_y + (v[:,1]-middle_y)*(1.+(width-1.)*handle_weight)
        transformed[key] = v
        mesh = UsdGeom.Mesh(stage.GetPrimAtPath(kp+suffix))
        mesh.GetPointsAttr().Set(v.tolist())
        mesh.GetExtentAttr().Set([Gf.Vec3f(*v.min(0).tolist()), Gf.Vec3f(*v.max(0).tolist())])
        mesh.GetNormalsAttr().Block()
    components = []
    for key,mass in [('handle',.10),('blade',.15)]:
        old = trimesh.convex.convex_hull(original[key])
        new = trimesh.convex.convex_hull(transformed[key])
        new.density = mass/old.volume
        components.append((float(new.mass), new.center_mass, new.moment_inertia))
    mass = sum(m for m,_,_ in components)
    com = sum(m*p for m,p,_ in components)/mass
    inertia = sum(I+m*(np.eye(3)*(d@d)-np.outer(d,d)) for m,p,I in components for d in [p-com])
    moments,axes = np.linalg.eigh(inertia)
    assert (moments>0).all()
    if np.linalg.det(axes)<0:
        axes[:,0] *= -1
    q = Rotation.from_matrix(axes).as_quat()
    api = UsdPhysics.MassAPI.Apply(stage.GetPrimAtPath(kp))
    api.CreateMassAttr(mass)
    api.CreateCenterOfMassAttr(Gf.Vec3f(*com))
    api.CreateDiagonalInertiaAttr(Gf.Vec3f(*moments))
    api.CreatePrincipalAxesAttr(Gf.Quatf(float(q[3]),Gf.Vec3f(*q[:3])))
    stage.GetRootLayer().Save()
    rows.append(dict(name=name, scene=str(destination), blade_length_factor=ratio, handle_width_factor=width,
                     mass_kg=mass, length_m=float(np.ptp(transformed['visual'][:,0])),
                     centre_of_mass=com.tolist(), density_assumption='Original provisional component densities; not measured calibration',
                     physics_qualified=False, use='Held-out geometry; do not use to fit the first student.'))
(W/'heldout_knife_geometry.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
