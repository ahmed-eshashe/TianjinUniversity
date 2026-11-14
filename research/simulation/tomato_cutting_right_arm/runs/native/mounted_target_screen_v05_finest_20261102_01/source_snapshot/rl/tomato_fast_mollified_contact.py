"""Algebraically equivalent contact blocks with fixed embedding rows cached per query."""
import warp as wp
from tomato_mollified_self_contact import MollifiedEmbeddedSelfContact,closest_segments,skew
from tomato_canonical_self_contact import barycentric_closest,force_norm,precise_embedding

@wp.kernel(enable_backward=False)
def cache_embedding(endpoints:wp.array[wp.vec4i],count:wp.array[int],capacity:int,embedding:wp.array[wp.vec4i],weights:wp.array[wp.vec4d],ids:wp.array2d[int],matrix:wp.array2d[wp.vec4d]):
 record=wp.tid()
 if record<wp.min(count[0],capacity):
  for slot in range(16):
   node=embedding[endpoints[record][slot//4]][slot%4];duplicate=bool(False)
   for before in range(slot):
    if embedding[endpoints[record][before//4]][before%4]==node:duplicate=True
   value=wp.vec4d(0.);ids[record,slot]=-1
   if not duplicate:
    ids[record,slot]=node
    for other in range(16):
     at=other//4;p=endpoints[record][at]
     if embedding[p][other%4]==node:value[at]+=weights[p][other%4]
   matrix[record,slot]=value

@wp.kernel(enable_backward=False)
def current_contact_fast(proxy:wp.array[wp.vec3d],physical_ids:wp.array2d[int],endpoint_weight:wp.array2d[wp.vec4d],endpoints:wp.array[wp.vec4i],kind:wp.array[int],threshold:wp.array[wp.float64],count:wp.array[int],capacity:int,radius:wp.float64,stiffness:wp.float64,force:wp.array[wp.vec3d],hessian:wp.array[wp.mat33d],proxy_force:wp.array[wp.vec3d],proxy_hessian:wp.array[wp.mat33d],energy:wp.array[wp.float64],invalid:wp.array[int]):
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
    node=physical_ids[record,slot]
    if node>=0:
     w=endpoint_weight[record,slot];c=wp.dot(coeff,w);uc=w[1]-w[0];vc=w[3]-w[2]
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

class FastMollifiedEmbeddedSelfContact(MollifiedEmbeddedSelfContact):
 def __init__(self,data,**kwargs):
  super().__init__(data,**kwargs);self.endpoint_weight=wp.empty((self.stencil_capacity,16),dtype=wp.vec4d)
 def detect(self,physical):
  super().detect(physical);wp.launch(cache_embedding,dim=self.stencil_capacity,inputs=[self.endpoint,self.stencil_count,self.stencil_capacity,self.indices,self.weights],outputs=[self.physical_ids,self.endpoint_weight])
 def evaluate(self,physical,dt):
  wp.launch(precise_embedding,dim=self.model.particle_count,inputs=[physical,self.indices,self.weights],outputs=[self.precise_position,self.state.particle_q]);self.force.zero_();self.hessian.zero_();self.physical_force.zero_();self.physical_hessian.zero_();self.contact_energy.zero_()
  wp.launch(current_contact_fast,dim=self.stencil_capacity,inputs=[self.precise_position,self.physical_ids,self.endpoint_weight,self.endpoint,self.kind,self.mollifier_threshold,self.stencil_count,self.stencil_capacity,wp.float64(self.margin),wp.float64(self.model.soft_contact_ke)],outputs=[self.physical_force,self.physical_hessian,self.force,self.hessian,self.contact_energy,self.invalid])
