"""Bounded instantaneous no-slip kinematics for a contact-only seating diagnostic."""
import numpy as np


def project_contact_motion(jacobian,goal,limits):
    j=np.asarray(jacobian,dtype=float);goal=np.asarray(goal,dtype=float);limits=np.asarray(limits,dtype=float)
    if j.ndim!=2 or j.shape[1]!=len(goal) or goal.shape!=limits.shape or not all(np.isfinite(x).all() for x in [j,goal,limits]) or np.any(limits<=0):
        raise ValueError('Invalid rolling contact input')
    scaled=j*limits[None,:]
    null=np.eye(len(goal))-np.linalg.pinv(scaled,rcond=1e-6)@scaled
    direction=np.clip(goal/limits,-1,1)
    delta=null@direction
    delta/=max(1.,float(np.max(abs(delta))))
    return delta*limits
