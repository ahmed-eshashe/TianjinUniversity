"""A separately identified shorter blade family; original knife/handle files preserved."""
from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom,UsdPhysics,Gf
W=Path(__file__).resolve().parent;c=json.loads((W/'scene_config.json').read_text());source=Usd.Stage.Open(c['scene']);kp=c['knife_path'];original={name:np.array(UsdGeom.Mesh(source.GetPrimAtPath(kp+suffix)).GetPointsAttr().Get()) for name,suffix in [('visual',''),('handle','/CollisionHandle'),('blade','/CollisionBlade')]};join=float(original['handle'][:,0].min());ratio=.5
path=W/'knife_short_blade_v01.usda';s=Usd.Stage.Open(str(path)) if path.exists() else Usd.Stage.CreateNew(str(path));s.GetRootLayer().Clear();s.GetRootLayer().subLayerPaths=[c['scene']];transformed={}
for name,suffix in [('visual',''),('handle','/CollisionHandle'),('blade','/CollisionBlade')]:
 v=original[name].copy();v[:,0]=np.where(v[:,0]<join,join+(v[:,0]-join)*ratio,v[:,0]);transformed[name]=v;m=UsdGeom.Mesh(s.GetPrimAtPath(kp+suffix));m.GetPointsAttr().Set(v.tolist());m.GetExtentAttr().Set([Gf.Vec3f(*v.min(0).tolist()),Gf.Vec3f(*v.max(0).tolist())]);m.GetNormalsAttr().Block()
components=[];massparts={}
for name,oldmass in [('handle',.10),('blade',.15)]:
 old=trimesh.convex.convex_hull(original[name]);new=trimesh.convex.convex_hull(transformed[name]);new.density=oldmass/old.volume;mass=float(new.mass);massparts[name]=mass;components.append((mass,new.center_mass,new.moment_inertia))
mass=sum(x[0] for x in components);com=sum(m*p for m,p,I in components)/mass;I=sum(I+m*(np.eye(3)*(d@d)-np.outer(d,d)) for m,p,I in components for d in [p-com]);e,axes=np.linalg.eigh(I)
if np.linalg.det(axes)<0:axes[:,0]*=-1
q=Rotation.from_matrix(axes).as_quat();ma=UsdPhysics.MassAPI.Apply(s.GetPrimAtPath(kp));ma.CreateMassAttr(mass);ma.CreateCenterOfMassAttr(Gf.Vec3f(*com));ma.CreateDiagonalInertiaAttr(Gf.Vec3f(*e));ma.CreatePrincipalAxesAttr(Gf.Quatf(float(q[3]),Gf.Vec3f(*q[:3])));s.GetRootLayer().Save();report=dict(name='short_blade_v01',scene=str(path),status='asset_prepared_not_physically_validated',original_length_m=float(np.ptp(original['visual'],axis=0)[0]),new_length_m=float(np.ptp(transformed['visual'],axis=0)[0]),mass_kg=mass,component_masses_kg=massparts,centre_of_mass_local_m=com.tolist(),principal_inertia_kg_m2=e.tolist(),density_assumption='Original provisional per-component density preserved; no measured knife calibration.',handle_vertices_identical=bool(np.array_equal(original['handle'],transformed['handle'])),friction_unchanged=True,grasp_source='Existing hand-fitting candidate; requires fresh physical qualification.',original_scene_sha256=hashlib.sha256(Path(c['scene']).read_bytes()).hexdigest());(W/'reports/short_blade_variant.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
