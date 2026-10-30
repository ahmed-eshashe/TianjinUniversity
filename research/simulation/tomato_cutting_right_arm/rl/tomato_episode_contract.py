"""Explicit offline episode export/reset contract, not native state restoration.

Native adapters must export every buffer they own and demonstrate registry
completeness separately. Matching this declared export cannot reveal omitted
engine state. No constitutive update or runtime backend import is performed.
"""
import copy
import json
import math

STATE_FIELDS = frozenset({'positions_m', 'velocities_m_s', 'damage_states',
    'edge_hits', 'contact_state', 'solver_history', 'work_ledger',
    'phase_clock_s', 'previous_action', 'random_state', 'topology_state'})
MIN_HISTORY = frozenset({'body_q_prev', 'particle_q_prev',
                         'contact_warm_start', 'coupling_snapshot'})


def canonical(value):
    """Reject nonfinite or non-JSON exports before comparisons/serialization."""
    def check(v):
        if v is None or type(v) in (str, bool, int):
            return
        if type(v) is float and math.isfinite(v):
            return
        if type(v) is list:
            for x in v:
                check(x)
            return
        if type(v) is dict and all(type(k) is str for k in v):
            for x in v.values():
                check(x)
            return
        raise ValueError('Expected finite explicit JSON state')
    check(value)
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def validate_export(export):
    if set(export) != {'episode_id', 'seed', 'backend_state_fields', 'state'}:
        raise ValueError('Episode metadata or state registry missing/unknown')
    if type(export['episode_id']) is not str or not export['episode_id']:
        raise ValueError('Episode identity required')
    if type(export['seed']) is not int or export['seed'] < 0:
        raise ValueError('Explicit nonnegative seed required')
    state = export['state']
    if type(state) is not dict or set(state) != STATE_FIELDS:
        raise ValueError('Incomplete or unknown episode state fields')
    registry = export['backend_state_fields']
    if type(registry) is not list or not all(type(x) is str for x in registry):
        raise ValueError('Explicit backend buffer registry required')
    if len(registry) != len(set(registry)) or not MIN_HISTORY <= set(registry):
        raise ValueError('History registry incomplete/duplicated')
    if type(state['solver_history']) is not dict or set(state['solver_history']) != set(registry):
        raise ValueError('Export does not match declared backend registry')
    if type(state['contact_state']) is not dict or set(state['contact_state']) != {'multipliers', 'active_ids', 'eligibility'}:
        raise ValueError('Contact registry incomplete')
    if type(state['damage_states']) is not list or not state['damage_states']:
        raise ValueError('Nonempty material history required')
    for patch in state['damage_states']:
        if type(patch) is not dict or set(patch) != {'damage', 'kappa_m'}:
            raise ValueError('Expected original DamageState fields')
        if any(type(patch[k]) not in (float, int) for k in patch):
            raise ValueError('Damage/history must be numeric')
        if not 0 <= patch['damage'] <= 1 or not patch['kappa_m'] >= 0:
            raise ValueError('Invalid damage/history')
    if type(state['phase_clock_s']) not in (float, int) or state['phase_clock_s'] < 0:
        raise ValueError('Invalid phase clock')
    canonical(export)


def expected_reset(baseline, *, new_episode_id, seed):
    """Create an expected EXPORT for comparison; does not reset an engine.

    Randomized states require a separately captured baseline for that seed.
    Never relabel one seed's random state as another seed's fresh episode.
    """
    validate_export(baseline)
    if new_episode_id == baseline['episode_id'] or seed != baseline['seed']:
        raise ValueError('Reset requires new identity and matching baseline seed')
    result = copy.deepcopy(baseline)
    result['episode_id'] = new_episode_id
    validate_export(result)
    return result


def assert_reset_matches(actual, expected):
    validate_export(actual)
    validate_export(expected)
    if canonical(actual) != canonical(expected):
        raise ValueError('Reset export differs from expected full state')


def assert_irreversible(previous, current, *, eligible_patch_ids, phase):
    validate_export(previous)
    validate_export(current)
    if previous['episode_id'] != current['episode_id'] or previous['seed'] != current['seed']:
        raise ValueError('Transition crosses episodes')
    if previous['backend_state_fields'] != current['backend_state_fields']:
        raise ValueError('Transition changes backend registry')
    old, new = previous['state']['damage_states'], current['state']['damage_states']
    if len(old) != len(new):
        raise ValueError('Patch registry size changed')
    if phase not in {'loading', 'hold', 'withdrawal', 'reclosure'}:
        raise ValueError('Explicit supported phase required')
    ids = list(eligible_patch_ids)
    if len(ids) != len(set(ids)) or any(type(i) is not int or not 0 <= i < len(old) for i in ids):
        raise ValueError('Invalid eligibility registry')
    for i, (a, b) in enumerate(zip(old, new)):
        if b['damage'] < a['damage'] or b['kappa_m'] < a['kappa_m']:
            raise ValueError('Damage/history healing within episode')
        if (i not in ids or phase in {'withdrawal', 'reclosure'}) and a != b:
            raise ValueError('History changed without allowed local loading')
