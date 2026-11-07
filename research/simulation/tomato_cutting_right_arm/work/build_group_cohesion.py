from pathlib import Path
r=Path('rl');base=(r/'tomato_native_cohesive_operator.py').read_text();method=base[base.index(' def _solve_particle_iteration('):]
method=method.replace('dim=self.pairs.shape[0],inputs=[color,model.particle_colors,state_in.particle_q,self.pairs,self.rest,self.stiffness,self.law,self.history,self.eligible,self.invalid]', 'dim=self.pairs.shape[0],inputs=[color,model.particle_colors,state_in.particle_q,self.pairs,self.rest,self.weights,self.counts,self.nodes,self.node_counts,self.stiffness,self.law,self.history,self.eligible,self.invalid]').replace('wp.launch(cohesive_blocks,','wp.launch(group_blocks,')
head='''"""Shared-budget, multi-quadrature fixed-frame cohesion for guarded native coupons.

All vertices in a patch must have distinct colors. Not an objective rotating
material frame or a volumetric tomato calibration.
"""
import warp as wp
from newton import State,Contacts
from newton._src.solvers.vbd.solver_vbd import (SolverVBD,SolverBase,accumulate_particle_body_contact_force_and_hessian,
 accumulate_spring_force_and_hessian,accumulate_self_contact_force_and_hessian,solve_elasticity_tile,solve_elasticity,TILE_SIZE_TRI_MESH_ELASTICITY_SOLVE)

@wp.kernel
def group_blocks(color:int,colors:wp.array[int],x:wp.array[wp.vec3],pairs:wp.array2d[wp.vec2i],rest:wp.array2d[wp.vec3],weights:wp.array2d[float],counts:wp.array[int],
 nodes:wp.array2d[int],node_counts:wp.array[int],stiffness:wp.array[wp.mat33],law:wp.array[wp.vec3],history:wp.array[wp.vec2],eligible:wp.array[int],invalid:wp.array[int],forces:wp.array[wp.vec3],hessians:wp.array[wp.mat33]):
 patch=wp.tid();k=stiffness[patch];u=float(0.)
 for j in range(counts[patch]):
  pair=pairs[patch,j];g=x[pair[1]]-x[pair[0]]-rest[patch,j];e=wp.vec3(wp.max(g[0],0.),g[1],g[2]);u+=.5*weights[patch,j]*wp.dot(e,k*e)
  if g[0]<-1.e-12 and wp.length(wp.vec2(g[1],g[2]))>1.e-12:wp.atomic_add(invalid,0,1)
 q=wp.sqrt(wp.max(2.*u/law[patch][0],0.));a=law[patch][1];b=law[patch][2];old=history[patch];d=old[1];derivative=float(0.)
 if eligible[patch]!=0 and q>=old[0]:
  if q>=b:d=1.
  elif q>a:
   candidate=b*(q-a)/(q*(b-a))
   if candidate>=d:d=candidate;derivative=b*a/((b-a)*q*q)
 for n in range(node_counts[patch]):
  node=nodes[patch,n]
  if colors[node]==color:
   gradient=wp.vec3(0.);h=wp.mat33(0.)
   for j in range(counts[patch]):
    pair=pairs[patch,j];sign=float(0.)
    if node==pair[0]:sign=-1.
    if node==pair[1]:sign=1.
    if sign!=0.:
     g=x[pair[1]]-x[pair[0]]-rest[patch,j];e=wp.vec3(wp.max(g[0],0.),g[1],g[2]);gradient+=sign*weights[patch,j]*(k*e)
     block=k
     if g[0]<0.:block[0,0]=0.
     h+=weights[patch,j]*block
   h=(1.-d)*h
   if derivative>0.:h-=derivative/(law[patch][0]*q)*wp.outer(gradient,gradient)
   wp.atomic_add(forces,node,-(1.-d)*gradient);wp.atomic_add(hessians,node,h)

class GroupCohesiveVBD(SolverVBD):
 def configure(self,pairs,rest,weights,counts,nodes,node_counts,stiffness,law,history,eligible):
  self.pairs=pairs;self.rest=rest;self.weights=weights;self.counts=counts;self.nodes=nodes;self.node_counts=node_counts;self.stiffness=stiffness;self.law=law;self.history=history;self.eligible=eligible
  self.invalid=wp.zeros(1,dtype=int,device=self.device)
  colors=self.model.particle_colors.numpy().tolist()
  for ids,n in zip(nodes.numpy().tolist(),node_counts.numpy().tolist()):
   if len({colors[i] for i in ids[:n]})!=n:raise ValueError('Patch clique coloring required')
  for w,n in zip(weights.numpy().tolist(),counts.numpy().tolist()):
   if any(v<=0 for v in w[:n]) or abs(sum(w[:n])-1.)>1.e-6:raise ValueError('Normalized positive patch quadrature required')
'''
(r/'tomato_native_group_cohesion.py').write_text(head+'\n'+method)
