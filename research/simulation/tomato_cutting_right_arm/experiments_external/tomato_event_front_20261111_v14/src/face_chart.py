"""Conservative patches inside an actual finite-width CAD edge-face sweep.

Tensor coefficient hulls certify spatial coverage. Endpoint fields interpolate
linearly for this geometry update; coupling refinement must be checked separately.
The selected reference patch is planar, not the exact centreline preimage.
"""
import numpy as np
from scipy.interpolate import BSpline
from planar_chart import Monotone,axis_coefficients,TOL
from integrated_cut import RejectedEvent

NORMAL_BOUND=1e-5
FRONT_BOUND=1e-5

def edge_rectangle(blade):
    # This rectangle is INSIDE the two original CAD edge-face triangles, not a
    # widened marker. Both endpoints carry their original unequal thickness.
    V=blade.local_vertices[[14,15,16,17]]
    if np.max(abs(V[:,1]))>TOL:raise RejectedEvent('CAD edge face is not planar in the declared frame')
    if not all(any(set(f)==s for f in map(tuple,blade.faces.tolist())) for s in [{14,15,16},{15,16,17}]):raise RejectedEvent('CAD edge face triangles changed')
    lo=float(max(V[[0,1],0]));hi=float(min(V[[2,3],0]));half=float(min(abs(V[:,2])))
    return lo,hi,half

def full_coeff(p):return (p.T@p.q).reshape(*[len(t)-3 for t in p.knots],3)

def select_plane(p,pose):
    C=full_coeff(p)@pose[:3,2];target=float(pose[:3,3]@pose[:3,2]);choices=[]
    for axis in range(3):
        c,res=axis_coefficients(C,axis)
        if np.ptp(c)<.001:continue
        try:m=Monotone(p.knots[axis],c)
        except RejectedEvent:continue
        if m.range[0]+TOL<target<m.range[1]-TOL:choices.append((axis,m.inverse(target)))
    if not choices:return None
    if len(choices)!=1:raise RejectedEvent('ambiguous material normal for edge-face patch')
    return choices[0]

def traces(p,axis,plane):
    Q=full_coeff(p);t=p.knots[axis];values=[]
    for x in [np.nextafter(plane,-np.inf),plane]:
        N=BSpline(t,np.eye(len(t)-3),2)(x);values.append(np.tensordot(N,np.moveaxis(Q,axis,0),axes=(0,0)))
    return values

class FaceChart:
    def __init__(self,p,blade,pose,axis,plane):
        self.axis,self.plane=axis,plane;self.pose=pose;self.others=[i for i in range(3) if i!=axis]
        lo,hi,half=edge_rectangle(blade);self.halfwidth=half;self.edge_world=[lo+pose[:3,3]@pose[:3,0],hi+pose[:3,3]@pose[:3,0]];self.advance_world=float(pose[:3,3]@pose[:3,1])
        S=traces(p,axis,plane);normal=np.stack([s@pose[:3,2]-pose[:3,3]@pose[:3,2] for s in S]);self.normal_bound=float(abs(normal).max())
        if self.normal_bound>min(half,NORMAL_BOUND):raise RejectedEvent('material cut patch is outside the finite edge-face accuracy envelope',{'offset_m':self.normal_bound,'CAD_halfwidth_m':half,'numerical_bound_m':NORMAL_BOUND})
        advance=[s@pose[:3,1] for s in S];edge=[s@pose[:3,0] for s in S]
        # Identify which material tangent varies along the inward direction.
        variations=[np.ptp(axis_coefficients(advance[0],i)[0]) for i in range(2)]
        self.localmove=int(np.argmax(variations));self.localedge=1-self.localmove
        self.move=self.others[self.localmove];self.edge_axis=self.others[self.localedge]
        self.adv_coeff=np.stack([np.moveaxis(c,self.localmove,0) for c in advance])
        self.edge_coeff=np.stack([np.moveaxis(c,self.localedge,0) for c in edge])
        self.maps=[Monotone(p.knots[self.move],c[:,j]) for c in self.adv_coeff for j in range(c.shape[1])]
        if len(set(m.sign for m in self.maps))!=1:raise RejectedEvent('nonmonotone face-sweep advance')
        self.sign=self.maps[0].sign
        self.roots=[m.inverse(self.advance_world,clip=True) for m in self.maps]
        self.front_spread=float(max(self.roots)-min(self.roots))
        if self.front_spread>FRONT_BOUND:raise RejectedEvent('curved front exceeds the conservative rectangle accuracy envelope',{'reference_spread_m':self.front_spread})
        emaps=[Monotone(p.knots[self.edge_axis],c[:,j]) for c in self.edge_coeff for j in range(c.shape[1])]
        if len(set(m.sign for m in emaps))!=1:raise RejectedEvent('folded finite edge footprint')
        intervals=[sorted([m.inverse(v,clip=True) for v in self.edge_world]) for m in emaps]
        self.edge_interval=[max(a[0] for a in intervals),min(a[1] for a in intervals)]
        self.edge_overlap=all(self.edge_world[1]>m.range[0]+TOL and self.edge_world[0]<m.range[1]-TOL for m in emaps)

def certified_face_rectangle(old_piece,new_piece,blade,old_pose,new_pose,history=None):
    if np.max(abs(old_pose[:3,:3]-new_pose[:3,:3]))>1e-10:raise RejectedEvent('rotating blade within an action unsupported')
    selected=(history['axis'],history['plane']) if history is not None else select_plane(new_piece,new_pose)
    if selected is None:return None
    axis,plane=selected;a=FaceChart(old_piece,blade,old_pose,axis,plane);b=FaceChart(new_piece,blade,new_pose,axis,plane)
    if a.move!=b.move or a.edge_axis!=b.edge_axis or a.sign!=b.sign:raise RejectedEvent('material chart axes changed')
    if not a.edge_overlap or not b.edge_overlap:return {'area_none':True,'stroke_reset':True}
    relative=(b.advance_world-a.advance_world)-(b.adv_coeff-a.adv_coeff)
    if relative.min()>=-TOL:
        return {'area_none':True,'stroke_reset':bool(np.max(abs(relative))>TOL or np.max(abs(new_pose-old_pose))>TOL)}
    if relative.max()>TOL:raise RejectedEvent('nonmonotone relative traversal under endpoint interpolation')
    low,high=(max(b.roots),min(a.roots)) if b.sign>0 else (max(a.roots),min(b.roots))
    elo,ehi=max(a.edge_interval[0],b.edge_interval[0]),min(a.edge_interval[1],b.edge_interval[1])
    if high-low>.0011+TOL:raise RejectedEvent('front advance exceeds action envelope')
    # A monotone proof chain may safely join earlier uncertain curved-front
    # strips. This is not a bounding-box union: every segment must certify the
    # same plane, forward traversal, and common finite edge coverage. Withdrawal
    # or lateral repositioning resets the chain and cannot bridge a skipped band.
    stroke=history.get('stroke') if history is not None else None
    if stroke:
        if stroke['move']!=b.move or stroke['sign']!=b.sign:raise RejectedEvent('stroke chart changed')
        if b.sign>0:high=stroke['start_bound']
        else:low=stroke['start_bound']
        elo=max(elo,stroke['edge_interval'][0]);ehi=min(ehi,stroke['edge_interval'][1])
    if high-low<=TOL or ehi-elo<=TOL:return None
    next_stroke={'move':b.move,'sign':b.sign,'start_bound':high if b.sign>0 else low,'edge_interval':[elo,ehi],'segments':1+(stroke['segments'] if stroke else 0)}
    vals={b.move:[low,high],b.edge_axis:[elo,ehi]};rectangle=[v for ax in range(3) if ax!=axis for v in vals[ax]]
    return {'axis':axis,'plane':plane,'rectangle':rectangle,'front':low if b.sign>0 else high,'stroke':next_stroke,'normal_offset_bound_m':max(a.normal_bound,b.normal_bound),'front_spread_bound_m':max(a.front_spread,b.front_spread),'CAD_minimum_edge_halfwidth_m':b.halfwidth,'inside_actual_edge_face':True,'temporal_scope':'monotone linear interpolation of endpoint coefficient fields; action subdivision required, not continuous contact proof'}
