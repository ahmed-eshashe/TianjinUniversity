"""Reward-independent physical grasp criteria. Inputs are evaluator-only simulation evidence."""
from dataclasses import dataclass, field
import math
import numpy as np


@dataclass(frozen=True)
class GraspCriteria:
    lift_m: float=.05
    hold_s: float=3.
    max_slip_m: float=.01
    contact_n: float=.05
    max_board_support_n: float=.05
    inner_distance_m: float=.015
    minimum_curl_rad: float=math.radians(115)
    minimum_fingers: int=3
    minimum_inner_fingers: int=2


@dataclass
class GraspEvaluator:
    """Contiguous hold window; any unsafe event invalidates the entire episode."""
    initial_height: float
    criteria: GraspCriteria=field(default_factory=GraspCriteria)
    hold: float=0.
    reference: object=None
    unsafe_seen: bool=False
    success: bool=False

    def update(self, sample, dt):
        c=self.criteria
        if not math.isfinite(dt) or not 0<dt<=.1:
            raise ValueError('Evaluator requires positive physics/control intervals no greater than 0.1 seconds')
        if not math.isfinite(sample['support_force_n']) or not math.isfinite(sample['support_clearance_m']):
            self.unsafe_seen=True
        self.unsafe_seen |= bool(sample['blade_contact'] or sample['unsafe_contact'] or
                                 sample['attachment'] or sample['joint_limit_violation'] or sample['contact_buffer_full'])
        fingers=set(); inner=set(); vectors=[]; thumb=[]; finger_vectors=[]; palm=False
        for contact in sample['contacts']:
            if contact['force_n']<c.contact_n or not contact['on_handle']:continue
            if not math.isfinite(contact['force_n']):
                self.unsafe_seen=True
                continue
            v=np.array(contact['radial_vector'],dtype=float,copy=True)
            if not np.isfinite(v).all() or np.linalg.norm(v)<1e-8:continue
            v/=np.linalg.norm(v)
            body=contact['part']
            if body=='palm':palm=True;vectors.append(v)
            elif body=='thumb':thumb.append(v);vectors.append(v)
            elif body in ('index','middle','ring','pinky') and contact['curl_rad']>=c.minimum_curl_rad:
                fingers.add(body);vectors.append(v);finger_vectors.append(v)
                if contact['proximal'] or contact['distance_from_tip_m']>=c.inner_distance_m:inner.add(body)
        # Radial vectors are expressed in the knife's local cross-section, independent of world yaw.
        angles=sorted(math.atan2(v[1],v[0])%(2*math.pi) for v in vectors)
        maxgap=max(np.diff(angles+[angles[0]+2*math.pi])) if angles else 2*math.pi
        enclosed=bool(maxgap<=math.pi+.05)
        opposed=bool(thumb and any(np.dot(t,v)<-.5 for t in thumb for v in finger_vectors))
        wrapped=palm and opposed and enclosed and len(fingers)>=c.minimum_fingers and len(inner)>=c.minimum_inner_fingers
        relative=np.asarray(sample['handle_in_palm_m'],dtype=float)
        finite=np.isfinite(relative).all() and math.isfinite(sample['handle_height_m'])
        lifted=finite and sample['handle_height_m']-self.initial_height>=c.lift_m
        supported=sample['support_force_n']>c.max_board_support_n or sample['support_clearance_m']<=.003
        ready=wrapped and lifted and not supported and not self.unsafe_seen and not sample['dropped']
        if ready:
            if self.reference is None:self.reference=relative.copy()
            slip=float(np.linalg.norm(relative-self.reference))
            if slip>c.max_slip_m:ready=False
        else:slip=0.
        if ready:self.hold+=dt
        else:self.hold=0.;self.reference=None
        self.success=bool(ready and self.hold+1e-9>=c.hold_s)
        return {'success':self.success,'wrapped':wrapped,'lifted':bool(lifted),'supported':supported,
                'unsafe_seen':self.unsafe_seen,'hold_s':self.hold,'slip_m':slip,
                'fingers':sorted(fingers),'inner_fingers':sorted(inner),'enclosed':enclosed,'opposed':opposed}
