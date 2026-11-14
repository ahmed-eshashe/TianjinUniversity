"""Same-fragment affine extension with exact reduced local inertia.

This is an isolated adaptation of aggregation principles, not AgMPM software.
"""
import numpy as np
from scipy.sparse import coo_matrix,csr_matrix,diags,kron,eye
from update_kernels import full_flags,vertex_values,select_roots
from scipy.sparse.csgraph import connected_components
from scipy.linalg import cho_factor,cho_solve,eigvalsh
from reference_v17 import compatible

def full_region(body,i):
 p=body.polys[i];corners=body.grid[body.ids[i]]
 if len(p)!=4:return False
 # Roundoff tolerance only; never a material-volume/mass cutoff.
 return np.max(np.min(np.linalg.norm(p[:,None,:]-corners[None,:,:],axis=2),axis=1))<1e-14

def extension(body,max_root_distance_cells=3.5,support_threshold=1e-8):
 ptr=body.poly_ptr if hasattr(body,'poly_ptr') else np.r_[0,np.cumsum([len(p) for p in body.polys])]
 vertices=body.poly_vertices if hasattr(body,'poly_vertices') else np.concatenate(body.polys)
 full=full_flags(ptr,vertices,body.grid,body.ids)
 roots=np.flatnonzero(full);root_code=body.codes[roots];allow_cache={}
 support=body.mass/(body.rho*body.config['h']**3)
 stable=np.union1d(np.unique(body.ids[full]),np.flatnonzero(support>=support_threshold))
 if len(stable)==len(body.u):
  # Exactly the reference identity operator; no approximation or mass relumping.
  n=len(body.u)
  report={'support_threshold':support_threshold,'minimum_support_fraction':float(support.min()),'full_regions':int(full.sum()),'original_nodes':n,'reduced_nodes':n,'aggregated_nodes':0,'aggregated_original_inertia_fraction':0.,'unresolved_nodes':[],'max_root_distance_m':0.,'affine_error':0.,'no_cross_fragment_entries':True,'root_for_node':{},'identity_fast_path':True}
  return eye(n,format='csr'),np.arange(n),report
 pcomp,ncomp=body.components()
 stable_mask=np.zeros(len(body.u),bool);stable_mask[stable]=True
 root_for,distances=select_roots(body.ids,body.codes,body.grid,body.X,full,pcomp,ncomp,stable_mask,max_root_distance_cells*body.config['h'])
 chosen_ids=np.flatnonzero(root_for>=0);unresolved=np.flatnonzero((root_for<0)&~stable_mask).tolist()
 masters=np.flatnonzero(root_for<0);col=np.full(len(body.u),-1,int);col[masters]=np.arange(len(masters))
 rows=masters.tolist();cols=np.arange(len(masters)).tolist();vals=np.ones(len(masters)).tolist();chosen={};root_distances=distances[chosen_ids].tolist()
 for a in chosen_ids:
  r=root_for[a];coef=np.r_[1.,body.grid[a]]@body.inv[r];chosen[a]=(r,coef)
  for b,w in zip(body.ids[r],coef):
   if w!=0:
    if col[b]<0:raise ValueError('chained extension forbidden')
    rows.append(a);cols.append(col[b]);vals.append(float(w))
 E=coo_matrix((vals,(rows,cols)),shape=(len(body.u),len(masters))).tocsr();affine=np.c_[np.ones(len(body.u)),body.grid];err=float(np.max(abs(E@affine[masters]-affine)))
 if err>1e-10:raise ValueError(('affine extension failed',err))
 for a,r in zip(rows,cols):
  if ncomp[a]!=ncomp[masters[r]]:raise ValueError('cross-fragment aggregation forbidden')
 report={'support_threshold':support_threshold,'minimum_support_fraction':float(support.min()),'full_regions':int(full.sum()),'original_nodes':len(body.u),'reduced_nodes':len(masters),'aggregated_nodes':len(chosen),'aggregated_original_inertia_fraction':float(body.mass[list(chosen)].sum()/body.mass.sum()) if chosen else 0.,'unresolved_nodes':unresolved,'max_root_distance_m':max(root_distances,default=0.),'affine_error':err,'no_cross_fragment_entries':True,'root_for_node':{str(a):int(r) for a,(r,w) in chosen.items()}}
 return E,masters,report

def strain_matrix(b):
 B=np.zeros((6*len(b.X),3*len(b.u)))
 for p in range(len(b.X)):
  for k,a in enumerate(b.ids[p]):
   x,y,z=b.G[p,k];j=3*a;r=6*p;B[r,j]+=x;B[r+1,j+1]+=y;B[r+2,j+2]+=z;B[r+3,j]+=y;B[r+3,j+1]+=x;B[r+4,j]+=z;B[r+4,j+2]+=x;B[r+5,j+1]+=z;B[r+5,j+2]+=y
 return B*np.repeat(np.sqrt(b.V),6)[:,None]

def vertex_fields(b):
 ptr=b.poly_ptr if hasattr(b,'poly_ptr') else np.r_[0,np.cumsum([len(p) for p in b.polys])]
 v=b.poly_vertices if hasattr(b,'poly_vertices') else np.concatenate(b.polys)
 return vertex_values(ptr,v,b.inv,b.ids,b.u,b.v)

class Aggregate:
 def __init__(self,body,support_threshold=1e-8):
  self.body=body.clone()
  cache=getattr(body,'_operator_cache',None)
  signature=(id(body.ids),id(body.mass),id(body.polys),float(support_threshold))
  keys=['E','masters','M','singletons','single_mass','coupled','order','bounds']
  if cache is not None and cache['signature']==signature:
   for k in keys:setattr(self,k,cache[k])
   self.report=cache['report'].copy()
  else:
   self.E,self.masters,self.report=extension(self.body,support_threshold=support_threshold);self.M=(self.E.T@diags(body.mass)@self.E).tocsr();n=len(self.masters);nc,labels=connected_components(self.M,directed=False)
   self.order=np.argsort(labels,kind='stable');sizes=np.bincount(labels);self.bounds=np.r_[0,np.cumsum(sizes)];diagonal=self.M.diagonal()
   self.singletons=self.order[self.bounds[:-1][sizes==1]];self.single_mass=diagonal[self.singletons]
   if np.any(self.single_mass<=0):raise ValueError('nonpositive singleton mass')
   self.coupled=[]
   for c in np.flatnonzero(sizes>1):
    ids=self.order[self.bounds[c]:self.bounds[c+1]];factor=cho_factor(self.M[ids][:,ids].toarray(),lower=True,check_finite=True);self.coupled.append((ids,factor))
   self.report['mass_block_sizes']=sorted(sizes.tolist(),reverse=True);self.report['max_mass_block']=int(sizes.max());self.report['mass_total_kg']=float(np.ones(n)@(self.M@np.ones(n)));self.report['mass_relative_error']=abs(self.report['mass_total_kg']-body.mass.sum())/body.mass.sum()
   cache={k:getattr(self,k) for k in keys};cache.update(signature=signature,report=self.report.copy())
   body._operator_cache=cache;self.body._operator_cache=cache
  self.q=self.solve(self.E.T@(body.mass[:,None]*body.u));self.v=self.solve(self.E.T@(body.mass[:,None]*body.v));before=body.metrics();x0,v0=vertex_fields(body);self.sync();after=self.body.metrics();x1,v1=vertex_fields(self.body)
  self.transfer={'position_m':float(np.max(np.linalg.norm(x1-x0,axis=1))),'velocity_m_s':float(np.max(np.linalg.norm(v1-v0,axis=1))),'F':float(np.max(abs(self.body.fields()[2]-body.fields()[2]))),'elastic_change_J':after['U']-before['U'],'kinetic_change_J':after['T']-before['T'],'energy_relative':abs(after['U']+after['T']-before['U']-before['T'])/max(before['U']+before['T'],1e-10),'linear_momentum_abs':float(np.linalg.norm(after['momentum']-before['momentum'])),'angular_momentum_abs':float(np.linalg.norm(after['angular']-before['angular'])),'angular_relative':float(np.linalg.norm(after['angular']-before['angular'])/max(np.linalg.norm(before['angular']),1e-12))}
  self.report['transfer']=self.transfer
 @property
 def blocks(self):return [self.order[a:b] for a,b in zip(self.bounds[:-1],self.bounds[1:])]
 @property
 def factors(self):
  diag=self.M.diagonal();coupled={int(ids[0]):f for ids,f in self.coupled}
  return [(np.array([[np.sqrt(diag[ids[0]])]]),True) if len(ids)==1 else coupled[int(ids[0])] for ids in self.blocks]
 def solve(self,rhs):
  out=np.empty_like(rhs)
  if len(self.singletons):out[self.singletons]=rhs[self.singletons]/self.single_mass[:,None]
  for ids,factor in self.coupled:out[ids]=cho_solve(factor,rhs[ids],check_finite=False)
  return out
 def sync(self):self.body.u=np.asarray(self.E@self.q);self.body.v=np.asarray(self.E@self.v)
 def energy_force(self,q=None):
  u=self.E@(self.q if q is None else q);U,f=self.body.energy_force(u);return U,np.asarray(self.E.T@f)
 def metrics(self):
  self.sync();m=self.body.metrics();m['reduced_T']=float(.5*np.sum(self.v*(self.M@self.v)));return m
 def step(self,dt,external=None):
  ext=np.zeros_like(self.q) if external is None else self.E.T@external;_,f=self.energy_force();vh=self.v+.5*dt*self.solve(f+ext);q=self.q+dt*vh;_,f=self.energy_force(q);v=vh+.5*dt*self.solve(f+ext)
  if not np.isfinite(q).all() or not np.isfinite(v).all():raise ValueError('nonfinite aggregate state')
  self.q,self.v=q,v;self.body.time+=dt;self.body.steps+=1;self.sync()
 def audit(self):
  B=strain_matrix(self.body)@kron(self.E,np.eye(3));s=np.linalg.svd(B,compute_uv=False);rank=int(np.sum(s>s[0]*1e-9));nc=len(np.unique(self.body.components()[0]));C=np.eye(6)*self.body.mu;C[:3,:3]=self.body.lam;C[:3,:3]+=np.eye(3)*2*self.body.mu;CB=np.einsum('ij,pjk->pik',C,B.reshape(-1,6,B.shape[1])).reshape(B.shape);K=B.T@CB;M=kron(self.M,np.eye(3)).toarray();eigs=eigvalsh(K,M,check_finite=True);return {'rank':rank,'expected_rank':3*len(self.masters)-6*nc,'components':nc,'linearized_stability_dt_s':float(2/np.sqrt(eigs[-1])),'min_mass_eigenvalue':float(np.linalg.eigvalsh(self.M.toarray())[0]),'max_mass_block':self.report['max_mass_block'],'nodes':len(self.masters)}
