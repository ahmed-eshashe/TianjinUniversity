"""Endpoint reaction/COM kinematics adapter. Endpoint loads are not averages."""
import math
from tomato_wrench_contract import vector,cross,dot,to_world
I=((1.,0.,0.),(0.,1.,0.),(0.,0.,1.))


def quaternion_rotation(xyzw):
    if len(xyzw)!=4 or not all(type(v) in (int,float) and math.isfinite(v) for v in xyzw):raise ValueError('Finite xyzw quaternion required')
    norm=math.hypot(*xyzw)
    if norm==0 or not math.isfinite(norm):raise ValueError('Nonzero finite quaternion required')
    x,y,z,w=[v/norm for v in xyzw]
    return ((1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)),
            (2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)),
            (2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)))


def endpoint_metadata(row,*,body_pose_xyzw,body_com_local_m,body_spatial_velocity,target_origin_world_m,body='blade'):
    if row.get('force_convention')!='force_then_moment':raise ValueError('Explicit world force-then-moment convention required')
    if len(body_pose_xyzw)!=7 or len(body_spatial_velocity)!=6:raise ValueError('Native pose/twist dimensions required')
    translation=vector(body_pose_xyzw[:3]);rotation=quaternion_rotation(body_pose_xyzw[3:]);local=vector(body_com_local_m)
    com=tuple(t+dot(r,local) for t,r in zip(translation,rotation));target=vector(target_origin_world_m)
    spatial=row['spatial_wrench_world_about_com']
    if len(spatial)!=1 or len(spatial[0])!=6:raise ValueError('Exactly one isolated blade wrench required')
    force,moment=to_world(spatial[0][:3],spatial[0][3:],I,com,target)
    v=vector(body_spatial_velocity[:3]);omega=vector(body_spatial_velocity[3:])
    shift=cross(omega,tuple(t-c for t,c in zip(target,com)))
    vt=tuple(a+b for a,b in zip(v,shift))
    step,start,dt=row['step'],row['start_s'],row['dt_s']
    if type(step)is not int or step<0 or any(type(t) not in (int,float) or not math.isfinite(t) for t in (start,dt)) or start<0 or dt<=0:raise ValueError('Valid finite step interval required')
    return {'body':body,'step':step,'start_s':start,'dt_s':dt,'sample_time_s':start+dt,
        'temporal_semantics':'end_of_step_force_not_step_average','com_world_m':com,
        'origin_world_m':target,'force_world_n':force,'moment_world_nm':moment,
        'velocity_at_origin_world_m_s':vt,'angular_velocity_world_rad_s':omega,
        'native_physics_validated':False,'work_ledger_admissible':False,
        'quaternion_normalized_for_rotation':True}


def endpoint_work_estimate(sample):
    """Right-endpoint rectangular estimate only; no hidden step-average claim."""
    if sample.get('temporal_semantics')!='end_of_step_force_not_step_average':raise ValueError('Explicit endpoint sample required')
    p=dot(sample['force_world_n'],sample['velocity_at_origin_world_m_s'])+dot(sample['moment_world_nm'],sample['angular_velocity_world_rad_s'])
    value=p*sample['dt_s']
    if not math.isfinite(value):raise ValueError('Nonfinite estimated work')
    return {'estimated_contact_work_on_blade_j':value,'quadrature':'right_endpoint_load_and_twist',
        'exact_step_work':False,'native_work_balance_validated':False,
        'actuator_and_material_work_require_separate_accounting':True}


def capture_metadata(bundle,row,*,target_origin_world_m,native_execution_authorized=False):
    if native_execution_authorized is not True:raise PermissionError('Native state read disabled during preparation')
    if bundle['model'].body_count!=1:raise ValueError('Isolated blade body required')
    state=bundle['state0']
    return endpoint_metadata(row,body_pose_xyzw=state.body_q.numpy()[0].tolist(),
        body_com_local_m=bundle['model'].body_com.numpy()[0].tolist(),
        body_spatial_velocity=state.body_qd.numpy()[0].tolist(),target_origin_world_m=target_origin_world_m)
