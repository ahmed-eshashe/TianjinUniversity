"""Canonical, float64, frozen-stencil self-contact forces on physical nodes.

The native detector supplies candidates. Each edge pair is evaluated once and
both reactions use the same geometry. Nearly parallel overlapping edges use a
symmetric midpoint feature. Stencils freeze until the next collision query;
forces are exact gradients of their frozen distance potentials. Hessian blocks
are the positive Gauss-Newton preconditioner used by the contact solver.
"""
import warp as wp
from newton._src.geometry.tri_mesh_collision import TriMeshCollisionInfo

@wp.func
def barycentric_closest(a:wp.vec3d,b:wp.vec3d,c:wp.vec3d,p:wp.vec3d):
 zero=wp.float64(0.);one=wp.float64(1.);ab=b-a;ac=c-a;ap=p-a;d1=wp.dot(ab,ap);d2=wp.dot(ac,ap)
 if d1<=zero and d2<=zero:return wp.vec3d(one,zero,zero)
 bp=p-b;d3=wp.dot(ab,bp);d4=wp.dot(ac,bp)
 if d3>=zero and d4<=d3:return wp.vec3d(zero,one,zero)
 vc=d1*d4-d3*d2
 if vc<=zero and d1>=zero and d3<=zero:
  v=d1/(d1-d3);return wp.vec3d(one-v,v,zero)
 cp=p-c;d5=wp.dot(ab,cp);d6=wp.dot(ac,cp)
 if d6>=zero and d5<=d6:return wp.vec3d(zero,zero,one)
 vb=d5*d2-d1*d6
 if vb<=zero and d2>=zero and d6<=zero:
  v=d2/(d2-d6);return wp.vec3d(one-v,zero,v)
 va=d3*d6-d5*d4
 if va<=zero and d4-d3>=zero and d5-d6>=zero:
  v=(d4-d3)/((d4-d3)+(d5-d6));return wp.vec3d(zero,one-v,v)
 inv=one/(va+vb+vc);v=vb*inv;w=vc*inv;return wp.vec3d(one-v-w,v,w)

@wp.func
def segment_parameters(a:wp.vec3d,b:wp.vec3d,c:wp.vec3d,d:wp.vec3d):
 u=b-a;v=d-c;w=a-c;aa=wp.dot(u,u);bb=wp.dot(u,v);cc=wp.dot(v,v);dd=wp.dot(u,w);ee=wp.dot(v,w);det=aa*cc-bb*bb;zero=wp.float64(0.);one=wp.float64(1.)
 s=zero;t=wp.clamp(ee/cc,zero,one);delta=a-(c+t*v);best=wp.dot(delta,delta)
 tt=wp.clamp(wp.dot(b-c,v)/cc,zero,one);delta=b-(c+tt*v);value=wp.dot(delta,delta)
 if value<best:best=value;s=one;t=tt
 ss=wp.clamp(-dd/aa,zero,one);delta=(a+ss*u)-c;value=wp.dot(delta,delta)
 if value<best:best=value;s=ss;t=zero
 ss=wp.clamp(wp.dot(d-a,u)/aa,zero,one);delta=(a+ss*u)-d;value=wp.dot(delta,delta)
 if value<best:best=value;s=ss;t=one
 if det>wp.float64(1.e-8)*aa*cc:
  ss=(bb*ee-cc*dd)/det;tt=(aa*ee-bb*dd)/det
  if ss>=zero and ss<=one and tt>=zero and tt<=one:
   delta=a+ss*u-c-tt*v;value=wp.dot(delta,delta)
   if value<best:s=ss;t=tt
 else:
  # Stable representative of the parallel closest-point family. This is a
  # declared contact feature rule, not an exact nonparallel distance claim.
  sc=wp.dot(c-a,u)/aa;sd=wp.dot(d-a,u)/aa;lo=wp.max(zero,wp.min(sc,sd));hi=wp.min(one,wp.max(sc,sd))
  if hi>=lo:s=wp.float64(.5)*(lo+hi);t=wp.clamp(wp.dot(a+s*u-c,v)/cc,zero,one)
 return wp.vec2d(s,t)

@wp.kernel
def build_stencils(x:wp.array[wp.vec3d],triangles:wp.array2d[int],edges:wp.array2d[int],info_array:wp.array[TriMeshCollisionInfo],capacity:int,endpoint:wp.array[wp.vec4i],coefficient:wp.array[wp.vec4d],count:wp.array[int],invalid:wp.array[int]):
 source=wp.tid();info=info_array[0]
 if source<info.vertex_colliding_triangles_count.shape[0]:
  n=wp.min(info.vertex_colliding_triangles_count[source],info.vertex_colliding_triangles_buffer_sizes[source]);offset=info.vertex_colliding_triangles_offsets[source]
  for j in range(n):
   v=info.vertex_colliding_triangles[2*(offset+j)];t=info.vertex_colliding_triangles[2*(offset+j)+1];a=triangles[t,0];b=triangles[t,1];c=triangles[t,2];bary=barycentric_closest(x[a],x[b],x[c],x[v]);at=wp.atomic_add(count,0,1)
   if at>=capacity:wp.atomic_add(invalid,0,1)
   else:endpoint[at]=wp.vec4i(v,a,b,c);coefficient[at]=wp.vec4d(wp.float64(1.),-bary[0],-bary[1],-bary[2])
 if source<info.edge_colliding_edges_count.shape[0]:
  n=wp.min(info.edge_colliding_edges_count[source],info.edge_colliding_edges_buffer_sizes[source]);offset=info.edge_colliding_edges_offsets[source]
  for j in range(n):
   e0=info.edge_colliding_edges[2*(offset+j)];e1=info.edge_colliding_edges[2*(offset+j)+1]
   if e0<e1:
    a=edges[e0,2];b=edges[e0,3];c=edges[e1,2];d=edges[e1,3];st=segment_parameters(x[a],x[b],x[c],x[d]);at=wp.atomic_add(count,0,1)
    if at>=capacity:wp.atomic_add(invalid,0,1)
    else:endpoint[at]=wp.vec4i(a,b,c,d);coefficient[at]=wp.vec4d(wp.float64(1.)-st[0],st[0],-wp.float64(1.)+st[1],-st[1])

@wp.kernel
def embed_stencils(endpoint:wp.array[wp.vec4i],coefficient:wp.array[wp.vec4d],count:wp.array[int],capacity:int,embedding:wp.array[wp.vec4i],weights:wp.array[wp.vec4d],physical_ids:wp.array2d[int],physical_coeff:wp.array2d[wp.float64]):
 record=wp.tid()
 if record<wp.min(count[0],capacity):
  for slot in range(16):
   proxy=endpoint[record][slot//4];node=embedding[proxy][slot%4];value=wp.float64(0.);duplicate=bool(False)
   for before in range(slot):
    previous=endpoint[record][before//4]
    if embedding[previous][before%4]==node:duplicate=True
   if not duplicate:
    for other in range(16):
     p=endpoint[record][other//4]
     if embedding[p][other%4]==node:value+=coefficient[record][other//4]*weights[p][other%4]
   physical_ids[record,slot]=node;physical_coeff[record,slot]=value

@wp.func
def force_norm(distance:wp.float64,radius:wp.float64,stiffness:wp.float64):
 first=wp.float64(0.);second=wp.float64(0.);energy=wp.float64(0.);tau=radius*wp.float64(.5);minimum=wp.float64(1.e-5);k2=tau*tau*stiffness
 if distance<radius:
  if tau>distance and distance>minimum:
   first=-k2/distance;second=k2/(distance*distance);energy=wp.float64(.5)*k2-k2*wp.log(distance/tau)
  elif distance<=minimum:
   first=k2*(distance-wp.float64(2.)*minimum)/(minimum*minimum);second=k2/(minimum*minimum);gap=distance-minimum;base=wp.float64(.5)*k2-k2*wp.log(minimum/tau);energy=base-k2/minimum*gap+wp.float64(.5)*second*gap*gap
  else:
   gap=radius-distance;first=-stiffness*gap;second=stiffness;energy=wp.float64(.5)*stiffness*gap*gap
 return first,second,energy

@wp.kernel
def evaluate_stencils(x:wp.array[wp.vec3],physical_ids:wp.array2d[int],physical_coeff:wp.array2d[wp.float64],endpoint:wp.array[wp.vec4i],coefficient:wp.array[wp.vec4d],count:wp.array[int],capacity:int,radius:wp.float64,stiffness:wp.float64,force:wp.array[wp.vec3d],hessian:wp.array[wp.mat33d],proxy_force:wp.array[wp.vec3d],proxy_hessian:wp.array[wp.mat33d],energy:wp.array[wp.float64],invalid:wp.array[int]):
 record=wp.tid()
 if record<wp.min(count[0],capacity):
  delta=wp.vec3d(0.)
  for j in range(16):
   p=x[physical_ids[record,j]];delta+=physical_coeff[record,j]*wp.vec3d(wp.float64(p[0]),wp.float64(p[1]),wp.float64(p[2]))
  distance=wp.length(delta)
  if distance<=wp.float64(1.e-8):wp.atomic_add(invalid,0,1)
  elif distance<radius:
   normal=delta/distance;first,second,value=force_norm(distance,radius,stiffness);f=-first*normal;h=second*wp.outer(normal,normal);wp.atomic_add(energy,0,value)
   for j in range(16):
    node=physical_ids[record,j];c=physical_coeff[record,j]
    if c!=wp.float64(0.):wp.atomic_add(force,node,c*f);wp.atomic_add(hessian,node,c*c*h)
   for j in range(4):
    c=coefficient[record][j];node=endpoint[record][j];wp.atomic_add(proxy_force,node,c*f);wp.atomic_add(proxy_hessian,node,c*c*h)

@wp.kernel
def precise_embedding(x:wp.array[wp.vec3],indices:wp.array[wp.vec4i],weights:wp.array[wp.vec4d],precise:wp.array[wp.vec3d],rounded:wp.array[wp.vec3]):
 i=wp.tid();p=wp.vec3d(0.)
 for j in range(4):
  a=x[indices[i][j]];p+=weights[i][j]*wp.vec3d(wp.float64(a[0]),wp.float64(a[1]),wp.float64(a[2]))
 precise[i]=p;rounded[i]=wp.vec3(float(p[0]),float(p[1]),float(p[2]))

@wp.kernel
def add_physical_contact(color:int,colors:wp.array[int],source_force:wp.array[wp.vec3d],source_hessian:wp.array[wp.mat33d],force:wp.array[wp.vec3],hessian:wp.array[wp.mat33]):
 node=wp.tid()
 if color<0 or colors[node]==color:
  f=source_force[node];h=source_hessian[node];force[node]+=wp.vec3(float(f[0]),float(f[1]),float(f[2]));hessian[node]+=wp.mat33(float(h[0,0]),float(h[0,1]),float(h[0,2]),float(h[1,0]),float(h[1,1]),float(h[1,2]),float(h[2,0]),float(h[2,1]),float(h[2,2]))
