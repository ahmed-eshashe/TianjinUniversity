from pathlib import Path
w=Path(__file__).resolve().parents[1];s=(w/'src/adaptive_gpu.py').read_text()
s=s.replace('from scipy.spatial import ConvexHull','from pathlib import Path')
s=s.replace('  if not active:r.error=wp.max(r.error,wp.float64(1e9)*Ar*wp.max(radius-sd.phi,wp.float64(0.))*wp.sqrt(wp.float64(1.04)))','  # Exact CAD-interior partition; no unresolved outside-contact region.')
s=s.replace('hull:wp.array(dtype=wp.vec4d),','planes:wp.array2d(dtype=wp.vec4d),bounds:wp.array2d(dtype=wp.vec3d),ncells:int,')
s=s.replace(' face=wp.tid();X=', ' pair=wp.tid();face=pair//ncells;cell=pair%ncells;X=')
s=s.replace('  cf[k]=wp.vec3(0.);cu[k]=0.;cp[k]=0.;power[k]=0.;moment[k]=wp.vec3(0.)','  out=3*pair+vertex;cf[out]=wp.vec3(0.);cu[out]=0.;cp[out]=0.;power[out]=0.;moment[out]=wp.vec3(0.)')
s=s.replace('counts[face]','counts[pair]').replace('query_counts[face]','query_counts[pair]')
s=s.replace('if hi<bbmin[axis] or lo>bbmax[axis]:intersects=False','if hi<bounds[cell,0][axis] or lo>bounds[cell,1][axis]:intersects=False')
s=s.replace('polygon[face,','polygon[pair,').replace('Bs[face,','Bs[pair,').replace('vals[face,','vals[pair,').replace('depths[face,','depths[pair,')
s=s.replace('for h in range(hull.shape[0]):','for h in range(4):').replace('plane=hull[h]','plane=planes[cell,h]').replace('plane[3]-wp.float64(2e-9)','plane[3]')
s=s.replace('>=128','>=10')
s=s.replace('atol=absolute_tol*areas[face]/area_total','atol=absolute_tol*areas[face]/(area_total*wp.float64(ncells))')
s=s.replace('k=3*face+vertex;cf[k]=wp.vec3(total[vertex])','k=3*pair+vertex;cf[k]=wp.vec3(total[vertex])')
a=s.index('class ContactGPU(Base):')
s=s[:a]+'''
@wp.kernel
def collect(ncells:int,ff:wp.array(dtype=wp.vec3),uu:wp.array(dtype=float),dd:wp.array(dtype=float),ww:wp.array(dtype=float),mm:wp.array(dtype=wp.vec3),cf:wp.array(dtype=wp.vec3),cu:wp.array(dtype=float),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3)):
 k=wp.tid();face=k//3;vertex=k%3;f=wp.vec3d(wp.float64(0.));u=wp.float64(0.);d=wp.float64(0.);w=wp.float64(0.);m=wp.vec3d(wp.float64(0.))
 for c in range(ncells):
  j=(face*ncells+c)*3+vertex;f+=wp.vec3d(ff[j]);u+=wp.float64(uu[j]);d+=wp.float64(dd[j]);w+=wp.float64(ww[j]);m+=wp.vec3d(mm[j])
 cf[k]=wp.vec3(f);cu[k]=float(u);cp[k]=float(d);power[k]=float(w);moment[k]=wp.vec3(m)

class ContactGPU(Base):
 def __init__(self,*args,relative_tol=.002,absolute_tol=1e-6,capacity=64,maxdepth=32,**kwargs):
  self.adaptive=False;super().__init__(*args,**kwargs);self.nfaces=len(self._surface.tri_area);self.capacity=capacity;self.relative_tol=relative_tol;self.absolute_tol=absolute_tol;self.maxdepth=maxdepth
  z=np.load(Path(__file__).resolve().parents[1]/'assets/blade_partition.npz');cells=z['x'][z['tets']];self.ncells=len(cells);self.npairs=self.nfaces*self.ncells
  self.planes=wp.array(z['planes'],dtype=wp.vec4d,device='cuda:0');self.bounds=wp.array(np.stack([cells.min(1),cells.max(1)],axis=1),dtype=wp.vec3d,device='cuda:0');self.areas=wp.array(self._surface.tri_area,dtype=wp.float64,device='cuda:0');self.area_total=float(sum(self._surface.tri_area))
  self.polygon=wp.empty((self.npairs,2,10),dtype=wp.vec3d,device='cuda:0');self.Bs=wp.empty((self.npairs,capacity),dtype=wp.mat33d,device='cuda:0');self.vals=wp.empty((self.npairs,capacity),dtype=Value,device='cuda:0');self.depths=wp.empty((self.npairs,capacity),dtype=int,device='cuda:0');self.leaves=wp.zeros(self.npairs,dtype=int,device='cuda:0');self.queries=wp.zeros(self.npairs,dtype=int,device='cuda:0')
  self.pf=wp.zeros(3*self.npairs,dtype=wp.vec3,device='cuda:0');self.pu=wp.zeros(3*self.npairs,dtype=float,device='cuda:0');self.pd=wp.zeros(3*self.npairs,dtype=float,device='cuda:0');self.pw=wp.zeros(3*self.npairs,dtype=float,device='cuda:0');self.pm=wp.zeros(3*self.npairs,dtype=wp.vec3,device='cuda:0');self.adaptive=True
 def contact_force(self):
  if not self.adaptive:return super().contact_force()
  wp.launch(integrate,self.npairs,[self.cad.mesh.id,self.tri,wp.vec3d(self.cad.vertices.min(0)-2e-6),wp.vec3d(self.cad.vertices.max(0)+2e-6),self.planes,self.bounds,self.ncells,wp.mat33d(self.R),wp.vec3d(self.T0),wp.vec3d(self.travel),wp.float64(self.load),wp.float64(self.hold),self.clock,self.sptr,self.sids,self.sw,self.reference,self.areas,wp.float64(self.area_total),self.q,self.vh,self.polygon,self.Bs,self.vals,self.depths,self.leaves,self.queries,self.pf,self.pu,self.pd,self.pw,self.pm,self.bad,self.capacity,wp.float64(self.relative_tol),wp.float64(self.absolute_tol),self.maxdepth],block_dim=32)
  wp.launch(collect,self.ns,[self.ncells,self.pf,self.pu,self.pd,self.pw,self.pm,self.cf,self.cu,self.cp,self.power,self.moment])
  wp.launch(pullback_parallel,((self.n+3)//4)*128,[self.cptr,self.cids,self.cw,self.cf,self.external,self.n],block_dim=128);wp.launch(force_parts,self.nparts,[self.cf,self.part_sum,self.part_mag,self.ns]);wp.launch(force_guard,1,[self.part_sum,self.part_mag,self.bad,self.peak,self.nparts]);self.stress();wp.launch(gather,((self.ncap+3)//4)*128,[self.iptr,self.iidx,self.ig,self.P,self.external,self.force,self.counts],block_dim=128)
'''
(w/'src/partition_gpu.py').write_text(s)
s=(w/'tests/static_gpu.py').read_text().replace('from adaptive_gpu import','from partition_gpu import').replace('static_reference.json','partition_static_reference.json').replace('static_gpu.json','partition_static_gpu.json')
(w/'tests/partition_static_gpu.py').write_text(s)
s=(w/'tests/contact_cycle.py').read_text().replace('from adaptive_gpu import','from partition_gpu import').replace("name='adaptive_'","name='partition_'")
(w/'tests/partition_contact_cycle.py').write_text(s)
