"""Reset-time effective-bulk tomato preserving the saved convex exterior.

No pre-cut interfaces, no discarded positive-volume cells, no new material law.
Its virtual-node discretization remains subject to independent qualification.
"""
from pathlib import Path
import ctypes as c,json,hashlib,time
import numpy as np
from scipy.spatial import ConvexHull
from compiled_body import Body
from packed_polys import PackedPolys
from reference_v17 import moments
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/work/disect_mesh_validation_20261108_v02/proposed_exterior_input.npz')
L=c.CDLL(str(ROOT/'build/tomato_geometry.so'));I=c.POINTER(c.c_longlong);D=c.POINTER(c.c_double);H=c.c_void_p
L.surface_prepare.argtypes=[c.c_int,I,D];L.surface_prepare.restype=H;L.surface_crop.argtypes=[H,c.c_int,D];L.surface_crop.restype=H;L.surface_free.argtypes=[H];L.geometry_error.restype=c.c_char_p
for k in ['count','vertex_count']:getattr(L,'surface_'+k).argtypes=[H];getattr(L,'surface_'+k).restype=c.c_int
L.surface_data.argtypes=[H,I,D,I,I,D,D]

def generate(h=.006,scale=(1.,1.,1.),rotation=None):
 start=time.perf_counter();z=np.load(SOURCE);vertices=z['vertices'];faces=z['triangles'];center=(vertices.min(0)+vertices.max(0))/2;vertices=vertices-center;scale=np.asarray(scale,float)
 if scale.shape!=(3,) or np.any(scale<=0):raise ValueError('positive reset-time scale required')
 R=np.array([[1.,0,0],[0,0,1],[0,-1.,0]]) if rotation is None else np.asarray(rotation,float)
 if np.max(abs(R.T@R-np.eye(3)))>1e-12 or abs(np.linalg.det(R)-1)>1e-12:raise ValueError('proper rotation required')
 vertices=(vertices*scale)@R.T;tri=vertices[faces];normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.linalg.norm(normal,axis=1)[:,None];normal*=np.sign(np.einsum('ij,ij->i',normal,tri.mean(1)))[:,None];offset=-np.einsum('ij,ij->i',normal,tri[:,0]);planes=np.c_[normal,offset];outside=max(float(np.max(vertices@n+d)) for n,d in zip(normal,offset));source_volume=abs(np.sum(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])))/6)
 hull=ConvexHull(vertices)
 if outside>1e-12 or abs(hull.volume-source_volume)>hull.volume*1e-10:raise ValueError('source is not verified convex; no hull replacement allowed')
 # Coplanar source triangles define the same halfspace; keep an original
 # equation per group, never average normals or approximate curved geometry.
 _,keep=np.unique(np.round(planes,13),axis=0,return_index=True);planes=np.ascontiguousarray(planes[np.sort(keep)])
 n=int(np.ceil(2*np.max(abs(vertices))/h));b=Body(n=n,h=h);p=np.ascontiguousarray(b.poly_ptr,np.int64);v=np.ascontiguousarray(b.poly_vertices);old=L.surface_prepare(len(b.polys),p.ctypes.data_as(I),v.ctypes.data_as(D))
 if not old:raise ValueError(L.geometry_error().decode())
 handle=None
 try:
  handle=L.surface_crop(old,len(planes),planes.ctypes.data_as(D))
  if not handle:raise ValueError(L.geometry_error().decode())
  nr=L.surface_count(handle);nv=L.surface_vertex_count(handle);ptr=np.empty(nr+1,np.int64);xyz=np.empty((nv,3));origin=np.empty(nr,np.int64);codes=np.empty(nr,np.int64);V=np.empty(nr);X=np.empty((nr,3));L.surface_data(handle,ptr.ctypes.data_as(I),xyz.ctypes.data_as(D),origin.ctypes.data_as(I),codes.ctypes.data_as(I),V.ctypes.data_as(D),X.ctypes.data_as(D))
 finally:
  if handle:L.surface_free(handle)
  L.surface_free(old)
 ids=b.ids[origin];used,newids=np.unique(ids,return_inverse=True);b.ids=newids.reshape(-1,4);b.grid=b.grid[used].copy();b.u=b.u[used].copy();b.v=b.v[used].copy();b.inv=b.inv[origin].copy();b.G=b.G[origin].copy();b.polys=PackedPolys(ptr,xyz);b.V=V;b.X=X;b.N=np.einsum('pi,pij->pj',np.c_[np.ones(nr),X],b.inv);b.codes=codes;b.rebuild();b.freeze_geometry();b._moment_V=V.copy();b._moment_X=X.copy()
 error=abs(V.sum()-source_volume)/source_volume
 if error>1e-6:
  independent=np.array([moments(p)[0] for p in b.polys]);np.savez(ROOT/'reports/tomato_generation_rejected.npz',ptr=ptr,vertices=xyz,volume=V,independent_volume=independent,source_volume=source_volume,origin=origin)
  raise ValueError(('reset volume mismatch',error,'independent',float(independent.sum()/source_volume-1),'largest local',float(np.max(abs(independent-V)))))
 fixtures=((z['fixture_coordinates']-center)*scale)@R.T
 b.tomato_metadata=dict(source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),reference_volume_m3=float(source_volume),generated_volume_m3=float(V.sum()),volume_relative_error=float(error),mass_kg=float(b.mass.sum()),rho_kg_m3=b.rho,h_m=h,scale=scale.tolist(),rotation=R.tolist(),nodes=len(b.u),regions=len(V),source_exterior_triangles=len(faces),source_plane_count=len(planes),source_convex_outside_m=outside,wall_s=time.perf_counter()-start,experimental_validation='pending',physical_cut=False,rl_ready=False,model='Uncalibrated homogeneous neo-Hookean bulk; exact original convex exterior. Four cut histories, no pre-cut topology. Geometry generation only.')
 return b,dict(vertices=vertices,triangles=faces,fixture_coordinates=fixtures,metadata=b.tomato_metadata)
