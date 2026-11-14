"""Continuous determinant bound with the inherited engineering rounding allowance."""
import numpy as np
from scipy.interpolate import BSpline
from basis_volume_guard import multiply

def box_certificate(knots,q):
    transforms,widths,nc=[],[],[]
    for t in knots:
        breaks=np.unique(t);d=np.diff(breaks);m=len(d)
        sample=(breaks[:-1,None]+np.array([0,.5,1])*d[:,None]).ravel()
        values=BSpline(t,np.eye(len(t)-3),2)(sample).reshape(m,3,-1)
        K=np.array([[1,0,0],[-.5,2,-.5],[0,0,1.]])
        transforms.append(np.einsum('ij,cjk->cik',K,values).reshape(m*3,-1));widths.append(d);nc.append(m)
    Q=q.reshape(*[len(t)-3 for t in knots],3)
    B=np.einsum('ai,ijkd->ajkd',transforms[0],Q)
    B=np.einsum('bj,ajkd->abkd',transforms[1],B)
    B=np.einsum('ck,abkd->abcd',transforms[2],B).reshape(nc[0],3,nc[1],3,nc[2],3,3).transpose(0,2,4,1,3,5,6)
    lo,hi=np.empty((*nc,3,3)),np.empty((*nc,3,3))
    for j in range(3):
        shape=[1]*7;shape[j]=nc[j]
        D=np.diff(B,axis=3+j)*2/widths[j].reshape(shape)
        lo[:,:,:,:,j]=D.min(axis=(3,4,5))-1e-8;hi[:,:,:,:,j]=D.max(axis=(3,4,5))+1e-8
    lower,upper=np.zeros(nc),np.zeros(nc)
    for perm,sign in [((0,1,2),1),((1,2,0),1),((2,0,1),1),((0,2,1),-1),((2,1,0),-1),((1,0,2),-1)]:
        v=(np.ones(nc),np.ones(nc))
        for row,col in enumerate(perm):v=multiply(v,(lo[:,:,:,row,col],hi[:,:,:,row,col]))
        if sign>0:lower+=v[0];upper+=v[1]
        else:lower-=v[1];upper-=v[0]
    return {'passed':bool(np.isfinite(lower).all() and np.isfinite(upper).all() and lower.min()>.1 and upper.max()<10),'minJ_lower_bound':float(lower.min()),'maxJ_upper_bound':float(upper.max()),'cells':int(np.prod(nc)),'gradient_roundoff_allowance':1e-8}

def certificate(body):
    if getattr(body,'plane',None) is None:return [box_certificate(body.knots,body.q)]
    left,right=body.split_knots();q=body.T@body.q;n=np.prod([len(t)-3 for t in left])
    return [box_certificate(left,q[:n]),box_certificate(right,q[n:])]
