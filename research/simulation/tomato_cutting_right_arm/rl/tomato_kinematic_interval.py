"""Discrete prescribed-pose contract for inspected VBD kinematic handling.

VBD leaves kinematic poses unchanged and finalizes COM velocity from the pose
history difference. Therefore prescribe the interval END pose and secant velocity,
not a start pose mislabeled as an end-of-step observation. Fixed orientation only.
"""
from tomato_coupon_trajectory import pose_at


def interval_target(trajectory,*,step,dt_s):
    if type(step)is not int or step<0 or dt_s!=trajectory['dt_s']:
        raise ValueError('Consecutive nonnegative step and exact declared trajectory timestep required')
    start=pose_at(trajectory,step*dt_s);end=pose_at(trajectory,(step+1)*dt_s)
    if start['rotation']!=end['rotation']:raise ValueError('Rotating blade path requires reviewed angular kinematics')
    delta=[b-a for a,b in zip(start['translation_m'],end['translation_m'])]
    # First-step VBD history rebaseline snaps to the supplied pose. A stationary
    # startup interval avoids inventing an unobserved first displacement/history.
    if step==0 and any(x!=0 for x in delta):raise ValueError('Stationary first interval required for native first-step rebaseline')
    target={**end,'linear_velocity_m_s':[x/dt_s for x in delta],
            'angular_velocity_rad_s':[0.,0.,0.]}
    return {'pose':target,'start_pose':start,'start_s':step*dt_s,
            'end_s':(step+1)*dt_s,'velocity_convention':'interval_secant_COM_for_fixed_rotation',
            'native_kinematic_runtime_validated':False}
