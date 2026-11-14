"""Conservative affine-parent broad phase before exact boundary evaluation.

A material face lies inside the affine image of its original parent tetrahedron
(up to explicitly bounded barycentric roundoff). Test that envelope first, then
run the ORIGINAL triangle-box filter and exact CAD quadrature on every survivor.
This changes search cost, never the contact geometry or contact law.
"""
import numpy as np,warp as wp
from sparse_contact_gpu import ContactGPU as Base,clear_previous,collect_active,guard_active
from compact_contact_gpu import candidate_pairs,clip_pairs,integrate_interior
from grid_quadrature import integrate_grid
from persistent_gpu import gather

@wp.kernel
def corner_frame(R:wp.mat33d,T0:wp.vec3d,travel:wp.vec3d,load:wp.float64,hold:wp.float64,clock:wp.array(dtype=wp.float64),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),weights:wp.array(dtype=wp.float64),ref:wp.array(dtype=wp.vec3d),q:wp.array(dtype=wp.vec3),corners:wp.array(dtype=wp.vec3d),pose:wp.array(dtype=wp.vec3d)):
 i=wp.tid();t=clock[0];shape=wp.float64(0.);speed=wp.float64(0.);pi=wp.float64(3.141592653589793)
 if t<load:shape=wp.float64(.5)*(wp.float64(1.)-wp.cos(pi*t/load));speed=wp.float64(.5)*pi/load*wp.sin(pi*t/load)
 elif t<load+hold:shape=wp.float64(1.)
 elif t<wp.float64(2.)*load+hold:
  z=(t-load-hold)/load;shape=wp.float64(.5)*(wp.float64(1.)+wp.cos(pi*z));speed=-wp.float64(.5)*pi/load*wp.sin(pi*z)
 T=T0+travel*shape;tv=travel*speed;x=ref[i]
 for k in range(ptr[i],ptr[i+1]):x+=weights[k]*wp.vec3d(q[ids[k]])
 corners[i]=wp.transpose(R)*(x-T)
 if i==0:pose[0]=T;pose[1]=tv

@wp.kernel
def parent_faces(parent:wp.array2d(dtype=int),owner:wp.array(dtype=int),corners:wp.array(dtype=wp.vec3d),roundoff:wp.array(dtype=wp.vec3d),lo:wp.vec3d,hi:wp.vec3d,count:wp.array(dtype=int),ids:wp.array(dtype=int),bad:wp.array(dtype=int)):
 face=wp.tid();r=owner[face];overlap=True
 for k in range(3):
  low=wp.float64(1e30);high=wp.float64(-1e30)
  for j in range(4):low=wp.min(low,corners[parent[r,j]][k]);high=wp.max(high,corners[parent[r,j]][k])
  mag=wp.max(wp.abs(low),wp.abs(high));error=roundoff[face][0]*(high-low)+roundoff[face][1]*mag+roundoff[face][2]+wp.float64(1e-10)*(wp.float64(1.)+mag)
  if high+error<lo[k] or low-error>hi[k]:overlap=False
 if overlap and bad[0]==0:
  index=wp.atomic_add(count,0,1)
  if index>=ids.shape[0]:wp.atomic_max(bad,0,5)
  else:ids[index]=face

@wp.kernel
def exact_active_frame(R:wp.mat33d,pose:wp.array(dtype=wp.vec3d),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),w:wp.array(dtype=wp.float64),ref:wp.array(dtype=wp.vec3d),q:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),X:wp.array(dtype=wp.mat33d),V:wp.array(dtype=wp.mat33d),local:wp.array(dtype=wp.mat33d),bcount:wp.array(dtype=int),bids:wp.array(dtype=int),lo:wp.vec3d,hi:wp.vec3d,count:wp.array(dtype=int),faces:wp.array(dtype=int),bad:wp.array(dtype=int)):
 slot=wp.tid()
 if slot>=bcount[0] or bad[0]!=0:return
 face=bids[slot];T=pose[0];xx=wp.mat33d(wp.float64(0.));vv=wp.mat33d(wp.float64(0.));ll=wp.mat33d(wp.float64(0.))
 for u in range(3):
  i=3*face+u;x=ref[i];vel=wp.vec3d(wp.float64(0.))
  for j in range(ptr[i],ptr[i+1]):x+=w[j]*wp.vec3d(q[ids[j]]);vel+=w[j]*wp.vec3d(v[ids[j]])
  p=wp.transpose(R)*(x-T)
  for k in range(3):xx[u,k]=x[k];vv[u,k]=vel[k];ll[u,k]=p[k]
 overlap=True
 for k in range(3):
  amin=wp.min(ll[0,k],wp.min(ll[1,k],ll[2,k]));amax=wp.max(ll[0,k],wp.max(ll[1,k],ll[2,k]))
  if amax<lo[k] or amin>hi[k]:overlap=False
 if overlap:
  X[face]=xx;V[face]=vv;local[face]=ll;index=wp.atomic_add(count,0,1)
  if index>=faces.shape[0]:wp.atomic_max(bad,0,5)
  else:faces[index]=face

class ContactGPU(Base):
 def __init__(self,*args,**kwargs):
  self.hierarchy_ready=False;super().__init__(*args,**kwargs);a=self.aggregates[0];b=a.body;s=self._surface
  def arr(name,value,dtype):setattr(self,name,wp.array(value,dtype=dtype,device='cuda:0'))
  for name,value in [('hptr',a.E.indptr),('hids',a.E.indices),('hparent',b.ids),('howner',s.tri_owner)]:arr(name,value,int)
  arr('hw',a.E.data,wp.float64);arr('href',b.grid,wp.vec3d);self.hcorners=wp.empty(len(b.u),dtype=wp.vec3d,device='cuda:0');self.hcount=wp.zeros(1,dtype=int,device='cuda:0');self.hfaces=wp.empty(self.nfaces,dtype=int,device='cuda:0')
  N=np.einsum('pi,pij->pj',np.c_[np.ones(len(s.X)),s.X],b.inv[s.owner]);res=s.X-np.einsum('pi,pij->pj',N,b.grid[b.ids[s.owner]]);negative=np.maximum(-N,0).sum(1).reshape(-1,3).max(1);unit=np.abs(N.sum(1)-1).reshape(-1,3).max(1);offset=np.linalg.norm(res,axis=1).reshape(-1,3).max(1);arr('hroundoff',np.c_[negative,unit,offset],wp.vec3d);self.hierarchy_ready=True
  # Velocity is identical for exactly equal sparse rows, so retain one row
  # per distinct mapping. This is exact deduplication, not subsampling.
  m=self.velocity_map;seen=set();keep=[]
  for i in range(m.shape[0]):
   lo,hi=m.indptr[i:i+2];key=(m.indices[lo:hi].tobytes(),m.data[lo:hi].tobytes())
   if key not in seen:seen.add(key);keep.append(i)
  self.velocity_map=m[keep].tocsr();arr('speed_ptr',self.velocity_map.indptr,int);arr('speed_ids',self.velocity_map.indices,int);arr('speed_weights',self.velocity_map.data,wp.float64);self.graphs.clear();self.speed_map_rows_before=m.shape[0]
 def contact_force(self):
  if not self.hierarchy_ready:return super().contact_force()
  wp.launch(clear_previous,self.face_ids.size,[self.face_count,self.face_ids,self.ff,self.uu,self.dd,self.ww,self.mm,self.cf,self.cu,self.cp,self.power,self.moment])
  for a in [self.active,self.face_count,self.candidate_count,self.external,self.hcount]:a.zero_()
  lo=wp.vec3d(self.cad.vertices.min(0));hi=wp.vec3d(self.cad.vertices.max(0))
  wp.launch(corner_frame,self.href.size,[wp.mat33d(self.R),wp.vec3d(self.T0),wp.vec3d(self.travel),wp.float64(self.load),wp.float64(self.hold),self.clock,self.hptr,self.hids,self.hw,self.href,self.q,self.hcorners,self.toolpose])
  wp.launch(parent_faces,self.nfaces,[self.hparent,self.howner,self.hcorners,self.hroundoff,lo,hi,self.hcount,self.hfaces,self.bad])
  wp.launch(exact_active_frame,self.nfaces,[wp.mat33d(self.R),self.toolpose,self.sptr,self.sids,self.sw,self.reference,self.q,self.vh,self.xx,self.vv,self.local,self.hcount,self.hfaces,lo,hi,self.face_count,self.face_ids,self.bad])
  wp.launch(candidate_pairs,self.face_ids.size*self.ncells,[self.local,self.cellbounds,self.ncells,self.face_count,self.face_ids,self.candidate_count,self.candidate_ids,self.bad])
  wp.launch(clip_pairs,self.candidate_ids.size,[self.local,self.planes,self.ncells,self.candidate_count,self.candidate_ids,self.active,self.compact_faces,self.compact_counts,self.compact_polygon,self.compact_cells,self.bad])
  query_args=[self.inside_ptr,self.inside_ids,self.compact_cells]
  if self.grid_query:
   g=self.grid_candidates;query_args=[g.ptr,g.ids,wp.vec3d(g.origin),wp.vec3i(g.shape),g.h]
  wp.launch(integrate_grid if self.grid_query else integrate_interior,64*8*self.resolution*self.resolution,[self.cad.mesh.id,self.tri]+query_args+[wp.mat33d(self.R),self.toolpose,self.xx,self.vv,self.areas,self.masters,self.compact_polygon,self.compact_counts,self.compact_faces,self.active,self.bad,self.ff,self.uu,self.dd,self.ww,self.mm])
  wp.launch(collect_active,self.face_ids.size,[self.face_count,self.face_ids,self.ff,self.uu,self.dd,self.ww,self.mm,self.cf,self.cu,self.cp,self.power,self.moment,self.sptr,self.sids,self.sw,self.external])
  wp.launch(guard_active,1,[self.face_count,self.face_ids,self.cf,self.bad,self.peak,self.cut_force]);self.stress();wp.launch(gather,((self.ncap+3)//4)*128,[self.iptr,self.iidx,self.ig,self.P,self.external,self.force,self.counts],block_dim=128)
