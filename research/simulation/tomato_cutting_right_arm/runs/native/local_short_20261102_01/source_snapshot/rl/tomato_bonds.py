"""Offline cohesive coupons only. No Newton imports, contact or dynamics solver."""
from dataclasses import dataclass
import math


def finite_positive(value):
    if not math.isfinite(value) or value <= 0:
        raise ValueError('Expected a finite positive value')
    return value


@dataclass(frozen=True)
class CohesiveLaw:
    """Scalar bilinear opening law; synthetic inputs must be explicitly supplied."""
    stiffness_n_m: float
    area_m2: float
    peak_traction_pa: float
    fracture_energy_j_m2: float
    damping_n_s_m: float

    def __post_init__(self):
        for value in (self.stiffness_n_m, self.area_m2, self.peak_traction_pa,
                      self.fracture_energy_j_m2):
            finite_positive(value)
        if not math.isfinite(self.damping_n_s_m) or self.damping_n_s_m < 0:
            raise ValueError('Invalid damping')
        if self.failure_m <= self.onset_m:
            raise ValueError('Fracture energy must exceed onset elastic energy')

    @property
    def onset_m(self):
        return self.peak_traction_pa * self.area_m2 / self.stiffness_n_m

    @property
    def failure_m(self):
        return 2 * self.fracture_energy_j_m2 / self.peak_traction_pa


@dataclass(frozen=True)
class DamageState:
    kappa_m: float = 0.
    damage: float = 0.


def update_damage(law, state, opening_m, shear_m=0., *, shear_weight=1., eligible=False):
    """Update only with explicit external contact eligibility, not a contact detector."""
    values = (state.kappa_m, state.damage, opening_m, shear_m, shear_weight)
    if not all(math.isfinite(x) for x in values):
        raise ValueError('Nonfinite damage input')
    if state.kappa_m < 0 or not 0 <= state.damage <= 1 or shear_weight < 0:
        raise ValueError('Invalid damage state or shear weight')
    if not eligible:
        return state
    separation = math.hypot(max(opening_m, 0.), math.sqrt(shear_weight) * shear_m)
    kappa = max(state.kappa_m, separation)
    if kappa <= law.onset_m:
        damage = 0.
    elif kappa >= law.failure_m:
        damage = 1.
    else:
        damage = law.failure_m * (kappa-law.onset_m) / (kappa*(law.failure_m-law.onset_m))
    return DamageState(kappa, max(state.damage, damage))


def scalar_response(law, state, extension_m, velocity_m_s=0.):
    """Bilateral Newton-style spring magnitude, stiffness and damping after damage."""
    if not all(math.isfinite(x) for x in (extension_m, velocity_m_s, state.damage)) or not 0 <= state.damage <= 1:
        raise ValueError('Invalid response input')
    k = (1-state.damage)*law.stiffness_n_m
    c = (1-state.damage)*law.damping_n_s_m
    return {'force_n': k*extension_m+c*velocity_m_s, 'stiffness_n_m': k, 'damping_n_s_m': c,
            'stored_energy_j': .5*k*extension_m**2}


def bundle_response(rest_vectors, current_vectors, stiffnesses, dampings, state, *, velocities=None):
    """Finite-length axial bundle; no claim of calibrated mixed-mode cohesive energy."""
    size = len(rest_vectors)
    if not size or not (size == len(current_vectors) == len(stiffnesses) == len(dampings)):
        raise ValueError('Mismatched bundle')
    if velocities is None:
        velocities = [(0., 0., 0.)]*size
    if len(velocities) != size or not math.isfinite(state.damage) or not 0 <= state.damage <= 1:
        raise ValueError('Invalid bundle state')
    total = [0., 0., 0.]
    energy = 0.
    for rest, current, k0, c0, velocity in zip(rest_vectors, current_vectors, stiffnesses, dampings, velocities):
        if not all(len(v) == 3 for v in (rest, current, velocity)):
            raise ValueError('Expected 3-vectors')
        if not all(math.isfinite(x) for v in (rest, current, velocity) for x in v):
            raise ValueError('Nonfinite vector')
        l0 = math.sqrt(sum(x*x for x in rest)); length = math.sqrt(sum(x*x for x in current))
        if min(l0, length) < 1e-9:
            raise ValueError('Degenerate spring length; no silent clamp')
        finite_positive(k0)
        if not math.isfinite(c0) or c0 < 0:
            raise ValueError('Invalid damping')
        direction = [x/length for x in current]
        extension = length-l0
        k = (1-state.damage)*k0; c = (1-state.damage)*c0
        magnitude = k*extension+c*sum(x*y for x,y in zip(velocity, direction))
        total = [a+magnitude*b for a,b in zip(total, direction)]
        energy += .5*k*extension**2
    return {'force_n': total, 'stored_energy_j': energy}


def update_bundle_damage(law, state, rest_vectors, current_vectors, stiffnesses,
                         *, opening_m, shear_m, eligible=False):
    """Drive common patch damage by actual undamaged bundle energy [J].

    q = sqrt(2 U0/Kref) makes U0 = Kref*q**2/2 exactly. Native
    bundle forces remain the gradient of U0, scaled by (1-D); no force
    rescaling or per-mode fitted fracture energy is needed. One patch owns
    one area/energy budget, including all its oblique springs.

    Opening and shear are objective caller-supplied material measures.
    This first coupon law excludes simultaneous compression and shear;
    compression alone freezes damage. Contact detection, frame recovery,
    compression contact and timestep control remain unimplemented.
    """
    if not math.isfinite(opening_m) or not math.isfinite(shear_m) or shear_m < 0:
        raise ValueError('Invalid material opening/shear')
    # Validate state even if damage is contact gated.
    update_damage(law, state, 0., eligible=False)
    energy = bundle_response(rest_vectors, current_vectors, stiffnesses,
                             [0.]*len(stiffnesses), DamageState())['stored_energy_j']
    if opening_m < -1e-12 and shear_m > 1e-12:
        raise ValueError('Compression-plus-shear fracture is outside this coupon law')
    if not eligible or (opening_m <= 1e-12 and shear_m <= 1e-12):
        return state
    equivalent_opening = math.sqrt(2*energy/law.stiffness_n_m)
    return update_damage(law, state, equivalent_opening, eligible=True)


def local_separation(rest_delta, current_delta, rest_basis, current_basis):
    """Co-rotated opening/shear; caller supplies orthonormal material frames."""
    for basis in (rest_basis, current_basis):
        if len(basis) != 3 or any(len(v) != 3 for v in basis):
            raise ValueError('Expected 3x3 basis')
        for i in range(3):
            for j in range(3):
                dot = sum(x*y for x,y in zip(basis[i],basis[j]))
                if not math.isfinite(dot) or abs(dot-(1. if i == j else 0.)) > 1e-8:
                    raise ValueError('Nonorthonormal material frame')
    if len(rest_delta) != 3 or len(current_delta) != 3 or not all(math.isfinite(x) for v in (rest_delta,current_delta) for x in v):
        raise ValueError('Invalid separation vectors')
    local = [sum(x*y for x,y in zip(current_delta, b))-sum(x*y for x,y in zip(rest_delta, a))
             for a,b in zip(rest_basis,current_basis)]
    return local[0], math.hypot(local[1],local[2])
