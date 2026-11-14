"""Pure staged mechanics evidence logic, not a native physics validator.

Numeric tolerances remain in independent versioned auditors. This orchestrator
only consumes their explicit outcomes; it never infers separation from depth.
The one-second release requirement comes from the approved slicing plan.
"""
import math
STAGES=('rest','indentation','draw_down','stop','withdraw','release')
AUDITS=('contact','damage','energy','stability')


def evaluate(records):
    """Return the furthest justified stage and a scoped evidence verdict.

    Records are summaries, not authenticated runtime evidence. Even a successful
    synthetic input only demonstrates the evaluator's logic. Native validation
    requires independently verified trace/source provenance outside this module.
    """
    done=[];previous_end=None;episode=None
    def result(status,reason):
        return {'status':status,'reason':reason,'completed_stages':list(done),
                'next_stage':STAGES[len(done)] if len(done)<len(STAGES) else None,
                'native_runtime_validated':False}
    if not isinstance(records,list) or len(records)>len(STAGES):raise ValueError('Invalid stage records')
    for i,row in enumerate(records):
        if row.get('stage')!=STAGES[i]:raise ValueError('Stage skipped, repeated or out of order')
        if not isinstance(row.get('episode_id'),str) or not row['episode_id']:raise ValueError('Episode identity required')
        if episode is None:episode=row['episode_id']
        if row['episode_id']!=episode:raise ValueError('Episode histories cannot be spliced')
        start,end=row.get('start_s'),row.get('end_s')
        if any(type(t) not in (float,int) or not math.isfinite(t) or t<0 for t in (start,end)) or end<=start:
            raise ValueError('Finite positive stage interval required')
        if previous_end is not None and start!=previous_end:raise ValueError('Missing or overlapping stage history')
        previous_end=end
        status=row.get('outcome')
        if status=='timeout':return result('inconclusive','stage_timeout')
        if status=='failed':return result('review_required','stage_failed')
        if status!='completed':raise ValueError('Explicit stage outcome required')
        audits=row.get('audits',{})
        if set(audits)!=set(AUDITS):return result('inconclusive','missing_independent_audits')
        ids=[]
        for kind in AUDITS:
            a=audits[kind]
            if not isinstance(a,dict) or a.get('scope')!='native_mechanics' or not isinstance(a.get('evidence_id'),str) or not a['evidence_id']:
                return result('inconclusive','missing_audit_scope_or_identity')
            ids.append(a['evidence_id'])
            if a.get('outcome')=='failed':return result('review_required',kind+'_audit_failed')
            if a.get('outcome')!='passed':return result('inconclusive',kind+'_audit_inconclusive')
        if len(set(ids))!=len(AUDITS):return result('inconclusive','independent_audit_identities_required')
        if row['stage']=='release':
            t=row.get('topology',{})
            # Graph separation includes bulk/volume/cohesive links, not just D=1.
            if t.get('materially_disconnected') is not True or t.get('all_patches_failed') is not True:
                return result('partial_attached','material_connections_remain')
            if t.get('cross_bulk_couplings')!=0 or t.get('active_cohesive_patches')!=0 or t.get('components')!=2:
                return result('review_required','inconsistent_topology_summary')
            if row.get('blade_absent') is not True or row.get('fixture_bridges_interface') is not False:
                return result('detached_unverified','external_support_or_blade_not_cleared')
            if end-start<1.:return result('inconclusive','release_observation_shorter_than_one_second')
            if row.get('continuous_observation') is not True or row.get('independent_motion_verified') is not True or row.get('no_healing') is not True:
                return result('detached_unverified','release_motion_or_history_unverified')
        done.append(row['stage'])
    return result('release_evidence_candidate' if len(done)==len(STAGES) else 'in_progress',
                  'external_provenance_verification_required' if len(done)==len(STAGES) else 'awaiting_next_stage')
