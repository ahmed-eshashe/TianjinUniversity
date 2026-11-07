"""Versioned weighted affine interface frames on the existing research material.

The same eight paired nodes, quadrature, stiffness, bilinear law and eligibility
are retained. Only the co-rotating frame estimator is changed; this changes
finite-deformation forces and therefore requires a fresh trajectory.
"""
import numpy as np
import warp as wp
from tomato_patch_frame_fracture import LiveFractureCandidate
from tomato_bounded_cad_interval import BoundedCADInterval
from tomato_global_pressure import FrozenPressurePacket,PressureAssembly,add_pressure

def frame_coefficients(data):
 from tomato_objective_cohesion_reference import make_patch
 coefficients=np.zeros((len(data['cohesion'].patches),8,2));models=[]
 for i,p in enumerate(data['cohesion'].patches):
  ids=data['pairs'][p['indices']];law=p['law'];m=make_patch(data['x'][ids],p['weights'],p['stiffness'],(law.onset_m,law.failure_m,law.stiffness_n_m));mid=data['x'][ids].mean(1);a,b,c=m['anchors'];u=mid[b]-mid[a];u/=np.linalg.norm(u);v=mid[c]-mid[a];v-=u*(v@u);v/=np.linalg.norm(v);basis=np.column_stack([u,v]);weights=p['weights'];center=weights@mid;coordinates=(mid-center)@basis
  # Weighted affine least-squares map. Translation annihilation is explicit.
  fit=np.linalg.solve(coordinates.T@(weights[:,None]*coordinates),coordinates.T*weights)
  fit-=fit.sum(1)[:,None]*weights[None,:]
  if np.max(abs(fit@coordinates-np.eye(2)))>1e-10 or np.max(abs(fit.sum(1)))>1e-10:raise ValueError('Invalid patch affine fit')
  coefficients[i,:len(ids)]=fit.T;models.append(m)
 return coefficients,models

def configure_patch_frame(holder,data):
 coefficients,_=frame_coefficients(data)
 holder.objective_anchors=wp.array(coefficients,dtype=wp.float64)
 return holder

class PatchFrameLiveCAD(LiveFractureCandidate):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.pressure=FrozenPressurePacket(self.n);self.assembly=PressureAssembly(self.assembly,self.pressure)
 bind_domain=BoundedCADInterval.bind_domain
 domain_motion=BoundedCADInterval.domain_motion
 def force(self,x,dt):
  if max(self.domain_motion(x))>self.domain_bound_m:raise ValueError('Actual target/rigid motion exceeds preregistered fixed material coverage bound')
  super().force(x,dt);self.pressure.evaluate(x);self.norm_sum.zero_();self.maximum_acceleration_defect.zero_();wp.launch(add_pressure,dim=self.n,inputs=[self.pressure.force,self.assembly.free,self.assembly.mass],outputs=[self.rhs,self.norm_sum,self.maximum_acceleration_defect],block_dim=64)
  return float(self.norm_sum.numpy()[0])
 def energy(self,x,dt,*,trial=False):
  if max(self.domain_motion(x))>self.domain_bound_m:
   if trial:return float('inf')
   raise ValueError('Accepted geometry exceeds fixed material coverage bound')
  return super().energy(x,dt,trial=trial)+self.pressure.evaluate(x)
