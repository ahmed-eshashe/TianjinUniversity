"""World-axis wrench/twist point transport, with explicit source/destination."""
import numpy as np

def shift_wrench(wrench, source_point, destination_point):
    w=np.asarray(wrench,dtype=float);a=np.asarray(source_point,dtype=float);b=np.asarray(destination_point,dtype=float)
    if w.shape!=(6,)or a.shape!=(3,)or b.shape!=(3,)or not all(np.isfinite(x).all()for x in [w,a,b]):raise ValueError('Finite world wrench and source/destination points required')
    return np.r_[w[:3],w[3:]+np.cross(a-b,w[:3])]

def shift_twist(twist, source_point, destination_point):
    v=np.asarray(twist,dtype=float);a=np.asarray(source_point,dtype=float);b=np.asarray(destination_point,dtype=float)
    if v.shape!=(6,)or a.shape!=(3,)or b.shape!=(3,)or not all(np.isfinite(x).all()for x in [v,a,b]):raise ValueError('Finite world twist and source/destination points required')
    return np.r_[v[:3]+np.cross(v[3:],b-a),v[3:]]
