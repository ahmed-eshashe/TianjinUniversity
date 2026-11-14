"""Read-only capture of caller-owned contact arrays; no engine import or writer."""
import copy
from tomato_contact_snapshot import ARRAY_FIELDS, _digest, _i32, _identity
from tomato_reaction_metadata import quaternion_rotation
from tomato_wrench_contract import vector


def capture_owned_prefix(contacts, particle_q, shape_body, body_q, identity, context, *,
                         expected_generation, native_capture_authorized=False):
    if native_capture_authorized is not True:
        raise PermissionError('Owned native capture requires guarded diagnostic authorization')
    _identity(identity)
    before_generation = int(contacts.contact_generation.numpy().tolist()[0])
    before_count = contacts.soft_contact_count.numpy().tolist()
    if before_generation != expected_generation:
        raise ValueError('Stale contact generation')
    if len(before_count) != 1:
        raise ValueError('Single contact count view required')
    count = _i32(before_count[0]); capacity = _i32(contacts.soft_contact_max)
    if count < 0 or capacity <= 0 or count >= capacity:
        raise ValueError('Invalid/saturated native count before transfer')
    arrays = {}
    for field in ARRAY_FIELDS:
        array = getattr(contacts, field)
        if array.shape[0] < count:
            raise ValueError('Native contact field shorter than active count')
        arrays[field] = array.numpy()[:count].tolist()
    particles = particle_q.numpy().tolist(); mapping = shape_body.numpy().tolist()
    poses = body_q.numpy().tolist()
    if not 0 <= context['body_id'] < len(poses):
        raise ValueError('Missing native target pose')
    pose = poses[context['body_id']]
    if len(pose) != 7:
        raise ValueError('Native transform requires xyz/xyzw')
    captured_context = copy.deepcopy(context)
    captured_context['body_to_world'] = {'translation_m': vector(pose[:3]),
                                         'rotation': quaternion_rotation(pose[3:])}
    after_count = contacts.soft_contact_count.numpy().tolist()
    after_generation = int(contacts.contact_generation.numpy().tolist()[0])
    if before_count != after_count or before_generation != after_generation:
        raise ValueError('Contact count/generation changed during capture')
    payload = {'identity': copy.deepcopy(identity), 'origin': 'owned_synthetic_native_buffer_diagnostic',
               'contact_generation': before_generation, 'soft_contact_count': before_count,
               'soft_contact_max': capacity, 'active_prefix_only': True, 'arrays': arrays,
               'shape_body': mapping, 'particle_q_world_m': particles,
               'conversion_qualified': False, 'native_runtime_validated': False,
               'solver_launch_enabled': False,
               'pose_source': 'owned synthetic native transform array',
               'capture_limits': ['caller must exclude all concurrent writers; same-count in-place writes are not detected',
                                  'generation/count check is not an atomic live-solver snapshot or full checkpoint']}
    return {'payload': payload, 'sha256': _digest(payload)}, captured_context
