"""Unchanged quadrature, block reduction replacing contended double atomics."""
import warp as wp
from inside_cad_gpu import signed_inside
@wp.kernel
def integrate_reduced(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),iptr:wp.array(dtype=int),iids:wp.array(dtype=int),cells:wp.array(dtype=int),R:wp.mat33d,pose:wp.array(dtype=wp.vec3d),X:wp.array(dtype=wp.mat33d),V:wp.array(dtype=wp.mat33d),areas:wp.array(dtype=wp.float64),masters:wp.array(dtype=wp.mat33d),polygon:wp.array2d(dtype=wp.vec3d),counts:wp.array(dtype=int),faces:wp.array(dtype=int),active:wp.array(dtype=int),bad:wp.array(dtype=int),ff:wp.array2d(dtype=wp.vec3d),uu:wp.array(dtype=wp.float64),dd:wp.array(dtype=wp.float64),ww:wp.array(dtype=wp.float64),mm:wp.array(dtype=wp.vec3d)):
 thread=wp.tid();nm=masters.shape[0];first=thread//128;lane=thread%128;root=lane//nm;leaf=lane%nm
 for slot in range(first,active[0],64):
  if bad[0]!=0:break
  face=faces[slot];n=counts[slot];forces=wp.mat33d(wp.float64(0.));U=wp.float64(0.);D=wp.float64(0.);W=wp.float64(0.);M=wp.vec3d(wp.float64(0.))
  if root<n-2:
   B=wp.matrix_from_rows(polygon[slot,0],polygon[slot,root+1],polygon[slot,root+2]);area=areas[face]*wp.abs(wp.determinant(B))/wp.float64(nm);B=masters[leaf]*B;x=X[face];v=V[face];T=pose[0];tv=pose[1];forces=wp.mat33d(wp.float64(0.));U=wp.float64(0.);D=wp.float64(0.);W=wp.float64(0.);M=wp.vec3d(wp.float64(0.))
   for k in range(3):
    rule=wp.vec3d(wp.float64(1./6.));rule[k]=wp.float64(2./3.);bary=wp.transpose(B)*rule;p=wp.transpose(x)*bary;vel=wp.transpose(v)*bary;s=signed_inside(tri,iptr,iids,cells[slot],wp.transpose(R)*(p-T));depth=wp.max(-s.phi,wp.float64(0.));normal=R*s.normal;fn=wp.float64(1e9)*area/wp.float64(3.)*depth;rel=vel-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))
    if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed
    f=fn*normal+fr
    for u in range(3):
     for a in range(3):forces[u,a]+=bary[u]*f[a]
    U+=wp.float64(.5)*fn*depth;D-=wp.dot(fr,rel);W+=wp.dot(f,tv);M+=wp.cross(p-T,f)
  f0=wp.tile_sum(wp.tile(forces[0],preserve_type=True));f1=wp.tile_sum(wp.tile(forces[1],preserve_type=True));f2=wp.tile_sum(wp.tile(forces[2],preserve_type=True))
  su=wp.tile_sum(wp.tile(U));sd=wp.tile_sum(wp.tile(D));sw=wp.tile_sum(wp.tile(W));sm=wp.tile_sum(wp.tile(M,preserve_type=True))
  if lane==0:
   wp.atomic_add(ff,face,0,f0[0]);wp.atomic_add(ff,face,1,f1[0]);wp.atomic_add(ff,face,2,f2[0]);wp.atomic_add(uu,face,su[0]);wp.atomic_add(dd,face,sd[0]);wp.atomic_add(ww,face,sw[0]);wp.atomic_add(mm,face,sm[0])
