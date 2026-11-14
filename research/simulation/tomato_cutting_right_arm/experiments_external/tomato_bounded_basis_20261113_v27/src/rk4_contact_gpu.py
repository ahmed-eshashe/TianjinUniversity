"""Fourth-order explicit time integration of the unchanged coupled ODE.

Stage forces also update support, tool-work, friction and impulse quadratures.
No stage clips force, changes inertia, modifies material or creates fracture.
"""
import warp as wp
import numpy as np
from scipy.sparse import coo_matrix
from parallel_partition_gpu import ContactGPU as Base,TriangleSurface
from contact_gpu import ledger

@wp.kernel
def stage(ptr:wp.array(dtype=int),ids:wp.array(dtype=int),mi:wp.array(dtype=float),force:wp.array(dtype=wp.vec3),q0:wp.array(dtype=wp.vec3),v0:wp.array(dtype=wp.vec3),q:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),dq:wp.array(dtype=wp.vec3),dv:wp.array(dtype=wp.vec3),fixed:wp.array(dtype=int),support:wp.array(dtype=wp.vec3),dt:float,weight:float,beta:float,last:int,n:int,bad:wp.array(dtype=int),maxspeed:wp.array(dtype=float)):
 i=wp.tid()
 if i<n and bad[0]==0:
  if fixed[i]!=0:support[i]-=dt*weight*force[i];q[i]=q0[i];v[i]=wp.vec3(0.)
  else:
   acc=wp.vec3(0.)
   for j in range(ptr[i],ptr[i+1]):acc+=mi[j]*force[ids[j]]
   vel=v[i];dq[i]+=weight*vel;dv[i]+=weight*acc
   if last!=0:q[i]=q0[i]+dt*dq[i];v[i]=v0[i]+dt*dv[i]
   else:q[i]=q0[i]+beta*dt*vel;v[i]=v0[i]+beta*dt*acc

@wp.kernel
def stage_time(clock:wp.array(dtype=wp.float64),base:wp.array(dtype=wp.float64),delta:wp.float64,bad:wp.array(dtype=int)):
 if bad[0]==0:clock[0]=base[0]+delta

@wp.kernel
def material_speed(ptr:wp.array(dtype=int),ids:wp.array(dtype=int),weights:wp.array(dtype=wp.float64),v:wp.array(dtype=wp.vec3),maximum:wp.array(dtype=float)):
 i=wp.tid();value=wp.vec3d(wp.float64(0.))
 for j in range(ptr[i],ptr[i+1]):value+=weights[j]*wp.vec3d(v[ids[j]])
 # Outward rounding cushion for the float storage of this conservative bound.
 bound=wp.length(value)*wp.float64(1.0000002)+wp.float64(1e-10);wp.atomic_max(maximum,0,float(bound))

class ContactGPU(Base):
 def __init__(self,*args,**kwargs):
  self.rk=False;super().__init__(*args,**kwargs);self.rq=wp.empty_like(self.q);self.rv=wp.empty_like(self.vh);self.dq=wp.empty_like(self.q);self.dv=wp.empty_like(self.vh);self.time0=wp.empty_like(self.clock)
  a=self.aggregates[0];b=a.body;X=b.poly_vertices;owner=np.repeat(np.arange(len(b.polys)),np.diff(b.poly_ptr));N=np.einsum('pi,pij->pj',np.c_[np.ones(len(X)),X],b.inv[owner]);Q0=coo_matrix((N.ravel(),(np.repeat(np.arange(len(X)),4),b.ids[owner].ravel())),shape=(len(X),len(b.u)));self.velocity_map=(Q0@a.E).tocsr();self.speed_ptr=wp.array(self.velocity_map.indptr,dtype=int,device='cuda:0');self.speed_ids=wp.array(self.velocity_map.indices,dtype=int,device='cuda:0');self.speed_weights=wp.array(self.velocity_map.data,dtype=wp.float64,device='cuda:0');self.rk=True
 def one(self):
  if not self.rk:return super().one()
  wp.copy(self.rq,self.q);wp.copy(self.rv,self.vh);wp.copy(self.time0,self.clock);self.dq.zero_();self.dv.zero_()
  for weight,beta,last in [(1/6,.5,0),(1/3,.5,0),(1/3,1.,0),(1/6,1.,1)]:
   wp.launch(material_speed,self.velocity_map.shape[0],[self.speed_ptr,self.speed_ids,self.speed_weights,self.vh,self.maxspeed]);self.contact_force();wp.launch(ledger,self.ns,[self.cf,self.cp,self.power,self.moment,self.impulse,self.angular,self.work,self.diss,weight*self.dt,self.bad]);wp.launch(stage,self.n,[self.mptr,self.midx,self.mi,self.force,self.rq,self.rv,self.q,self.vh,self.dq,self.dv,self.fixed,self.support,self.dt,weight,beta,last,self.n,self.bad,self.maxspeed]);wp.launch(stage_time,1,[self.clock,self.time0,wp.float64(beta*self.dt),self.bad])
