"""Same-fragment affine extension with exact reduced local inertia.

This is an isolated adaptation of aggregation principles, not AgMPM software.
"""
import numpy as np
from scipy.sparse import coo_matrix,csr_matrix,diags,kron
from scipy.sparse.csgraph import connected_components
from scipy.linalg import cho_factor,cho_solve,eigvalsh
from reference_v17 import compatible

def full_region(body,i):
 p=body.polys[i];corners=body.grid[body.ids[i]]
 if len(p)!=4:return False
 # Roundoff tolerance only; never a material-volume/mass cutoff.
 return np.max(np.min(np.linalg.norm(p[:,None,:]-corners[None,:,:],axis=2),axis=1))<1e-14

def extension(body,max_root_distance_cells=2.5):
 pcomp,ncomp=body.components();full=np.array([full_region(body,i) for i in range(len(body.X))]);roots=np.flatnonzero(full);stable=np.unique(body.ids[full]);stable_set=set(stable.tolist());incident=[set() for _ in range(len(body.u))]
 for ids,code in zip(body.ids,body.codes):
  for a in ids:incident[a].add(int(code))
 chosen={};unresolved=[];root_distances=[]
 for a in range(len(body.u)):
  if a in stable_set:continue
  allowed=[i for i in roots if pcomp[i]==ncomp[a] and all(compatible(c,int(body.codes[i])) for c in incident[a])]
  if not allowed:unresolved.append(a);continue
  dist=np.linalg.norm(body.X[allowed]-body.grid[a],axis=1);idx=int(np.argmin(dist));r=allowed[idx]
  if dist[idx]>max_root_distance_cells*body.config['h']:unresolved.append(a);continue
  # Root nodes already have full material support. Never chain extensions.
  coefficients=np.r_[1.,body.grid[a]]@body.inv[r];chosen[a]=(r,coefficients);root_distances.append(float(dist[idx]))
 masters=np.array(sorted(stable_set|set(unresolved)),int);col={a:i for i,a in enumerate(masters)};rows=[];cols=[];vals=[]
 for a in range(len(body.u)):
  if a in col:rows.append(a);cols.append(col[a]);vals.append(1.)
  else:
   r,coef=chosen[a]
   for b,w in zip(body.ids[r],coef):
    if w!=0:rows.append(a);cols.append(col[int(b)]);vals.append(float(w))
 E=coo_matrix((vals,(rows,cols)),shape=(len(body.u),len(masters))).tocsr();affine=np.c_[np.ones(len(body.u)),body.grid];err=float(np.max(abs(E@affine[masters]-affine)))
 if err>1e-10:raise ValueError(('affine extension failed',err))
 for a,r in zip(rows,cols):
  if ncomp[a]!=ncomp[masters[r]]:raise ValueError('cross-fragment aggregation forbidden')
 report={'full_regions':int(full.sum()),'original_nodes':len(body.u),'reduced_nodes':len(masters),'aggregated_nodes':len(chosen),'unresolved_nodes':unresolved,'max_root_distance_m':max(root_distances,default=0.),'affine_error':err,'no_cross_fragment_entries':True,'root_for_node':{str(a):int(r) for a,(r,w) in chosen.items()}}
 return E,masters,report

def strain_matrix(b):
 B=np.zeros((6*len(b.X),3*len(b.u)))
 for p in range(len(b.X)):
  for k,a in enumerate(b.ids[p]):
   x,y,z=b.G[p,k];j=3*a;r=6*p;B[r,j]+=x;B[r+1,j+1]+=y;B[r+2,j+2]+=z;B[r+3,j]+=y;B[r+3,j+1]+=x;B[r+4,j]+=z;B[r+4,j+2]+=x;B[r+5,j+1]+=z;B[r+5,j+2]+=y
 return B*np.repeat(np.sqrt(b.V),6)[:,None]

def vertex_fields(b):
 pos=[];vel=[]
 for i,p in enumerate(b.polys):
  N=np.c_[np.ones(len(p)),p]@b.inv[i];pos.append(p+N@b.u[b.ids[i]]);vel.append(N@b.v[b.ids[i]])
 return np.concatenate(pos),np.concatenate(vel)

class Aggregate:
 def __init__(self,body):
  self.body=body.clone();self.E,self.masters,self.report=extension(self.body);self.M=(self.E.T@diags(body.mass)@self.E).tocsr();n=len(self.masters);nc,labels=connected_components(self.M,directed=False);self.blocks=[];self.factors=[]
  for c in range(nc):
   ids=np.flatnonzero(labels==c);mat=self.M[ids][:,ids].toarray();factor=cho_factor(mat,lower=True,check_finite=True);self.blocks.append(ids);self.factors.append(factor)
  self.report['mass_block_sizes']=sorted([len(x) for x in self.blocks],reverse=True);self.report['max_mass_block']=max(map(len,self.blocks));self.report['mass_total_kg']=float(np.ones(n)@(self.M@np.ones(n)));self.report['mass_relative_error']=abs(self.report['mass_total_kg']-body.mass.sum())/body.mass.sum()
  self.q=self.solve(self.E.T@(body.mass[:,None]*body.u));self.v=self.solve(self.E.T@(body.mass[:,None]*body.v));before=body.metrics();x0,v0=vertex_fields(body);self.sync();after=self.body.metrics();x1,v1=vertex_fields(self.body)
  self.transfer={'position_m':float(np.max(np.linalg.norm(x1-x0,axis=1))),'velocity_m_s':float(np.max(np.linalg.norm(v1-v0,axis=1))),'F':float(np.max(abs(self.body.fields()[2]-body.fields()[2]))),'elastic_change_J':after['U']-before['U'],'kinetic_change_J':after['T']-before['T'],'energy_relative':abs(after['U']+after['T']-before['U']-before['T'])/max(before['U']+before['T'],1e-10),'linear_momentum_abs':float(np.linalg.norm(after['momentum']-before['momentum'])),'angular_momentum_abs':float(np.linalg.norm(after['angular']-before['angular'])),'angular_relative':float(np.linalg.norm(after['angular']-before['angular'])/max(np.linalg.norm(before['angular']),1e-12))}
  self.report['transfer']=self.transfer
 def solve(self,rhs):
  out=np.empty_like(rhs)
  for ids,factor in zip(self.blocks,self.factors):out[ids]=cho_solve(factor,rhs[ids],check_finite=False)
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
