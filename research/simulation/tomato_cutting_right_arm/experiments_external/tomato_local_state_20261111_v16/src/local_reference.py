import copy,json
from itertools import product
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.sparse import coo_matrix,csr_matrix
from scipy.sparse.csgraph import connected_components


def energy_stress(F,mu,lam):
 J=np.linalg.det(F)
 if not np.isfinite(J).all() or J.min()<=.1 or J.max()>=10:raise ValueError('inadmissible material volume')
 lj=np.log(J);P=mu*F+(lam*lj-mu)[:,None,None]*np.linalg.inv(F).transpose(0,2,1)
 e=.5*mu*((F*F).sum((1,2))-3)-mu*lj+.5*lam*lj*lj
 return e,P


def quadrature(n=2,h=.006,order=2,cells=None):
 corners=np.array(list(product([0,1],repeat=3)),int)
 if cells is None:cells=np.array(list(product(range(n),repeat=3)),int)
 coords=(cells[:,None,:]+corners).reshape(-1,3);nodes,inv=np.unique(coords,axis=0,return_inverse=True);cell_ids=inv.reshape(-1,8);grid=(nodes-n/2)*h
 r,w=leggauss(order);r=(r+1)*.5;w=w*.5;local=np.array(list(product(r,repeat=3)));weights=np.array([np.prod(a) for a in product(w,repeat=3)])
 f=np.where(corners[None,:,:]==1,local[:,None,:],1-local[:,None,:]);N=f.prod(2);G=np.empty((*N.shape,3))
 for j in range(3):G[:,:,j]=np.where(corners[None,:,j]==1,1.,-1.)*f[:,:,np.arange(3)!=j].prod(2)/h
 # Enforce exact algebraic partition in the subtraction form used by GPU.
 G[:,0,:]=-G[:,1:,:].sum(1)
 X=((cells[:,None,:]+local[None,:,:])-n/2)*h
 return dict(X=X.reshape(-1,3),grid=grid,ids=np.repeat(cell_ids,order**3,axis=0),N=np.tile(N,(len(cells),1)),G=np.tile(G,(len(cells),1,1)),V=np.tile(weights*h**3,len(cells)),cell_index=np.repeat(np.arange(len(cells)),order**3),cells=cells,h=h,n=n,order=order)


def compatible(a,b):
 for k in range(4):
  x=(int(a)//3**k)%3;y=(int(b)//3**k)%3
  if x*y==2:return False
 return True

class LocalBody:
 def __init__(self,n=2,h=.006,order=2,E=1e5,nu=.4,rho=1000.,cells=None):
  for k,v in quadrature(n,h,order,cells).items():setattr(self,k,v)
  self.config=dict(n=n,h=h,order=order,E=E,nu=nu,rho=rho);self.mu=E/(2*(1+nu));self.lam=E*nu/((1+nu)*(1-2*nu));self.rho=rho
  self.u=np.zeros_like(self.grid);self.v=np.zeros_like(self.grid);self.codes=np.zeros(len(self.X),int);self.original_ids=self.ids.copy();self.time=0.;self.steps=0;self.history=[];self.rebuild()
 def rebuild(self):
  self.mass=np.bincount(self.ids.ravel(),weights=(self.rho*self.V[:,None]*self.N).ravel(),minlength=len(self.u));assert self.mass.min()>0
  edges=np.argsort(self.ids.ravel(),kind='stable');counts=np.bincount(self.ids.ravel(),minlength=len(self.u));self.ptr=np.r_[0,np.cumsum(counts)].astype(np.int32);self.edge_p=np.repeat(np.arange(len(self.X)),8)[edges].astype(np.int32);self.edge_g=self.G.reshape(-1,3)[edges]
  self.O=coo_matrix((self.N.ravel(),(np.repeat(np.arange(len(self.X)),8),self.ids.ravel())),shape=(len(self.X),len(self.u))).tocsr()
 def clone(self):
  out=copy.copy(self)
  for f in ['u','v','codes','ids','mass','grid']:setattr(out,f,getattr(self,f).copy())
  out.history=copy.deepcopy(self.history);return out
 def fields(self,u=None,v=None):
  u=self.u if u is None else u;v=self.v if v is None else v;values=u[self.ids];F=np.eye(3)[None,:,:]+np.einsum('pki,pkj->pij',values[:,1:]-values[:,:1],self.G[:,1:]);return self.X+self.O@u,self.O@v,F
 def energy_force(self,u=None):
  _,_,F=self.fields(u);e,P=energy_stress(F,self.mu,self.lam);weighted=self.V[:,None,None]*P;out=np.zeros_like(self.u)
  np.add.at(out,self.ids.ravel(),(-np.einsum('pij,pkj->pki',weighted,self.G)).reshape(-1,3))
  return float(self.V@e),out
 def step(self,dt,external=None):
  ext=np.zeros_like(self.u) if external is None else np.asarray(external);_,f=self.energy_force();vh=self.v+.5*dt*(f+ext)/self.mass[:,None];un=self.u+dt*vh;_,f1=self.energy_force(un);vn=vh+.5*dt*(f1+ext)/self.mass[:,None]
  if not np.isfinite(un).all() or not np.isfinite(vn).all():raise ValueError('nonfinite mechanical state')
  self.u,self.v=un,vn;self.time+=dt;self.steps+=1
 def metrics(self):
  U,_=self.energy_force();return {'mass':float(self.mass.sum()),'U':U,'T':float(.5*np.sum(self.mass[:,None]*self.v*self.v)),'momentum':np.sum(self.mass[:,None]*self.v,axis=0),'angular':np.sum(self.mass[:,None]*np.cross(self.grid+self.u,self.v),axis=0)}
 def topology(self,codes,commit=True):
  codes=np.asarray(codes,int)
  if codes.shape!=self.codes.shape or np.any(codes<0) or np.any(codes>=81):raise ValueError('four-cut capacity')
  for k in range(4):
   old=(self.codes//3**k)%3;new=(codes//3**k)%3
   if np.any((old!=0)&(new!=old)):raise ValueError('history cannot be erased or relabelled')
  newids=np.empty_like(self.ids);parents=[];flat=self.ids.ravel();newflat=newids.ravel();pcodes=np.repeat(codes,8)
  order=np.argsort(flat,kind='stable');bounds=np.r_[0,np.cumsum(np.bincount(flat,minlength=len(self.u)))]
  for old in range(len(self.u)):
   where=order[bounds[old]:bounds[old+1]];active,inverse=np.unique(pcodes[where],return_inverse=True);adj=np.array([[compatible(a,b) for b in active] for a in active]);_,labels=connected_components(csr_matrix(adj),directed=False)
   mapping={c:len(parents)+j for j,c in enumerate(np.unique(labels))};parents.extend([old]*len(mapping));newflat[where]=[mapping[c] for c in labels[inverse]]
  parents=np.asarray(parents);out=self.clone();out.ids=newids;out.u=self.u[parents].copy();out.v=self.v[parents].copy();out.grid=self.grid[parents].copy();out.codes=codes.copy();out.rebuild()
  oldfields=self.fields();newfields=out.fields();before,after=self.metrics(),out.metrics();errors={f:float(np.max(abs(a-b))) for f,a,b in zip(['x','v','F'],oldfields,newfields)};errors.update(mass=after['mass']-before['mass'],U=after['U']-before['U'],T=after['T']-before['T'],momentum=float(np.linalg.norm(after['momentum']-before['momentum'])),angular=float(np.linalg.norm(after['angular']-before['angular'])))
  if max(errors[f] for f in ['x','v','F'])>1e-12 or abs(errors['mass'])>before['mass']*1e-6 or abs(errors['U'])>max(1e-12,abs(before['U'])*1e-8) or abs(errors['T'])>max(1e-12,abs(before['T'])*1e-8):raise ValueError(('topology transfer failed',errors))
  out.history.append({'groups_before':len(self.u),'groups_after':len(out.u),'errors':errors,'geometry_only':True})
  if commit:self.__dict__.update(out.__dict__)
  return out,errors
 def components(self):
  npart=len(self.X);r=np.repeat(np.arange(npart),8);c=npart+self.ids.ravel();a=coo_matrix((np.ones(len(r)),(r,c)),shape=(npart+len(self.u),)*2).tocsr();_,lab=connected_components(a,directed=False);_,lab=np.unique(lab[:npart],return_inverse=True);return lab
 def save(self,path):
  np.savez_compressed(path,config=json.dumps(self.config),cells=self.cells,u=self.u,v=self.v,grid=self.grid,ids=self.ids,codes=self.codes,time=self.time,steps=self.steps,history=json.dumps(self.history))
 @classmethod
 def restore(cls,path):
  with np.load(path,allow_pickle=False) as z:
   b=cls(cells=z['cells'],**json.loads(str(z['config'])))
   for f in ['u','v','grid','ids','codes']:setattr(b,f,z[f].copy())
   b.time=float(z['time']);b.steps=int(z['steps']);b.history=json.loads(str(z['history']));b.rebuild();return b
