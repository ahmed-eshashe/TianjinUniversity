"""Compiled construction of the same reduced gradients; no reduced model change."""
import numpy as np
from numba import njit
from scipy.linalg import cho_solve

@njit(cache=True)
def gradients(ids,G,eptr,eidx,edata):
 maxwidth=0
 for p in range(len(ids)):
  width=0
  for k in range(4):width+=eptr[ids[p,k]+1]-eptr[ids[p,k]]
  maxwidth=max(maxwidth,width)
 allidx=np.empty((len(ids),maxwidth),np.int32);allg=np.zeros((len(ids),maxwidth,3));length=np.zeros(len(ids),np.int32)
 for p in range(len(ids)):
  count=0
  for k in range(4):
   old=ids[p,k]
   for e in range(eptr[old],eptr[old+1]):
    j=eidx[e];found=-1
    for t in range(count):
     if allidx[p,t]==j:found=t;break
    if found<0:found=count;allidx[p,count]=j;count+=1
    for axis in range(3):allg[p,found,axis]+=edata[e]*G[p,k,axis]
  # Stable explicit ordering, dropping exactly zero gradients as v20 does.
  n=0
  for t in range(count):
   if np.any(allg[p,t]!=0):
    allidx[p,n]=allidx[p,t];allg[p,n]=allg[p,t];n+=1
  order=np.argsort(allidx[p,:n]);ii=allidx[p,:n].copy();gg=allg[p,:n].copy()
  for t in range(n):allidx[p,t]=ii[order[t]];allg[p,t]=gg[order[t]]
  for axis in range(3):
   total=0.
   for t in range(1,n):total+=allg[p,t,axis]
   allg[p,0,axis]=-total
  length[p]=n
 ptr=np.zeros(len(ids)+1,np.int32)
 for p in range(len(ids)):ptr[p+1]=ptr[p]+length[p]
 idx=np.empty(ptr[-1],np.int32);grad=np.empty((ptr[-1],3))
 for p in range(len(ids)):
  for t in range(length[p]):idx[ptr[p]+t]=allidx[p,t];grad[ptr[p]+t]=allg[p,t]
 return ptr,idx,grad

def reduced_data(a):
 b=a.body;E=a.E;ptr,idx,grad=gradients(b.ids,b.G,E.indptr,E.indices,E.data)
 regions=np.repeat(np.arange(len(b.V)),np.diff(ptr));order=np.argsort(idx,kind='stable');iptr=np.r_[0,np.cumsum(np.bincount(idx,minlength=len(a.q)))].astype(np.int32)
 rows=np.arange(len(a.q));mass_i=rows[a.singletons];mass_j=mass_i.copy();factors=np.array([factor[0][0,0] for ids,factor in zip(a.blocks,a.factors) if len(ids)==1]);mass_v=(1./factors)/factors
 rr=[mass_i];cc=[mass_j];vv=[mass_v]
 for ids,factor in a.coupled:
  inv=cho_solve(factor,np.eye(len(ids)),check_finite=False);i,j=np.nonzero(inv);rr.append(ids[i]);cc.append(ids[j]);vv.append(inv[i,j])
 rr=np.concatenate(rr);cc=np.concatenate(cc);vv=np.concatenate(vv);o=np.lexsort((cc,rr));mptr=np.r_[0,np.cumsum(np.bincount(rr,minlength=len(a.q)))].astype(np.int32)
 return {'ptr':ptr,'idx':idx,'grad':grad,'iptr':iptr,'iidx':regions[order].astype(np.int32),'ig':grad[order],'mptr':mptr,'midx':cc[o].astype(np.int32),'mi':vv[o]}
