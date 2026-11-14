"""Finite-length spring energy, gradient and tangent for offline static tests."""
import numpy as np
from scipy.sparse import coo_matrix


def spring_state(positions,pairs,rest_lengths,stiffness,*,tangent=False):
    """Exact elastic derivatives; no volume barrier, contact or artificial stabilization."""
    x=np.asarray(positions);pairs=np.asarray(pairs);rest=np.asarray(rest_lengths);k=np.asarray(stiffness)
    if not np.isfinite(x).all() or np.any(k<=0) or np.any(rest<=0):raise ValueError('Invalid geometry/material')
    delta=x[pairs[:,1]]-x[pairs[:,0]];length=np.linalg.norm(delta,axis=1)
    if np.any(length<1e-9):raise ValueError('Spring approached zero-length singularity')
    n=delta/length[:,None];extension=length-rest
    force=(k*extension)[:,None]*n
    gradient=np.zeros_like(x);np.add.at(gradient,pairs[:,0],-force);np.add.at(gradient,pairs[:,1],force)
    result={'energy_j':float(.5*np.dot(k,extension**2)),'gradient_n':gradient,'min_length_ratio':float(np.min(length/rest))}
    if tangent:
        eye=np.eye(3)
        block=k[:,None,None]*((1-rest/length)[:,None,None]*eye+(rest/length)[:,None,None]*n[:,:,None]*n[:,None,:])
        ii,jj=np.meshgrid(np.arange(3),np.arange(3),indexing='ij')
        a=3*pairs[:,0,None]+ii.reshape(1,9);b=3*pairs[:,1,None]+ii.reshape(1,9)
        c=3*pairs[:,0,None]+jj.reshape(1,9);d=3*pairs[:,1,None]+jj.reshape(1,9)
        block=block.reshape(-1,9)
        matrix=coo_matrix((np.concatenate([block,-block,-block,block]).reshape(-1),
                          (np.concatenate([a,a,b,b]).reshape(-1),np.concatenate([c,d,c,d]).reshape(-1))),
                         shape=(3*len(x),3*len(x))).tocsr()
        matrix.eliminate_zeros();result['tangent_n_m']=matrix
    return result


def cell_ratios(positions,cells,reference_volumes):
    p=np.asarray(positions)[cells]
    signed=np.linalg.det(p[:,1:]-p[:,:1])/6
    return signed/np.asarray(reference_volumes)


def polish_equilibrium(points,displacement,pairs,rest_lengths,stiffness,free,fixed):
    """Newton polish with energy-descent backtracking, no material regularization."""
    from scipy.sparse.linalg import spsolve
    vector=np.asarray(displacement).reshape(-1).copy();steps=0
    for _ in range(12):
        state=spring_state(points+vector.reshape(-1,3),pairs,rest_lengths,stiffness,tangent=True)
        g=state['gradient_n'].reshape(-1)
        if np.linalg.norm(g[free])/max(np.linalg.norm(g[fixed]),1e-15)<1e-8:break
        h=state['tangent_n_m'][free][:,free]
        step=spsolve(h,-g[free]);slope=g[free]@step
        if not np.isfinite(step).all() or slope>=0:break
        alpha=1.
        while alpha>1e-8:
            candidate=vector.copy();candidate[free]+=alpha*step
            trial=spring_state(points+candidate.reshape(-1,3),pairs,rest_lengths,stiffness)
            if trial['energy_j']<=state['energy_j']+1e-4*alpha*slope:break
            alpha*=.5
        if alpha<=1e-8:break
        vector=candidate;steps+=1
    return vector,steps
