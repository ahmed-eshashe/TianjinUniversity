"""Same exact CAD-domain quadrature with compact temporary polygons.

Storage scales with active intersections, rather than every surface/CAD pair.
Capacity exhaustion rejects the step; no contact pair is silently omitted.
"""
import warp as wp
from rk4_contact_gpu import ContactGPU as Base
from parallel_partition_gpu import frame,collect
from contact_reductions import pullback_parallel,force_parts,force_guard
from persistent_gpu import gather
from exact_cad_gpu import signed
Poly=wp.types.matrix(shape=(10,3),dtype=wp.float64)

@wp.kernel
def active_faces(local:wp.array(dtype=wp.mat33d),lo:wp.vec3d,hi:wp.vec3d,count:wp.array(dtype=int),ids:wp.array(dtype=int),bad:wp.array(dtype=int)):
 face=wp.tid();x=local[face];overlap=True
 for axis in range(3):
  a=wp.min(x[0,axis],wp.min(x[1,axis],x[2,axis]));b=wp.max(x[0,axis],wp.max(x[1,axis],x[2,axis]))
  if b<lo[axis] or a>hi[axis]:overlap=False
 if overlap and bad[0]==0:
  index=wp.atomic_add(count,0,1)
  if index>=ids.shape[0]:wp.atomic_max(bad,0,5)
  else:ids[index]=face

@wp.kernel
def candidate_pairs(local:wp.array(dtype=wp.mat33d),bounds:wp.array2d(dtype=wp.vec3d),ncells:int,face_count:wp.array(dtype=int),face_ids:wp.array(dtype=int),count:wp.array(dtype=int),pairs:wp.array(dtype=int),bad:wp.array(dtype=int)):
 thread=wp.tid();slot=thread//ncells;cell=thread%ncells
 if slot>=face_count[0] or bad[0]!=0:return
 face=face_ids[slot];pair=face*ncells+cell;x=local[face];overlap=True
 for axis in range(3):
  lo=wp.min(x[0,axis],wp.min(x[1,axis],x[2,axis]));hi=wp.max(x[0,axis],wp.max(x[1,axis],x[2,axis]))
  if hi<bounds[cell,0][axis] or lo>bounds[cell,1][axis]:overlap=False
 if overlap and bad[0]==0:
  index=wp.atomic_add(count,0,1)
  if index>=pairs.shape[0]:wp.atomic_max(bad,0,5)
  else:pairs[index]=pair

@wp.kernel
def clip_pairs(local:wp.array(dtype=wp.mat33d),planes:wp.array2d(dtype=wp.vec4d),ncells:int,count:wp.array(dtype=int),pairs:wp.array(dtype=int),active:wp.array(dtype=int),faces:wp.array(dtype=int),counts:wp.array(dtype=int),polygon:wp.array2d(dtype=wp.vec3d),bad:wp.array(dtype=int)):
 item=wp.tid()
 if item<count[0] and bad[0]==0:
  pair=pairs[item];face=pair//ncells;cell=pair%ncells;x=local[face];poly=Poly(wp.float64(0.));poly[0,0]=wp.float64(1.);poly[1,1]=wp.float64(1.);poly[2,2]=wp.float64(1.);n=int(3)
  for h in range(4):
   plane=planes[cell,h];distance=x*wp.vec3d(plane[0],plane[1],plane[2])+wp.vec3d(plane[3]);out=Poly(wp.float64(0.));new=int(0)
   for k in range(n):
    p0=poly[k];p1=poly[(k+1)%n];d0=wp.dot(p0,distance);d1=wp.dot(p1,distance)
    if d0<=wp.float64(0.):
     if new>=10:wp.atomic_max(bad,0,6)
     else:out[new]=p0;new+=1
    if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):
     if new>=10:wp.atomic_max(bad,0,6)
     else:out[new]=p0+d0/(d0-d1)*(p1-p0);new+=1
   poly=out;n=new
   if n<3:break
  if n>=3 and bad[0]==0:
   area=wp.float64(0.)
   for k in range(1,n-1):area+=wp.abs(wp.determinant(wp.matrix_from_rows(poly[0],poly[k],poly[k+1])))
   if area>wp.float64(1e-30):
    slot=wp.atomic_add(active,0,1)
    if slot>=faces.shape[0]:wp.atomic_max(bad,0,5)
    else:
     faces[slot]=face;counts[slot]=n
     for k in range(n):polygon[slot,k]=poly[k]

@wp.kernel
def integrate(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),R:wp.mat33d,pose:wp.array(dtype=wp.vec3d),X:wp.array(dtype=wp.mat33d),V:wp.array(dtype=wp.mat33d),areas:wp.array(dtype=wp.float64),masters:wp.array(dtype=wp.mat33d),polygon:wp.array2d(dtype=wp.vec3d),counts:wp.array(dtype=int),faces:wp.array(dtype=int),active:wp.array(dtype=int),bad:wp.array(dtype=int),ff:wp.array2d(dtype=wp.vec3d),uu:wp.array(dtype=wp.float64),dd:wp.array(dtype=wp.float64),ww:wp.array(dtype=wp.float64),mm:wp.array(dtype=wp.vec3d)):
 thread=wp.tid();nm=masters.shape[0];first=thread//(8*nm);root=(thread//nm)%8;leaf=thread%nm
 for slot in range(first,active[0],64):
  if bad[0]!=0:break
  face=faces[slot];n=counts[slot]
  if root<n-2:
   B=wp.matrix_from_rows(polygon[slot,0],polygon[slot,root+1],polygon[slot,root+2]);area=areas[face]*wp.abs(wp.determinant(B))/wp.float64(nm);B=masters[leaf]*B;x=X[face];v=V[face];T=pose[0];tv=pose[1];forces=wp.mat33d(wp.float64(0.));U=wp.float64(0.);D=wp.float64(0.);W=wp.float64(0.);M=wp.vec3d(wp.float64(0.))
   for k in range(3):
    rule=wp.vec3d(wp.float64(1./6.));rule[k]=wp.float64(2./3.);bary=wp.transpose(B)*rule;p=wp.transpose(x)*bary;vel=wp.transpose(v)*bary;s=signed(mesh,tri,wp.transpose(R)*(p-T));depth=wp.max(-s.phi,wp.float64(0.));normal=R*s.normal;fn=wp.float64(1e9)*area/wp.float64(3.)*depth;rel=vel-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))
    if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed
    f=fn*normal+fr
    for u in range(3):
     for a in range(3):forces[u,a]+=bary[u]*f[a]
    U+=wp.float64(.5)*fn*depth;D-=wp.dot(fr,rel);W+=wp.dot(f,tv);M+=wp.cross(p-T,f)
   for u in range(3):wp.atomic_add(ff,face,u,forces[u])
   wp.atomic_add(uu,face,U);wp.atomic_add(dd,face,D);wp.atomic_add(ww,face,W);wp.atomic_add(mm,face,M)

class ContactGPU(Base):
 def __init__(self,*args,candidate_capacity=4096,face_capacity=256,**kwargs):
  self.compact=False;super().__init__(*args,compact_storage=True,**kwargs)
  self.polygon=None;self.leaves=None;self.sources=None;self.active_ids=None
  self.face_count=wp.zeros(1,dtype=int,device='cuda:0');self.face_ids=wp.empty(face_capacity,dtype=int,device='cuda:0');self.candidate_count=wp.zeros(1,dtype=int,device='cuda:0');self.candidate_ids=wp.empty(candidate_capacity,dtype=int,device='cuda:0');self.compact_faces=wp.empty(self.capacity,dtype=int,device='cuda:0');self.compact_counts=wp.empty(self.capacity,dtype=int,device='cuda:0');self.compact_polygon=wp.empty((self.capacity,10),dtype=wp.vec3d,device='cuda:0');self.compact=True
 def contact_force(self):
  if not self.compact:return super().contact_force()
  for a in [self.active,self.face_count,self.candidate_count,self.ff,self.uu,self.dd,self.ww,self.mm]:a.zero_()
  wp.launch(frame,self.nfaces,[wp.mat33d(self.R),wp.vec3d(self.T0),wp.vec3d(self.travel),wp.float64(self.load),wp.float64(self.hold),self.clock,self.sptr,self.sids,self.sw,self.reference,self.q,self.vh,self.xx,self.vv,self.local,self.toolpose]);wp.launch(active_faces,self.nfaces,[self.local,wp.vec3d(self.cad.vertices.min(0)),wp.vec3d(self.cad.vertices.max(0)),self.face_count,self.face_ids,self.bad]);wp.launch(candidate_pairs,self.face_ids.size*self.ncells,[self.local,self.cellbounds,self.ncells,self.face_count,self.face_ids,self.candidate_count,self.candidate_ids,self.bad]);wp.launch(clip_pairs,self.candidate_ids.size,[self.local,self.planes,self.ncells,self.candidate_count,self.candidate_ids,self.active,self.compact_faces,self.compact_counts,self.compact_polygon,self.bad]);wp.launch(integrate,64*8*self.resolution*self.resolution,[self.cad.mesh.id,self.tri,wp.mat33d(self.R),self.toolpose,self.xx,self.vv,self.areas,self.masters,self.compact_polygon,self.compact_counts,self.compact_faces,self.active,self.bad,self.ff,self.uu,self.dd,self.ww,self.mm]);wp.launch(collect,self.ns,[self.ff,self.uu,self.dd,self.ww,self.mm,self.cf,self.cu,self.cp,self.power,self.moment]);wp.launch(pullback_parallel,((self.n+3)//4)*128,[self.cptr,self.cids,self.cw,self.cf,self.external,self.n],block_dim=128);wp.launch(force_parts,self.nparts,[self.cf,self.part_sum,self.part_mag,self.ns]);wp.launch(force_guard,1,[self.part_sum,self.part_mag,self.bad,self.peak,self.nparts]);self.stress();wp.launch(gather,((self.ncap+3)//4)*128,[self.iptr,self.iidx,self.ig,self.P,self.external,self.force,self.counts],block_dim=128)
