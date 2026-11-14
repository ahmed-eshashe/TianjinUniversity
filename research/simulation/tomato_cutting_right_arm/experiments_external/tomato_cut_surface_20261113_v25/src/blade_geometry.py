from pathlib import Path
import json,numpy as np,warp as wp
from independent_cad_query import query_mesh
from exact_cad_gpu import query_precise

@wp.kernel
def query(mesh:wp.uint64,points:wp.array(dtype=wp.vec3),phi:wp.array(dtype=float),norm:wp.array(dtype=wp.vec3),face:wp.array(dtype=int)):
 i=wp.tid();p=points[i];r=wp.mesh_query_point_sign_winding_number(mesh,p,10.0)
 if r.result:
  c=wp.mesh_eval_position(mesh,r.face,r.u,r.v);d=p-c;l=wp.length(d);phi[i]=r.sign*l;face[i]=r.face
  if l>1.e-12:norm[i]=r.sign*d/l
  else:norm[i]=wp.mesh_eval_face_normal(mesh,r.face)
 else:phi[i]=100.;norm[i]=wp.vec3(0.);face[i]=-1

class CAD:
 def __init__(self):
  data=json.loads((Path(__file__).resolve().parents[1]/'assets/blade_export.json').read_text());v=np.array(data['vertices']);self.faces=np.array(data['triangles'],np.int32);self.vertices=v-[-.24,v[:,1].min(),.00125]
  self.tri=wp.array(self.vertices[self.faces],dtype=wp.vec3d,device="cuda:0")
  self.R=np.array([[0.,0,1],[0,1,0],[-1,0,0]])
  self.mesh=wp.Mesh(points=wp.array(self.vertices,dtype=wp.vec3,device='cuda:0'),indices=wp.array(self.faces.ravel(),dtype=int,device='cuda:0'),support_winding_number=True)
 def query(self,points,T=(0,0,0),R=None,cpu=False):
  R=self.R if R is None else R;local=(np.asarray(points)-T)@R
  if cpu:r=query_mesh(self.vertices,self.faces,local)
  else:
   n=len(local);p=wp.array(local,dtype=wp.vec3d,device='cuda:0');phi=wp.empty(n,dtype=wp.float64,device='cuda:0');norm=wp.empty(n,dtype=wp.vec3d,device='cuda:0')
   wp.launch(query_precise,n,[self.mesh.id,self.tri,p,phi,norm]);r={'phi':phi.numpy(),'normal':norm.numpy()}

  r['normal']=r['normal']@R.T;return r

def certify(tets,cad,T,R=None,limit=.0001,motion=0.,maxdepth=24,allowance=2e-6):
 """Whole closed affine material tets, not only boundary quadrature points.
 Lipschitz signed distance + covering radius; longest-edge bisection.
 motion bounds the complete endpoint-to-endpoint linear swept path.
 """
 pending=np.asarray(tets).copy();queries=0;bound=np.inf;observed=0.;peak=0
 pairs=np.array(list(__import__('itertools').combinations(range(4),2)))
 for level in range(maxdepth+1):
  if not len(pending):break
  c=pending.mean(1);radius=np.linalg.norm(pending-c[:,None],axis=2).max(1)
  phi=cad.query(c,T,R)['phi'];queries+=len(c);observed=max(observed,float(np.maximum(-phi,0).max()));lower=phi-radius-motion-allowance
  if np.any(phi<-limit+allowance):return dict(passed=False,reason='resolved_penetration',observed_m=observed,queries=queries)
  good=lower>=-limit
  if np.any(good):bound=min(bound,float(lower[good].min()))
  pending=pending[~good];peak=max(peak,len(pending))
  if len(pending)==0:break
  if level==maxdepth or len(pending)>300000:return dict(passed=False,reason='unresolved_volume_bound',unresolved=len(pending),queries=queries,depth=level)
  lengths=np.linalg.norm(pending[:,pairs[:,0]]-pending[:,pairs[:,1]],axis=2);edge=pairs[lengths.argmax(1)];ix=np.arange(len(pending));mid=(pending[ix,edge[:,0]]+pending[ix,edge[:,1]])*.5
  left=pending.copy();right=pending.copy();left[ix,edge[:,0]]=mid;right[ix,edge[:,1]]=mid;pending=np.concatenate([left,right])
 return dict(passed=True,reason='certified_affine_material_volume',bound_m=max(0.,-bound),observed_m=observed,queries=queries,max_pending=peak,depth=level,motion_bound_m=motion)
