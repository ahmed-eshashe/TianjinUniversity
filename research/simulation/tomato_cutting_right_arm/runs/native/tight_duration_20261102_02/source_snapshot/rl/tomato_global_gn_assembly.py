"""Global positive GN preconditioner for the unchanged source energy/forces.

Includes coupled off-diagonal blocks. This is a numerical candidate, not a new
constitutive law or an exact Hessian in deformed/damaging states. No stepping
or qualification is implied by assembling a matrix.
"""
import warp as wp
from tomato_objective_gn_compact import skew3
from tomato_canonical_self_contact import barycentric_closest,force_norm
from tomato_mollified_self_contact import closest_segments,skew

@wp.func
def put_block(at:int,a:int,b:int,h:wp.mat33d,free:wp.array[int],rows:wp.array[int],cols:wp.array[int],values:wp.array[wp.mat33d]):
 rows[at]=0;cols[at]=0;values[at]=wp.mat33d(0.)
 if a>=0 and b>=0:
  if free[a]!=0 and free[b]!=0:rows[at]=a;cols[at]=b;values[at]=h

@wp.kernel(enable_backward=False)
def mass_blocks(mass:wp.array[wp.float64],free:wp.array[int],x:wp.array[wp.vec3d],board_k:wp.array[float],height:wp.float64,dt:wp.float64,rows:wp.array[int],cols:wp.array[int],values:wp.array[wp.mat33d]):
 i=wp.tid();h=wp.identity(n=3,dtype=wp.float64)
 if free[i]!=0:
  h*=mass[i]/(dt*dt)
  if x[i][2]<height:h[2,2]+=wp.float64(board_k[i])
 rows[i]=i;cols[i]=i;values[i]=h

@wp.kernel(enable_backward=False)
def spring_blocks(offset:int,x:wp.array[wp.vec3d],pairs:wp.array[wp.vec2i],k:wp.array[wp.float64],free:wp.array[int],rows:wp.array[int],cols:wp.array[int],values:wp.array[wp.mat33d]):
 p,a,b=wp.tid();ids=pairs[p];v=x[ids[1]]-x[ids[0]];length=wp.length(v);h=wp.mat33d(0.)
 if length>wp.float64(1.e-8):
  normal=v/length;sgn=wp.float64(1.)
  if a!=b:sgn=wp.float64(-1.)
  h=sgn*k[p]*wp.outer(normal,normal)
 put_block(offset+4*p+2*a+b,ids[a],ids[b],h,free,rows,cols,values)

@wp.func
def tet_grad(a:wp.vec3d,b:wp.vec3d,c:wp.vec3d,V:wp.float64,slot:int):
 g1=wp.cross(b,c)/(wp.float64(6.)*V);g2=wp.cross(c,a)/(wp.float64(6.)*V);g3=wp.cross(a,b)/(wp.float64(6.)*V);g=-g1-g2-g3
 if slot==1:g=g1
 elif slot==2:g=g2
 elif slot==3:g=g3
 return g

@wp.kernel(enable_backward=False)
def volume_blocks(offset:int,x:wp.array[wp.vec3d],cells:wp.array[wp.vec4i],volumes:wp.array[wp.float64],free:wp.array[int],rows:wp.array[int],cols:wp.array[int],values:wp.array[wp.mat33d],invalid:wp.array[int]):
 p,sa,sb=wp.tid();ids=cells[p];a=x[ids[1]]-x[ids[0]];b=x[ids[2]]-x[ids[0]];c=x[ids[3]]-x[ids[0]];V=volumes[p];j=wp.dot(a,wp.cross(b,c))/(wp.float64(6.)*V);h=wp.mat33d(0.)
 if j<=wp.float64(.1):wp.atomic_add(invalid,0,1)
 elif j<wp.float64(.5):
  r=(j-wp.float64(.1))/wp.float64(.4);scale=wp.float64(10000.)*V/(wp.float64(.16)*r*r);h=scale*wp.outer(tet_grad(a,b,c,V,sa),tet_grad(a,b,c,V,sb))
 put_block(offset+16*p+4*sa+sb,ids[sa],ids[sb],h,free,rows,cols,values)

@wp.func
def frame_differentials(node:int,p0:wp.vec2i,p1:wp.vec2i,p2:wp.vec2i,u:wp.vec3d,v:wp.vec3d,t:wp.vec3d,n:wp.vec3d,sign:wp.float64):
 au=wp.float64(0.);av=wp.float64(0.);half=wp.float64(.5)
 for side in range(2):
  if p0[side]==node:au-=half;av-=half
  if p1[side]==node:au+=half
  if p2[side]==node:av+=half
 identity=wp.identity(n=3,dtype=wp.float64);T=(au/wp.length(u))*(identity-wp.outer(t,t));C=av*skew3(u)-au*skew3(v);N=(sign/wp.length(wp.cross(u,v)))*(identity-wp.outer(n,n))*C;B=-skew3(t)*N+skew3(n)*T;return N,T,B

@wp.func
def gap_jac(node:int,pair:wp.vec2i,gap:wp.vec3d,n:wp.vec3d,t:wp.vec3d,b:wp.vec3d,N:wp.mat33d,T:wp.mat33d,B:wp.mat33d):
 beta=wp.float64(0.)
 if pair[0]==node:beta-=wp.float64(1.)
 if pair[1]==node:beta+=wp.float64(1.)
 jn=wp.vec3d(0.)
 if wp.dot(gap,n)>=wp.float64(0.):jn=beta*n+wp.transpose(N)*gap
 jt=beta*t+wp.transpose(T)*gap;jb=beta*b+wp.transpose(B)*gap;return wp.mat33d(jn[0],jn[1],jn[2],jt[0],jt[1],jt[2],jb[0],jb[1],jb[2])

@wp.kernel(enable_backward=False)
def cohesive_blocks(offset:int,x:wp.array[wp.vec3d],pairs:wp.array2d[wp.vec2i],counts:wp.array[int],anchors:wp.array[wp.vec3i],sign:wp.array[wp.float64],weights:wp.array2d[wp.float64],stiffness:wp.array[wp.mat33d],law:wp.array[wp.vec3d],history:wp.array[wp.vec2d],eligible:wp.array[int],free:wp.array[int],rows:wp.array[int],cols:wp.array[int],values:wp.array[wp.mat33d]):
 p,sa,sb=wp.tid();at=offset+256*p+16*sa+sb;rows[at]=0;cols[at]=0;values[at]=wp.mat33d(0.)
 if sa<2*counts[p] and sb<2*counts[p]:
  na=pairs[p,sa//2][sa%2];nb=pairs[p,sb//2][sb%2];a=anchors[p];p0=pairs[p,a[0]];p1=pairs[p,a[1]];p2=pairs[p,a[2]];half=wp.float64(.5);zero=wp.float64(0.);one=wp.float64(1.);origin=half*(x[p0[0]]+x[p0[1]]);u=half*(x[p1[0]]+x[p1[1]])-origin;v=half*(x[p2[0]]+x[p2[1]])-origin;t=wp.normalize(u);n=sign[p]*wp.normalize(wp.cross(u,v));b=wp.cross(n,t);damage=history[p][1]
  if eligible[p]!=0:
   total=zero
   for q in range(counts[p]):
    pair=pairs[p,q];gap=x[pair[1]]-x[pair[0]];e=wp.vec3d(wp.max(wp.dot(gap,n),zero),wp.dot(gap,t),wp.dot(gap,b));total+=half*weights[p,q]*wp.dot(e,stiffness[p]*e)
   separation=wp.sqrt(wp.max(wp.float64(2.)*total/law[p][0],wp.float64(1.e-40)));maximum=wp.max(separation,history[p][0]);onset=law[p][1];failure=law[p][2]
   if maximum>=failure:damage=one
   elif maximum>onset:damage=wp.max(damage,failure*(maximum-onset)/(maximum*(failure-onset)))
  Na,Ta,Ba=frame_differentials(na,p0,p1,p2,u,v,t,n,sign[p]);Nb,Tb,Bb=frame_differentials(nb,p0,p1,p2,u,v,t,n,sign[p]);H=wp.mat33d(0.)
  for q in range(counts[p]):
   pair=pairs[p,q];gap=x[pair[1]]-x[pair[0]];Ja=gap_jac(na,pair,gap,n,t,b,Na,Ta,Ba);Jb=gap_jac(nb,pair,gap,n,t,b,Nb,Tb,Bb);H+=(one-damage)*weights[p,q]*(wp.transpose(Ja)*stiffness[p]*Jb)
  put_block(at,na,nb,H,free,rows,cols,values)

@wp.kernel(enable_backward=False)
def contact_cache(proxy:wp.array[wp.vec3d],endpoints:wp.array[wp.vec4i],kind:wp.array[int],threshold:wp.array[wp.float64],query_count:wp.array[int],capacity:int,radius:wp.float64,stiffness:wp.float64,active_ids:wp.array[int],active_count:wp.array[int],coefficients:wp.array[wp.vec4d],normals:wp.array[wp.vec3d],us:wp.array[wp.vec3d],vs:wp.array[wp.vec3d],normal_k:wp.array[wp.float64],mollifier_k:wp.array[wp.float64],invalid:wp.array[int]):
 record=wp.tid()
 if record<wp.min(query_count[0],capacity):
  ids=endpoints[record];p0=proxy[ids[0]];p1=proxy[ids[1]];p2=proxy[ids[2]];p3=proxy[ids[3]];coeff=wp.vec4d(0.);m=wp.float64(1.);dm=wp.float64(0.);u=wp.vec3d(0.);v=wp.vec3d(0.)
  if kind[record]==0:
   bary=barycentric_closest(p1,p2,p3,p0);coeff=wp.vec4d(wp.float64(1.),-bary[0],-bary[1],-bary[2])
  else:
   st=closest_segments(p0,p1,p2,p3);coeff=wp.vec4d(wp.float64(1.)-st[0],st[0],-wp.float64(1.)+st[1],-st[1]);u=p1-p0;v=p3-p2;squared=wp.dot(wp.cross(u,v),wp.cross(u,v));eps=threshold[record]
   if squared<eps:ratio=squared/eps;m=ratio*(wp.float64(2.)-ratio);dm=wp.float64(2.)*(wp.float64(1.)-ratio)/eps
  delta=coeff[0]*p0+coeff[1]*p1+coeff[2]*p2+coeff[3]*p3;distance=wp.length(delta)
  if distance<=wp.float64(1.e-8):wp.atomic_add(invalid,0,1)
  elif distance<radius:
   first,second,value=force_norm(distance,radius,stiffness);at=wp.atomic_add(active_count,0,1);active_ids[at]=record;coefficients[record]=coeff;normals[record]=delta/distance;us[record]=u;vs[record]=v;normal_k[record]=m*second;mollifier_k[record]=wp.float64(2.)*value*dm

@wp.kernel(enable_backward=False)
def contact_blocks(offset:int,active_ids:wp.array[int],physical_ids:wp.array2d[int],endpoint_weight:wp.array2d[wp.vec4d],coefficients:wp.array[wp.vec4d],normals:wp.array[wp.vec3d],us:wp.array[wp.vec3d],vs:wp.array[wp.vec3d],normal_k:wp.array[wp.float64],mollifier_k:wp.array[wp.float64],free:wp.array[int],rows:wp.array[int],cols:wp.array[int],values:wp.array[wp.mat33d]):
 index,sa,sb=wp.tid();record=active_ids[index];na=physical_ids[record,sa];nb=physical_ids[record,sb];wa=endpoint_weight[record,sa];wb=endpoint_weight[record,sb];ca=wp.dot(coefficients[record],wa);cb=wp.dot(coefficients[record],wb);Ja=(wa[3]-wa[2])*skew(us[record])-(wa[1]-wa[0])*skew(vs[record]);Jb=(wb[3]-wb[2])*skew(us[record])-(wb[1]-wb[0])*skew(vs[record]);H=normal_k[record]*ca*cb*wp.outer(normals[record],normals[record])+mollifier_k[record]*(wp.transpose(Ja)*Jb);put_block(offset+256*index+16*sa+sb,na,nb,H,free,rows,cols,values)

class GlobalGNAssembly:
 def __init__(self,s,data,fixed,*,maximum_triplets=8388608):
  import numpy as np
  from warp import sparse
  self.s=s;self.data=data;self.n=len(data['x']);free=np.ones(self.n,dtype=np.int32);free[fixed]=0;self.free=wp.array(free,dtype=int);self.mass=wp.array(data['mass'],dtype=wp.float64);self.springs=wp.array(data['springs'],dtype=wp.vec2i);self.maximum_triplets=maximum_triplets;self.matrix=sparse.bsr_zeros(self.n,self.n,block_type=wp.mat33d,device='cuda:0');capacity=s.surface_contact.stencil_capacity;self.active_ids=wp.empty(capacity,dtype=int);self.active_count=wp.zeros(1,dtype=int);self.coefficients=wp.empty(capacity,dtype=wp.vec4d);self.normals=wp.empty(capacity,dtype=wp.vec3d);self.us=wp.empty(capacity,dtype=wp.vec3d);self.vs=wp.empty(capacity,dtype=wp.vec3d);self.normal_k=wp.empty(capacity,dtype=wp.float64);self.mollifier_k=wp.empty(capacity,dtype=wp.float64);self.rows=self.cols=self.values=None
 def assemble(self,x,dt):
  from warp import sparse
  s=self.s;e=s.surface_contact;self.active_count.zero_();wp.launch(contact_cache,dim=e.stencil_capacity,inputs=[e.precise_position,e.endpoint,e.kind,e.mollifier_threshold,e.stencil_count,e.stencil_capacity,wp.float64(e.margin),wp.float64(e.model.soft_contact_ke)],outputs=[self.active_ids,self.active_count,self.coefficients,self.normals,self.us,self.vs,self.normal_k,self.mollifier_k,e.invalid],block_dim=64);active=int(self.active_count.numpy()[0]);ns=len(self.data['springs']);nc=len(self.data['cells']);np=s.pairs.shape[0];spring_offset=self.n;volume_offset=spring_offset+4*ns;cohesive_offset=volume_offset+16*nc;contact_offset=cohesive_offset+256*np;total=contact_offset+256*active
  if total>self.maximum_triplets:raise ValueError('Global sparse GN triplet memory budget exceeded; no state advanced')
  self.rows=wp.empty(total,dtype=int);self.cols=wp.empty(total,dtype=int);self.values=wp.empty(total,dtype=wp.mat33d);wp.launch(mass_blocks,dim=self.n,inputs=[self.mass,self.free,x,s.board_stiffness,wp.float64(s.board_height),wp.float64(dt)],outputs=[self.rows,self.cols,self.values],block_dim=64);wp.launch(spring_blocks,dim=(ns,2,2),inputs=[spring_offset,x,self.springs,s.relative_spring_k,self.free],outputs=[self.rows,self.cols,self.values],block_dim=64);wp.launch(volume_blocks,dim=(nc,4,4),inputs=[volume_offset,x,s.cells,s.volumes64,self.free],outputs=[self.rows,self.cols,self.values,s.volume_invalid],block_dim=64);wp.launch(cohesive_blocks,dim=(np,16,16),inputs=[cohesive_offset,x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible,self.free],outputs=[self.rows,self.cols,self.values],block_dim=64)
  if active:wp.launch(contact_blocks,dim=(active,16,16),inputs=[contact_offset,self.active_ids,e.physical_ids,e.endpoint_weight,self.coefficients,self.normals,self.us,self.vs,self.normal_k,self.mollifier_k,self.free],outputs=[self.rows,self.cols,self.values],block_dim=64)
  sparse.bsr_set_from_triplets(self.matrix,self.rows,self.cols,self.values);return dict(active_contact_stencils=active,triplets=total)
