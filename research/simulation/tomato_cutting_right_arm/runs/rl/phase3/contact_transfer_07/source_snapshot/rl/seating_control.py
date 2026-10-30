"""Small bounded contact-feedback updates for the scripted seating diagnostic."""
import numpy as np
FINGERS=('index','middle','ring','pinky')


def seating_hand_goals(sample, goals):
    """Unload over-pressed pads; approach missing contacts without large stored preload."""
    result=np.array(goals,dtype=float).copy()
    actual=np.array(sample['q_rad'][7:])
    for i,part in [(1,'thumb'),*[(i+2,f) for i,f in enumerate(FINGERS)]]:
        force=sum(c['force_n'] for c in sample['contacts'] if c['part']==part and c['on_handle'])
        if force>4.:result[i]-=.004
        elif force<1.5:result[i]+=.003
        if force<=.2:result[i]=min(result[i],actual[i]+.10)
        result[i]=np.clip(result[i],0.,(.38 if part=='thumb' else np.deg2rad(85)))
    return result


class SupportedPinchMonitor:
    """Reject persistent loss of the physical pinch before further closing commands."""
    def __init__(self):self.missing=0
    def update(self,sample):
        parts={c['part'] for c in sample['contacts'] if c['on_handle'] and c['force_n']>.2}
        present='thumb' in parts and any(f in parts for f in FINGERS)
        self.missing=0 if present else self.missing+1
        if self.missing>=3:raise RuntimeError('Opposed supported pinch lost; closing/motion stopped early')
