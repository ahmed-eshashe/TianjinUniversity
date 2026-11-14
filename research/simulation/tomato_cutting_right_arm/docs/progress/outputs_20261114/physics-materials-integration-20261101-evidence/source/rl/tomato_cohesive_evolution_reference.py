"""Preserved-law evolution adapter; external contact eligibility is not a detector."""
import math
from tomato_bonds import update_damage
from tomato_cohesive_adapter_reference import patch_reference


def fracture_dissipation(law,state):
    # Preserve the exact loading-envelope integral, not the larger explicit
    # fixed-geometry energy drop when a damage state jumps.
    a,b=law.onset_m,law.failure_m
    if not math.isfinite(state.kappa_m) or state.kappa_m<0 or not math.isfinite(state.damage) or not 0<=state.damage<=1:
        raise ValueError('Invalid committed damage history')
    q=min(b,max(a,state.kappa_m))
    return .5*law.stiffness_n_m*a*b/(b-a)*(q-a)


def evolve_patch(law,state,gaps,weights,stiffness,*,eligible=False):
    """Compute a trial state without mutation; caller commits only after audits.

    Same unsupported compression-plus-shear refusal and 1e-12 checks as the
    original surface evolution. No native stepping, dynamic stability claim,
    damping, frame update or permissive eligibility approximation is added.
    """
    if type(eligible)is not bool:raise ValueError('Explicit contact eligibility boolean required')
    # Validate shape/finite/SPD before unsupported-mode checks.
    response=patch_reference(gaps,weights,stiffness,0.)
    if any(g[0]<-1e-12 and math.hypot(*g[1:])>1e-12 for g in gaps):
        raise ValueError('Compression-plus-shear fracture remains unsupported')
    q=math.sqrt(2*response['energy_j']/law.stiffness_n_m)
    trial=update_damage(law,state,q,eligible=eligible)
    before=fracture_dissipation(law,state);after=fracture_dissipation(law,trial)
    return {'trial_state':trial,'equivalent_separation_m':q,'fracture_loss_j':after,
        'fracture_increment_j':after-before,'committed_state_mutated':False,
        'native_runtime_validated':False,'eligibility_is_external':True}


def patch_contact_eligibility(patch_indices,hits,multiplier_pairs,widths):
    """Exact legacy restricted-wedge eligibility threshold and patch OR mapping.

    This is NOT the eligibility detector for an arbitrary native blade. The
    multiplier values must have the original contact-force convention/units.
    """
    n=len(hits)
    if len(multiplier_pairs)!=n or len(widths)!=n:raise ValueError('Contact registry mismatch')
    active=[]
    for hit,m,w in zip(hits,multiplier_pairs,widths):
        if type(hit)is not bool or len(m)!=2 or not all(math.isfinite(x) for x in (*m,w)):
            raise ValueError('Invalid restricted-wedge contact evidence')
        active.append(hit and w>0 and max(m)>1e-9)
    result=[]
    for ids in patch_indices:
        if not ids or any(type(i)is not int or not 0<=i<n for i in ids):raise ValueError('Invalid patch contact registry')
        result.append(any(active[i] for i in ids))
    return result
