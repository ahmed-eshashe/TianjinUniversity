from pathlib import Path
import sys,numpy as np
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent/'disect_edge_contact_20261109_v26'))
from edge_blade import EdgeBlade,s,m,closure,torch,tensor
from embedded_dashpot import EmbeddedDashpot
from adaptive_contact import AdaptiveContact

class AdaptiveBlade(EdgeBlade):
    def __init__(self):
        super().__init__()
        self.adaptive=AdaptiveContact(m)

    def contact(self,q,v,translation,velocity):
        c=self.adaptive;cad=self.cad
        outer=cad.evaluate(q,v,c.outer,translation,velocity)
        ev=c.evaluate(q,v,cad.vertices@cad.rotation.T+translation,cad.triangles,
                      velocity,translation,kd=0.)
        force=ev['force']+outer['force']
        ids=ev['ids'];u=ev['u'];normal=ev['normal'];coefficient=ev['weights']
        oi=np.flatnonzero(outer['kd']>0)
        if len(oi):
            ids=np.concatenate((ids,np.column_stack((oi,oi))))
            u=np.r_[u,np.zeros(len(oi))]
            normal=np.concatenate((normal,outer['normal'][oi]))
            coefficient=np.r_[coefficient,outer['kd'][oi]]
        bd=EmbeddedDashpot(ids,u,normal,coefficient,velocity,tensor) if len(ids) else None
        com=cad.com_local@cad.rotation.T+translation
        energy=ev['energy_J']+float(np.sum(np.einsum('ij,ij->i',outer['force'],outer['normal'])**2)/(2*2000.))
        depth=max(outer['maximum_penetration_m'],float(np.maximum(-ev['phi'],0).max()) if len(ev['phi']) else 0.)
        return dict(force=force,reaction=-force.sum(0),moment=-np.cross(q-com,force).sum(0),
                    energy_J=energy,maximum_penetration_m=depth,
                    active_samples=int((ev['phi']<0).sum()),
                    active_nodes=int((np.linalg.norm(force,axis=1)>0).sum()),
                    estimated_contact_force_error_N=ev['estimated_force_error_N']),bd
