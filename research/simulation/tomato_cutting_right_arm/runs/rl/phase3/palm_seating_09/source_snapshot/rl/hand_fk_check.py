"""Compare authored joint-frame hand kinematics against actual native link transforms."""
import numpy as np
from scipy.spatial.transform import Rotation
from native_contacts import numpy


def check_hand_frames(env,kin):
    values=dict(zip(env.robot.joint_names,env.robot.data.joint_pos.torch[0].tolist()))
    cache={'/dual_ar5_o6':kin.root}
    def transform(path):
        if path in cache:return cache[path]
        parent,child,a,b,axis,name=kin.by_child[path];r=np.eye(4)
        if axis is not None:r[:3,:3]=Rotation.from_rotvec(axis*values.get(name,0.)).as_matrix()
        cache[path]=transform(parent)@a@r@b;return cache[path]
    actual=numpy(env.robot.root_view.get_link_transforms())[0];checks=[]
    for path in kin.by_child:
        name=path.rsplit('/',1)[-1]
        if not name.startswith('right_rh_') or name not in env.robot.body_names:continue
        predicted=transform(path);measured=actual[env.robot.body_names.index(name)]
        checks.append({'body':name,'position_error_m':float(np.linalg.norm(predicted[:3,3]-measured[:3])),
            'angle_error_rad':float(Rotation.from_matrix(predicted[:3,:3]@Rotation.from_quat(measured[3:]).as_matrix().T).magnitude())})
    return {'bodies':checks,'max_position_error_m':max(x['position_error_m'] for x in checks),
        'max_angle_error_rad':max(x['angle_error_rad'] for x in checks),'actual_joint_rad':values}
