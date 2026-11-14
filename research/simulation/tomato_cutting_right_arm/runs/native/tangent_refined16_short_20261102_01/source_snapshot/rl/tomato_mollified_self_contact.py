"""Current-geometry, float64 contact with an IPC-style parallel-edge mollifier.

Uses the installed Newton normal potential, not IPC's complete solver/barrier.
Mollifier m(s)=2s/eps-(s/eps)^2, eps=1e-3*|u_rest|^2*|v_rest|^2,
from the primary IPC Toolkit formulation. The derivative of m is included in
forces. Positive contact blocks are a preconditioner, not the exact Hessian.
"""
import warp as wp
from newton._src.geometry.tri_mesh_collision import TriMeshCollisionInfo
from tomato_canonical_self_contact import barycentric_closest,force_norm,precise_embedding
from tomato_embedded_self_contact import EmbeddedSelfContact

@wp.func
def closest_segments(a:wp.vec3d,b:wp.vec3d,c:wp.vec3d,d:wp.vec3d):
 u=b-a;v=d-c;w=a-c;aa=wp.dot(u,u);bb=wp.dot(u,v);cc=wp.dot(v,v);dd=wp.dot(u,w);ee=wp.dot(v,w);den=aa*cc-bb*bb;zero=wp.float64(0.);one=wp.float64(1.)
 s=zero;t=wp.clamp(ee/cc,zero,one);delta=a-c-t*v;best=wp.dot(delta,delta)
 tt=wp.clamp(wp.dot(b-c,v)/cc,zero,one);delta=b-c-tt*v;value=wp.dot(delta,delta)
 if value<best:best=value;s=one;t=tt
 ss=wp.clamp(-dd/aa,zero,one);delta=a+ss*u-c;value=wp.dot(delta,delta)
 if value<best:best=value;s=ss;t=zero
 ss=wp.clamp(wp.dot(d-a,u)/aa,zero,one);delta=a+ss*u-d;value=wp.dot(delta,delta)
 if value<best:best=value;s=ss;t=one
 if den>wp.float64(1.e-14)*aa*cc:
  ss=(bb*ee-cc*dd)/den;tt=(aa*ee-bb*dd)/den
  if ss>=zero and ss<=one and tt>=zero and tt<=one:
   delta=a+ss*u-c-tt*v;value=wp.dot(delta,delta)
   if value<best:s=ss;t=tt
 return wp.vec2d(s,t)

@wp.func
def skew(v:wp.vec3d):
 z=wp.float64(0.);return wp.mat33d(z,-v[2],v[1],v[2],z,-v[0],-v[1],v[0],z)

@wp.kernel
def candidate_pairs(rest:wp.array[wp.vec3d],triangles:wp.array2d[int],edges:wp.array2d[int],info_array:wp.array[TriMeshCollisionInfo],capacity:int,endpoints:wp.array[wp.vec4i],kind:wp.array[int],threshold:wp.array[wp.float64],count:wp.array[int],invalid:wp.array[int]):
 source=wp.tid();info=info_array[0]
 if source<info.vertex_colliding_triangles_count.shape[0]:
  n=wp.min(info.vertex_colliding_triangles_count[source],info.vertex_colliding_triangles_buffer_sizes[source]);offset=info.vertex_colliding_triangles_offsets[source]
  for j in range(n):
   vertex=info.vertex_colliding_triangles[2*(offset+j)];t=info.vertex_colliding_triangles[2*(offset+j)+1];at=wp.atomic_add(count,0,1)
   if at>=capacity:wp.atomic_add(invalid,0,1)
   else:endpoints[at]=wp.vec4i(vertex,triangles[t,0],triangles[t,1],triangles[t,2]);kind[at]=0;threshold[at]=wp.float64(0.)
 if source<info.edge_colliding_edges_count.shape[0]:
  n=wp.min(info.edge_colliding_edges_count[source],info.edge_colliding_edges_buffer_sizes[source]);offset=info.edge_colliding_edges_offsets[source]
  for j in range(n):
   e0=info.edge_colliding_edges[2*(offset+j)];e1=info.edge_colliding_edges[2*(offset+j)+1]
   if e0<e1:
    a=edges[e0,2];b=edges[e0,3];c=edges[e1,2];d=edges[e1,3];at=wp.atomic_add(count,0,1)
    if at>=capacity:wp.atomic_add(invalid,0,1)
    else:
     endpoints[at]=wp.vec4i(a,b,c,d);kind[at]=1;u=rest[b]-rest[a];v=rest[d]-rest[c];threshold[at]=wp.float64(.001)*wp.dot(u,u)*wp.dot(v,v)

@wp.kernel
def current_contact(proxy:wp.array[wp.vec3d],embedding:wp.array[wp.vec4i],weights:wp.array[wp.vec4d],endpoints:wp.array[wp.vec4i],kind:wp.array[int],threshold:wp.array[wp.float64],count:wp.array[int],capacity:int,radius:wp.float64,stiffness:wp.float64,force:wp.array[wp.vec3d],hessian:wp.array[wp.mat33d],proxy_force:wp.array[wp.vec3d],proxy_hessian:wp.array[wp.mat33d],energy:wp.array[wp.float64],invalid:wp.array[int]):
 record=wp.tid()
 if record<wp.min(count[0],capacity):
  ids=endpoints[record];p0=proxy[ids[0]];p1=proxy[ids[1]];p2=proxy[ids[2]];p3=proxy[ids[3]];coeff=wp.vec4d(0.);m=wp.float64(1.);dm=wp.float64(0.);u=wp.vec3d(0.);v=wp.vec3d(0.);gu=wp.vec3d(0.);gv=wp.vec3d(0.)
  if kind[record]==0:
   bary=barycentric_closest(p1,p2,p3,p0);coeff=wp.vec4d(wp.float64(1.),-bary[0],-bary[1],-bary[2])
  else:
   st=closest_segments(p0,p1,p2,p3);coeff=wp.vec4d(wp.float64(1.)-st[0],st[0],-wp.float64(1.)+st[1],-st[1]);u=p1-p0;v=p3-p2;cross=wp.cross(u,v);squared=wp.dot(cross,cross);eps=threshold[record]
   if squared<eps:
    ratio=squared/eps;m=ratio*(wp.float64(2.)-ratio);dm=wp.float64(2.)*(wp.float64(1.)-ratio)/eps;gu=wp.float64(2.)*wp.cross(v,cross);gv=wp.float64(2.)*wp.cross(cross,u)
  delta=coeff[0]*p0+coeff[1]*p1+coeff[2]*p2+coeff[3]*p3;distance=wp.length(delta)
  if distance<=wp.float64(1.e-8):wp.atomic_add(invalid,0,1)
  elif distance<radius:
   n=delta/distance;first,second,value=force_norm(distance,radius,stiffness);f=-first*n;normal_h=second*wp.outer(n,n);wp.atomic_add(energy,0,m*value)
   for slot in range(16):
    node=embedding[ids[slot//4]][slot%4];duplicate=bool(False)
    for before in range(slot):
     if embedding[ids[before//4]][before%4]==node:duplicate=True
    if not duplicate:
     c=wp.float64(0.);uc=wp.float64(0.);vc=wp.float64(0.)
     for other in range(16):
      at=other//4;p=ids[at]
      if embedding[p][other%4]==node:
       w=weights[p][other%4];c+=coeff[at]*w
       if at==0:uc-=w
       elif at==1:uc+=w
       elif at==2:vc-=w
       else:vc+=w
     grad=uc*gu+vc*gv;jac=vc*skew(u)-uc*skew(v);h=m*c*c*normal_h+wp.float64(2.)*value*dm*(wp.transpose(jac)*jac)
     wp.atomic_add(force,node,m*c*f-value*dm*grad);wp.atomic_add(hessian,node,h)
   for j in range(4):
    uc=wp.float64(0.);vc=wp.float64(0.)
    if kind[record]!=0:
     if j==0:uc=wp.float64(-1.)
     elif j==1:uc=wp.float64(1.)
     elif j==2:vc=wp.float64(-1.)
     else:vc=wp.float64(1.)
    jac=vc*skew(u)-uc*skew(v);grad=uc*gu+vc*gv;h=m*coeff[j]*coeff[j]*normal_h+wp.float64(2.)*value*dm*(wp.transpose(jac)*jac);wp.atomic_add(proxy_force,ids[j],m*coeff[j]*f-value*dm*grad);wp.atomic_add(proxy_hessian,ids[j],h)

class MollifiedEmbeddedSelfContact(EmbeddedSelfContact):
 def __init__(self,data,**kwargs):
  super().__init__(data,edge_epsilon=1e-16,**kwargs)
  self.rest_precise=wp.array(self.embedding['reference_positions'],dtype=wp.vec3d);self.kind=wp.empty(self.stencil_capacity,dtype=int);self.mollifier_threshold=wp.empty(self.stencil_capacity,dtype=wp.float64)
 def detect(self,physical):
  super().detect(physical);self.stencil_count.zero_();wp.launch(candidate_pairs,dim=max(self.model.particle_count,self.model.edge_count),inputs=[self.rest_precise,self.model.tri_indices,self.model.edge_indices,self.solver.trimesh_collision_info,self.stencil_capacity],outputs=[self.endpoint,self.kind,self.mollifier_threshold,self.stencil_count,self.invalid])
 def evaluate(self,physical,dt):
  wp.launch(precise_embedding,dim=self.model.particle_count,inputs=[physical,self.indices,self.weights],outputs=[self.precise_position,self.state.particle_q]);self.force.zero_();self.hessian.zero_();self.physical_force.zero_();self.physical_hessian.zero_();self.contact_energy.zero_()
  wp.launch(current_contact,dim=self.stencil_capacity,inputs=[self.precise_position,self.indices,self.weights,self.endpoint,self.kind,self.mollifier_threshold,self.stencil_count,self.stencil_capacity,wp.float64(self.margin),wp.float64(self.model.soft_contact_ke)],outputs=[self.physical_force,self.physical_hessian,self.force,self.hessian,self.contact_energy,self.invalid])
