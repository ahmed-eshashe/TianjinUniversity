"""Restricted one-approach band, selected from current geometry, before motion.
No prescribed future cut, no physical fracture, no changed material/inertia law.
"""
import copy
import numpy as np
from multicut import MultiCut,CutPiece,kron3,maximum,RejectedEvent
from front_system import inserted,prolongation
from face_chart import FaceChart,select_plane
from rectangle_union import covered

class BandSystem(MultiCut):
    def __init__(self,*args,band=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.band=None
        if band is not None:self.initialize_band(band)

    def current_band(self,blade,tool,cell=5e-5,depth=3e-4):
        p=self.pieces['root'];selected=select_plane(p,tool)
        if selected is None:raise RejectedEvent('current pose has no material normal')
        axis,plane=selected;c=FaceChart(p,blade,tool,axis,plane)
        if c.sign!=1:raise RejectedEvent('this bounded band supports the positive-entry approach only')
        entry=float(p.knots[c.move][-1]);low=entry-depth
        if low<=p.knots[c.move][0]:raise RejectedEvent('interaction band exceeds body')
        # Current pose must be at/above the material entry face. No trajectory read.
        if c.advance_world<max(m.range[1] for m in c.maps)-1e-12:raise RejectedEvent('initialize band before entry')
        return {'axis':int(axis),'plane':float(plane),'move':int(c.move),'sign':int(c.sign),'cell':cell,'depth':depth,'low':low,'entry':entry,'planes':[entry-i*cell for i in range(1,round(depth/cell)+1)],'initial_pose':tool.tolist()}

    def initialize_band(self,band):
        if self.events or self.time or self.band is not None:raise RejectedEvent('initialize band only in fresh state')
        old=self.pieces['root'];base=[t.copy() for t in old.knots];base[band['move']]=inserted(base[band['move']],band['planes'])
        if np.prod([len(t)-3 for t in base])>1000:raise RejectedEvent('band capacity exceeded')
        p=CutPiece(base,old.X,old.indices,old.order,old.E,old.nu,old.rho,old.fixed)
        A=kron3([prolongation(a,b) for a,b in zip(old.knots,base)])
        p.q=A@old.q;p.vg=A@old.vg;p.update_state()
        before,after=old.metrics(),p.metrics()
        err={k:maximum(getattr(p,k)-getattr(old,k)) for k in ['x','v','F']}
        err.update(mass=after['mass']-before['mass'],energy=after['energy']-before['energy'],energy_before=before['energy'],inertia_pullback=float(np.linalg.norm((A.T@p.M@A-old.M).toarray())/np.linalg.norm(old.M.toarray())))
        if err['x']>1e-11 or err['v']>1e-10 or err['F']>1e-10 or abs(err['energy'])>max(1e-12,before['energy']*1e-8) or abs(err['mass'])>before['mass']*1e-6 or err['inertia_pullback']>1e-10:raise RejectedEvent('band transfer failed',err)
        self.pieces={'root':p};self.band=copy.deepcopy(band);self.config['band']=copy.deepcopy(band);self.initial_transfer=err
        return err

    def preview(self,piece_id,axis,plane,rectangles):
        b=self.band
        if b is None or piece_id!='root' or axis!=b['axis'] or abs(plane-b['plane'])>1e-10:raise RejectedEvent('outside initialized single-plane band')
        p=self.pieces[piece_id];others=[i for i in range(3) if i!=axis];j=others.index(b['move'])
        if min(r[2*j] for r in rectangles)<b['low']-1e-12:raise RejectedEvent('front left the refined band; extension is not qualified')
        data=p.plane_data if p.plane_data is not None else p.plane_basis_axis(axis,plane)
        ty,tz=[data['knots'][a] for a in others]
        add=[(j,k,e) for j in range(len(ty)-3) for k in range(len(tz)-3) for e in range(data['E'].shape[1]) if covered([ty[j],ty[j+3],tz[k],tz[k+3]],rectangles)]
        return {'noop':set(add).issubset(set(p.keys))}

    def propose(self,piece_id,axis,plane,rectangle):
        self.preview(piece_id,axis,plane,rectangle)
        return super().propose(piece_id,axis,plane,rectangle)
