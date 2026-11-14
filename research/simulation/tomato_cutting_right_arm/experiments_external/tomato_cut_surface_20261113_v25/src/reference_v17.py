"""Isolated lumped virtual-node linear FEM reference; geometric splits only."""
import copy,json,itertools
import numpy as np
from scipy.spatial import ConvexHull
from scipy.sparse import coo_matrix,csr_matrix
from scipy.sparse.csgraph import connected_components

def clip(vertices,normal,offset):
 v=np.asarray(vertices);n=np.asarray(normal);s=v@n-offset
 if s.max()<=0:return v.copy()
 if s.min()>=0:return None
 # No physical mass floor or sliver removal. Zero-volume boundary facets do not
 # constitute material regions. Ambiguous numerical degeneracy raises an error.
 scale=np.max(np.ptp(v,axis=0));faces=ConvexHull((v-v.mean(0))/scale).simplices
 edges=set()
 for f in faces:edges.update(tuple(sorted(e)) for e in itertools.combinations(f,2))
 out=list(v[s<=0])
 for i,j in edges:
  if (s[i]<0<s[j]) or (s[j]<0<s[i]):out.append(v[i]+s[i]/(s[i]-s[j])*(v[j]-v[i]))
 result=np.unique(np.asarray(out),axis=0)
 if len(result)<4:raise ValueError('unresolved clipped region; no silent discard')
 return result

def moments(v):
 c=np.mean(v,axis=0);scale=np.max(np.ptp(v,axis=0));h=ConvexHull((v-c)/scale);a=v[h.simplices];vol=np.abs(np.linalg.det(a-c))/6.;V=vol.sum();cent=np.sum(vol[:,None]*(a.sum(1)+c)/4,axis=0)/V
 if not V>0 or not np.isfinite(cent).all():raise ValueError('invalid material volume')
 return V,cent

def compatible(a,b):
 for k in range(4):
  if ((int(a)//3**k)%3)*((int(b)//3**k)%3)==2:return False
 return True

def energy_stress(F,mu,lam):
 J=np.linalg.det(F)
 if not np.isfinite(J).all() or J.min()<=.1 or J.max()>=10:raise ValueError('inadmissible material volume')
 l=np.log(J);return .5*mu*((F*F).sum((1,2))-3)-mu*l+.5*lam*l*l,mu*F+(lam*l-mu)[:,None,None]*np.linalg.inv(F).transpose(0,2,1)

class Body:
 def __init__(self,n=2,h=.006,E=1e5,nu=.4,rho=1000.):
  self.config=dict(n=n,h=h,E=E,nu=nu,rho=rho);self.mu=E/(2*(1+nu));self.lam=E*nu/((1+nu)*(1-2*nu));self.rho=rho
  nodes=np.array(list(itertools.product(range(n+1),repeat=3)));lookup={tuple(p):i for i,p in enumerate(nodes)};self.grid=(nodes-n/2)*h;tets=[]
  for cell in itertools.product(range(n),repeat=3):
   for perm in itertools.permutations(range(3)):
    x=np.array(cell);v=[x.copy()]
    for axis in perm:x=x.copy();x[axis]+=1;v.append(x.copy())
    tets.append([lookup[tuple(p)] for p in v])
  self.ids=np.asarray(tets);self.polys=[p.copy() for p in self.grid[self.ids]];self.inv=np.linalg.inv(np.concatenate([np.ones((len(tets),4,1)),self.grid[self.ids]],axis=2));self.G=self.inv[:,1:,:].transpose(0,2,1).copy();self.G[:,0]=-self.G[:,1:].sum(1)
  self.V=np.abs(np.linalg.det(self.grid[self.ids][:,1:]-self.grid[self.ids][:,:1]))/6;self.X=self.grid[self.ids].mean(1);self.N=np.full((len(tets),4),.25);self.codes=np.zeros(len(tets),int);self.u=np.zeros_like(self.grid);self.v=self.u.copy();self.time=0.;self.steps=0;self.history=[];self.rebuild()
 def rebuild(self):
  self.mass=np.bincount(self.ids.ravel(),weights=(self.rho*self.V[:,None]*self.N).ravel(),minlength=len(self.u))
  if not np.isfinite(self.mass).all() or self.mass.min()<=0:raise ValueError('nonpositive nodal mass, no flooring allowed')
  order=np.argsort(self.ids.ravel(),kind='stable');self.ptr=np.r_[0,np.cumsum(np.bincount(self.ids.ravel(),minlength=len(self.u)))].astype(np.int32);self.edge_p=np.repeat(np.arange(len(self.X)),4)[order].astype(np.int32);self.edge_g=self.G.reshape(-1,3)[order];self.O=coo_matrix((self.N.ravel(),(np.repeat(np.arange(len(self.X)),4),self.ids.ravel())),shape=(len(self.X),len(self.u))).tocsr()
 def clone(self):
  o=copy.copy(self)
  for k in ['grid','ids','inv','G','V','X','N','codes','u','v','mass']:setattr(o,k,getattr(self,k).copy())
  o.polys=[p.copy() for p in self.polys];o.history=copy.deepcopy(self.history);return o
 def fields(self,u=None,v=None):
  u=self.u if u is None else u;v=self.v if v is None else v;local=u[self.ids];F=np.eye(3)[None,:,:]+np.einsum('pki,pkj->pij',local[:,1:]-local[:,:1],self.G[:,1:]);return self.X+self.O@u,self.O@v,F
 def energy_force(self,u=None):
  _,_,F=self.fields(u);e,P=energy_stress(F,self.mu,self.lam);f=np.zeros_like(self.u);np.add.at(f,self.ids.ravel(),(-np.einsum('pij,pkj->pki',P*self.V[:,None,None],self.G)).reshape(-1,3));return float(self.V@e),f
 def step(self,dt,external=None):
  ext=np.zeros_like(self.u) if external is None else external;_,f=self.energy_force();vh=self.v+.5*dt*(f+ext)/self.mass[:,None];u=self.u+dt*vh;_,f=self.energy_force(u);v=vh+.5*dt*(f+ext)/self.mass[:,None]
  if not np.isfinite(v).all():raise ValueError('nonfinite state')
  self.u,self.v=u,v;self.time+=dt;self.steps+=1
 def metrics(self):
  U,f=self.energy_force();return {'mass':float(self.mass.sum()),'volume':float(self.V.sum()),'U':U,'T':float(.5*np.sum(self.mass[:,None]*self.v**2)),'momentum':np.sum(self.mass[:,None]*self.v,axis=0),'angular':np.sum(self.mass[:,None]*np.cross(self.grid+self.u,self.v),axis=0)}
 def components(self):
  p=len(self.X);r=np.repeat(np.arange(p),4);c=p+self.ids.ravel();a=coo_matrix((np.ones(len(r)),(r,c)),shape=(p+len(self.u),)*2).tocsr();_,lab=connected_components(a,directed=False);return lab[:p],lab[p:]
 def split(self,normal,offset,cut_id=0,front=None,world=False):
  """Accepted geometric unit event. front=(n,d) selects n.x<=d.
  Never imply work-dependent fracture. Existing nonzero history is immutable.
  """
  if cut_id not in range(4):raise ValueError('four-cut capacity exceeded')
  oldfields=self.fields();before=self.metrics();newpolys=[];origin=[];codes=[]
  for i,p in enumerate(self.polys):
   digit=(self.codes[i]//3**cut_id)%3
   if digit:newpolys.append(p.copy());origin.append(i);codes.append(self.codes[i]);continue
   F=oldfields[2][i];trans=oldfields[0][i]-F@self.X[i]
   def mapped(n,d):return (F.T@np.asarray(n),float(d)-np.asarray(n)@trans) if world else (np.asarray(n),float(d))
   pending=[]
   if front is None:pending=[(p,True)]
   else:
    fn,fd=mapped(*front);active=clip(p,fn,fd);inactive=clip(p,-fn,-fd)
    if active is not None:pending.append((active,True))
    if inactive is not None:pending.append((inactive,False))
   cn,cd=mapped(normal,offset)
   for poly,active in pending:
    parts=[(poly,0)] if not active else [(clip(poly,cn,cd),1),(clip(poly,-cn,-cd),2)]
    for child,label in parts:
     if child is not None:newpolys.append(child);origin.append(i);codes.append(self.codes[i]+label*3**cut_id)
  origin=np.asarray(origin);out=self.clone();out.polys=newpolys;out.codes=np.asarray(codes);out.inv=self.inv[origin].copy();out.G=self.G[origin].copy();mv=[moments(p) for p in newpolys];out.V=np.array([x[0] for x in mv]);out.X=np.array([x[1] for x in mv]);out.N=np.einsum('pi,pij->pj',np.c_[np.ones(len(mv)),out.X],out.inv)
  if np.min(out.N)<-1e-11:raise ValueError('clipped centroid outside parent; no renormalization')
  oldids=self.ids[origin];newids=np.empty_like(oldids);flat=oldids.ravel();labs=np.repeat(out.codes,4);order=np.argsort(flat,kind='stable');bounds=np.r_[0,np.cumsum(np.bincount(flat,minlength=len(self.u)))];parents=[]
  for a in range(len(self.u)):
   w=order[bounds[a]:bounds[a+1]];active,inv=np.unique(labs[w],return_inverse=True);adj=np.array([[compatible(i,j) for j in active] for i in active]);nc,groups=connected_components(csr_matrix(adj),directed=False);base=len(parents);parents.extend([a]*nc);newids.ravel()[w]=base+groups[inv]
  parents=np.asarray(parents);out.ids=newids;out.grid=self.grid[parents].copy();out.u=self.u[parents].copy();out.v=self.v[parents].copy();out.rebuild();after=out.metrics();nf=out.fields();expected_x=out.X+np.einsum('pi,pij->pj',out.N,self.u[oldids]);expected_v=np.einsum('pi,pij->pj',out.N,self.v[oldids]);err={'x':float(np.max(abs(nf[0]-expected_x))),'v':float(np.max(abs(nf[1]-expected_v))),'F':float(np.max(abs(nf[2]-oldfields[2][origin])))}
  for k in ['mass','volume','U','T','momentum','angular']:err[k]=float(np.linalg.norm(np.asarray(after[k])-before[k]))
  if max(err[k] for k in ['x','v','F'])>1e-10 or err['mass']>before['mass']*1e-6 or any(err[k]>max(1e-12,abs(before[k])*1e-6) for k in ['U','T']):raise ValueError(('cut transfer failed',err))
  out.history.append({'cut_id':cut_id,'normal':list(normal),'offset':offset,'front':None if front is None else [list(front[0]),front[1]],'world':world,'geometry_only':True,'regions_before':len(self.X),'regions_after':len(out.X),'groups_before':len(self.u),'groups_after':len(out.u),'transfer':err});self.__dict__.update(out.__dict__);return err
 def save(self,path):
  ptr=np.r_[0,np.cumsum([len(p) for p in self.polys])];np.savez_compressed(path,config=json.dumps(self.config),time=self.time,steps=self.steps,history=json.dumps(self.history),poly_ptr=ptr,poly_vertices=np.concatenate(self.polys),**{k:getattr(self,k) for k in ['grid','ids','inv','G','V','X','N','codes','u','v']})
 @classmethod
 def restore(cls,path):
  with np.load(path,allow_pickle=False) as z:
   o=cls.__new__(cls);o.config=json.loads(str(z['config']));E=o.config['E'];nu=o.config['nu'];o.rho=o.config['rho'];o.mu=E/(2*(1+nu));o.lam=E*nu/((1+nu)*(1-2*nu))
   for k in ['grid','ids','inv','G','V','X','N','codes','u','v']:setattr(o,k,z[k].copy())
   ptr=z['poly_ptr'];o.polys=[z['poly_vertices'][a:b].copy() for a,b in zip(ptr[:-1],ptr[1:])];o.time=float(z['time']);o.steps=int(z['steps']);o.history=json.loads(str(z['history']));o.rebuild();return o

def strain_audit(b):
 B=np.zeros((6*len(b.X),3*len(b.u)))
 for p in range(len(b.X)):
  for k,a in enumerate(b.ids[p]):
   x,y,z=b.G[p,k];j=3*a;r=6*p;B[r,j]+=x;B[r+1,j+1]+=y;B[r+2,j+2]+=z;B[r+3,j]+=y;B[r+3,j+1]+=x;B[r+4,j]+=z;B[r+4,j+2]+=x;B[r+5,j+1]+=z;B[r+5,j+2]+=y
 B*=np.repeat(np.sqrt(b.V),6)[:,None];s=np.linalg.svd(B,compute_uv=False);rank=int(np.sum(s>s[0]*1e-9));nc=len(np.unique(b.components()[0]));C=np.eye(6)*b.mu;C[:3,:3]=b.lam;C[:3,:3]+=np.eye(3)*2*b.mu;CB=np.einsum('ij,pjk->pik',C,B.reshape(-1,6,B.shape[1])).reshape(B.shape);K=B.T@CB;im=1/np.sqrt(np.repeat(b.mass,3));maxeig=np.linalg.eigvalsh(K*im[:,None]*im[None,:])[-1]
 return {'rank':rank,'expected_rank':3*len(b.u)-6*nc,'nullity':3*len(b.u)-rank,'components':nc,'nodes':len(b.u),'regions':len(b.X),'minimum_mass_kg':float(b.mass.min()),'linearized_stability_dt_s':float(2/np.sqrt(maxeig))}
