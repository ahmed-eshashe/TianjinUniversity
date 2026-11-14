"""Certified restricted planar slice of a non-affine tensor spline body.

Convex-hull coefficient tests establish a unique monotone reference normal and
separable monotone tangents. General curved preimages are explicitly unsupported.
No corner-only or point-cloud certificate is used to infer the whole patch.
"""
import numpy as np
from scipy.interpolate import BSpline
from scipy.optimize import brentq
from integrated_cut import RejectedEvent

TOL=1e-11
def axis_coefficients(C,axis):
    other=tuple(i for i in range(C.ndim) if i!=axis)
    v=C.mean(axis=other);shape=[1]*C.ndim;shape[axis]=len(v)
    return v,float(np.max(abs(C-v.reshape(shape))))

class Monotone:
    def __init__(self,knots,c):
        self.knots=np.array(knots);self.c=np.array(c);self.bs=BSpline(knots,c,2)
        d=[]
        for i in range(len(c)-1):
            den=knots[i+3]-knots[i+1];jump=c[i+1]-c[i]
            if den<1e-14:
                if abs(jump)>TOL:raise RejectedEvent('discontinuous chart cannot supply unique inversion')
            else:d.append(2*jump/den)
        d=np.asarray(d)
        if d.min()>1e-5:self.sign=1
        elif d.max()<-1e-5:self.sign=-1
        else:raise RejectedEvent('chart derivative lacks a monotonicity certificate')
        self.lo,self.hi=float(knots[0]),float(knots[-1]);self.range=sorted([float(self.bs(self.lo)),float(self.bs(self.hi))])
    def inverse(self,value,clip=False):
        if value<self.range[0]-TOL or value>self.range[1]+TOL:
            if not clip:raise RejectedEvent('point outside certified chart')
        value=float(np.clip(value,*self.range))
        out=brentq(lambda x:float(self.bs(x))-value,self.lo,self.hi,xtol=1e-15)
        if abs(float(self.bs(out))-value)>TOL:raise RejectedEvent('inverse residual')
        return float(out)

class PlanarChart:
    def __init__(self,piece,blade,pose):
        self.pose=pose.copy();self.normal=pose[:3,2];self.along=pose[:3,0];self.inward=pose[:3,1]
        Q=(piece.T@piece.q).reshape(*[len(t)-3 for t in piece.knots],3)
        C=Q@self.normal;choices=[]
        for a in range(3):
            c,res=axis_coefficients(C,a)
            if res<=TOL and np.ptp(c)>1e-8:choices.append((a,c,res))
        if len(choices)!=1:raise RejectedEvent('blade plane has a curved or ambiguous material preimage')
        self.axis,c,self.normal_residual=choices[0];self.normal_map=Monotone(piece.knots[self.axis],c)
        target=float(np.dot(pose[:3,3],self.normal))
        self.intersects=self.normal_map.range[0]+TOL<target<self.normal_map.range[1]-TOL
        if not self.intersects:return
        self.plane=self.normal_map.inverse(target)
        N=BSpline(piece.knots[self.axis],np.eye(len(c)),2)(self.plane)
        surface=np.tensordot(N,np.moveaxis(Q,self.axis,0),axes=(0,0));others=[i for i in range(3) if i!=self.axis]
        self.tangents={};self.tangent_residuals={}
        for name,direction in [('edge',self.along),('advance',self.inward)]:
            projected=surface@direction;choices=[]
            for local in range(2):
                c,res=axis_coefficients(projected,local)
                if res<=TOL and np.ptp(c)>1e-8:choices.append((others[local],c,res))
            if len(choices)!=1:raise RejectedEvent('curved/nonseparable in-plane edge footprint unsupported')
            a,c,res=choices[0];self.tangents[name]=(a,Monotone(piece.knots[a],c));self.tangent_residuals[name]=res
        if self.tangents['edge'][0]==self.tangents['advance'][0]:raise RejectedEvent('singular planar chart')
        self.move=self.tangents['advance'][0];self.edge_axis=self.tangents['edge'][0]
        endpoints=blade.points(pose);vals=endpoints@self.along;self.edge_world_interval=[float(vals.min()),float(vals.max())]
        self.advance_world=float(pose[:3,3]@self.inward)
        e=self.tangents['edge'][1]
        self.edge_overlap=self.edge_world_interval[1]>e.range[0]+TOL and self.edge_world_interval[0]<e.range[1]-TOL
        self.edge_interval=sorted([e.inverse(v,clip=True) for v in self.edge_world_interval])
        self.front=self.tangents['advance'][1].inverse(self.advance_world,clip=True)

def certified_rectangle(old_piece,new_piece,blade,old_pose,new_pose):
    if np.max(abs(old_pose[:3,:3]-new_pose[:3,:3]))>1e-10:raise RejectedEvent('blade rotation inside an action unsupported')
    old=PlanarChart(old_piece,blade,old_pose);new=PlanarChart(new_piece,blade,new_pose)
    if not old.intersects and not new.intersects:return None
    if not old.intersects or not new.intersects or old.axis!=new.axis or abs(old.plane-new.plane)>1e-10:raise RejectedEvent('changing material cut surface during action')
    if not old.edge_overlap and not new.edge_overlap:return None
    if old.move!=new.move or old.edge_axis!=new.edge_axis:raise RejectedEvent('chart axis changed')
    # All control values of relative advance must have the same sign. This
    # certifies a monotone front under linear endpoint-field interpolation.
    a=old.tangents['advance'][1];b=new.tangents['advance'][1]
    if len(a.knots)!=len(b.knots) or np.max(abs(a.knots-b.knots))>TOL:raise RejectedEvent('topology changed within geometry interval')
    relative=(new.advance_world-old.advance_world)-(b.c-a.c)
    if relative.min()>=-TOL:return None
    if relative.max()>TOL:raise RejectedEvent('nonmonotone relative edge advance during action')
    if abs(new.front-old.front)>.0011+1e-12:raise RejectedEvent('reference advance exceeds action envelope')
    e0=old.tangents['edge'][1];e1=new.tangents['edge'][1]
    # Conservative common edge coverage: no filling a lateral unvisited gap.
    lo=max(old.edge_interval[0],new.edge_interval[0]);hi=min(old.edge_interval[1],new.edge_interval[1])
    if hi-lo<=TOL or abs(new.front-old.front)<=TOL:return None
    vals={new.move:sorted([old.front,new.front]),new.edge_axis:[lo,hi]}
    rectangle=[v for ax in range(3) if ax!=new.axis for v in vals[ax]]
    return {'axis':new.axis,'plane':new.plane,'rectangle':rectangle,'normal_residual':max(old.normal_residual,new.normal_residual),'tangent_residual':max(*old.tangent_residuals.values(),*new.tangent_residuals.values()),'front':new.front,'temporal_scope':'monotone linear interpolation of endpoint coefficient fields; not continuous dynamics/contact certification'}
