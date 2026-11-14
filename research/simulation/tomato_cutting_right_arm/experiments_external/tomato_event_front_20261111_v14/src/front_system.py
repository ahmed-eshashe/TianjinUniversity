"""Front-aligned tensor knot refinement, exact carried-field transfer.

Geometry fixture only: no knife contact or fracture work. New approximation
modes are deliberate; preserved mass/energy at transfer is not identical dynamics.
"""
import copy
import numpy as np
from scipy.interpolate import BSpline
from scipy.sparse import csr_matrix,eye
from multicut import MultiCut,CutPiece,kron3,volume_certificates,RejectedEvent,maximum

def inserted(knots,values):
    t=np.array(knots);bs=BSpline(t,np.eye(len(t)-3),2)
    for v in sorted(values):
        if v<=t[0]+1e-12 or v>=t[-1]-1e-12:continue
        # Match existing values rather than creating machine-width knot spans.
        close=bs.t[abs(bs.t-v)<1e-12]
        if len(close):v=float(close[0])
        m=np.count_nonzero(abs(bs.t-v)<1e-12)
        if m<2:bs=bs.insert_knot(v,2-m)
    if len(np.unique(bs.t))-2>11:raise RejectedEvent('front refinement capacity exceeded')
    return bs.t.copy()

def prolongation(old,new):
    bs=BSpline(old,np.eye(len(old)-3),2)
    for v in np.unique(new):
        oldn=np.count_nonzero(abs(bs.t-v)<1e-12);newn=np.count_nonzero(abs(new-v)<1e-12)
        if oldn>newn:raise RejectedEvent('refinement attempted to remove history knots')
        if newn>oldn:bs=bs.insert_knot(float(v),int(newn-oldn))
    if len(bs.t)!=len(new) or maximum(bs.t-new)>1e-11:raise RejectedEvent('incompatible refinement knot vectors')
    return csr_matrix(bs.c[:len(bs.t)-3])

def refined_piece(old,axis,plane,rectangles):
    if old.plane is not None and (axis!=old.axis or abs(plane-old.plane)>1e-10):
        raise RejectedEvent('only one active partial plane per connected fragment')
    if old.plane is not None:plane=old.plane
    rectangles=np.asarray(rectangles,float).reshape(-1,4)
    base=[t.copy() for t in old.meta['knots']];others=[i for i in range(3) if i!=axis]
    for j,a in enumerate(others):base[a]=inserted(base[a],rectangles[:,2*j:2*j+2].ravel())
    # Keep this experiment bounded; no hidden global refinement campaign.
    if np.prod([len(t)-3 for t in base])>1000:raise RejectedEvent('front basis capacity exceeded')
    trial=CutPiece(base,old.X,old.indices,old.order,old.E,old.nu,old.rho,old.fixed)
    proposal=trial.propose(rectangles.tolist(),plane,axis);trial.commit(proposal)
    A=kron3([prolongation(a,b) for a,b in zip(old.knots,trial.knots)])
    fullQ=A@(old.T@old.q);fullV=A@(old.T@old.vg)
    T=trial.T.toarray();coeff=np.linalg.lstsq(T,np.c_[fullQ,fullV],rcond=None)[0]
    residual=maximum(T@coeff-np.c_[fullQ,fullV])
    if residual>1e-11:raise RejectedEvent('new basis cannot carry old displacement/velocity',{'residual':residual})
    trial.q=coeff[:,:3];trial.vg=coeff[:,3:];trial.time=old.time;trial.steps=old.steps
    trial.support_impulse=old.support_impulse.copy();trial.support_moment=old.support_moment.copy();trial.update_state()
    before=old.metrics();after=trial.metrics()
    err={k:maximum(getattr(trial,k)-getattr(old,k)) for k in ['x','v','F']}
    err.update(energy=after['energy']-before['energy'],energy_before=before['energy'],mass=after['mass']-before['mass'],momentum=float(np.linalg.norm(after['momentum']-before['momentum'])),angular=float(np.linalg.norm(after['angular']-before['angular'])),coefficient_recovery=residual)
    if err['x']>1e-11 or err['v']>1e-10 or err['F']>1e-10 or abs(err['energy'])>max(1e-12,abs(before['energy'])*1e-8) or abs(err['mass'])>before['mass']*1e-6 or err['momentum']>1e-9 or err['angular']>1e-10:
        raise RejectedEvent('front insertion failed carried-state invariants',err)
    trial.history=copy.deepcopy(old.history)+trial.history;trial.epoch=old.epoch+1
    return trial,err

class FrontSystem(MultiCut):
    def propose(self,piece_id,axis,plane,rectangle):
        if piece_id not in self.pieces:raise RejectedEvent('unknown fragment')
        old=self.pieces[piece_id]
        if old.plane is None and self.cut_count>=self.config['max_cuts']:raise RejectedEvent('four-cut capacity exhausted')
        trial,err=refined_piece(old,axis,plane,rectangle)
        certs=volume_certificates(trial)
        if not all(c['passed'] for c in certs):raise RejectedEvent('refined continuous volume bound failed',{'certificates':certs})
        children,part=trial.partitions() if trial.completed() else (None,None)
        return {'noop':False,'fingerprint':self.fingerprint(),'piece_id':piece_id,'trial':trial,'children':children,'new_cut':old.plane is None and trial.plane is not None,'insertion':err,'partition':part,
                'event':{'piece_id':piece_id,'axis':axis,'plane':float(trial.plane if trial.plane is not None else plane),'rectangle':np.asarray(rectangle).tolist(),'complete':children is not None,'fixture_only':True,'paid_fracture_area':0.,'front_refined':True}}
