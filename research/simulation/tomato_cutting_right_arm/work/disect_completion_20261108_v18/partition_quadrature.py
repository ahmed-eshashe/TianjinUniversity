from cohesive_transfer import Transfer
from pathlib import Path
import numpy as np,json
W=Path(__file__).resolve().parent;s=Transfer();x=s.mesh['x'];faces=s.mesh['cut_minus'];tri=x[faces];centers=np.array([np.average(s.mapping['source_pair_coordinates'][p['pair_indices']],axis=0,weights=p['weights']) for p in s.registry['patches']])[:,1:]
def clip(poly,n,b):
 out=[]
 for a,c in zip(poly,np.roll(poly,-1,axis=0)):
  da=a@n-b;dc=c@n-b
  if da<=0:out.append(a)
  if (da<0 and dc>0) or (dc<0 and da>0):out.append(a+da/(da-dc)*(c-a))
 return np.array(out).reshape(-1,2)
base=np.array([[2/3,1/6,1/6],[1/6,2/3,1/6],[1/6,1/6,2/3]])
records=[]
for fi,t in enumerate(tri):
 for g,c in enumerate(centers):
  poly=t[:,1:].copy()
  for j,other in enumerate(centers):
   if j==g:continue
   poly=clip(poly,other-c,(other@other-c@c)/2)
   if len(poly)<3:break
  if len(poly)<3:continue
  D=np.column_stack([t[1,1:]-t[0,1:],t[2,1:]-t[0,1:]])
  for k in range(1,len(poly)-1):
   sub=poly[[0,k,k+1]];area=abs(np.linalg.det(np.column_stack([sub[1]-sub[0],sub[2]-sub[0]])))/2
   if area<=1e-24:continue
   uv=np.linalg.solve(D,(sub-t[0,1:]).T).T;B=np.column_stack([1-uv.sum(1),uv]);records.append((fi,g,area,B))
for refined,name in [(False,'quadrature_proposal.npz'),(True,'quadrature_refined.npz')]:
 F=[];B=[];G=[];R=[]
 for fi,g,area,b in records:
  patches=[b]
  if refined:
   a,c,d=b;ac=(a+c)/2;ad=(a+d)/2;cd=(c+d)/2;patches=[np.array(p) for p in [[a,ac,ad],[ac,c,cd],[ad,cd,d],[ac,cd,ad]]]
  for patch in patches:
   F.extend([faces[fi]]*3);B.extend(base@patch);G.extend([g]*3);R.extend([area/(3*len(patches))]*3)
 F=np.array(F);B=np.array(B);G=np.array(G);R=np.array(R);sums=np.bincount(G,weights=R,minlength=47);assert np.all(sums>0)
 np.savez_compressed(W/name,faces=F,barycentric=B,groups=G,weights=R/sums[G],points=np.einsum('ni,nij->nj',B,x[F]))
out=dict(method='Exact planar nearest-centroid partitions, positive triangle quadrature; same 47 groups and budgets',partition_triangles=len(records),area_sum_m2=float(sum(r[2] for r in records)),expected_area_m2=float(np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1).sum()/2))
(W/'partition_quadrature.json').write_text(json.dumps(out,indent=2));print(out)
