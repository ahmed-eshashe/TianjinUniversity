"""Replay comparison for coupled hinge traces; no engine imports."""
import math


def compare(baseline,replay):
    if not replay or len(replay)>len(baseline):raise ValueError('Replay must match a nonempty baseline prefix')
    errors=dict(particle_position_m=0.,particle_velocity_m_s=0.,joint_position_rad=0.,joint_velocity_rad_s=0.,force_n=0.,torque_nm=0.,link_position_m=0.,link_quaternion=0.,link_linear_velocity_m_s=0.,link_angular_velocity_rad_s=0.)
    limits=dict(particle_position_m=1e-7,particle_velocity_m_s=2e-5,joint_position_rad=1e-6,joint_velocity_rad_s=2e-5,force_n=2e-5,torque_nm=2e-7,link_position_m=1e-7,link_quaternion=5e-7,link_linear_velocity_m_s=2e-5,link_angular_velocity_rad_s=2e-6)
    def record(a,b,key):
        if not all(math.isfinite(v) for v in [*a,*b]) or len(a)!=len(b):raise ValueError('Invalid replay value')
        errors[key]=max(errors[key],math.dist(a,b))
    for a,b in zip(baseline,replay):
        if a['interval']!=b['interval'] or a['contact_count']!=b['contact_count']:raise ValueError('Contact/interval replay mismatch')
        for stage in ('before','after'):
            for field,key in [('p','particle_position_m'),('vp','particle_velocity_m_s')]:record(a[stage][field],b[stage][field],key)
            for field,key in [('q','joint_position_rad'),('qd','joint_velocity_rad_s')]:record(a[stage][field],b[stage][field],key)
        record(a['force_n'],b['force_n'],'force_n');record(a['wrench'][3:],b['wrench'][3:],'torque_nm')
        x=a['after_link_packet'];y=b['after_link_packet']
        record(x['link_pose'][:3],y['link_pose'][:3],'link_position_m');record(x['link_pose'][3:],y['link_pose'][3:],'link_quaternion')
        record(x['link_com_velocity'][:3],y['link_com_velocity'][:3],'link_linear_velocity_m_s');record(x['link_com_velocity'][3:],y['link_com_velocity'][3:],'link_angular_velocity_rad_s')
    if any(errors[k]>limits[k] for k in errors):raise ValueError(f'Hinge replay mismatch: {errors}')
    return dict(intervals_compared=len(replay),max_errors=errors,limits=limits)
