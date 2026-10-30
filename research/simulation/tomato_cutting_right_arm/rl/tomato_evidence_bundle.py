"""Saved artifact integrity and release coverage, never runtime authentication.

Hashes bind bytes; they cannot turn fabricated/synthetic data into native physics
or prove independent algorithms. Runtime provenance needs external review.
"""
import copy
import json
import math
from tomato_native_launch_contract import owned_file,digest
from tomato_staged_evaluator import evaluate,AUDITS


def read_bound_json(root,ref):
    p=owned_file(root,ref['path'])
    if p.stat().st_size>4*1024**2:raise ValueError('Evidence file exceeds bounded reader')
    if digest(p)!=ref['sha256']:raise ValueError('Evidence hash mismatch')
    return json.loads(p.read_text())


def release_coverage(samples,*,episode_id,start_tick,end_tick,tick_s):
    if any(type(t)is not int or t<0 for t in (start_tick,end_tick)) or end_tick<=start_tick:
        raise ValueError('Positive integer release tick interval required')
    if type(tick_s) not in (int,float) or not math.isfinite(tick_s) or tick_s<=0:
        raise ValueError('Finite positive tick duration required')
    if not isinstance(samples,list) or len(samples)>20000 or len(samples)!=end_tick-start_tick:
        raise ValueError('Every release integration interval must be represented within bounded size')
    for tick,s in zip(range(start_tick,end_tick),samples):
        if s.get('episode_id')!=episode_id or type(s.get('tick'))is not int or s['tick']!=tick:
            raise ValueError('Release history skipped, duplicated or spliced')
        if s.get('finite_state') is not True:raise ValueError('Nonfinite/unknown release state')
    duration=(end_tick-start_tick)*tick_s
    if not math.isfinite(duration) or duration<1.:raise ValueError('At least one simulated second required')
    return {'coverage_verified':True,'duration_s':duration,'native_motion_validated':False}


def verify_bundle(root,bundle):
    """Verify trace/source/audit cross references then run the common evaluator.

    Output always retains native_runtime_validated=False. No self-issued receipt
    or input flag is accepted as authorization/runtime authenticity.
    """
    trace=read_bound_json(root,bundle['trace'])
    if trace.get('origin') not in ('native_recording','synthetic_fixture'):
        raise ValueError('Explicit trace origin required')
    episode=trace['episode_id'];run=trace['run_id']
    if not isinstance(episode,str) or not episode or not isinstance(run,str) or not run:raise ValueError('Run/episode identity required')
    sources=bundle.get('source_sha256',{})
    if not isinstance(sources,dict) or not sources:raise ValueError('Pinned source registry required')
    for path,h in sources.items():
        if digest(owned_file(root,path))!=h:raise ValueError('Source digest mismatch')
    rows=copy.deepcopy(trace['stages'])
    if not isinstance(rows,list) or len(rows)>6:raise ValueError('Bounded stage list required')
    refs=bundle.get('audit_refs',{})
    for row in rows:
        stage=row['stage']
        if row['episode_id']!=episode:raise ValueError('Trace episode mismatch')
        # Even timeout summaries require provenance, but need no passing verdict.
        if row['outcome']!='completed':continue
        stage_refs=refs.get(stage,{})
        if set(stage_refs)!=set(AUDITS):raise ValueError('Four bound audit outputs required per completed stage')
        row['audits']={}
        identities=[]
        for kind,ref in stage_refs.items():
            a=read_bound_json(root,ref)
            if a.get('kind')!=kind or a.get('stage')!=stage or a.get('run_id')!=run or a.get('episode_id')!=episode or a.get('trace_sha256')!=bundle['trace']['sha256']:
                raise ValueError('Audit does not match this exact trace/run/stage')
            source=a.get('auditor_source_path')
            if source not in sources or a.get('auditor_source_sha256')!=sources[source]:raise ValueError('Unpinned auditor source')
            identities.append((ref['path'],ref['sha256']))
            row['audits'][kind]={'scope':'native_mechanics','evidence_id':ref['sha256'],'outcome':a['outcome']}
        if len(set(identities))!=4:raise ValueError('Independent output identities required')
        if stage=='release':
            coverage=read_bound_json(root,bundle['release_samples'])
            if coverage.get('run_id')!=run:raise ValueError('Release run mismatch')
            result=release_coverage(coverage['samples'],episode_id=episode,
                start_tick=coverage['start_tick'],end_tick=coverage['end_tick'],tick_s=coverage['tick_s'])
            if row['start_s']!=coverage['start_tick']*coverage['tick_s'] or row['end_s']!=coverage['end_tick']*coverage['tick_s']:
                raise ValueError('Release sample coverage does not match stage interval')
            row['continuous_observation']=result['coverage_verified']
    verdict=evaluate(rows)
    return {'artifact_integrity_verified':True,'declared_origin':trace['origin'],
        'evaluation':verdict,'native_runtime_validated':False,
        'independent_algorithm_review_required':True,'runtime_provenance_review_required':True}
