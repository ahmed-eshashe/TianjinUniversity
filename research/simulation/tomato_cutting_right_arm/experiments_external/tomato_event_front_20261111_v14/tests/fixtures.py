import numpy as np
from scipy.interpolate import BSpline
from front_system import FrontSystem
from integrated_cut import greville
from reference import block
from blade_sweep import pose
from deformed_sweep import DeformedSweep

def analytic(X,compression=.99,bend=1.5):
    x=np.asarray(X).copy();x[:,1]=compression*X[:,1]+2*X[:,1]**2+bend*X[:,0]**2;return x
def assign(p,fn=analytic):
    X=greville(p.meta['knots']);vals=[BSpline(t,np.eye(len(t)-3),2)(X[:,i]) for i,t in enumerate(p.meta['knots'])]
    N=np.einsum('pi,pj,pk->pijk',*vals).reshape(len(X),-1);q=np.linalg.solve(N,fn(X))
    p.q=np.zeros_like(p.q);p.q[:p.base_ng]=q;p.vg[:]=0;p.update_state()
def make():
    s=FrontSystem(block(8,.0015));assign(s.pieces['root']);return DeformedSweep(s,pose([.0003,world_y(.0061),0]))
def world_y(y):return .99*y+2*y*y+1.5*.0003**2
def action(d,y):
    p=d.propose(pose([.0003,world_y(y),0]));d.commit(p);return p
