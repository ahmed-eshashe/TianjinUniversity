"""Validation and synchronized targets for contact-preserving physical diagnostics."""
import numpy as np
from scipy.spatial.transform import Rotation


def synchronized_increment(delta,rates):
    delta=np.asarray(delta,dtype=float);rates=np.asarray(rates,dtype=float)
    if delta.shape!=rates.shape or not np.isfinite(delta).all() or not np.isfinite(rates).all() or np.any(rates<=0):
        raise ValueError('Invalid synchronized target input')
    steps=max(1.,float(np.max(np.abs(delta)/rates)))
    return delta/steps


def validated_waypoints(plan):
    waypoints=[w for w in plan['waypoints'] if not w.get('rejected')]
    if len(waypoints)<3:raise ValueError('Contact path has insufficient valid progress')
    previous=None
    for w in waypoints:
        t=np.array(w['hand_root_in_knife_m']);r=np.array(w['hand_rotation_in_knife']);q=np.array(w['joint_rad'])
        if t.shape!=(3,) or r.shape!=(3,3) or q.shape!=(6,) or not all(np.isfinite(x).all() for x in [t,r,q]):raise ValueError('Invalid contact path pose')
        if not np.allclose(r.T@r,np.eye(3),atol=1e-5) or np.linalg.det(r)<.999:raise ValueError('Invalid contact path rotation')
        if np.any(q<0) or np.any(q>np.array([.90,.315,*[np.deg2rad(85)]*4])+1e-7):raise ValueError('Contact path joint limit')
        if not 0<=w['anchor_error_m']<=.0005 or not 0<=w['normal_error']<=.35:raise ValueError('Contact path point/normal error')
        if not w['min_blade_gap_m']>=0 or not w['min_board_gap_m']>=0:raise ValueError('Contact path clearance')
        if previous is not None:
            pt,pr,pq=previous
            if np.linalg.norm(t-pt)>.006 or Rotation.from_matrix(r@pr.T).magnitude()>.10 or np.max(abs(q-pq))>.10:
                raise ValueError('Contact path waypoint discontinuity')
        previous=t,r,q
    return waypoints


def balanced_contact_goals(sample,goals,acquisition_goals=None,index_target=2.):
    if not .5<=index_target<=4.:raise ValueError('Index force target outside diagnostic bounds')
    result=np.array(goals,dtype=float).copy();actual=np.array(sample['q_rad'][7:]);forces={}
    for part in ['thumb','index','middle','ring','pinky']:
        forces[part]=sum(c['force_n'] for c in sample['contacts'] if c['part']==part and c['on_handle'])
    for i,f in enumerate(['index','middle','ring','pinky'],2):
        if f=='pinky' and (forces['middle']<.3 or forces['ring']<.3):continue
        if f!='index' and forces[f]<=.2 and acquisition_goals is not None:
            # Do not curl past a planned near-contact pose: more closure can move the pad away.
            result[i]=float(acquisition_goals[i]);continue
        target=index_target if f=='index' else .6
        if forces[f]<target-.2:result[i]+=.001
        elif forces[f]>target+1.:result[i]-=.0015
        if forces[f]<=.2:result[i]=min(result[i],actual[i]+.10)
        result[i]=np.clip(result[i],0,np.deg2rad(85))
    thumb_target=min(7.,max(3.,sum(forces[f] for f in ['index','middle','ring','pinky'])*.95))
    if forces['thumb']<thumb_target-.3:result[1]+=.002
    elif forces['thumb']>thumb_target+1.:result[1]-=.002
    result[1]=np.clip(result[1],0,.38)
    return result


def anchor_translation_correction(errors,max_step=.00015):
    """Bounded translation toward fixed physical contact references, never toward a moved knife."""
    errors=np.asarray(errors,dtype=float)
    if errors.ndim!=2 or errors.shape[1]!=3 or len(errors)<2 or not np.isfinite(errors).all() or not 0<max_step<=.0002:
        raise ValueError('Invalid contact feedback input')
    delta=errors.mean(0)
    if np.linalg.norm(delta)<.00005:return np.zeros(3)
    return delta*min(.25,max_step/np.linalg.norm(delta))
