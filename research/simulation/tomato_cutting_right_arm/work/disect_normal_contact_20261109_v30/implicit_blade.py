"""Separately authorized stronger normal contact; no material-law edits.

Exact CAD/edge quadrature is refreshed at every physical step. Inside intervals
and normals are frozen only in that step's implicit normal-displacement solve.
Tangential Brown force retains the existing lagged velocity treatment and its
original kf/mu, with the newly declared normal stiffness. This is not exact
nonpenetration or fully nonlinear end-position CAD contact.
"""
from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent/'disect_adaptive_contact_20261109_v27'))
from adaptive_blade import AdaptiveBlade,s,m,closure,torch,tensor
from adaptive_contact import law
from embedded_dashpot import EmbeddedDashpot
from normal_operator import NormalContact,CombinedContact

class ImplicitBlade(AdaptiveBlade):
    def __init__(self):
        super().__init__()
        controls=json.loads((W/'controls_result.json').read_text());assert controls['passed']
        self.normal_stiffness=controls['selected_stiffness_N_per_m']
        self.contact_step=None
    def implicit(self,h,**kwargs):
        self.contact_step=h
        try:return super().implicit(h,**kwargs)
        finally:self.contact_step=None
    def contact(self,q,v,translation,velocity):
        c=self.adaptive;cad=self.cad;ke=self.normal_stiffness
        ev=c.evaluate(q,v,cad.vertices@cad.rotation.T+translation,cad.triangles,
                      velocity,translation,kd=0.,ke=ke)
        force=ev['force'].copy();energy=ev['energy_J']
        ids=ev['ids'];u=ev['u'];normal=ev['normal'];weights=ev['weights'];phi=ev['phi']
        outer=c.outer;local=(q[outer]-translation)@cad.rotation
        keep=np.all((local>=cad.minimum)&(local<=cad.maximum),axis=1);candidates=outer[keep]
        if len(candidates):
            out=cad.query(q[candidates],translation);active=out['phi']<0;oi=candidates[active]
            ph=out['phi'][active];nn=out['normal'][active]
            if len(oi):
                force[oi]+=law(ph,nn,v[oi],velocity,ke=ke,kd=0.)
                energy+=float(.5*ke*np.dot(ph,ph))
                ids=np.concatenate((ids,np.column_stack((oi,oi))))
                u=np.r_[u,np.zeros(len(oi))];normal=np.concatenate((normal,nn))
                weights=np.r_[weights,np.ones(len(oi))];phi=np.r_[phi,ph]
        if len(ids):
            normal_force=np.zeros_like(q);sf=(ke*weights*np.maximum(-phi,0))[:,None]*normal
            np.add.at(normal_force,ids[:,0],(1-u)[:,None]*sf)
            np.add.at(normal_force,ids[:,1],u[:,None]*sf)
            damp=EmbeddedDashpot(ids,u,normal,weights,velocity,tensor)
            if self.contact_step is not None:
                implicit=NormalContact(ids,u,normal,weights,phi,velocity,self.contact_step,ke)
                force-=normal_force
                bd=CombinedContact(damp,implicit)
            else:bd=damp
        else:bd=None
        com=cad.com_local@cad.rotation.T+translation
        return dict(force=force,reaction=-force.sum(0),moment=-np.cross(q-com,force).sum(0),
                    energy_J=energy,maximum_penetration_m=float(np.maximum(-phi,0).max()) if len(phi) else 0.,
                    active_samples=int((phi<0).sum()),active_nodes=int((np.linalg.norm(force,axis=1)>0).sum()),
                    estimated_contact_force_error_N=ev['estimated_force_error_N'],
                    normal_stiffness_N_per_m=ke,implicit_normal=self.contact_step is not None),bd
