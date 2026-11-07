# Versioned research extension: remainder-side volume-backed material frame.
# Exact derivatives include the frame's dependence on remainder nodes.
# This is an asymmetric finite-deformation constitutive choice, not calibration.
# Fresh trajectories required. Traction quadrature and bilinear parameters unchanged.
"""Versioned volume-backed element interface frames on the existing research material.

The same eight paired nodes, quadrature, stiffness, bilinear law and eligibility
are retained. Only the co-rotating frame estimator is changed; this changes
finite-deformation forces and therefore requires a fresh trajectory.
"""
import numpy as np
import warp as wp
from tomato_master_frame_fracture import LiveFractureCandidate
from tomato_bounded_cad_interval import BoundedCADInterval
from tomato_global_pressure import FrozenPressurePacket,PressureAssembly,add_pressure

def frame_support(data):
 from tomato_objective_cohesion_reference import make_patch
 import itertools
 pairs=data['pairs'];lookup={int(a):i for i,(a,b) in enumerate(pairs)}
 tetra_faces={tuple(sorted(t[list(c)])) for t in data['cells'] for c in itertools.combinations(range(4),3)}
 piece=data['design']['pieces'][0];faces=[]
 for face,tag in zip(piece['triangles'],piece['face_tags']):
  if tag!='cut' or tuple(sorted(face)) not in tetra_faces:continue
  partner=[int(pairs[lookup[int(a)],1]) for a in face]
  if tuple(sorted(partner)) in tetra_faces:faces.append(face)
 faces=np.asarray(faces,int)
 if not len(faces):raise ValueError('No jointly volume-backed interface face')
 canonical=np.asarray([node['position_m'] for node in data['design']['nodes']]);centers=canonical[faces].mean(1);all_pairs=np.zeros((47,16,2),np.int32);coefficients=np.zeros((47,16,2));all_weights=np.zeros((47,16));counts=[];models=[];supports=[]
 for i,p in enumerate(data['cohesion'].patches):
  original=data['pairs'][p['indices']];law=p['law'];m=make_patch(canonical[original],p['weights'],p['stiffness'],(law.onset_m,law.failure_m,law.stiffness_n_m));mid=canonical[original].mean(1);a,b,c=m['anchors'];u=mid[b]-mid[a];u/=np.linalg.norm(u);v=mid[c]-mid[a];v-=u*(v@u);v/=np.linalg.norm(v);basis=np.column_stack([u,v])
  anchor=np.array(data['design']['interface_patches'][i]['anchor_yz_m']);face=faces[np.argmin(np.linalg.norm(centers[:,1:]-anchor,axis=1))];nodes=list(p['indices']);support_ids=[]
  for node in face:
   index=lookup[int(node)]
   if index not in nodes:nodes.append(index)
   support_ids.append(nodes.index(index))
  all_pairs[i,:len(nodes)]=pairs[nodes];counts.append(len(nodes));all_weights[i,:len(original)]=p['weights'];points=canonical[face];coordinates=(points-points.mean(0))@basis;fit=np.linalg.solve(coordinates.T@coordinates,coordinates.T);fit-=fit.sum(1)[:,None]/3
  if np.max(abs(fit@coordinates-np.eye(2)))>1e-10:raise ValueError('Invalid face deformation map')
  coefficients[i,support_ids]=fit.T;models.append(m);supports.append(face.tolist())
 return all_pairs,np.array(counts,np.int32),coefficients,all_weights,models,supports

def configure_patch_frame(holder,data):
 pairs,counts,coefficients,weights,_,_=frame_support(data)
 holder.pairs=wp.array(pairs,dtype=wp.vec2i);holder.counts=wp.array(counts,dtype=int);holder.objective_weights=wp.array(weights,dtype=wp.float64);holder.objective_anchors=wp.array(coefficients,dtype=wp.float64)
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
