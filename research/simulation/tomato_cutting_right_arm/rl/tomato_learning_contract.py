"""Offline deployment observation and bounded residual reference logic.

No controller commands, learner, sensor calibration or training launch. All
motion bounds must be supplied by a separately reviewed controller contract.
"""
import math
from tomato_staged_evaluator import evaluate

# Wrist channels intentionally have no enabling route until hardware is verified.
SOURCES={'joint_position_rad':'encoder','joint_velocity_rad_s':'encoder',
         'previous_action':'controller','knife_pose':'kinematics',
         'knife_velocity':'kinematics','tomato_pose_estimate':'vision',
         'target_plane_estimate':'vision'}
PRIVILEGED={'damage','connectivity','nodal_strain','material_truth','contact_ids'}


def finite_vector(values,size):
    if not isinstance(values,(list,tuple)) or len(values)!=size or any(type(v) not in (int,float) or not math.isfinite(v) for v in values):
        raise ValueError('Finite vector of declared width required')
    return list(values)


def actor_observation(samples,layout,*,now_s,max_age_s):
    """Allowlist only: hidden state and all wrist channels are ignored.

    Missing, stale or unverified channels are zeroed with explicit mask bits.
    Layout widths are frozen by the caller; adding a hidden name is rejected.
    Source labels still need external verification against real sensor wiring.
    """
    if type(now_s) not in (int,float) or not math.isfinite(now_s) or type(max_age_s) not in (int,float) or not math.isfinite(max_age_s) or max_age_s<0:
        raise ValueError('Finite observation time/age budget required')
    values=[];mask=[];names=[]
    for name,width in layout.items():
        if name not in SOURCES or type(width)is not int or width<=0:raise ValueError('Undeclared actor channel/width')
        sample=samples.get(name);valid=False;v=[0.]*width
        if isinstance(sample,dict) and sample.get('source')==SOURCES[name] and sample.get('verified') is True:
            t=sample.get('time_s')
            if type(t) in (int,float) and math.isfinite(t) and 0<=now_s-t<=max_age_s:
                v=finite_vector(sample.get('values'),width);valid=True
        values.extend(v);mask.extend([int(valid)]*width);names.extend([name]*width)
    return {'values':values,'mask':mask,'channel_names':names,'wrist_channels_enabled':False}


def privileged_observation(truth):
    return {key:truth[key] for key in PRIVILEGED if key in truth}


def bounded_residual(baseline,residual,previous,*,dt_s,lower,upper,max_acceleration):
    """Apply caller-supplied SI speed/acceleration limits to three action axes.

    Axes: draw m/s, down m/s, blade orientation rate rad/s. This reference cannot
    guarantee joint/effort feasibility; a robot controller must enforce those.
    """
    vectors=[finite_vector(v,3) for v in (baseline,residual,previous,lower,upper,max_acceleration)]
    b,r,p,lo,hi,acc=vectors
    if type(dt_s) not in (int,float) or not math.isfinite(dt_s) or dt_s<=0:raise ValueError('Positive finite step required')
    out=[]
    for i in range(3):
        if lo[i]>hi[i] or acc[i]<0 or not lo[i]<=p[i]<=hi[i]:raise ValueError('Inconsistent motion bounds/prior state')
        candidate=b[i]+r[i]
        if not math.isfinite(candidate):raise ValueError('Action arithmetic overflow')
        low=max(lo[i],p[i]-acc[i]*dt_s);high=min(hi[i],p[i]+acc[i]*dt_s)
        out.append(min(high,max(low,candidate)))
    return {'reference_action':out,'robot_command_authorized':False,'joint_effort_limits_verified':False}


def episode_outcome(stage_records,*,safety_failure=False):
    """Baseline and policy share this evaluator; no depth/damage reward shortcut.

    A reward value is intentionally absent until evidence provenance, thickness,
    load/quality terms and their scales are reviewed. Candidate release is not a
    successful physical episode and cannot earn a success bonus here.
    """
    if type(safety_failure)is not bool:raise ValueError('Explicit safety flag required')
    verdict=evaluate(stage_records)
    return {'evaluation':verdict,'terminate':safety_failure or verdict['status']=='review_required',
            'safety_failure':safety_failure,'success_bonus_enabled':False,'training_enabled':False}
