"""Same material/contact integration, visiting only current/previous active faces.

No material boundary face is discarded. The complete boundary is tested each
force evaluation; stored contact and ledgers are explicitly cleared/updated.
"""
import warp as wp
from paid_contact_gpu import ContactGPU as Base
from supported_contact_gpu import ContactGPU as MechanicalBase
from compact_contact_gpu import active_faces,candidate_pairs,clip_pairs,integrate_interior
from parallel_partition_gpu import frame
from persistent_gpu import gather
from grid_quadrature import integrate_grid
from grid_cad_candidates import GridCandidates

@wp.kernel
def clear_previous(n:wp.array(dtype=int),ids:wp.array(dtype=int),ff:wp.array2d(dtype=wp.vec3d),uu:wp.array(dtype=wp.float64),dd:wp.array(dtype=wp.float64),ww:wp.array(dtype=wp.float64),mm:wp.array(dtype=wp.vec3d),cf:wp.array(dtype=wp.vec3),cu:wp.array(dtype=float),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3)):
 k=wp.tid()
 if k<n[0]:
  face=ids[k];uu[face]=wp.float64(0.);dd[face]=wp.float64(0.);ww[face]=wp.float64(0.);mm[face]=wp.vec3d(wp.float64(0.))
  for v in range(3):
   i=face*3+v;ff[face,v]=wp.vec3d(wp.float64(0.));cf[i]=wp.vec3(0.);cu[i]=0.;cp[i]=0.;power[i]=0.;moment[i]=wp.vec3(0.)

@wp.kernel
def collect_active(n:wp.array(dtype=int),ids:wp.array(dtype=int),ff:wp.array2d(dtype=wp.vec3d),uu:wp.array(dtype=wp.float64),dd:wp.array(dtype=wp.float64),ww:wp.array(dtype=wp.float64),mm:wp.array(dtype=wp.vec3d),cf:wp.array(dtype=wp.vec3),cu:wp.array(dtype=float),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3),ptr:wp.array(dtype=int),nodes:wp.array(dtype=int),weights:wp.array(dtype=wp.float64),external:wp.array(dtype=wp.vec3)):
 k=wp.tid()
 if k<n[0]:
  face=ids[k]
  for v in range(3):
   i=face*3+v;f=wp.vec3(ff[face,v]);cf[i]=f;cu[i]=float(uu[face]/wp.float64(3.));cp[i]=float(dd[face]/wp.float64(3.));power[i]=float(ww[face]/wp.float64(3.));moment[i]=wp.vec3(mm[face]/wp.float64(3.))
   for j in range(ptr[i],ptr[i+1]):wp.atomic_add(external,nodes[j],float(weights[j])*f)

@wp.kernel
def guard_active(n:wp.array(dtype=int),ids:wp.array(dtype=int),cf:wp.array(dtype=wp.vec3),bad:wp.array(dtype=int),peak:wp.array(dtype=float),cut:wp.array(dtype=wp.vec3d)):
 total=wp.float64(0.)
 for k in range(n[0]):
  for v in range(3):total+=wp.length(wp.vec3d(cf[3*ids[k]+v]))
 total+=wp.length(cut[0]);wp.atomic_max(peak,0,float(total))
 if total>wp.float64(2.) or not wp.isfinite(total):wp.atomic_max(bad,0,3)

@wp.kernel
def ledger_active(n:wp.array(dtype=int),ids:wp.array(dtype=int),cf:wp.array(dtype=wp.vec3),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3),impulse:wp.array(dtype=wp.vec3),angular:wp.array(dtype=wp.vec3),work:wp.array(dtype=float),diss:wp.array(dtype=float),dt:float,bad:wp.array(dtype=int)):
 k=wp.tid()
 if k<n[0] and bad[0]==0:
  for v in range(3):
   i=3*ids[k]+v;impulse[i]+=dt*cf[i];angular[i]+=dt*moment[i];work[i]+=dt*power[i];diss[i]+=dt*cp[i]

class ContactGPU(Base):
 def __init__(self,*args,grid_query=False,**kwargs):
  self.enable_cutting=False;self.sparse_ready=False;super().__init__(*args,**kwargs)
  if not self.exact_interior:raise ValueError('exact CAD-domain quadrature required')
  self.grid_query=grid_query
  if grid_query:self.grid_candidates=GridCandidates(self.cad)
  self.sparse_ready=True
 def one(self):
  if self.enable_cutting:return super().one()
  return MechanicalBase.one(self)
 def configure_vectors(self,*args,**kwargs):
  if not self.enable_cutting:self.enable_cutting=True;self.graphs.clear()
  return super().configure_vectors(*args,**kwargs)
 def guard_cut_force(self):
  if not self.sparse_ready:return super().guard_cut_force()
  wp.launch(guard_active,1,[self.face_count,self.face_ids,self.cf,self.bad,self.peak,self.cut_force])
 def contact_ledger(self,weight):
  if not self.sparse_ready:return super().contact_ledger(weight)
  wp.launch(ledger_active,self.face_ids.size,[self.face_count,self.face_ids,self.cf,self.cp,self.power,self.moment,self.impulse,self.angular,self.work,self.diss,weight*self.dt,self.bad])
 def contact_force(self):
  if not self.sparse_ready:return super().contact_force()
  wp.launch(clear_previous,self.face_ids.size,[self.face_count,self.face_ids,self.ff,self.uu,self.dd,self.ww,self.mm,self.cf,self.cu,self.cp,self.power,self.moment])
  for a in [self.active,self.face_count,self.candidate_count,self.external]:a.zero_()
  wp.launch(frame,self.nfaces,[wp.mat33d(self.R),wp.vec3d(self.T0),wp.vec3d(self.travel),wp.float64(self.load),wp.float64(self.hold),self.clock,self.sptr,self.sids,self.sw,self.reference,self.q,self.vh,self.xx,self.vv,self.local,self.toolpose])
  wp.launch(active_faces,self.nfaces,[self.local,wp.vec3d(self.cad.vertices.min(0)),wp.vec3d(self.cad.vertices.max(0)),self.face_count,self.face_ids,self.bad])
  wp.launch(candidate_pairs,self.face_ids.size*self.ncells,[self.local,self.cellbounds,self.ncells,self.face_count,self.face_ids,self.candidate_count,self.candidate_ids,self.bad])
  wp.launch(clip_pairs,self.candidate_ids.size,[self.local,self.planes,self.ncells,self.candidate_count,self.candidate_ids,self.active,self.compact_faces,self.compact_counts,self.compact_polygon,self.compact_cells,self.bad])
  query_args=[self.inside_ptr,self.inside_ids,self.compact_cells]
  if self.grid_query:
   g=self.grid_candidates;query_args=[g.ptr,g.ids,wp.vec3d(g.origin),wp.vec3i(g.shape),g.h]
  wp.launch(integrate_grid if self.grid_query else integrate_interior,64*8*self.resolution*self.resolution,[self.cad.mesh.id,self.tri]+query_args+[wp.mat33d(self.R),self.toolpose,self.xx,self.vv,self.areas,self.masters,self.compact_polygon,self.compact_counts,self.compact_faces,self.active,self.bad,self.ff,self.uu,self.dd,self.ww,self.mm])
  wp.launch(collect_active,self.face_ids.size,[self.face_count,self.face_ids,self.ff,self.uu,self.dd,self.ww,self.mm,self.cf,self.cu,self.cp,self.power,self.moment,self.sptr,self.sids,self.sw,self.external])
  wp.launch(guard_active,1,[self.face_count,self.face_ids,self.cf,self.bad,self.peak,self.cut_force]);self.stress();wp.launch(gather,((self.ncap+3)//4)*128,[self.iptr,self.iidx,self.ig,self.P,self.external,self.force,self.counts],block_dim=128)
