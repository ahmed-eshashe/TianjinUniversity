"""Whole-cell determinant bound for the continuous quadratic block basis.
Uses Bernstein convex hulls of derivative coefficients and interval determinant.
1e-8 component allowance covers declared floating-point evaluation uncertainty;
this is an engineering bound, not a formal verified-arithmetic proof.
"""
import numpy as np
from scipy.interpolate import BSpline
from block_basis import block_basis

def multiply(a,b):
 vals=np.stack([a[0]*b[0],a[0]*b[1],a[1]*b[0],a[1]*b[1]])
 return np.nextafter(vals.min(0),-np.inf),np.nextafter(vals.max(0),np.inf)
def certificate(X,q,spacing=.0015,h=.003):
 _,_,_,_,meta=block_basis(X,spacing,h);transforms=[];nc=[]
 for knots in meta['knots']:
  breaks=np.unique(knots);m=len(breaks)-1;sample=(breaks[:-1,None]+np.array([0,.5,1])[None,:]*np.diff(breaks)[:,None]).ravel();values=BSpline(knots,np.eye(len(knots)-3),2)(sample).reshape(m,3,-1);K=np.array([[1,0,0],[-.5,2,-.5],[0,0,1.]]);T=np.einsum('ij,cjk->cik',K,values).reshape(m*3,-1);transforms.append(T);nc.append(m)
 Q=np.asarray(q).reshape(*meta['dims'],3);B=np.einsum('ai,ijkd->ajkd',transforms[0],Q);B=np.einsum('bj,ajkd->abkd',transforms[1],B);B=np.einsum('ck,abkd->abcd',transforms[2],B).reshape(nc[0],3,nc[1],3,nc[2],3,3).transpose(0,2,4,1,3,5,6)
 lo=np.empty((*nc,3,3));hi=np.empty_like(lo)
 for j in range(3):
  D=np.diff(B,axis=3+j)*2/h;lo[:,:,:,:,j]=D.min(axis=(3,4,5))-1e-8;hi[:,:,:,:,j]=D.max(axis=(3,4,5))+1e-8
 lower=np.zeros(nc);upper=np.zeros(nc)
 for perm,sign in [((0,1,2),1),((1,2,0),1),((2,0,1),1),((0,2,1),-1),((2,1,0),-1),((1,0,2),-1)]:
  v=(np.ones(nc),np.ones(nc))
  for row,col in enumerate(perm):v=multiply(v,(lo[:,:,:,row,col],hi[:,:,:,row,col]))
  if sign>0:lower+=v[0];upper+=v[1]
  else:lower-=v[1];upper-=v[0]
 lower=np.nextafter(lower,-np.inf);upper=np.nextafter(upper,np.inf)
 return {'passed':bool(lower.min()>.1 and upper.max()<10 and np.isfinite(lower).all() and np.isfinite(upper).all()),'minJ_lower_bound':float(lower.min()),'maxJ_upper_bound':float(upper.max()),'cells':int(np.prod(nc)),'gradient_roundoff_allowance':1e-8,'method':'Continuous quadratic basis / Bernstein derivative hull / interval determinant'}
