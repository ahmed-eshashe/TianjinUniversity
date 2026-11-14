"""Stable, mathematically equivalent convex-potential remainders.

The Newton objective increment is g.d + d.A.d/2 + h*Bregman(Psi).
This avoids subtracting O(1) potentials to resolve O(1e-23) increments.
No force, Hessian, material coefficient or convergence limit is changed.
"""
import torch

def unilateral_remainder(g,delta):
    """Bregman remainder of .5*min(g,0)^2, with exact path increment."""
    end=g+delta
    both=(g<=0)&(end<=0)
    enter=(g>0)&(end<0)
    leave=(g<0)&(end>0)
    return torch.where(both,.5*delta.square(),torch.where(enter,.5*end.square(),
                       torch.where(leave,.5*g.square()-g*end,torch.zeros_like(g))))

def contact_remainder(operator,v,delta):
    if operator is None:return v.new_tensor(0.)
    if hasattr(operator,'operators'):
        return sum((contact_remainder(o,v,delta) for o in operator.operators),v.new_tensor(0.))
    dv=(1-operator.u)*delta[operator.ids[:,0]]+operator.u*delta[operator.ids[:,1]]
    normal_increment=(dv*operator.n).sum(1)
    if hasattr(operator,'phi'):
        g=operator.gap(v);dg=operator.h*normal_increment
        coefficient=operator.ke/operator.h*operator.weights
    else:
        g=operator.project(v);dg=normal_increment;coefficient=operator.k
    return (coefficient*unilateral_remainder(g,dg)).sum()

def ground_remainder(v,delta,k,limit):
    """Exact integral of Huber curvature along a velocity segment.

f''(v)=k inside [-limit/k,limit/k] and zero outside. The remainder is
k*delta^2*integral(1-t) dt over the portion of t in [0,1] inside it.
Ground k is either zero or the unchanged 1000 N.s/m in this operator.
"""
    cap=limit/k.clamp_min(1.)
    safe=torch.where(delta!=0,delta,torch.ones_like(delta))
    a=(-cap-v)/safe;b=(cap-v)/safe
    lo=torch.minimum(a,b).clamp(0,1);hi=torch.maximum(a,b).clamp(0,1)
    width=(hi-lo).clamp_min(0)
    return (k*delta.square()*width*(1-.5*(hi+lo))).sum()
