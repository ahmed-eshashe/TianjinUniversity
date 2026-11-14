from pathlib import Path
import sys,os,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from blade_geometry import CAD
from partition_gpu import signed
from independent_cad_query import query_mesh
@wp.kernel
def queries(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),x:wp.array(dtype=wp.vec3d),phi:wp.array(dtype=wp.float64),normal:wp.array(dtype=wp.vec3d),face:wp.array(dtype=int)):
 i=wp.tid();s=signed(mesh,tri,x[i]);phi[i]=s.phi;normal[i]=s.normal;face[i]=wp.mesh_query_point_sign_winding_number(mesh,wp.vec3(x[i]),10.).face
cad=CAD();rng=np.random.default_rng(731);x=np.column_stack([rng.uniform(-.003,.003,10000),rng.uniform(-5e-5,5e-5,10000),rng.uniform(-.003,.003,10000)])
ref=query_mesh(cad.vertices,cad.faces,x);tri=wp.array(cad.vertices[cad.faces],dtype=wp.vec3d);xx=wp.array(x,dtype=wp.vec3d);p=wp.empty(len(x),dtype=wp.float64);n=wp.empty(len(x),dtype=wp.vec3d);f=wp.empty(len(x),dtype=int);wp.launch(queries,len(x),[cad.mesh.id,tri,xx,p,n,f]);phi=p.numpy();normal=n.numpy();face=f.numpy();error=abs(phi-ref['phi']);ne=np.linalg.norm(normal-ref['normal'],axis=1);idx=np.argsort(error)[-10:];r={'max_distance_error_m':float(error.max()),'max_normal_error':float(ne.max()),'wrong_sign':int(((phi<0)!=(ref['phi']<0)).sum()),'different_face':int((face!=ref['face']).sum()),'largest':[dict(x=x[i].tolist(),phi=phi[i],reference=ref['phi'][i],face=int(face[i]),reference_face=int(ref['face'][i]),normal_error=ne[i]) for i in idx]};(W/'reports/query_audit_corrected.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
