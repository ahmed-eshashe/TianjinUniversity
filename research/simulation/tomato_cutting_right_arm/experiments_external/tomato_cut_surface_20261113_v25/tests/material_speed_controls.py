from pathlib import Path
import sys,os,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from compiled_body import Body
from fast_aggregation import Aggregate,vertex_fields
from poly_surface import Surface
from blade_geometry import CAD
from rk4_contact_gpu import ContactGPU,material_speed
checks={};rows=[];rng=np.random.default_rng(9871);cad=CAD()
for label,offset in [('intact',None),('split',.0001),('aggregated',1e-7)]:
 b=Body(n=2,h=.003)
 if offset is not None:b.split([1,0,0],offset)
 a=Aggregate(b);s=Surface(a)
 # Runtime currently rejects constrained coupled inertia, but its material
 # interpolation map and speed kernel can be checked for that case directly.
 from scipy.sparse import coo_matrix
 X=b.poly_vertices;owner=np.repeat(np.arange(len(b.polys)),np.diff(b.poly_ptr));N=np.einsum('pi,pij->pj',np.c_[np.ones(len(X)),X],b.inv[owner]);Q=(coo_matrix((N.ravel(),(np.repeat(np.arange(len(X)),4),b.ids[owner].ravel())),shape=(len(X),len(b.u)))@a.E).tocsr()
 ptr=wp.array(Q.indptr,dtype=int,device='cuda:0');ids=wp.array(Q.indices,dtype=int,device='cuda:0');weights=wp.array(Q.data,dtype=wp.float64,device='cuda:0');maximum=wp.zeros(1,dtype=float,device='cuda:0')
 for scale in [0.,1e-5,.01,1.]:
  a.v=rng.normal(size=a.v.shape)*scale;a.sync();vv=wp.array(a.v,dtype=wp.vec3,device='cuda:0');maximum.zero_();wp.launch(material_speed,len(X),[ptr,ids,weights,vv,maximum]);bound=float(maximum.numpy()[0]);stored=vv.numpy().astype(float);cpu=float(np.linalg.norm(Q@stored,axis=1).max());checks[f'{label}_{scale}_bounds_physical_vertices']=bound>=cpu;checks[f'{label}_{scale}_tight']=bound-cpu<=max(1e-8,cpu*1e-6)
  # Convex combinations independently sample the complete physical regions.
  maxinterior=0.
  for r,p in enumerate(b.polys):
   bary=rng.dirichlet(np.ones(len(p)),size=50);x=bary@p;Nq=np.c_[np.ones(len(x)),x]@b.inv[r];vals=Nq@(a.E@stored)[b.ids[r]];maxinterior=max(maxinterior,float(np.linalg.norm(vals,axis=1).max()))
  checks[f'{label}_{scale}_bounds_interior']=bound>=maxinterior;rows.append(dict(case=label,scale=scale,bound=bound,vertex_max=cpu,interior_max=maxinterior,aggregated_nodes=a.report['aggregated_nodes']))
out=dict(passed=all(checks.values()),checks=checks,rows=rows,scope='Actual material velocity bound, including aggregated virtual nodes; independent convex interior probes. No physical cut.')
(W/'reports/material_speed_controls.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
