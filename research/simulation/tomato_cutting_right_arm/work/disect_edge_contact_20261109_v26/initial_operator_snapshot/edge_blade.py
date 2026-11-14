from pathlib import Path
import sys,numpy as np,warp as wp
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent/'disect_fracture_20261109_v23'))
from damage_blade import DamageBlade,s,m,closure,torch,tensor,Bulk
from distributed_contact import DistributedContact
from embedded_dashpot import EmbeddedDashpot
from embedded_numerics import EmbeddedContactBulk

class EdgeBlade(DamageBlade):
    implicit=EmbeddedContactBulk.implicit

    def __init__(self,order=512):
        super().__init__()
        self.distributed=DistributedContact(m,order)

    def contact(self,q,v,translation,velocity):
        c=self.distributed;cad=self.cad
        outer=cad.evaluate(q,v,c.outer,translation,velocity)
        local=(q-translation)@cad.rotation
        a,b=c.edges.T
        keep=np.all((np.maximum(local[a],local[b])>=cad.minimum)&
                    (np.minimum(local[a],local[b])<=cad.maximum),axis=1)
        ids=[];us=[];normals=[];coefficients=[]
        oi=np.flatnonzero(outer['kd']>0)
        if len(oi):
            ids.append(np.column_stack((oi,oi)));us.append(np.zeros(len(oi)))
            normals.append(outer['normal'][oi]);coefficients.append(outer['kd'][oi])
        force=outer['force'].copy()
        energy=float(np.sum(np.einsum('ij,ij->i',outer['force'],outer['normal'])**2)/(2*2000.))
        depth=outer['maximum_penetration_m'];active_samples=0
        if keep.any():
            sub=DistributedContact.__new__(DistributedContact)
            sub.__dict__.update(c.__dict__)
            sub.edges=c.edges[keep];sub.edge_weights=c.edge_weights[keep]
            def query(points):
                lp=(points-translation)@cad.rotation
                inside=np.all((lp>=cad.minimum)&(lp<=cad.maximum),axis=1)
                phi=np.ones(len(points));normal=np.zeros_like(points)
                if inside.any():
                    result=cad.query(points[inside],translation)
                    phi[inside]=result['phi'];normal[inside]=result['normal']
                return dict(phi=phi,normal=normal)
            ev=sub.evaluate(q,v,query,velocity,translation,kd=0.)
            force+=ev['force'];energy+=ev['energy_J']
            depth=max(depth,ev['maximum_sample_penetration_m'])
            active=ev['phi']<0;ei,qi=np.where(active)
            if len(ei):
                ids.append(sub.edges[ei]);us.append(c.coordinates[qi])
                normals.append(ev['sample_normal'][ei,qi]);coefficients.append(ev['sample_weights'][ei,qi])
            active_samples=ev['active_samples']
        if ids:
            bd=EmbeddedDashpot(np.concatenate(ids),np.concatenate(us),np.concatenate(normals),
                               np.concatenate(coefficients),velocity,tensor)
        else:bd=None
        com=cad.com_local@cad.rotation.T+translation
        ev=dict(force=force,reaction=-force.sum(0),moment=-np.cross(q-com,force).sum(0),
                energy_J=energy,maximum_penetration_m=depth,active_samples=active_samples,
                active_nodes=int((np.linalg.norm(force,axis=1)>0).sum()))
        return ev,bd

    def geometry(self):
        f=Bulk.geometry(self);self.blade_dashpot=None;self.eligibility=np.zeros(47,bool)
        if self.blade_enabled:
            q,v=self.arrays()
            ev,bd=self.contact(q,v,self.blade_translation,self.blade_velocity)
            self.blade_sample=ev;self.blade_dashpot=bd
            fd=np.zeros_like(q) if bd is None else -bd.apply(self.v).cpu().numpy()
            self.eligibility=s.eligibility_from_contact(ev['force']+fd) if self.eligibility_override is None else self.eligibility_override.copy()
            f.add_(tensor(ev['force']))
        self.fracture_trial=self.fracture.evaluate(self.x,self.eligibility)
        f.add_(self.fracture_trial['force'])
        with wp.ScopedStream(wp.stream_from_torch(torch.cuda.current_stream())):
            f.add_(closure.evaluate(self.x))
        return f
