"""Local affine continuity, replacing over-merged virtual-node labels.

Only clipped regions gain separate affine coefficients. Compatible neighbours
agree at their physical common face; fracture faces receive no such constraint.
No springs, force corrections, mass scaling or rest-state resets are added.
This candidate must pass mechanics and response refinement before adoption.
"""
import numpy as np,time,copy
from scipy.spatial import ConvexHull
from scipy.sparse import coo_matrix,csr_matrix,diags,vstack,eye
from scipy.sparse.csgraph import connected_components
from scipy.linalg import qr,cho_factor,cho_solve,eigvalsh
from shapely import Polygon,STRtree
from reference_v17 import compatible
from fast_aggregation import Aggregate as Base,vertex_fields,strain_matrix

def facet_groups(b):
 groups={};cache=list(getattr(b,'_facet_cache',[None for _ in b.polys]))
 if len(cache)!=len(b.polys):raise ValueError('facet cache ownership mismatch')
 for r,poly in enumerate(b.polys):
  if cache[r] is None:
   center=poly.mean(0);scale=np.ptp(poly,axis=0).max();hull=ConvexHull((poly-center)/scale);faces={};records=[]
   for tri,eq in zip(hull.simplices,hull.equations):
    normal=eq[:3];d=eq[3]*scale-normal@center;faces.setdefault(tuple(np.round(np.r_[normal,d],10)),[]).extend(tri)
   for oriented,ids in faces.items():
    pts=poly[np.unique(ids)];normal=np.array(oriented[:3]);normal/=np.linalg.norm(normal)
    hints=[(b.G[r,k],-b.inv[r,0,k]) for k in range(4)]+getattr(b,'_region_plane_hints',[[] for _ in b.polys])[r]
    for hn,hd in hints:
     length=np.linalg.norm(hn);unit=hn/length
     if abs(unit@normal)>1.-1e-7 and np.max(abs(pts@unit-hd/length))<1e-12:
      normal=unit*np.sign(unit@normal);break
    flip=1 if normal[np.argmax(abs(normal))]>0 else -1;canonical=normal*flip;d=-canonical@pts[0];key=tuple(np.round(np.r_[canonical,d],10));records.append((key,pts,normal))
   cache[r]=dict(center=center,triangles=poly[hull.simplices],faces=records)
  for key,pts,normal in cache[r]['faces']:groups.setdefault(key,[]).append((r,pts,normal))
 b._facet_cache=cache
 return groups

def loosen(body):
 b=body.clone();ids=b.ids.copy();grid=b.grid.tolist();u=b.u.tolist();v=b.v.tolist();legacy=list(range(len(b.u)));clipped=np.zeros(len(b.X),bool)
 for r,p in enumerate(b.polys):
  corners=b.grid[b.ids[r]]
  full=len(p)==4 and np.array_equal(np.array(sorted(map(tuple,p))),np.array(sorted(map(tuple,corners))))
  if full:continue
  clipped[r]=True;ids[r]=np.arange(len(grid),len(grid)+4);grid.extend(corners.tolist());u.extend(b.u[b.ids[r]].tolist());v.extend(b.v[b.ids[r]].tolist());legacy.extend(b.ids[r].tolist())
 used,newids=np.unique(ids,return_inverse=True);b.ids=newids.reshape(-1,4);b.grid=np.array(grid)[used];b.u=np.array(u)[used];b.v=np.array(v)[used];b._legacy_mapping=np.array(legacy)[used];b._legacy_count=len(body.u);b._previous_valid_basis=getattr(body,'_valid_basis',None);b.rebuild();b.freeze_geometry();return b,clipped

def elimination(b,clipped,coalesce=True):
 n=len(b.u);rows=[];specs=[];pair_edges=[];patches=0;rejected_slivers=[];groups=facet_groups(b);h=b.config['h'];parent_corners=[set(map(tuple,b.grid[ids])) for ids in b.ids]
 legacy=coo_matrix((np.ones(n),(np.arange(n),b._legacy_mapping)),shape=(n,b._legacy_count)).tocsr();legacy=legacy if b._previous_valid_basis is None else legacy@b._previous_valid_basis
 for key,entries in groups.items():
  normal=entries[0][2].copy();normal*=np.sign(normal@np.array(key[:3]));normal/=np.linalg.norm(normal);axis=np.eye(3)[np.argmin(abs(normal))];u=np.cross(normal,axis);u/=np.linalg.norm(u);v=np.cross(normal,u);basis=np.array([u,v]);origin=entries[0][1][0];polys=[]
  for owner,pts,norm in entries:
   if np.max(abs((pts-origin)@normal))>1e-11:raise ValueError('ambiguous continuity plane')
   polys.append(Polygon((pts-origin)@basis.T).convex_hull)
  tree=STRtree(polys)
  for i,poly in enumerate(polys):
   r,pts,nr=entries[i]
   for j in tree.query(poly):
    if j<=i:continue
    q,other,nq=entries[j]
    if nr@nq>=0 or not compatible(b.codes[r],b.codes[q]):continue
    # Distinct original tetrahedra sharing only an edge or vertex cannot have
    # a positive-area material interface. Reject polygon roundoff slivers
    # using that exact combinatorial fact, not an area/material cutoff.
    common=parent_corners[r]&parent_corners[q]
    if len(common)<3:continue
    if len(common)==3 and np.max(abs((np.asarray(list(common))-origin)@normal))>1e-12:continue
    # An active/inactive pair for a cut can share material area only on a
    # recorded crack-front plane. Otherwise their projected overlap is a
    # line/point; roundoff must not turn it into a hard continuity constraint.
    front_mismatch=False
    for cut in range(4):
     dr=(b.codes[r]//3**cut)%3;dq=(b.codes[q]//3**cut)%3
     if (dr==0)==(dq==0):continue
     for owner,points in [(r,pts),(q,other)]:
      matching=False
      for cid,fn,fd in getattr(b,'_region_front_planes',[[] for _ in b.polys])[owner]:
       unit=fn/np.linalg.norm(fn)
       if cid==cut and abs(unit@normal)>1.-1e-7 and np.max(abs(points@unit-fd/np.linalg.norm(fn)))<1e-12:matching=True;break
      if not matching:front_mismatch=True
    if front_mismatch:continue
    shared=poly.intersection(polys[j])
    if shared.area<=0:continue
    if not(clipped[r] or clipped[q]):pair_edges.append((r,q));continue
    point=origin+np.array(shared.centroid.coords[0])@basis;coefficients=[(np.r_[1.,point]@b.inv[r],np.r_[1.,point]@b.inv[q]),(h*b.G[r]@u,h*b.G[q]@u),(h*b.G[r]@v,h*b.G[q]@v)]
    candidate_rows=[];candidate_specs=[]
    for component,(left,right) in enumerate(coefficients):
     row=coo_matrix((np.r_[left,-right],(np.zeros(8,int),np.r_[b.ids[r],b.ids[q]])),shape=(1,n)).tocsr();row.eliminate_zeros();norm=np.linalg.norm(row.data)
     if norm>1e-14:candidate_rows.append(row/norm);candidate_specs.append((r,q,component,normal.copy(),nr.copy(),nq.copy(),float(shared.area),point.copy()))
    # Fracture removes bonds; it can never create a constraint excluding a
    # previously admissible field. Use this invariant to reject only numerical
    # line-overlap slivers. A finite-area inconsistency remains a hard failure.
    if candidate_rows and abs(vstack(candidate_rows)@legacy).max()>1e-10:
     roundoff_area=128*np.finfo(float).eps*h*shared.length
     if shared.area>roundoff_area:raise ValueError(('finite-area continuity conflicts with prior admissible space',r,q,shared.area,roundoff_area))
     rejected_slivers.append((r,q,float(shared.area),float(roundoff_area)));continue
    pair_edges.append((r,q));rows.extend(candidate_rows);specs.extend(candidate_specs);patches+=1
 b._constraint_specs=specs;C=vstack(rows).tocsr() if rows else csr_matrix((0,n));legacy_error=float(abs(C@legacy).max()) if C.shape[0] else 0.
 if legacy_error>1e-10:
  row=int(np.argmax(np.asarray(abs(C@legacy).max(axis=1).toarray()).ravel()));r,q,component,n,nr,nq,area,point=specs[row];raise ValueError(('constraints remove valid original fields',legacy_error,'pair',r,q,'codes',b.codes[r],b.codes[q],'component',component,'normal',n,'area',area,'point',point))
 full_C=C;original_n=n;coordinate_roots=np.arange(n);S=eye(n,format='csr')
 if coalesce:
  parent=np.arange(n);blocked_coalescences=0
  def root(i):
   while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
   return i
  # Share affine coefficients only within the SAME original tetrahedron,
  # identical entire fracture history, and an actual positive-area bond.
  # Opposite crack lips and disconnected pieces can never be merged.
  for r,q,*_ in specs:
   if b.codes[r]!=b.codes[q] or not np.array_equal(b.inv[r],b.inv[q]):continue
   for i,j in zip(b.ids[r],b.ids[q]):
    ri,rj=root(i),root(j)
    if ri!=rj:
     # Removing an existing admissible displacement mode can heal a crack
     # even when the actual saved displacement and energy are nearly zero.
     # Equal geometry/history is insufficient; merge only if the PREVIOUS
     # complete state space already enforces equality of these coordinates.
     difference=legacy[ri]-legacy[rj]
     if difference.nnz and abs(difference).max()>1e-10:blocked_coalescences+=1;continue
     parent[max(ri,rj)]=min(ri,rj)
  roots=np.array([root(i) for i in range(n)]);coordinate_roots,index=np.unique(roots,return_inverse=True);S=coo_matrix((np.ones(n),(np.arange(n),index)),shape=(n,len(coordinate_roots))).tocsr();C=C@S;n=len(coordinate_roots)
 C=C.toarray()
 active=np.flatnonzero(np.any(C!=0,axis=0)) if len(C) else np.array([],int);local=C[:,active]
 if not len(C):E=eye(n,format='csr');masters=np.arange(n);rank=0;condition=1.
 else:
  _,R,independent=qr(local.T,mode='economic',pivoting=True);rank=int(np.sum(abs(np.diag(R))>max(abs(R).max(),1.)*1e-11));C0=local[independent[:rank]];_,R,piv=qr(C0,mode='economic',pivoting=True);dependent=active[piv[:rank]];masters=np.setdiff1d(np.arange(n),dependent);A=C[independent[:rank]][:,dependent];rhs=-C[independent[:rank]][:,masters];condition=float(np.linalg.cond(A));values=np.linalg.solve(A,rhs);ei=list(masters);ej=list(range(len(masters)));ev=list(np.ones(len(masters)));ii,jj=np.nonzero(values);ei.extend(dependent[ii]);ej.extend(jj);ev.extend(values[ii,jj]);E=coo_matrix((ev,(ei,ej)),shape=(n,len(masters))).tocsr()
 E=S@E;masters=coordinate_roots[masters];preservation=E@legacy[masters]-legacy;preservation_error=float(abs(preservation).max()) if preservation.nnz else 0.
 if preservation_error>1e-9:raise ValueError(('previous admissible fields removed',preservation_error))
 residual=float(abs(full_C@E).max()) if full_C.shape[0] else 0.;affine=np.c_[np.ones(original_n),b.grid];affine_error=float(np.max(abs(E@affine[masters]-affine)))
 if residual>1e-9 or affine_error>1e-10:raise ValueError(('continuity elimination residual',residual,affine_error,'condition',condition,'rank',rank,'raw_affine_error',float(np.max(abs(full_C@affine)))))
 # Physical connectivity uses shared positive-area compatible material faces.
 rr=[r for r,q in pair_edges]+[q for r,q in pair_edges];cc=[q for r,q in pair_edges]+[r for r,q in pair_edges];graph=coo_matrix((np.ones(len(rr)),(rr,cc)),shape=(len(b.X),len(b.X))).tocsr();components,labels=connected_components(graph,directed=False)
 return E,masters,dict(previous_space_error=preservation_error,blocked_coalescences=blocked_coalescences if coalesce else 0,coalesced_affine_coordinates=original_n-n,rejected_roundoff_bonds=rejected_slivers,continuity_rows=len(C),constraint_rank=rank,local_constraint_columns=len(active),independent_coefficients=len(masters),elimination_condition=condition,constraint_residual=residual,affine_error=affine_error,legacy_field_continuity_error=legacy_error,continuity_patches=patches,physical_components=components),full_C

class Aggregate(Base):
 def __init__(self,body,support_threshold=None,coalesce=True):
  start=time.perf_counter();before=body.metrics();x0,v0=vertex_fields(body);self.body,clipped=loosen(body);b=self.body;self.E,self.masters,self.report,self.constraints=elimination(b,clipped,coalesce=coalesce);b._valid_basis=self.E.copy();self.M=(self.E.T@diags(b.mass)@self.E).tocsr();n=len(self.masters);nc,labels=connected_components(self.M,directed=False);self.order=np.argsort(labels,kind='stable');sizes=np.bincount(labels);self.bounds=np.r_[0,np.cumsum(sizes)];self.singletons=self.order[self.bounds[:-1][sizes==1]];self.single_mass=self.M.diagonal()[self.singletons];self.coupled=[]
  for c in np.flatnonzero(sizes>1):
   ids=self.order[self.bounds[c]:self.bounds[c+1]];self.coupled.append((ids,cho_factor(self.M[ids][:,ids].toarray(),lower=True)))
  self.q=self.solve(self.E.T@(b.mass[:,None]*b.u));self.v=self.solve(self.E.T@(b.mass[:,None]*b.v));self.sync();after=b.metrics();x1,v1=vertex_fields(b);self.transfer=dict(position_m=float(np.max(np.linalg.norm(x1-x0,axis=1))),velocity_m_s=float(np.max(np.linalg.norm(v1-v0,axis=1))),elastic_change_J=after['U']-before['U'],kinetic_change_J=after['T']-before['T'],linear_momentum_abs=float(np.linalg.norm(after['momentum']-before['momentum'])),angular_momentum_abs=float(np.linalg.norm(after['angular']-before['angular'])));dv=np.linalg.norm(v1-v0,axis=1);region=np.maximum.reduceat(dv,b.poly_ptr[:-1]);self.transfer['weighted_velocity_bound_m_s']=float(np.sqrt(b.V@region**2/b.V.sum()));self.transfer['energy_relative']=abs(after['U']+after['T']-before['U']-before['T'])/max(before['U']+before['T'],1e-10);self.transfer['angular_relative']=self.transfer['angular_momentum_abs']/max(float(np.linalg.norm(before['angular'])),1e-12);self.report.update(transfer=self.transfer,aggregated_nodes=0,max_mass_block=int(sizes.max()),mass_total_kg=float(np.ones(n)@(self.M@np.ones(n))),mass_relative_error=abs(float(np.ones(n)@(self.M@np.ones(n)))-body.mass.sum())/body.mass.sum(),clipped_regions=int(clipped.sum()),wall_s=time.perf_counter()-start)
 def audit(self):
  from scipy.sparse import kron
  B=strain_matrix(self.body)@kron(self.E,np.eye(3));s=np.linalg.svd(B,compute_uv=False);rank=int(np.sum(s>s[0]*1e-9));nc=self.report['physical_components'];C=np.eye(6)*self.body.mu;C[:3,:3]=self.body.lam;C[:3,:3]+=np.eye(3)*2*self.body.mu;CB=np.einsum('ij,pjk->pik',C,B.reshape(-1,6,B.shape[1])).reshape(B.shape);K=B.T@CB;M=kron(self.M,np.eye(3)).toarray();eigs=eigvalsh(K,M);return dict(rank=rank,expected_rank=3*len(self.masters)-6*nc,components=nc,linearized_stability_dt_s=float(2/np.sqrt(eigs[-1])),min_mass_eigenvalue=float(np.linalg.eigvalsh(self.M.toarray())[0]),nodes=len(self.masters),regions=len(self.body.X))
