"""Surface contact between already-separated material fragments.
Normal forces derive from distance energy. Friction uses a common midpoint
with affine-exact pullbacks on both bodies, preserving force, torque and power.
"""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.spatial import cKDTree
from contact_geometry import wp,cad_query

class Surface:
 def __init__(self,cells,owners,x):
  self.cells=cells;self.owners=owners;tri=[];quads=[]
  for p,axis,side in cells.boundary:
   if not owners[p]:continue
   other=[a for a in range(3) if a!=axis];indices=[]
   for a,b in [(0,0),(1,0),(1,1),(0,1)]:
    target=np.zeros(3,int);target[axis]=side;target[other]=[a,b];indices.append(cells.cell[p,np.where(np.all(cells.bits==target,axis=1))[0][0]])
   v=cells.corner_X[indices];normal=np.cross(v[1]-v[0],v[2]-v[0]);desired=np.eye(3)[axis]*(2*side-1)
   if normal@desired<0:indices=indices[::-1]
   quads.append(indices);tri.extend([[indices[0],indices[1],indices[2]],[indices[0],indices[2],indices[3]]])
  self.quads=np.array(quads);self.faces=np.array(tri,np.int32);self.vertices=cells.C@x
  self.mesh=wp.Mesh(points=wp.array(self.vertices,dtype=wp.vec3,device='cuda:0'),indices=wp.array(self.faces.ravel(),dtype=int,device='cuda:0'),support_winding_number=True)
 def update(self,x):
  self.vertices=self.cells.C@x;self.mesh.points.assign(self.vertices);self.mesh.refit()
 def deviation(self):
  q=self.vertices[self.quads];return float(.25*np.linalg.norm(q[:,0]+q[:,2]-q[:,1]-q[:,3],axis=1).max())
 def query(self,points,translation=None,rotation=None):
  n=len(points);a=wp.array(points,dtype=wp.vec3,device='cuda:0');phi=wp.empty(n,dtype=float,device='cuda:0');normal=wp.empty(n,dtype=wp.vec3,device='cuda:0');closest=wp.empty(n,dtype=wp.vec3,device='cuda:0');face=wp.empty(n,dtype=int,device='cuda:0');wp.launch(cad_query,dim=n,inputs=[self.mesh.id,a,phi,normal,closest,face],device='cuda:0');wp.synchronize();return {'phi':phi.numpy().astype(float),'normal':normal.numpy().astype(float),'closest':closest.numpy().astype(float),'face':face.numpy()}
 def matrix(self,query):
  f=self.faces[query['face']];verts=self.vertices[f];q=query['closest'];a=verts[:,1]-verts[:,0];b=verts[:,2]-verts[:,0];r=q-verts[:,0];aa=np.sum(a*a,1);bb=np.sum(b*b,1);ab=np.sum(a*b,1);ar=np.sum(a*r,1);br=np.sum(b*r,1);det=aa*bb-ab*ab;u=(ar*bb-br*ab)/det;v=(br*aa-ar*ab)/det;weights=np.stack((1-u-v,u,v),1)
  mat=coo_matrix((weights.ravel(),(np.repeat(np.arange(len(q)),3),f.ravel())),shape=(len(q),len(self.vertices))).tocsr();return mat@self.cells.C

def correct_to_point(base,target,x,owners,spacing):
 old=base@x;delta=target-old;ids_all=np.flatnonzero(owners);tree=cKDTree(x[ids_all]);_,ids=tree.query(old,k=16);ids=ids_all[ids]
 D=(x[ids]-old[:,None,:])/spacing;A=np.concatenate((np.ones((len(old),16,1)),D),axis=2).transpose(0,2,1);rhs=np.concatenate((np.zeros((len(old),1)),delta/spacing),axis=1);g=A@A.transpose(0,2,1);sol=np.linalg.solve(g,rhs);corr=np.einsum('nki,nk->ni',A,sol)
 add=coo_matrix((corr.ravel(),(np.repeat(np.arange(len(old)),16),ids.ravel())),shape=base.shape).tocsr();return base+add

class FragmentContact:
 def __init__(self,cells,x,left,right,K=1e9,mu=.2,vs=.001):
  self.cells=cells;self.left=left;self.right=right;self.K=K;self.mu=mu;self.vs=vs;self.surface=Surface(cells,right,x)
  points=cells.Q@cells.X;select=left[cells.qowner]&np.isclose(points[:,0],0.,atol=1e-10);self.QA=cells.Q[select];self.area=cells.area[select]
 def evaluate(self,x,v):
  self.surface.update(x);q=self.QA@x;query=self.surface.query(q);active=query['phi']<0
  if not np.any(active):return {'force':np.zeros_like(x),'energy':0.,'friction_power':0.,'max_force':0.,'sum_force':0.,'active':0,'net_force':0.,'net_moment':0.}
  A=self.QA[active];qr={k:a[active] for k,a in query.items()};B=self.surface.matrix(qr);qa=A@x;qb=B@x;n=qr['normal'];depth=-qr['phi'];area=self.area[active];fn=self.K*area*depth;normalforce=fn[:,None]*n
  mid=.5*(qa+qb);Am=correct_to_point(A,mid,x,self.left,self.cells.spacing);Bm=correct_to_point(B,mid,x,self.right,self.cells.spacing);rel=(Am-Bm)@v;vt=rel-np.sum(rel*n,1)[:,None]*n;speed=np.linalg.norm(vt,axis=1);fr=-self.mu*fn[:,None]*np.tanh(speed/self.vs)[:,None]*vt/np.maximum(speed[:,None],1e-30);force=(A-B).T@normalforce+(Am-Bm).T@fr
  return {'force':force,'energy':float(.5*self.K*np.sum(area*depth**2)),'friction_power':float(-np.sum(fr*rel)),'max_force':float(np.linalg.norm(force[self.left].sum(0))),'sum_force':float(np.linalg.norm(normalforce+fr,axis=1).sum()),'active':int(active.sum()),'net_force':float(np.linalg.norm(force.sum(0))),'net_moment':float(np.linalg.norm(np.cross(x,force).sum(0)))}
