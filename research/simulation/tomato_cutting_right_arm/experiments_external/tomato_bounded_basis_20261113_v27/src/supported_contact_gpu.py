"""Exact constrained reduced inertia for the selected contact integrator.

The inverse is assembled blockwise from M_ff, never by relumping or by zeroing
rows of an unconstrained inverse. Fixed-row reactions include M_fixed,free a.
"""
import numpy as np,warp as wp
from scipy.sparse import coo_matrix
from scipy.linalg import cho_factor,cho_solve
from compact_contact_gpu import ContactGPU as Base
from rk4_contact_gpu import stage_time,material_speed
from contact_gpu import ledger

@wp.kernel
def acceleration(ptr:wp.array(dtype=int),ids:wp.array(dtype=int),values:wp.array(dtype=wp.float64),force:wp.array(dtype=wp.vec3),acc:wp.array(dtype=wp.vec3d),bad:wp.array(dtype=int)):
 i=wp.tid();a=wp.vec3d(wp.float64(0.))
 if bad[0]==0:
  for j in range(ptr[i],ptr[i+1]):a+=values[j]*wp.vec3d(force[ids[j]])
 acc[i]=a

@wp.kernel
def constrained_stage(mptr:wp.array(dtype=int),mids:wp.array(dtype=int),mass:wp.array(dtype=wp.float64),force:wp.array(dtype=wp.vec3),acc:wp.array(dtype=wp.vec3d),q0:wp.array(dtype=wp.vec3),v0:wp.array(dtype=wp.vec3),q:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),dq:wp.array(dtype=wp.vec3),dv:wp.array(dtype=wp.vec3),fixed:wp.array(dtype=int),support:wp.array(dtype=wp.vec3),dt:float,weight:float,beta:float,last:int,bad:wp.array(dtype=int)):
 i=wp.tid()
 if bad[0]==0:
  if fixed[i]!=0:
   reaction=-wp.vec3d(force[i])
   for j in range(mptr[i],mptr[i+1]):reaction+=mass[j]*acc[mids[j]]
   support[i]+=dt*weight*wp.vec3(reaction);q[i]=q0[i];v[i]=wp.vec3(0.)
  else:
   vel=v[i];a=wp.vec3(acc[i]);dq[i]+=weight*vel;dv[i]+=weight*a
   if last!=0:q[i]=q0[i]+dt*dq[i];v[i]=v0[i]+dt*dv[i]
   else:q[i]=q0[i]+beta*dt*vel;v[i]=v0[i]+beta*dt*a

def constrained_inverse(a,fixed):
 fixed=np.asarray(fixed,bool);rows=[];cols=[];values=[]
 for block in a.blocks:
  free=block[~fixed[block]]
  if not len(free):continue
  mf=a.M[free][:,free].toarray();inverse=cho_solve(cho_factor(mf,lower=True),np.eye(len(free)));ii,jj=np.nonzero(inverse);rows.extend(free[ii]);cols.extend(free[jj]);values.extend(inverse[ii,jj])
 return coo_matrix((values,(rows,cols)),shape=a.M.shape).tocsr()

class ContactGPU(Base):
 supports_coupled_constraints=True
 def __init__(self,*args,**kwargs):
  self.constrained=False;super().__init__(*args,**kwargs);a=self.aggregates[0];self.exact_inverse=constrained_inverse(a,self.fixed.numpy()[:self.n].astype(bool))
  for prefix,mat in [('ci',self.exact_inverse),('cm',a.M)]:
   for suffix,value,dtype in [('ptr',mat.indptr,int),('ids',mat.indices,int),('value',mat.data,wp.float64)]:setattr(self,prefix+suffix,wp.array(value,dtype=dtype,device='cuda:0'))
  self.acc=wp.empty(self.n,dtype=wp.vec3d,device='cuda:0');self.constrained=True
 def contact_ledger(self,weight):
  wp.launch(ledger,self.ns,[self.cf,self.cp,self.power,self.moment,self.impulse,self.angular,self.work,self.diss,weight*self.dt,self.bad])
 def one(self):
  if not self.constrained:return super().one()
  wp.copy(self.rq,self.q);wp.copy(self.rv,self.vh);wp.copy(self.time0,self.clock);self.dq.zero_();self.dv.zero_()
  for weight,beta,last in [(1/6,.5,0),(1/3,.5,0),(1/3,1.,0),(1/6,1.,1)]:
   wp.launch(material_speed,self.velocity_map.shape[0],[self.speed_ptr,self.speed_ids,self.speed_weights,self.vh,self.maxspeed]);self.contact_force();self.contact_ledger(weight);wp.launch(acceleration,self.n,[self.ciptr,self.ciids,self.civalue,self.force,self.acc,self.bad]);wp.launch(constrained_stage,self.n,[self.cmptr,self.cmids,self.cmvalue,self.force,self.acc,self.rq,self.rv,self.q,self.vh,self.dq,self.dv,self.fixed,self.support,self.dt,weight,beta,last,self.bad]);wp.launch(stage_time,1,[self.clock,self.time0,wp.float64(beta*self.dt),self.bad])
