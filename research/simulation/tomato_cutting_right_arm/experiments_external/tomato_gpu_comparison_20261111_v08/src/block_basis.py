"""Quadratic open-knot tensor basis on an intact block's physical reference box.
Clamped knots describe the basis; they do NOT impose fixed mechanical boundaries.
Non-block or trimmed sampling is explicitly unsupported by this probe.
"""
import numpy as np
from scipy.interpolate import BSpline
from itertools import product

def block_basis(X,spacing,h):
 axes=[np.unique(X[:,j]) for j in range(3)];shape=tuple(map(len,axes));expected=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1).reshape(-1,3)
 if not np.allclose(expected,X,rtol=0,atol=1e-14):raise ValueError('Only full ordered tensor blocks supported; no silent tomato/cut remeshing')
 dims=[];ids1=[];w1=[];g1=[];greville=[];mass1=[];knots=[]
 for x in axes:
  if not np.allclose(np.diff(x),spacing,rtol=0,atol=1e-14):raise ValueError('particle spacing mismatch')
  a=x[0]-spacing/2;b=x[-1]+spacing/2;nc=round((b-a)/h)
  if abs(nc*h-(b-a))>1e-12:raise ValueError('box must contain integer grid cells')
  t=np.r_[np.repeat(a,3),np.linspace(a,b,nc+1)[1:-1],np.repeat(b,3)];nb=len(t)-3;B=BSpline(t,np.eye(nb),2);A=B(x);G=B.derivative()(x);ids=np.argsort(-A,axis=1)[:,:3];ids.sort(axis=1);rows=np.arange(len(x))[:,None];dims.append(nb);ids1.append(ids);w1.append(A[rows,ids]);g1.append(G[rows,ids]);greville.append(np.array([np.mean(t[i+1:i+3]) for i in range(nb)]));mass1.append(A.T@A);knots.append(t)
 pi=np.stack(np.meshgrid(*[np.arange(n) for n in shape],indexing='ij'),axis=-1).reshape(-1,3);ids=[];weights=[];grads=[]
 for a,b,c in product(range(3),repeat=3):
  ix,iy,iz=[ids1[k][pi[:,k],j] for k,j in enumerate([a,b,c])];wx,wy,wz=[w1[k][pi[:,k],j] for k,j in enumerate([a,b,c])];gx,gy,gz=[g1[k][pi[:,k],j] for k,j in enumerate([a,b,c])];ids.append((ix*dims[1]+iy)*dims[2]+iz);weights.append(wx*wy*wz);grads.append(np.stack([gx*wy*wz,wx*gy*wz,wx*wy*gz],axis=1))
 grid=np.stack(np.meshgrid(*greville,indexing='ij'),axis=-1).reshape(-1,3)
 return np.stack(ids,axis=1),np.stack(weights,axis=1),np.stack(grads,axis=1),grid,{'dims':dims,'mass1':mass1,'knots':knots,'particle_axes':axes,'greville':greville}
