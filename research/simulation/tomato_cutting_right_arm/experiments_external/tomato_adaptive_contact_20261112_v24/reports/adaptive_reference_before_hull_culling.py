"""Independent adaptive surface integral of the unchanged CAD/contact law.

Priority refinement controls a reported quadrature error estimate. It is not a
replacement for the separate conservative whole-volume penetration certificate.
"""
import heapq,itertools,time
import numpy as np
from independent_cad_query import query_mesh
from contact_law import evaluate
RULE=np.array([[2/3,1/6,1/6],[1/6,2/3,1/6],[1/6,1/6,2/3]])

def facets(a):
 b=a.body;registry={}
 if np.any(b.codes) or any(len(p)!=4 for p in b.polys):raise ValueError('intact surface reference only')
 for ids in b.ids:
  for c in itertools.combinations(ids,3):registry.setdefault(tuple(sorted(c)),[]).append(c)
 ids=np.array([v[0] for v in registry.values() if len(v)==1]);X=b.grid[ids];area=np.linalg.norm(np.cross(X[:,1]-X[:,0],X[:,2]-X[:,0]),axis=1)/2
 return ids,X,area

def integral(a,cad,T,R,tool_velocity,relative_tol=.002,absolute_tol_N=1e-7,max_leaves=4096,max_depth=24):
 ids,X,areas=facets(a);points=a.body.grid+a.E@a.q;vel=a.E@a.v;F=np.zeros_like(points);energy=friction=power=0.;resultant=np.zeros(3);moment=np.zeros(3);diagnostics=[];queries=0;started=time.perf_counter();bbmin=cad.vertices.min(0);bbmax=cad.vertices.max(0);seq=0
 for face,nodes in enumerate(ids):
  x=points[nodes];vv=vel[nodes];xlocal=(x-T)@R;A=areas[face]
  if np.any(xlocal.max(0)<bbmin) or np.any(xlocal.min(0)>bbmax):continue
  def leaf(B,depth):
   nonlocal queries
   p=B@x;ref=B@X[face];Ar=np.linalg.norm(np.cross(ref[1]-ref[0],ref[2]-ref[0]))/2
   center=p.mean(0);radius=np.linalg.norm(p-center,axis=1).max()
   q=query_mesh(cad.vertices,cad.faces,((center-T)@R)[None]);queries+=1
   # Exact zero from a conservative Lipschitz bound (CPU float64 query).
   if q['phi'][0]>radius+2e-9:return (np.zeros((3,3)),0.,0.,0.,np.zeros(3),0.,B,depth,True)
   edges=np.array([[0,1],[0,2],[1,2]]);long=edges[np.linalg.norm(p[edges[:,0]]-p[edges[:,1]],axis=1).argmax()];mid=(B[long[0]]+B[long[1]])/2;left=B.copy();right=B.copy();left[long[0]]=mid;right[long[1]]=mid
   bary=np.concatenate([RULE@B,RULE@left,RULE@right]);pos=bary@x;v=bary@vv;query=query_mesh(cad.vertices,cad.faces,(pos-T)@R);queries+=len(pos);normal=query['normal']@R.T;area=np.r_[np.full(3,Ar/3),np.full(6,Ar/6)];law=evaluate(query['phi'],normal,v-tool_velocity,area);f=law['force'];low=bary[:3].T@f[:3];high=bary[3:].T@f[3:];err=float(np.linalg.norm(high-low,axis=1).sum())
   if not np.any(query['phi']<0):err=max(err,1e9*Ar*max(radius-q['phi'][0],0)*np.sqrt(1.04))
   U=.5*1e9*np.sum(area[3:]*np.maximum(-query['phi'][3:],0)**2);D=-np.sum(law['friction_force'][3:]*(v[3:]-tool_velocity));W=np.sum(f[3:]*tool_velocity);M=np.cross(pos[3:]-T,f[3:]).sum(0)
   return (high,U,D,W,M,err,B,depth,False)
  first=leaf(np.eye(3),0);leaves={0:first};heap=[(-first[5],0)];total=first[0].copy();U,D,W,M,err=first[1],first[2],first[3],first[4].copy(),first[5];seq=1;depth_max=0
  atol=absolute_tol_N*A/areas.sum()
  while err>atol+relative_tol*np.linalg.norm(total,axis=1).sum():
   if len(leaves)>=max_leaves:raise ValueError(('adaptive surface capacity',face,len(leaves),err))
   _,k=heapq.heappop(heap);old=leaves.pop(k);B,depth=old[6],old[7];depth_max=max(depth_max,depth)
   if depth>=max_depth:raise ValueError(('unresolved adaptive contact',face,depth,err))
   p=B@x;edges=np.array([[0,1],[0,2],[1,2]]);i,j=edges[np.linalg.norm(p[edges[:,0]]-p[edges[:,1]],axis=1).argmax()];mid=(B[i]+B[j])/2;left=B.copy();right=B.copy();left[i]=mid;right[j]=mid
   total-=old[0];U-=old[1];D-=old[2];W-=old[3];M-=old[4];err-=old[5]
   for child in [left,right]:
    r=leaf(child,depth+1);leaves[seq]=r;heapq.heappush(heap,(-r[5],seq));seq+=1;total+=r[0];U+=r[1];D+=r[2];W+=r[3];M+=r[4];err+=r[5]
  F[nodes]+=total;energy+=U;friction+=D;power+=W;moment+=M;diagnostics.append({'face':face,'leaves':len(leaves),'depth':depth_max,'estimated_force_error_N':err,'force_N':np.linalg.norm(total,axis=1).sum()})
 return dict(force=a.E.T@F,energy=energy,friction_power=friction,tool_power=power,moment=moment,diagnostics=diagnostics,queries=queries,wall_s=time.perf_counter()-started)
