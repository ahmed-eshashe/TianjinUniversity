"""Bounded hand paths and measured knife limits for contact-only repositioning."""
import numpy as np
from scipy.spatial.transform import Rotation


def tilt_path(palm, hand_rotation, knife_pose, handle_local, blade_points, roll_deg=0.):
    """Pitch the handle up 8 degrees about the supported blade, optionally roll 12 degrees.

    Returns hand targets only. It never sets the knife pose or creates a constraint.
    """
    if abs(roll_deg)>12:raise ValueError('Roll command exceeds 12 degrees')
    kr=Rotation.from_quat(knife_pose[3:]).as_matrix()
    handle=kr@handle_local+knife_pose[:3]
    pivot_local=blade_points.mean(0).copy()
    pivot_local[0]=blade_points[:,0].min()+.06
    pivot_local[2]=blade_points[:,2].min()
    pivot=kr@pivot_local+knife_pose[:3]
    axis=np.cross(handle-pivot,[0.,0.,1.]);axis/=np.linalg.norm(axis)
    for fraction in np.linspace(0,1,25)[1:]:
        pitch=Rotation.from_rotvec(axis*np.deg2rad(8)*fraction).as_matrix()
        roll=Rotation.from_rotvec(kr[:,0]*np.deg2rad(roll_deg)*fraction).as_matrix()
        rotation=pitch@roll
        yield pivot+rotation@(palm-pivot),rotation@hand_rotation


def knife_motion(knife_points, initial_pose, pose, board_lo, board_hi):
    """Measured limits apply to the whole knife, not just the handle."""
    kr=Rotation.from_quat(pose[3:]).as_matrix()
    initial_r=Rotation.from_quat(initial_pose[3:]).as_matrix()
    world=knife_points@kr.T+pose[:3]
    initial=knife_points@initial_r.T+initial_pose[:3]
    margin=float(min(np.min(world[:,:2]-board_lo[:2]),np.min(board_hi[:2]-world[:,:2])))
    shift=float(np.linalg.norm(world.mean(0)[:2]-initial.mean(0)[:2]))
    angle=float(np.rad2deg(Rotation.from_matrix(kr@initial_r.T).magnitude()))
    return {'footprint_margin_m':margin,'centre_xy_shift_m':shift,'rotation_deg':angle,
            'within_bounds':bool(margin>=.005 and shift<=.03 and angle<=20.)}
