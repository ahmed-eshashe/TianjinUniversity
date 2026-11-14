"""Offline contact-coverage evidence contract; no collision backend invocation."""
import math

CHALLENGES=('blade_vertex','blade_triangle_interior','blade_edge','cut_face_closure',
            'cut_face_slide','cut_face_rim','cut_face_reopening','exact_touching_rest',
            'off_plane_pass','withdrawal_no_healing')


def pair_set(rows):
    result=set()
    for row in rows:
        if not isinstance(row,(list,tuple)) or len(row)!=3:raise ValueError('Feature/primitive/shape triple required')
        kind,primitive,shape=row
        if kind not in ('vertex','edge','face') or type(primitive)is not int or primitive<0 or type(shape)is not int or shape<0:raise ValueError('Invalid contact pair identity')
        item=(kind,primitive,shape)
        if item in result:raise ValueError('Duplicate pair identity')
        result.add(item)
    return result


def coverage_report(*,candidate_pairs,emitted_pairs,reference_active_pairs,
                    attempted_count,record_capacity,body_counts,body_capacity,
                    independent_reference_reviewed=False):
    """Compare feature pairs, not just retained solver records.

    Reference must be a separately reviewed geometric oracle. Matching IDs cannot
    prove contact multiplicity, correct normals, distance, forces or work.
    """
    candidates=pair_set(candidate_pairs);emitted=pair_set(emitted_pairs)
    for x in [attempted_count,record_capacity,body_capacity,*body_counts]:
        if type(x)is not int or x<0:raise ValueError('Nonnegative integer counters required')
    if record_capacity==0 or body_capacity==0:raise ValueError('Positive buffers required')
    if not emitted<=candidates:raise ValueError('Emitted pair absent from broadphase registry')
    if attempted_count<len(emitted):raise ValueError('Attempt counter below retained pair count')
    saturated=attempted_count>=record_capacity or any(n>=body_capacity for n in body_counts)
    if reference_active_pairs is None:
        return {'status':'inconclusive','reason':'independent_reference_missing','saturated':saturated,'native_contact_validated':False}
    reference=pair_set(reference_active_pairs)
    missing_candidates=reference-candidates;missing_emitted=reference-emitted
    status='coverage_candidate'
    if saturated:status='refused_saturated'
    elif missing_candidates or missing_emitted:status='failed_missing_pairs'
    elif independent_reference_reviewed is not True:status='inconclusive_reference_unreviewed'
    return {'status':status,'saturated':saturated,
            'missing_candidate_pairs':[list(x) for x in sorted(missing_candidates)],
            'missing_emitted_pairs':[list(x) for x in sorted(missing_emitted)],
            'native_contact_validated':False,'normal_force_multiplicity_checks_still_required':True}


def challenge_registry():
    return [{'id':name,'execution_enabled':False,'native_result':'unexecuted',
             'required':['source-bound geometry and pair filters','independent geometric reference',
                         'candidate/attempt/retained and per-body counters','distance/normal/load/work evidence',
                         'half-timestep and spatial-resolution comparison']} for name in CHALLENGES]


def refinement_report(coarse,fine,*,relative_budget=.1,budget_status='draft'):
    """Prior plans propose <10% peak-load/work change. This remains provisional.

    Exact zero metrics require equality; near-zero scales need a separately
    justified dimensional error budget, not an invented denominator floor.
    """
    if budget_status not in ('draft','frozen') or type(relative_budget) not in (int,float) or not math.isfinite(relative_budget) or not 0<relative_budget<=.1:raise ValueError('Cannot loosen provisional 10% ceiling')
    if coarse['physical_config_sha256']!=fine['physical_config_sha256']:raise ValueError('Physical model changed across numerical refinement')
    errors={}
    for k in ('peak_load_n','cutting_work_j'):
        a,b=coarse[k],fine[k]
        if any(type(v) not in (int,float) or not math.isfinite(v) for v in (a,b)):raise ValueError('Finite measured metrics required')
        scale=max(abs(a),abs(b));errors[k]=abs(a-b)/scale if scale else 0.
    return {'relative_changes':errors,'within_provisional_budget':all(v<relative_budget for v in errors.values()),
            'budget_status':budget_status,'native_convergence_validated':False}
