"""Stable node-owned force accumulation for the full tomato integration."""
import warp as wp
from newton._src.solvers.vbd.particle_vbd_kernels import evaluate_spring_force_and_hessian

@wp.kernel
def gather(color:int,colors:wp.array[int],x:wp.array[wp.vec3],previous:wp.array[wp.vec3],dt:float,
 spring_offsets:wp.array[int],spring_ids:wp.array[int],spring_pairs:wp.array[int],spring_rest:wp.array[float],spring_k:wp.array[float],spring_d:wp.array[float],
 patch_offsets:wp.array[int],patch_ids:wp.array[int],pairs:wp.array2d[wp.vec2i],rest:wp.array2d[wp.vec3],weights:wp.array2d[float],counts:wp.array[int],stiffness:wp.array[wp.mat33],law:wp.array[wp.vec3],history:wp.array[wp.vec2],eligible:wp.array[int],invalid:wp.array[int],
 cell_offsets:wp.array[int],cell_ids:wp.array[int],cells:wp.array[wp.vec4i],volumes:wp.array[float],volume_invalid:wp.array[int],forces:wp.array[wp.vec3],hessians:wp.array[wp.mat33]):
 node=wp.tid()
 if colors[node]==color:
  force=wp.vec3(0.);hessian=wp.mat33(0.)
  for index in range(spring_offsets[node],spring_offsets[node+1]):
   f,h=evaluate_spring_force_and_hessian(node,spring_ids[index],dt,x,previous,spring_pairs,spring_rest,spring_k,spring_d);force+=f;hessian+=h
  for index in range(patch_offsets[node],patch_offsets[node+1]):
   patch=patch_ids[index];k=stiffness[patch];u=float(0.)
   for j in range(counts[patch]):
    pair=pairs[patch,j];g=x[pair[1]]-x[pair[0]]-rest[patch,j];e=wp.vec3(wp.max(g[0],0.),g[1],g[2]);u+=.5*weights[patch,j]*wp.dot(e,k*e)
    if eligible[patch]!=0 and history[patch][1]<1. and g[0]<-1.e-12 and wp.length(wp.vec2(g[1],g[2]))>1.e-12:wp.atomic_add(invalid,0,1)
   q=wp.sqrt(wp.max(2.*u/law[patch][0],0.));a=law[patch][1];b=law[patch][2];old=history[patch];d=old[1];derivative=float(0.)
   if eligible[patch]!=0 and q>=old[0]:
    if q>=b:d=1.
    elif q>a:
     candidate=b*(q-a)/(q*(b-a))
     if candidate>=d:d=candidate;derivative=b*a/((b-a)*q*q)
   gradient=wp.vec3(0.);h=wp.mat33(0.)
   for j in range(counts[patch]):
    pair=pairs[patch,j];sign=float(0.)
    if node==pair[0]:sign=-1.
    if node==pair[1]:sign=1.
    if sign!=0.:
     g=x[pair[1]]-x[pair[0]]-rest[patch,j];e=wp.vec3(wp.max(g[0],0.),g[1],g[2]);gradient+=sign*weights[patch,j]*(k*e);block=k
     if g[0]<0.:block[0,0]=0.
     h+=weights[patch,j]*block
   h=(1.-d)*h
   if derivative>0.:h-=derivative/(law[patch][0]*q)*wp.outer(gradient,gradient)
   force-=(1.-d)*gradient;hessian+=h
  for index in range(cell_offsets[node],cell_offsets[node+1]):
   i=cell_ids[index];ids=cells[i];d1=x[ids[1]]-x[ids[0]];d2=x[ids[2]]-x[ids[0]];d3=x[ids[3]]-x[ids[0]];v=volumes[i];ratio=wp.dot(d1,wp.cross(d2,d3))/(6.*v)
   if ratio<=.1:wp.atomic_add(volume_invalid,0,1)
   elif ratio<.5:
    r=(ratio-.1)/.4;prime=(1.-1./r)/.4;second=1./(r*r*.16);g1=wp.cross(d2,d3)/(6.*v);g2=wp.cross(d3,d1)/(6.*v);g3=wp.cross(d1,d2)/(6.*v);g=-g1-g2-g3
    if node==ids[1]:g=g1
    elif node==ids[2]:g=g2
    elif node==ids[3]:g=g3
    force-=10000.*v*prime*g;hessian+=10000.*v*second*wp.outer(g,g)
  forces[node]=force;hessians[node]=hessian

def adjacency(registry,node_count):
 ids=[[] for _ in range(node_count)]
 for index,nodes in enumerate(registry):
  for node in sorted(set(nodes)):ids[node].append(index)
 offsets=[0];flat=[]
 for rows in ids:flat.extend(rows);offsets.append(len(flat))
 return wp.array(offsets,dtype=int),wp.array(flat,dtype=int)
