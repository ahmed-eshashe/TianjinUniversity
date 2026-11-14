"""Nested, finite-footprint enrichment for ONE reference-X normal plane.
Prescribed topology unit fixtures only. No fracture/work rule or knife contact.
"""
import hashlib
import numpy as np
from scipy.interpolate import BSpline
from scipy.linalg import null_space
from scipy.sparse import csr_matrix,kron,eye,hstack,coo_matrix
from scipy.sparse.linalg import splu
from consistent_reference import ConsistentReference
from block_basis import block_basis

class RejectedEvent(RuntimeError):
 def __init__(self,reason,detail=None):super().__init__(reason);self.detail=detail or {};self.reason=reason

def values_and_derivative(t,x):
 n=len(t)-3;B=BSpline(t,np.eye(n),2)(x);low=BSpline(t,np.eye(n+1),1)(x);G=np.zeros_like(B)
 for i in range(n):
  a=t[i+2]-t[i];b=t[i+3]-t[i+1]
  if a>0:G[:,i]+=2/a*low[:,i]
  if b>0:G[:,i]-=2/b*low[:,i+1]
 return csr_matrix(B),csr_matrix(G)

class CutReference(ConsistentReference):
 def __init__(self,X,spacing=.0015,h=.003,E=1e5,nu=.4,fixed=None):
  super().__init__(X,spacing,h,E,nu,fixed);self.base_ng=self.ng;self.base_W=self.W.copy();self.base_G=[g.copy() for g in self.G];self.base_grid=self.grid.copy();self.meta=block_basis(X,spacing,h)[4];self.keys=[];self.plane=None;self.plane_data=None;self.history=[];self.epoch=0;self.translation=np.ones(self.ng)
 def fingerprint(self):
  h=hashlib.sha256();h.update(self.q.tobytes());h.update(self.vg.tobytes());h.update(str((self.steps,self.epoch,self.keys)).encode());return h.hexdigest()
 def _plane_data(self,plane):
  if not self.meta['knots'][0][0]<plane<self.meta['knots'][0][-1]:raise RejectedEvent('plane outside material')
  if np.any(abs(self.X[:,0]-plane)<1e-12):raise RejectedEvent('plane coincides with particle quadrature; unresolved side assignment')
  old=self.meta['knots'][0];n=len(old)-3;count=np.count_nonzero(abs(old-plane)<1e-12);insert=BSpline(old,np.eye(n),2).insert_knot(plane,3-count);t=insert.t;K=insert.c[:len(t)-3];E=null_space(K.T);dims=[len(t)-3,*self.meta['dims'][1:]]
  Bx,Gx=values_and_derivative(t,self.meta['particle_axes'][0]);By,Gy=values_and_derivative(self.meta['knots'][1],self.meta['particle_axes'][1]);Bz,Gz=values_and_derivative(self.meta['knots'][2],self.meta['particle_axes'][2]);W=kron(kron(Bx,By),Bz,format='csr');G=[kron(kron(Gx,By),Bz,format='csr'),kron(kron(Bx,Gy),Bz,format='csr'),kron(kron(Bx,By),Gz,format='csr')];T0=kron(csr_matrix(K),eye(dims[1]*dims[2]),format='csr')
  if abs((W@T0-self.base_W).data).max(initial=0)>1e-12 or max(abs((a@T0-b).data).max(initial=0) for a,b in zip(G,self.base_G))>1e-9:raise RejectedEvent('knot insertion did not preserve base value/gradient')
  return dict(plane=plane,t=t,K=K,E=E,dims=dims,Wfull=W,Gfull=G,T0=T0)
 def _build(self,data,keys):
  nfull=int(np.prod(data['dims']));ny,nz=data['dims'][1:];rr=[];cc=[];vv=[]
  for col,(j,k,e) in enumerate(keys):
   for i,value in enumerate(data['E'][:,e]):
    if abs(value)>0:rr.append((i*ny+j)*nz+k);cc.append(col);vv.append(value)
  extra=coo_matrix((vv,(rr,cc)),shape=(nfull,len(keys))).tocsr();T=hstack([data['T0'],extra],format='csr');B=(data['Wfull']@T).tocsr();G=[(g@T).tocsr() for g in data['Gfull']];M=(self.mass*(B.T@B)).tocsc();eigen=np.linalg.eigvalsh(M.toarray());rank=int(np.sum(eigen>eigen[-1]*1e-12));cond=float(eigen[-1]/eigen[0]) if eigen[0]>0 else float('inf');audit={'dofs':M.shape[0],'mass_rank':rank,'mass_condition':cond if np.isfinite(cond) else None,'smallest_mass_eigenvalue':float(eigen[0]),'largest_mass_eigenvalue':float(eigen[-1])}
  if rank<M.shape[0] or cond>1e8:raise RejectedEvent('cut basis is rank deficient or ill conditioned',audit)
  return {'W':B,'G':G,'M':M,'factor':splu(M),'T':T,'audit':audit}
 def propose(self,rectangle,plane=0.):
  if self.plane is not None and abs(plane-self.plane)>1e-12:raise RejectedEvent('one-plane capacity; no state mutation')
  ylo,yhi,zlo,zhi=map(float,rectangle)
  if ylo>yhi or zlo>zhi:raise RejectedEvent('invalid finite rectangle')
  data=self.plane_data if self.plane_data is not None else self._plane_data(plane);ne=data['E'].shape[1];ty,tz=self.meta['knots'][1:];add=[]
  for j in range(len(ty)-3):
   for k in range(len(tz)-3):
    if ty[j]>=ylo-1e-12 and ty[j+3]<=yhi+1e-12 and tz[k]>=zlo-1e-12 and tz[k+3]<=zhi+1e-12:add.extend((j,k,e) for e in range(ne))
  keys=sorted(set(self.keys)|set(add))
  if keys==self.keys:return {'noop':True,'reason':'no newly covered complete enrichment support','fingerprint':self.fingerprint()}
  candidate=self._build(data,keys);q=np.zeros((self.base_ng+len(keys),3));v=np.zeros_like(q);q[:self.base_ng]=self.q[:self.base_ng];v[:self.base_ng]=self.vg[:self.base_ng];lookup={key:i for i,key in enumerate(keys)}
  for old,key in enumerate(self.keys):q[self.base_ng+lookup[key]]=self.q[self.base_ng+old];v[self.base_ng+lookup[key]]=self.vg[self.base_ng+old]
  x=candidate['W']@q;vel=candidate['W']@v;F=np.stack([g@q for g in candidate['G']],axis=2);from reference import energy_stress
  energy=self.vol*energy_stress(F,self.mu,self.lam)[0].sum()+.5*self.mass*np.sum(vel*vel);oldenergy=self.metrics()['energy'];change={'x':float(abs(x-self.x).max()),'v':float(abs(vel-self.v).max()),'F':float(abs(F-self.F).max()),'energy':float(energy-oldenergy),'energy_before':oldenergy}
  if change['x']>1e-11 or change['v']>1e-10 or change['F']>1e-10 or abs(change['energy'])>max(1e-12,abs(oldenergy)*1e-8):raise RejectedEvent('topology insertion changed existing mechanical state',change)
  return {**candidate,'q':q,'vg':v,'keys':keys,'data':data,'plane':plane,'rectangle':list(rectangle),'transfer':change,'fingerprint':self.fingerprint(),'noop':False}
 def commit(self,p):
  if p['fingerprint']!=self.fingerprint():raise RejectedEvent('stale proposal; mechanical state changed')
  if p['noop']:return False
  for name in ['W','G','M','factor','q','vg','keys','plane']:setattr(self,name,p[name])
  self.plane_data=p['data'];self.T=p['T'];self.ng=len(self.q);self.translation=np.r_[np.ones(self.base_ng),np.zeros(len(self.keys))];self.S=self.W[self.fixed];self.Z=self.factor.solve(self.S.T.toarray()) if self.S.shape[0] else None
  if self.Z is not None:
   H=self.S@self.Z;d,U=np.linalg.eigh(H);iv=np.zeros_like(d);np.divide(1,d,out=iv,where=d>max(d.max()*1e-12,1e-30));self.Hinv=(U*iv)@U.T
  self.epoch+=1;self.history.append({'fixture_only':True,'plane':self.plane,'rectangle':p['rectangle'],'keys_after':len(self.keys),'paid_fracture_area':0.});self.update_state();return True
 def step(self,dt,force0=None,force1=None):
  a,r0=self.acceleration(self.q,force0);vh=self.vg+.5*dt*a;qn=self.q+dt*vh;a1,r1=self.acceleration(qn,force1 if force1 is not None else force0);self.support_impulse+=.5*dt*(self.translation@(r0+r1));self.support_moment+=.5*dt*(np.cross(self.q,r0).sum(0)+np.cross(qn,r1).sum(0));self.q=qn;self.vg=vh+.5*dt*a1;self.time+=dt;self.steps+=1;self.update_state()
 def refined_coefficients(self):return self.T@self.q,self.T@self.vg
 def set_full_piece_state(self,left_q,right_q,left_v=None,right_v=None):
  if self.plane_data is None or len(self.keys)!=self.plane_data['E'].shape[1]*self.meta['dims'][1]*self.meta['dims'][2]:raise ValueError('independent piece initialization requires full unit cut')
  target=np.concatenate([left_q.reshape(-1,3),right_q.reshape(-1,3)]);targetv=np.zeros_like(target) if left_v is None else np.concatenate([left_v.reshape(-1,3),right_v.reshape(-1,3)]);self.q=np.linalg.solve(self.T.toarray(),target);self.vg=np.linalg.solve(self.T.toarray(),targetv);self.update_state()
 def face_jump(self,yz):
  if self.plane_data is None:return np.zeros((len(yz),3))
  Q,_=self.refined_coefficients();Q=Q.reshape(*self.plane_data['dims'],3);indices=np.flatnonzero(abs(self.plane_data['t']-self.plane)<1e-12);left=int(indices[0]-1);right=left+1;ty,tz=self.meta['knots'][1:];Y=BSpline(ty,np.eye(len(ty)-3),2)(np.asarray(yz)[:,0]);Z=BSpline(tz,np.eye(len(tz)-3),2)(np.asarray(yz)[:,1]);return np.einsum('nj,nk,jkc->nc',Y,Z,Q[right]-Q[left])
 def save(self,path):
  np.savez_compressed(path,X=self.X,q=self.q,vg=self.vg,x=self.x,v=self.v,F=self.F,keys=np.array(self.keys,dtype=int).reshape(-1,3),plane=np.nan if self.plane is None else self.plane,time=self.time,steps=self.steps,epoch=self.epoch)
