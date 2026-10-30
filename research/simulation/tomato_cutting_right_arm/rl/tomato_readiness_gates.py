"""Post-upgrade evidence sequence. No evaluation here authorizes execution."""
from tomato_evidence_bundle import read_bound_json
from tomato_native_launch_contract import owned_file,digest

GATES=('resources','native_startup','contact_coupons','damage_release_reset_convergence',
       'robot_coupling_and_frozen_grasp','baseline_and_throughput','learning_smoke')


def draft_manifest():
    return {'version':1,'execution_authorized':False,'training_authorized':False,
        'gates':[{'id':name,'status':'pending_runtime','evidence':None,
                  'prerequisites':list(GATES[:i])} for i,name in enumerate(GATES)],
        'full_training_separate_authorization_required':True}


def assess(root,manifest):
    """Check immutable references and dependency order, not review authenticity.

    Input reports can claim a native origin, but that alone is not proof. A
    successful reference chain still requires actual runtime provenance and
    independent physical review; all permission outputs remain false.
    """
    rows=manifest.get('gates')
    if not isinstance(rows,list) or [r.get('id') for r in rows]!=list(GATES):raise ValueError('Exact ordered post-upgrade gate registry required')
    candidates=[];blocked=[];seen=set()
    for i,row in enumerate(rows):
        name=row['id']
        if row.get('prerequisites')!=list(GATES[:i]):raise ValueError('Gate dependencies cannot be bypassed')
        if row.get('status')!='passed':blocked.append({'id':name,'reason':'runtime_evidence_pending'});continue
        if any(p not in candidates for p in GATES[:i]):blocked.append({'id':name,'reason':'earlier_gate_not_qualified'});continue
        ref=row.get('evidence')
        if not isinstance(ref,dict):raise ValueError('Bound report required')
        report=read_bound_json(root,ref)
        if ref['sha256'] in seen:raise ValueError('One report cannot stand in for distinct runtime gates')
        seen.add(ref['sha256'])
        if report.get('gate')!=name or report.get('outcome')!='passed' or report.get('evidence_class')!='runtime_measurement' or report.get('origin')!='native_recording':
            blocked.append({'id':name,'reason':'source_synthetic_or_unqualified_report'});continue
        run_id=report.get('run_id');sources=report.get('source_sha256');config=report.get('config_ref')
        if not isinstance(run_id,str) or not run_id or not isinstance(sources,dict) or not sources or not isinstance(config,dict):raise ValueError('Runtime run/source/config binding required')
        for path,h in sources.items():
            if digest(owned_file(root,path))!=h:raise ValueError('Runtime source changed')
        if digest(owned_file(root,config['path']))!=config['sha256']:raise ValueError('Runtime configuration changed')
        if report.get('independent_review_status') not in ('pending','externally_reviewed'):
            raise ValueError('Explicit independent review status required; authenticity remains external')
        candidates.append(name)
    return {'reference_consistent_runtime_candidates':candidates,'blocked':blocked,
        'next_runtime_gate':next((g for g in GATES if g not in candidates),None),
        'independent_review_and_actual_runtime_provenance_required':True,
        'native_execution_authorized':False,'training_authorized':False,
        'full_training_separate_authorization_required':True}
