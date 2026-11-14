"""Episode-local actor history and explicit residual amplitude contract; offline."""
import copy
import math
from collections import deque
from tomato_learning_contract import actor_observation,bounded_residual,finite_vector


class ObservationHistory:
    def __init__(self,layout,length):
        if type(length)is not int or not 1<=length<=64:raise ValueError('Bounded history length required')
        # Validate allowlist and widths before retaining the schema.
        actor_observation({},layout,now_s=0.,max_age_s=0.)
        self.layout=dict(layout);self.length=length;self.width=sum(layout.values())
        if not self.width:raise ValueError('Nonempty actor schema required')
        self.frames=deque(maxlen=length);self.episode_id=None;self.seed=None;self.step=None;self.time=None
    def reset(self,episode_id,seed):
        if not isinstance(episode_id,str) or not episode_id or episode_id==self.episode_id or type(seed)is not int or seed<0:
            raise ValueError('Fresh episode identity and nonnegative integer seed required')
        self.episode_id=episode_id;self.seed=seed;self.step=None;self.time=None;self.frames.clear()
    def append(self,samples,*,episode_id,step,time_s,max_age_s):
        if self.episode_id is None or episode_id!=self.episode_id:raise ValueError('Explicit reset and matching episode required')
        if type(step)is not int or step!=(0 if self.step is None else self.step+1):raise ValueError('Missing, duplicate or reordered observation step')
        if self.time is not None and time_s<=self.time:raise ValueError('Observation clock must advance')
        frame=actor_observation(samples,self.layout,now_s=time_s,max_age_s=max_age_s)
        self.frames.append(copy.deepcopy(frame));self.step=step;self.time=time_s
        return self.snapshot()
    def snapshot(self):
        pad=self.length-len(self.frames)
        return {'episode_id':self.episode_id,'seed':self.seed,'last_step':self.step,
            'values':[[0.]*self.width for _ in range(pad)]+[list(f['values']) for f in self.frames],
            'mask':[[0]*self.width for _ in range(pad)]+[list(f['mask']) for f in self.frames],
            'native_reset_verified':False}


def residual_reference(baseline,residual,previous,*,max_residual,**limits):
    residual=finite_vector(residual,3);amplitude=finite_vector(max_residual,3)
    if any(a<0 for a in amplitude):raise ValueError('Nonnegative residual amplitude required')
    clipped=[min(a,max(-a,r)) for r,a in zip(residual,amplitude)]
    result=bounded_residual(baseline,clipped,previous,**limits)
    result['clipped_residual']=clipped
    return result


def validate_case_registry(cases):
    """Split integrity only; ranges/material calibration remain external gates.

    A case identity hashes physical geometry/material/config, excluding random
    seed. Duplicate physical configurations across splits are rejected even if
    assigned different seeds or labels. This is strict configuration holdout.
    """
    ids=set();physical={};seeds={};counts={'baseline':0,'train':0,'heldout':0}
    for c in cases:
        split=c['split'];ident=c['case_id'];seed=c['seed'];digest=c['physical_config_sha256']
        if split not in counts or not isinstance(ident,str) or not ident or ident in ids:raise ValueError('Unique case identity and declared split required')
        if type(seed)is not int or seed<0:raise ValueError('Nonnegative integer seed required')
        if not isinstance(digest,str) or len(digest)!=64 or any(x not in '0123456789abcdef' for x in digest):raise ValueError('Physical configuration digest required')
        if digest in physical and physical[digest]!=split:raise ValueError('Physical configuration leaks across splits')
        if seed in seeds and seeds[seed]!=split:raise ValueError('Random seed leaks across splits')
        physical[digest]=split;seeds[seed]=split;ids.add(ident);counts[split]+=1
    if not counts['baseline'] or not counts['heldout']:raise ValueError('Baseline and heldout cases required')
    return {'counts':counts,'split_integrity_verified':True,'material_calibrated':False,'training_authorized':False}
