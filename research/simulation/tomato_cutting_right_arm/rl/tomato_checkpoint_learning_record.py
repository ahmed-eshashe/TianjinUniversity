"""Read-only checkpoint adapter. No learner, motor command, or success label.

Samples are simulated observations, not verified real sensors. Exact tomato
state and simulated reaction stay outside actor inputs. Sparse checkpoints
have no demonstrated action label and must not be used as imitation targets.
"""
from tomato_learning_contract import actor_observation, finite_vector

def record(metadata, joint_names):
    state = metadata['robot_state']
    n = len(joint_names)
    if not n or len(set(joint_names)) != n:
        raise ValueError('Unique joint names required')
    clock = metadata['clock']
    layout = {'joint_position_rad': n, 'joint_velocity_rad_s': n,
              'knife_pose': 7, 'knife_velocity': 6,
              'tomato_pose_estimate': 7, 'previous_action': 3}
    samples = {}
    for name, key, width, source in (
        ('joint_position_rad', 'q', n, 'encoder'),
        ('joint_velocity_rad_s', 'qd', n, 'encoder'),
        ('knife_pose', 'tool_pose', 7, 'kinematics'),
        ('knife_velocity', 'tool_com_velocity', 6, 'kinematics')):
        samples[name] = {'values': finite_vector(state[key], width),
                         'source': source, 'verified': True, 'time_s': clock}
    observation = actor_observation(samples, layout, now_s=clock, max_age_s=0.)
    return {'time_s': clock, 'outer_step': metadata['outer_step'],
            'observation': observation, 'layout': layout,
            'demonstrated_action': None, 'action_label_valid': False,
            'successful_demonstration': False,
            'training_enabled': False, 'real_sensor_validation': False,
            'frames': {'knife_pose': 'world; tool origin; quaternion xyzw',
                       'knife_velocity': 'world; tool COM linear then angular'},
            'units': {'joint_position_rad': 'rad', 'joint_velocity_rad_s': 'rad/s',
                      'knife_pose': 'm and unit quaternion',
                      'knife_velocity': 'm/s then rad/s'},
            'missing_channels': ['tomato_pose_estimate', 'previous_action', 'wrist_force']}
