"""World inertia transform and initially resting one-interval impulse reference."""
import math
from tomato_reaction_metadata import quaternion_rotation
from tomato_wrench_contract import dot


def apply_inertia(pose,principal,world_vector,inverse=False):
    if len(principal)!=3 or len(world_vector)!=3 or not all(math.isfinite(x) for x in [*principal,*world_vector]) or min(principal)<=0:
        raise ValueError('Finite vector and positive principal inertia required')
    if max(principal)>sum(principal)-max(principal):raise ValueError('Principal moments violate triangle inequality')
    rotation=quaternion_rotation(pose[3:])
    local=[sum(rotation[j][i]*world_vector[j] for j in range(3)) for i in range(3)]
    scaled=[local[i]/principal[i] if inverse else local[i]*principal[i] for i in range(3)]
    return [dot(row,scaled) for row in rotation]


def assess_rest_pulse(initial_pose,final_pose,velocity,force,torque,mass,principal,dt):
    if len(velocity)!=6 or not all(math.isfinite(v) for v in [*velocity,*force,*torque,mass,dt]) or min(mass,dt)<=0:
        raise ValueError('Finite initially resting pulse inputs required')
    expected_linear=[dt*f/mass for f in force]
    # Leading-order impulse using the tensor sampled at interval start. Rotation is tiny;
    # the existing angular gate bounds any within-interval tensor evolution as well as roundoff.
    alpha=apply_inertia(initial_pose,principal,torque,inverse=True)
    expected_angular=[dt*a for a in alpha]
    le=math.dist(velocity[:3],expected_linear);ae=math.dist(velocity[3:],expected_angular)
    spin=apply_inertia(final_pose,principal,velocity[3:])
    spin_error=math.dist(spin,[dt*t for t in torque])
    if le>2e-5 or ae>2e-6 or spin_error>2e-8:
        raise ValueError(f'Anisotropic impulse mismatch: {le=}, {ae=}, {spin_error=}')
    return dict(expected_linear_velocity=expected_linear,initial_tensor_expected_angular_velocity=expected_angular,
        linear_velocity_error_m_s=le,angular_velocity_error_rad_s=ae,
        final_world_spin=spin,spin_impulse_error_nms=spin_error,
        angular_reference_scope='Initially at rest, small one-interval rotation; initial inertia tensor impulse approximation, not a general rotating Euler solution.')
