"""Explicit binary32 constant-velocity substep replay; diagnostic, not a new gate."""
import math,struct


def f32(value):return struct.unpack('f',struct.pack('f',value))[0]


def replay(initial,velocity,dt,frames,substeps=16):
    if len(initial)!=3 or len(velocity)!=3 or not all(math.isfinite(v) for v in [*initial,*velocity,dt]) or dt<=0:
        raise ValueError('Finite COM packet and positive dt required')
    if type(frames)is not int or frames<1 or type(substeps)is not int or substeps<1:raise ValueError('Positive integer counts required')
    pos=list(initial);h=f32(f32(dt)/substeps);trace=[]
    for frame in range(frames):
        for _ in range(substeps):pos=[f32(p+f32(h*v)) for p,v in zip(pos,velocity)]
        trace.append(pos.copy())
    return trace
