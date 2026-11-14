"""Whole-volume proof with an 80 um cache target and unchanged 100 um limit.
The cache target is not a physical stop: when needed, recertify closer to the
actual limit, leaving enough margin to bound motion over the accepted step.
"""
import numpy as np
from volume_certificate import certify

class WholeVolumeGuard:
    def __init__(self,cad,tets,limit=.0001):
        self.cad=cad;self.tets=tets;self.limit=limit
        self.q=None;self.translation=None;self.lower=None;self.records=[]

    def check(self,q,translation,step_motion=0.):
        if self.q is not None:
            move=np.linalg.norm(q-self.q,axis=1).max()+np.linalg.norm(translation-self.translation)
            lower=self.lower-move
            if lower-step_motion>=-self.limit:
                return dict(passed=True,lower_bound_m=float(lower),recertified=False)
        vertices=self.cad.vertices@self.cad.rotation.T+translation
        near_limit=self.limit-max(2*step_motion,1e-8)
        if near_limit<=0:
            return dict(passed=False,reason='Step movement exceeds geometric proof budget')
        targets=sorted(set([x for x in [.00008,.00009,.000095,.000098] if x<near_limit]+[near_limit]))
        for target in targets:
            is_final=target==near_limit
            result=certify(q,self.tets,vertices,self.cad.triangles,limit=target,max_depth=40 if is_final else 20,wall_cap=180. if is_final else 10.)
            self.records.append(dict(requested_intrusion_bound_m=target,**result))
            passed=bool(result['passed'] and result['lower_bound_m']-step_motion>=-self.limit)
            if passed:
                self.q=q.copy();self.translation=translation.copy();self.lower=result['lower_bound_m']
                return dict(passed=True,lower_bound_m=self.lower,recertified=True,certificate=result)
        return dict(passed=False,reason='Whole-volume intrusion bound failed or remained unresolved',
                    lower_bound_m=result.get('lower_bound_m'),recertified=True,certificate=result)
