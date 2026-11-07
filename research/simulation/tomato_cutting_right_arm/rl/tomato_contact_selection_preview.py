"""Read-only representative-contact policy; never authorizes native writes.

One aligned-normal patch on one disclosed soft support may yield a diagnostic
representative. Conflicting normal branches and mixed supports are refused.
This is not a manifold, quadrature, or force-acceptance policy for production.
"""
import copy
import json
import math
from tomato_mesh_contact_contract import review_record
from tomato_wrench_contract import dot


def selection_preview(records, context, *, raw_capacity=2048):
    if type(raw_capacity) is not int or raw_capacity <= 0 or len(records) >= raw_capacity:
        raise ValueError('Raw candidate capacity saturated or invalid')
    reviewed = []
    unique = {}
    for record in records:
        row = review_record(record, context)
        if row['reference_penetration_m'] <= 0:
            raise ValueError('Only strictly penetrating signed reference candidates accepted')
        # Exact events only. IDs are provenance, not different physical events.
        key=json.dumps({k:v for k,v in record.items() if k!='id'},sort_keys=True,separators=(',',':'),allow_nan=False)
        unique.setdefault(key,(record,row))
        reviewed.append(row)
    result={'raw_count':len(records),'unique_count':len(unique),'exact_duplicate_count':len(records)-len(unique),
            'selected_records':[],'native_write_allowed':False,'production_manifold_validated':False}
    if not unique:
        return dict(result,status='empty',reason='No admissible records supplied; this alone does not prove collision clearance.')
    supports={(row['body_id'],row['shape_id'],row['corners']) for _,row in unique.values()}
    if len(supports)!=1:
        return dict(result,status='blocked',reason='Mixed soft supports require an explicit cross-feature manifold policy.')
    normals=[row['normal_world'] for _,row in unique.values()]
    minimum_dot=min(dot(a,b) for a in normals for b in normals)
    result['minimum_normal_dot']=minimum_dot
    result['maximum_normal_spread_deg']=math.degrees(math.acos(max(-1.,min(1.,minimum_dot))))
    if minimum_dot < 1.-1e-6:
        return dict(result,status='blocked',reason='Conflicting outward-normal branches; one deepest sample would discard distinct contact directions.')
    # Stable tie break on semantic record values, independent of input order or ID.
    key,(record,row)=min(unique.items(),key=lambda pair:(-pair[1][1]['reference_penetration_m'],pair[0]))
    selected=copy.deepcopy(record);selected['id']='diagnostic_representative:0'
    result.update(status='diagnostic_representative_only',selected_records=[selected],
                  selected_penetration_m=row['reference_penetration_m'],
                  reason='Deepest sampled candidate on one aligned-normal support. Resampling invariance and physical manifold remain unproven.')
    return result
