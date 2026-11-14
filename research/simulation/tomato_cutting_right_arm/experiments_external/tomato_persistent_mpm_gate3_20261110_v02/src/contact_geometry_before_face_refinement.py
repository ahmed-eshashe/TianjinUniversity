"""Exact original CAD queries and a declared closed-cell material reconstruction."""
from pathlib import Path
import os,json,itertools,numpy as np
W=Path(__file__).resolve().parents[1]
os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from reference import compatible
from independent_cad_query import query_mesh

@wp.kernel
def cad_query(mesh:wp.uint64,points:wp.array(dtype=wp.vec3),phi:wp.array(dtype=float),normal:wp.array(dtype=wp.vec3),closest:wp.array(dtype=wp.vec3),face:wp.array(dtype=int)):
 i=wp.tid();p=points[i];q=wp.mesh_query_point_sign_winding_number(mesh,p,10.0)
 if q.result:
  c=wp.mesh_eval_position(mesh,q.face,q.u,q.v);d=p-c;distance=wp.length(d);phi[i]=q.sign*distance;closest[i]=c;face[i]=q.face
  if distance>1e-12:normal[i]=q.sign*d/distance
  else:normal[i]=wp.mesh_eval_face_normal(mesh,q.face)
 else:phi[i]=100.0;normal[i]=wp.vec3(0.0);closest[i]=p;face[i]=-1

class CAD:
 def __init__(self):
  d=json.loads((W/'assets/blade_export.json').read_text());self.original_vertices=np.array(d['vertices']);self.faces=np.array(d['triangles'],np.int32)
  self.anchor=np.array([-.24,self.original_vertices[:,1].min(),.00125]);self.vertices=self.original_vertices-self.anchor
  self.rotation=np.array([[0.,0,1],[0,1,0],[-1,0,0]])
  wp.init();self.mesh=wp.Mesh(points=wp.array(self.vertices,dtype=wp.vec3,device='cuda:0'),indices=wp.array(self.faces.ravel(),dtype=int,device='cuda:0'),support_winding_number=True)
  self.rmax=float(np.linalg.norm(self.vertices,axis=1).max());self.face_kind=np.full(len(self.faces),0,np.int32)
  self.face_kind[2:26]=1 # lower cutting perimeter; frozen exact CAD face IDs
  self.face_kind[40:56]=2 # upper spine
  self.face_kind[[0,1,56,57,58,59,60,61]]=3 # tip perimeter
 def query(self,points,translation=(0,0,0),rotation=None,cpu=False):
  points=np.asarray(points,float);R=self.rotation if rotation is None else np.asarray(rotation,float);T=np.asarray(translation,float);local=(points-T)@R
  if cpu:
   q=query_mesh(self.vertices,self.faces,local)
  else:
   n=len(local);a=wp.array(local,dtype=wp.vec3,device='cuda:0');phi=wp.empty(n,dtype=float,device='cuda:0');normal=wp.empty(n,dtype=wp.vec3,device='cuda:0');close=wp.empty(n,dtype=wp.vec3,device='cuda:0');face=wp.empty(n,dtype=int,device='cuda:0')
   wp.launch(cad_query,dim=n,inputs=[self.mesh.id,a,phi,normal,close,face],device='cuda:0');wp.synchronize();q={'phi':phi.numpy().astype(float),'normal':normal.numpy().astype(float),'closest':close.numpy().astype(float),'face':face.numpy()}
  q['normal']=q['normal']@R.T;q['closest']=q['closest']@R.T+T;q['kind']=self.face_kind[np.clip(q['face'],0,len(self.faces)-1)];return q

class Cells:
 """Union of closed trilinear cells, affine-exact particle pullback per corner.
 This is an explicit candidate contact geometry, not an exact continuum boundary.
 """
 def __init__(self,X,codes,spacing=.0015,qspacing=.00025):
  self.X=np.asarray(X,float);self.codes=np.array(codes,int);self.spacing=spacing;self.bits=np.array(list(itertools.product([0,1],repeat=3)));offsets=(self.bits-.5)*spacing
  tree=cKDTree(X);keys={};corners=[];owner=[];cell=[]
  for p in range(len(X)):
   cc=[]
   for k,z in enumerate(X[p]+offsets):
    key=(*np.rint(z/(spacing/2)).astype(int),int(codes[p]))
    if key not in keys:keys[key]=len(corners);corners.append(z);owner.append(p)
    cc.append(keys[key])
   cell.append(cc)
  self.corner_X=np.array(corners);self.cell=np.array(cell,np.int32);rows=[];cols=[];vals=[];maxcond=0.
  # Local affine reproduction prevents spurious torque from surface-force pullback.
  for i,(z,p) in enumerate(zip(corners,owner)):
   _,ids=tree.query(z,k=min(128,len(X)));ids=np.atleast_1d(ids);ids=np.array([j for j in ids if compatible(int(codes[p]),int(codes[j]))])[:32]
   A=np.vstack((np.ones(len(ids)),((X[ids]-z)/spacing).T));gram=A@A.T
   if np.linalg.matrix_rank(gram)<4:raise ValueError('insufficient same-side geometry to reconstruct cell')
   weights=A.T@np.linalg.solve(gram,np.array([1.,0,0,0]));maxcond=max(maxcond,np.linalg.cond(gram));rows.extend([i]*len(ids));cols.extend(ids);vals.extend(weights)
  self.C=coo_matrix((vals,(rows,cols)),shape=(len(corners),len(X))).tocsr();self.affine_error=float(abs(self.C@X-self.corner_X).max());self.partition_error=float(abs(self.C.sum(1).A.ravel()-1).max());self.max_condition=maxcond
  lookup={tuple(np.rint(x/spacing).astype(int)):i for i,x in enumerate(X)}
  # Avoid bankers-rounding collisions for grids with half-integer coordinates.
  lookup={tuple(np.rint((x-X.min(0))/spacing).astype(int)):i for i,x in enumerate(X)}
  self.boundary=[];nq=int(np.ceil(spacing/qspacing));uv=(np.arange(nq)+.5)/nq;qr=[];qc=[];qv=[];areas=[];qowner=[]
  for p in range(len(X)):
   lattice=np.rint((X[p]-X.min(0))/spacing).astype(int)
   for axis in range(3):
    for side in (0,1):
     adj=lattice.copy();adj[axis]+=2*side-1;j=lookup.get(tuple(adj));external=j is None or not compatible(int(codes[p]),int(codes[j]))
     if not external:continue
     self.boundary.append((p,axis,side));other=[a for a in range(3) if a!=axis]
     for u in uv:
      for v in uv:
       xyz=np.zeros(3);xyz[axis]=side;xyz[other]=[u,v];weights=np.prod(np.where(self.bits,xyz,1-xyz),axis=1);q=len(areas)
       for local,w in enumerate(weights):
        if w:qr.append(q);qc.append(self.cell[p,local]);qv.append(w)
       areas.append(spacing**2/nq**2);qowner.append(p)
  self.QC=coo_matrix((qv,(qr,qc)),shape=(len(areas),len(corners))).tocsr();self.Q=(self.QC@self.C).tocsr();self.area=np.array(areas);self.qowner=np.array(qowner);self.nq=nq
 def points(self,x):return self.Q@x
 def corners(self,x):return (self.C@x)[self.cell]
 def pullback(self,force):return self.Q.T@force
 def certificate(self,x,cad,T=(0,0,0),R=None,limit=.0001,motion_bound=0.,maxdepth=8,cell_mask=None):
  # All trilinear images lie in their corner convex hull. Signed distance is
  # 1-Lipschitz: phi(center)-covering_radius bounds penetration everywhere.
  corners=self.corners(x);corners=corners if cell_mask is None else corners[cell_mask];pending=corners;worst=0.;queries=0;unresolved=0;deepest=0;bound_min=np.inf
  for depth in range(maxdepth+1):
   if not len(pending):break
   centers=pending.mean(1);r=np.linalg.norm(pending-centers[:,None,:],axis=2).max(1);phi=cad.query(centers,T,R)['phi'];queries+=len(centers);lower=phi-r-motion_bound-2e-6
   worst=max(worst,float(np.maximum(-phi,0).max()));deepest=depth
   failed=phi < -limit+2e-6
   if np.any(failed):return {'passed':False,'reason':'resolved_material_penetration','observed_penetration_m':worst,'queries':queries,'depth':depth}
   certified=lower>=-limit
   if np.any(certified):bound_min=min(bound_min,float(lower[certified].min()))
   pending=pending[~certified]
   if not len(pending):break
   if depth==maxdepth:unresolved=len(pending);break
   # Exact subdivision of trilinear maps: use the parent interpolation at new corners.
   children=[]
   for shift in self.bits:
    loc=(self.bits+shift)*.5;weights=np.prod(np.where(self.bits[None,:,:],loc[:,None,:],1-loc[:,None,:]),axis=2)
    children.append(np.einsum('ij,njk->nik',weights,pending))
   pending=np.concatenate(children)
   if len(pending)>1000000:return {'passed':False,'reason':'certificate_capacity','unresolved':len(pending),'queries':queries,'depth':depth}
  return {'passed':not unresolved,'reason':'certified' if not unresolved else 'unresolved_bound','observed_penetration_m':worst,'certified_max_penetration_bound_m':max(0.,-bound_min) if np.isfinite(bound_min) else None,'queries':queries,'depth':deepest,'unresolved':unresolved,'geometry':'entire declared trilinear-cell union, not only sampled centers'}
