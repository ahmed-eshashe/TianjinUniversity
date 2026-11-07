"""Compare replay traces only at meaningful active state/contact fields."""
import math


def compare_traces(baseline,replay):
    if not replay or len(replay)>len(baseline):raise ValueError('Replay must be a nonempty baseline prefix')
    errors=dict(position_m=0.,linear_velocity_m_s=0.,angular_velocity_rad_s=0.,quaternion_component=0.,force_n=0.,torque_nm=0.)
    limits=dict(position_m=1e-7,linear_velocity_m_s=2e-5,angular_velocity_rad_s=2e-6,quaternion_component=5e-7,force_n=2e-5,torque_nm=2e-7)
    def compare(a,b,key):
        if len(a)!=len(b) or not all(math.isfinite(v) for v in [*a,*b]):raise ValueError('Invalid replay field')
        errors[key]=max(errors[key],math.dist(a,b))
    for a,b in zip(baseline,replay):
        if a['interval']!=b['interval'] or a['contact_count']!=b['contact_count']:
            raise ValueError('Replay contact sequence mismatch')
        for stage in ('before','after'):
            x=a[stage];y=b[stage]
            compare(x['p'],y['p'],'position_m');compare(x['vp'],y['vp'],'linear_velocity_m_s')
            compare(x['pose'][:3],y['pose'][:3],'position_m');compare(x['pose'][3:],y['pose'][3:],'quaternion_component')
            compare(x['velocity'][:3],y['velocity'][:3],'linear_velocity_m_s');compare(x['velocity'][3:],y['velocity'][3:],'angular_velocity_rad_s')
        compare(a['force_n'],b['force_n'],'force_n');compare(a['wrench'][3:],b['wrench'][3:],'torque_nm')
    if any(errors[k]>limits[k] for k in errors):raise ValueError(f'Replay mismatch: {errors}')
    return dict(intervals_compared=len(replay),max_errors=errors,limits=limits)
