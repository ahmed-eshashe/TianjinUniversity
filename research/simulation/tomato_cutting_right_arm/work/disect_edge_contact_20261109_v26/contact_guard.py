"""Cached whole-volume bound; movement consumes the geometric certificate.
The maximum material displacement bounds every point of each affine tet.
Fixed tool rotation is required. Invalid/unresolved certificates reject trials.
"""
import numpy as np
from volume_certificate import certify

class WholeVolumeGuard:
    def __init__(self,cad,tets,limit=.0001):
        self.cad=cad;self.tets=tets;self.limit=limit
        self.q=None;self.translation=None;self.lower=None;self.records=[]

    def check(self,q,translation,step_motion=0.):
        if self.q is not None:
            movement=np.linalg.norm(q-self.q,axis=1).max()+np.linalg.norm(translation-self.translation)
            lower=self.lower-movement
            if lower-step_motion >= -self.limit:
                return dict(passed=True,lower_bound_m=float(lower),recertified=False)
        vertices=self.cad.vertices@self.cad.rotation.T+translation
        result=certify(q,self.tets,vertices,self.cad.triangles,limit=.00008)
        self.records.append(result)
        passed=bool(result['passed'] and result['lower_bound_m']-step_motion>=-self.limit)
        if passed:
            self.q=q.copy();self.translation=translation.copy();self.lower=result['lower_bound_m']
        return dict(passed=passed,lower_bound_m=result.get('lower_bound_m'),recertified=True,certificate=result)
