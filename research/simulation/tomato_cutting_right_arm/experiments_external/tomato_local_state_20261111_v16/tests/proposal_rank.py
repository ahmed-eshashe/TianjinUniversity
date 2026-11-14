"""Static algebra feasibility for a proposed alternative; not a new simulator."""
from pathlib import Path
import sys,itertools,json,time,numpy as np
from scipy.spatial import ConvexHull
from scipy.sparse import coo_matrix,csr_matrix
from scipy.sparse.csgraph import connected_components
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from local_reference import compatible

def clip(v,n,d):
 s=v@np.array(n)-d
 if np.max(s)<=1e-14:return v
 if np.min(s)>=-1e-14:return None
 faces=ConvexHull(v).simplices;edges=set()
 for f in faces:
  edges.update(tuple(sorted(a)) for a in itertools.combinations(f,2))
 out=list(v[s<=1e-14])
 for i,j in edges:
  if s[i]*s[j]<-1e-25:out.append(v[i]+s[i]/(s[i]-s[j])*(v[j]-v[i]))
 return np.unique(np.round(np.array(out),14),axis=0)

def moments(v):
 h=ConvexHull(v);c=np.mean(v,axis=0);V=0.;m=np.zeros(3)
 for f in h.simplices:
  p=v[f];vol=abs(np.linalg.det(p-c))/6;V+=vol;m+=vol*(p.sum(0)+c)/4
 return V,m/V

def audit(normal,d,partial=False):
 n=2;h=.006;nodes=np.array(list(itertools.product(range(n+1),repeat=3)),int);lookup={tuple(p):i for i,p in enumerate(nodes)};grid=(nodes-n/2)*h;pieces=[];total_original=0.
 for c in itertools.product(range(n),repeat=3):
  for perm in itertools.permutations(range(3)):
   v=[np.array(c)];x=np.array(c)
   for axis in perm:x=x.copy();x[axis]+=1;v.append(x)
   ids=np.array([lookup[tuple(p)] for p in v]);coords=grid[ids];inv=np.linalg.inv(np.c_[np.ones(4),coords]);G=inv[1:,:].T;V0=abs(np.linalg.det(coords[1:]-coords[0]))/6;total_original+=V0
   pending=[(coords,0)]
   if partial:
    lower=clip(coords,[0,1,0],0);upper=clip(coords,[0,-1,0],0);pending=[]
    if lower is not None:pending.append((lower,0))
    if upper is not None:pending.append((upper,3))
   for poly,code in pending:
    if partial and code==0:parts=[(poly,0)]
    else:parts=[(clip(poly,normal,d),1),(clip(poly,-np.array(normal),-d),2)]
    for pv,lab in parts:
     if pv is None:continue
     vol,cent=moments(pv);N=np.r_[1,cent]@inv
     assert vol>0 and N.min()>-1e-8 and abs(N.sum()-1)<1e-10
     pieces.append((ids,G,vol,N,lab,cent))
 mapping={};parent=[]
 for a in range(len(grid)):
  labs=sorted(set(p[4] for p in pieces if a in p[0]));adj=np.array([[compatible(i,j) for j in labs] for i in labs]);nc,lab=connected_components(csr_matrix(adj),directed=False)
  for k in range(nc):
   new=len(parent);parent.append(a)
   for j,z in enumerate(labs):
    if lab[j]==k:mapping[(a,z)]=new
 ids=np.array([[mapping[(a,p[4])] for a in p[0]] for p in pieces]);B=np.zeros((6*len(pieces),3*len(parent)));mass=np.zeros(len(parent))
 for pi,(old,G,V,N,code,c) in enumerate(pieces):
  for k,a in enumerate(ids[pi]):
   x,y,z=G[k];j=3*a;r=6*pi;mass[a]+=1000*V*N[k]
   B[r,j]+=x;B[r+1,j+1]+=y;B[r+2,j+2]+=z;B[r+3,j]+=y;B[r+3,j+1]+=x;B[r+4,j]+=z;B[r+4,j+2]+=x;B[r+5,j+1]+=z;B[r+5,j+2]+=y
  B[6*pi:6*pi+6]*=np.sqrt(V)
 ri=np.repeat(np.arange(len(pieces)),4);ci=len(pieces)+ids.ravel();adj=coo_matrix((np.ones(len(ri)),(ri,ci)),shape=(len(pieces)+len(parent),)*2).tocsr();nc,_=connected_components(adj,directed=False);s=np.linalg.svd(B,compute_uv=False);rank=int(np.count_nonzero(s>s[0]*1e-9));expected=3*len(parent)-6*nc
 mu=1e5/(2*1.4);lam=1e5*.4/(1.4*.2);C=np.eye(6)*mu;C[:3,:3]=lam;C[:3,:3]+=np.eye(3)*2*mu;CB=np.einsum('ij,pjk->pik',C,B.reshape(-1,6,B.shape[1])).reshape(B.shape);K=B.T@CB;im=1/np.sqrt(np.repeat(mass,3));maxeig=np.linalg.eigvalsh(K*im[:,None]*im[None,:])[-1]
 return {'normal':list(normal),'offset_m':d,'partial':partial,'pieces':len(pieces),'nodes':len(parent),'components':nc,'rank':rank,'expected':expected,'rank_pass':rank==expected,'volume_error_relative':abs(sum(p[2] for p in pieces)-total_original)/total_original,'minimum_local_mass_kg':float(mass.min()),'linearized_max_dt_s':float(2/np.sqrt(maxeig)),'static_algebra_only':True}

rows=[]
for n,d,partial in [([1,0,0],0,False),([1,.27,.13],.001,False),([1,.51,.31],-.0007,False),([1,1,1],.00013,False),([1,0,0],0,True),([1,.27,.13],.001,True)]:
 rows.append(audit(n,d,partial));print(rows[-1],flush=True)
(W/'proposal_rank.json').write_text(json.dumps({'status':'static_feasibility_only','results':rows,'no_dynamics_or_fracture_qualification':True},indent=2))
