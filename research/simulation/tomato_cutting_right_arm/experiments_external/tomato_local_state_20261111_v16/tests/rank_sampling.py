from pathlib import Path
import sys,json,numpy as np,time
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from local_reference import LocalBody
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

def audit(b):
 B=np.zeros((6*len(b.X),3*len(b.u)))
 for p in range(len(b.X)):
  for k,a in enumerate(b.ids[p]):
   x,y,z=b.G[p,k];j=3*a;r=6*p
   B[r,j]+=x;B[r+1,j+1]+=y;B[r+2,j+2]+=z;B[r+3,j]+=y;B[r+3,j+1]+=x;B[r+4,j]+=z;B[r+4,j+2]+=x;B[r+5,j+1]+=z;B[r+5,j+2]+=y
 B*=np.repeat(np.sqrt(b.V),6)[:,None];s=np.linalg.svd(B,compute_uv=False);rank=int(np.sum(s>s[0]*1e-9));comp=len(np.unique(b.components()));return {'rank':rank,'expected':3*len(b.u)-6*comp,'nullity':3*len(b.u)-rank,'groups':len(b.u),'components':comp}
out=[]
for order in [2,3]:
 for normal,plane in [([1,.27,.13],.001),([1,.51,.31],-.0007),([1,1,1],0.)]:
  b=LocalBody(order=order);b.topology(np.where(b.X@normal<plane,1,2));row={'order':order,'normal':normal,'plane':plane,'quadrature_points':len(b.X),**audit(b)};out.append(row);print(row,flush=True)
(W/'rank_sampling.json').write_text(json.dumps(out,indent=2))
