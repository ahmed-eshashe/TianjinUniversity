"""Pure SI sample boundary for a future native adapter; no engine imports.

Newton VBD's inspected proxy harvest writes spatial_vector(force, torque),
with world components and moment about world COM. Other sources must declare
their convention instead of relying on that ordering. This module normalizes
measured samples; it does not collect or fabricate simulator reactions.
"""
from dataclasses import dataclass
import math
from tomato_wrench_contract import to_world, vector


@dataclass(frozen=True)
class LoadSample:
    body: str
    step: int
    start_s: float
    dt_s: float
    force_n: tuple
    moment_nm: tuple
    origin_world_m: tuple
    interaction: str


def decode_sample(*, body, step, start_s, dt_s, spatial, convention,
                  quantity, frame_rotation, source_origin_world_m,
                  target_origin_world_m, interaction):
    """Normalize a complete step sample to world axes at the target origin.

    quantity is either force_N_moment_Nm or impulse_Ns_moment_Nms. Impulses
    become step-average loads, not instantaneous forces. All metadata required.
    """
    if not isinstance(body, str) or not body or not isinstance(interaction, str) or not interaction:
        raise ValueError('Named body and isolated interaction are required')
    if isinstance(step, bool) or not isinstance(step, int) or step < 0:
        raise ValueError('Step must be a nonnegative integer')
    start_s, dt_s = float(start_s), float(dt_s)
    if not math.isfinite(start_s) or start_s < 0 or not math.isfinite(dt_s) or dt_s <= 0:
        raise ValueError('Invalid sample interval')
    values = tuple(float(x) for x in spatial)
    if len(values) != 6 or not all(math.isfinite(x) for x in values):
        raise ValueError('Six finite load components required')
    if convention == 'force_then_moment':
        f, m = values[:3], values[3:]
    elif convention == 'moment_then_force':
        m, f = values[:3], values[3:]
    else:
        raise ValueError('Explicit spatial component convention required')
    if quantity == 'impulse_Ns_moment_Nms':
        f, m = tuple(x/dt_s for x in f), tuple(x/dt_s for x in m)
    elif quantity != 'force_N_moment_Nm':
        raise ValueError('Unsupported or undeclared units')
    f, m = to_world(f, m, frame_rotation, source_origin_world_m, target_origin_world_m)
    if not all(math.isfinite(x) for x in (*f, *m)):
        raise ValueError('Nonfinite normalized load')
    return LoadSample(body, step, start_s, dt_s, f, m,
                      vector(target_origin_world_m), interaction)


def validate_pair(first, second):
    """Reject mismatched samples before an action/reaction residual is used."""
    if first.body == second.body:
        raise ValueError('Action/reaction requires distinct bodies')
    for name in ('step', 'start_s', 'dt_s', 'origin_world_m', 'interaction'):
        if getattr(first, name) != getattr(second, name):
            raise ValueError('Unsynchronized or incompatible pair: ' + name)


def validate_sequence(samples):
    """Reject missing/duplicated steps and gaps before integrating a ledger.

    Strict step numbering; time boundary rounding allowance is 1e-12 seconds.
    This is a data-integrity tolerance, not a physical acceptance threshold.
    """
    if not samples:
        raise ValueError('Empty trace cannot demonstrate load or work')
    for a, b in zip(samples, samples[1:]):
        if a.body != b.body or a.interaction != b.interaction or a.origin_world_m != b.origin_world_m:
            raise ValueError('Trace changes body, interaction or reference origin')
        if b.step != a.step + 1:
            raise ValueError('Missing or duplicate step')
        if not math.isclose(b.start_s, a.start_s + a.dt_s, rel_tol=0, abs_tol=1e-12):
            raise ValueError('Trace has a gap or overlap')
