"""Conservative Jacobian bounds for each declared trilinear material cell."""
import itertools,numpy as np
BITS=np.array(list(itertools.product([0.,1.],repeat=3)))
PERMS=[((0,1,2),1),((1,2,0),1),((2,0,1),1),((0,2,1),-1),((2,1,0),-1),((1,0,2),-1)]
def jacobians(corners,spacing):
 # All eight derivatives at the parameter-space corners; F entries are bilinear.
 grad=np.empty((8,8,3))
 for k,u in enumerate(BITS):
  for d in range(3):
   other=[a for a in range(3) if a!=d];grad[k,:,d]=(2*BITS[:,d]-1)/spacing*np.prod(np.where(BITS[:,other],u[other],1-u[other]),axis=1)
 return np.einsum('nbi,kbj->nkij',corners,grad)
def interval_product(la,ua,lb,ub):
 terms=np.stack([la*lb,la*ub,ua*lb,ua*ub]);return terms.min(0),terms.max(0)
def det_bounds(F):
 low=F.min(1);high=F.max(1);lo=np.zeros(len(F));hi=np.zeros(len(F))
 for perm,sign in PERMS:
  a,b=interval_product(low[:,0,perm[0]],high[:,0,perm[0]],low[:,1,perm[1]],high[:,1,perm[1]])
  a,b=interval_product(a,b,low[:,2,perm[2]],high[:,2,perm[2]])
  lo+=a if sign==1 else -b;hi+=b if sign==1 else -a
 return lo,hi
def certificate(cells,x,minJ=.1,maxJ=10.,maxdepth=4):
 pending=cells.corners(x);lower=np.inf;upper=-np.inf;observed_min=np.inf;observed_max=-np.inf;count=0
 for depth in range(maxdepth+1):
  F=jacobians(pending,cells.spacing/(2**depth));d=np.linalg.det(F);observed_min=min(observed_min,float(d.min()));observed_max=max(observed_max,float(d.max()));count+=len(pending)
  if observed_min<=minJ or observed_max>=maxJ:return {'passed':False,'reason':'resolved_inadmissible_material_volume','observed_minJ':observed_min,'observed_maxJ':observed_max,'subcells':count,'depth':depth}
  lo,hi=det_bounds(F);valid=(lo>minJ)&(hi<maxJ)
  if np.any(valid):lower=min(lower,float(lo[valid].min()));upper=max(upper,float(hi[valid].max()))
  pending=pending[~valid]
  if not len(pending):return {'passed':True,'reason':'certified','minJ_lower_bound':lower,'maxJ_upper_bound':upper,'observed_minJ':observed_min,'observed_maxJ':observed_max,'subcells':count,'depth':depth}
  if depth==maxdepth:break
  children=[]
  for shift in BITS:
   loc=(BITS+shift)*.5;weights=np.prod(np.where(BITS[None,:,:],loc[:,None,:],1-loc[:,None,:]),axis=2);children.append(np.einsum('ij,njk->nik',weights,pending))
  pending=np.concatenate(children)
  if len(pending)>1000000:break
 return {'passed':False,'reason':'unproved_material_volume','observed_minJ':observed_min,'observed_maxJ':observed_max,'unresolved':len(pending),'subcells':count,'depth':depth}
