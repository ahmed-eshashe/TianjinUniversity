"""Wrench origin and measured-pose work definitions for recorded intervals."""
import numpy as np
from scipy.spatial.transform import Rotation

def shift_wrench(wrench,old_origin,new_origin):
 wrench=np.asarray(wrench,dtype=float);return np.r_[wrench[:3],wrench[3:]+np.cross(np.asarray(old_origin)-np.asarray(new_origin),wrench[:3])]

def measured_interval_work(before_link_pose,after_link_pose,local_com,held_world_wrench):
 before=np.asarray(before_link_pose,dtype=float);after=np.asarray(after_link_pose,dtype=float);local_com=np.asarray(local_com,dtype=float);w=np.asarray(held_world_wrench,dtype=float);r0=Rotation.from_quat(before[3:]);r1=Rotation.from_quat(after[3:]);c0=before[:3]+r0.apply(local_com);c1=after[:3]+r1.apply(local_com);increment=(r1*r0.inv()).as_rotvec()
 return dict(work_j=float(w[:3]@(c1-c0)+w[3:]@increment),com_displacement_m=(c1-c0).tolist(),world_rotation_increment_rad=increment.tolist(),scope='Held world wrench about actual COM, actual endpoint poses, geodesic angular increment. Finite-step approximation; refine against synchronized velocity/work traces. Not actuator work or whole-system energy closure.')
