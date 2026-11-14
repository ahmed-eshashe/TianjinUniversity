"""Exact original CAD with the legacy DiSECt knife normal/Brown friction law.
Nodal exterior collocation is a new, declared adapter, not legacy virtual-edge
quadrature equivalence. Prescribed translation only: angular coupling untested.
"""
from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;ROOT=W.parents[1];sys.path.insert(0,str(ROOT/'rl'));sys.path.insert(0,str(W/'backend'))
from tomato_compiled_blade_query import query_mesh
from numerics import Bulk,tensor
from blade_numerics import BladeContactBulk
def law(phi,normal,velocity,tool_velocity,ke=2000.,kd=1.,kf=2500.,mu=.5):
    phi=np.asarray(phi);normal=np.asarray(normal);relative=np.asarray(velocity)-np.asarray(tool_velocity);vn=np.sum(relative*normal,axis=1);tangent=relative-vn[:,None]*normal;speed=np.linalg.norm(tangent,axis=1);active=phi<0;elastic=ke*np.maximum(-phi,0);compressive=elastic+kd*np.maximum(-vn,0)*active
    ratio=speed/kf;friction=elastic*(mu*np.tanh(4*ratio)+(.5-mu)*ratio/(.25*ratio**2+.75)**2);direction=tangent/np.maximum(speed[:,None],1e-300);force=normal*compressive[:,None]-direction*friction[:,None]
    return force*active[:,None]
class CADBlade:
    def __init__(self):
        source=ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json';data=json.loads(source.read_text());self.vertices=np.array(data['vertices']);self.triangles=np.array(data['triangles']);ref=np.load(ROOT/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');sim_to_original=np.array([[1,0,0],[0,0,-1],[0,1,0]],float);self.rotation=sim_to_original.T@ref['rotation'];self.com_local=ref['com_local'];self.minimum=self.vertices.min(0);self.maximum=self.vertices.max(0)
    def query(self,points,translation):
        local=(points-translation)@self.rotation;result=query_mesh(self.vertices,self.triangles,local);result['normal']=result['normal']@self.rotation.T;result['closest']=result['closest']@self.rotation.T+translation;return result
    def evaluate(self,q,v,ids,translation,tool_velocity):
        # For zero SDF radius, outside the exact CAD AABB cannot be penetrating.
        ids=np.asarray(ids);local=(q[ids]-translation)@self.rotation;inside=np.all((local>=self.minimum)&(local<=self.maximum),axis=1);candidates=ids[inside];force=np.zeros_like(q);normals=np.zeros_like(q);dashpot_k=np.zeros(len(q))
        if len(candidates):
            result=self.query(q[candidates],translation);f=law(result['phi'],result['normal'],v[candidates],tool_velocity,kd=0.);force[candidates]=f;active=result['phi']<0;normals[candidates[active]]=result['normal'][active];dashpot_k[candidates[active]]=1.;depth=float(np.maximum(-result['phi'],0).max())
        else:depth=0.
        com=self.com_local@self.rotation.T+translation;reaction=-force.sum(0);moment=-np.cross(q-com,force).sum(0)
        return {'normal':normals,'kd':dashpot_k,'force':force,'reaction':reaction,'moment':moment,'sum_magnitudes_N':float(np.linalg.norm(force,axis=1).sum()),'maximum_penetration_m':depth,'active_nodes':int((np.linalg.norm(force,axis=1)>0).sum())}
class BladeBulk(BladeContactBulk):
    def __init__(self):
        super().__init__();mesh=np.load(W.parent/'disect_mesh_validation_20261108_v02/tomato_fem_mesh.npz');self.surface_ids=np.unique(mesh['boundary']);self.cad=CADBlade();self.blade_enabled=False;self.blade_translation=np.zeros(3);self.blade_velocity=np.zeros(3);self.blade_sample=None
    def geometry(self):
        super().geometry()
        if self.blade_enabled:
            q,v=self.arrays();self.blade_sample=self.cad.evaluate(q,v,self.surface_ids,self.blade_translation,self.blade_velocity);self.f.add_(tensor(self.blade_sample['force']));self.blade_dashpot={'normal':tensor(self.blade_sample['normal']),'velocity':tensor(np.broadcast_to(self.blade_velocity,q.shape).copy()),'kd':tensor(self.blade_sample['kd'])}
        return self.f
    def material(self):
        # Material reporting excludes the separately recorded applied CAD force.
        Bulk.geometry(self);return self.f-self.damping(self.v)
    def reset(self):
        super().reset();self.blade_sample=None;self.blade_dashpot=None;self.blade_enabled=False;self.blade_translation[:]=0;self.blade_velocity[:]=0
