"""Forward, damage-disabled evaluation of the unchanged moving-frame energy.
Two force stages retain both gap and frame derivatives. Research adapter only.
"""
import warp as wp
import numpy as np
@wp.func
def source_vector(v:wp.vec3d):return wp.vec3d(v[0],-v[2],v[1])
@wp.func
def world_vector(v:wp.vec3d):return wp.vec3d(v[0],v[2],-v[1])
@wp.func
def anchor_position(q:wp.array[wp.vec3d],ai:wp.array[wp.vec3i],bi:wp.array[wp.vec3i],aw:wp.array[wp.vec3d],i:int):
 p=wp.vec3d(0.)
 for j in range(3):p+=wp.float64(.5)*aw[i][j]*(q[ai[i][j]]+q[bi[i][j]])
 return source_vector(p)
@wp.kernel(enable_backward=False)
def frames(q:wp.array[wp.vec3d],ai:wp.array[wp.vec3i],bi:wp.array[wp.vec3i],aw:wp.array[wp.vec3d],sign:wp.array[wp.float64],frame:wp.array[wp.mat33d],invalid:wp.array[int]):
 i=wp.tid();a=anchor_position(q,ai,bi,aw,3*i);u=anchor_position(q,ai,bi,aw,3*i+1)-a;v=anchor_position(q,ai,bi,aw,3*i+2)-a;c=wp.cross(u,v)
 if wp.length(u)<wp.float64(1.e-12) or wp.length(c)<wp.float64(1.e-12):wp.atomic_add(invalid,0,1)
 else:
  t=u/wp.length(u);n=sign[i]*c/wp.length(c);b=wp.cross(n,t);frame[i]=wp.mat33d(n[0],t[0],b[0],n[1],t[1],b[1],n[2],t[2],b[2])
@wp.kernel(enable_backward=False)
def quadrature(q:wp.array[wp.vec3d],li:wp.array[wp.vec3i],ri:wp.array[wp.vec3i],bary:wp.array[wp.vec3d],group:wp.array[int],weight:wp.array[wp.float64],K:wp.array[wp.mat33d],frame:wp.array[wp.mat33d],force:wp.array[wp.vec3d],frame_gradient:wp.array[wp.mat33d],energy:wp.array[wp.float64]):
 i=wp.tid();g=group[i];gap=wp.vec3d(0.)
 for j in range(3):gap+=bary[i][j]*source_vector(q[ri[i][j]]-q[li[i][j]])
 local=wp.transpose(frame[g])*gap;e=wp.vec3d(wp.max(local[0],wp.float64(0.)),local[1],local[2]);gl=K[g]*e
 wp.atomic_add(energy,g,wp.float64(.5)*weight[i]*wp.dot(e,gl))
 if local[0]<wp.float64(0.):gl[0]=wp.float64(0.)
 gl=weight[i]*gl;f=world_vector(frame[g]*gl)
 for j in range(3):
  wp.atomic_add(force,li[i][j],bary[i][j]*f);wp.atomic_add(force,ri[i][j],-bary[i][j]*f)
 wp.atomic_add(frame_gradient,g,wp.outer(gap,gl))
@wp.kernel(enable_backward=False)
def anchor_force(q:wp.array[wp.vec3d],ai:wp.array[wp.vec3i],bi:wp.array[wp.vec3i],aw:wp.array[wp.vec3d],sign:wp.array[wp.float64],frame:wp.array[wp.mat33d],frame_gradient:wp.array[wp.mat33d],force:wp.array[wp.vec3d]):
 i=wp.tid();a=anchor_position(q,ai,bi,aw,3*i);u=anchor_position(q,ai,bi,aw,3*i+1)-a;v=anchor_position(q,ai,bi,aw,3*i+2)-a;F=frame[i];G=frame_gradient[i]
 n=wp.vec3d(F[0,0],F[1,0],F[2,0]);t=wp.vec3d(F[0,1],F[1,1],F[2,1]);gn=wp.vec3d(G[0,0],G[1,0],G[2,0]);gt=wp.vec3d(G[0,1],G[1,1],G[2,1]);gb=wp.vec3d(G[0,2],G[1,2],G[2,2]);gn+=wp.cross(t,gb);gt+=wp.cross(gb,n)
 gc=sign[i]*(gn-n*wp.dot(n,gn))/wp.length(wp.cross(u,v));gu=(gt-t*wp.dot(t,gt))/wp.length(u)+wp.cross(v,gc);gv=wp.cross(gc,u)
 for aidx in range(3):
  grad=-gu-gv
  if aidx==1:grad=gu
  elif aidx==2:grad=gv
  f=-wp.float64(.5)*world_vector(grad)
  for j in range(3):
   wp.atomic_add(force,ai[3*i+aidx][j],aw[3*i+aidx][j]*f);wp.atomic_add(force,bi[3*i+aidx][j],aw[3*i+aidx][j]*f)
class CohesionGPU:
 def __init__(self,s):
  def A(t,dtype,shape=None):
   a=t.detach().cpu().numpy()
   if shape is not None:a=a.reshape(shape)
   return wp.array(a,dtype=dtype,device='cuda:0')
  self.ai=A(s.ai,wp.vec3i,(-1,3));self.bi=A(s.bi,wp.vec3i,(-1,3));self.aw=A(s.aw,wp.vec3d,(-1,3));self.sign=A(s.sign,wp.float64);self.li=A(s.li,wp.vec3i);self.ri=A(s.ri,wp.vec3i);self.bary=A(s.bary,wp.vec3d);self.group=A(s.group,wp.int32);self.weight=A(s.weight,wp.float64);self.K=A(s.K,wp.mat33d)
  self.frame=wp.zeros(47,dtype=wp.mat33d);self.fg=wp.zeros_like(self.frame);self.force=wp.zeros(len(s.mesh['x']),dtype=wp.vec3d);self.energy=wp.zeros(47,dtype=wp.float64);self.invalid=wp.zeros(1,dtype=int)
 def evaluate(self,q):
  q=wp.from_torch(q,dtype=wp.vec3d);self.force.zero_();self.fg.zero_();self.energy.zero_();self.invalid.zero_()
  wp.launch(frames,47,inputs=[q,self.ai,self.bi,self.aw,self.sign],outputs=[self.frame,self.invalid])
  wp.launch(quadrature,len(self.group),inputs=[q,self.li,self.ri,self.bary,self.group,self.weight,self.K,self.frame],outputs=[self.force,self.fg,self.energy])
  wp.launch(anchor_force,47,inputs=[q,self.ai,self.bi,self.aw,self.sign,self.frame,self.fg],outputs=[self.force])
  return wp.to_torch(self.force)
