"""Read-only diagnostic journal reconciliation, never native-state recovery."""
import ast
import hashlib
import json
import re
from pathlib import Path


def read_json(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size>4*1024**2:raise ValueError('Bounded nonsymlink journal file required')
    data=path.read_bytes()
    # JSON's permissive NaN/Infinity defaults are inappropriate for state evidence.
    value=json.loads(data,parse_constant=lambda value:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    return value,hashlib.sha256(data).hexdigest()


def reconcile(root,*,expected_identity_sha256,expected_last_record_sha256=None):
    root=Path(root)
    identity,identity_hash=read_json(root/'identity.json')
    if identity_hash!=expected_identity_sha256:raise ValueError('Externally bound identity mismatch')
    if set(identity)!=set(('run_id','episode_id','source_sha256')) or not identity['source_sha256']:raise ValueError('Complete journal identity required')
    files=sorted(root.glob('step*.json'))
    if len(files)>12:raise ValueError('Segment exceeds twelve-record cap')
    previous=None;hashes=[];issue=None
    for step,p in enumerate(files):
        if p.name!=f'step{step:06d}.json':issue='missing_or_misnamed_step';break
        try:
            row,h=read_json(p)
            if any(row.get(k)!=v for k,v in identity.items()):raise ValueError('Journal identity/source spliced')
            if row.get('previous_record_sha256')!=previous or row.get('diagnostic',{}).get('step')!=step or type(row.get('diagnostic',{}).get('step'))is not int:raise ValueError('Chain or step mismatch')
            if row.get('native_physics_pass') is not False:raise ValueError('Diagnostic journal cannot claim physics pass')
        except (ValueError,TypeError,KeyError,OSError,json.JSONDecodeError):issue='invalid_or_partial_record';break
        hashes.append(h);previous=h
    checkpoints=[]
    for p in sorted(root.glob('checkpoint*.json')):
        try:
            c,h=read_json(p);n=c['committed_steps']
            if type(n)is not int or not 0<=n<=len(hashes) or p.name!=f'checkpoint{n:06d}.json':raise ValueError('Invalid checkpoint extent')
            if any(c.get(k)!=v for k,v in identity.items()) or c.get('last_record_sha256')!=(hashes[n-1] if n else None):raise ValueError('Checkpoint source/chain mismatch')
            if c.get('native_state_registry_complete') is not False or c.get('restart_supported') is not False:raise ValueError('Unsupported restart/completeness claim')
            checkpoints.append({'path':p.name,'sha256':h,'committed_steps':n})
        except (ValueError,TypeError,KeyError,OSError,json.JSONDecodeError):issue=issue or 'invalid_or_partial_checkpoint'
    anchored=expected_last_record_sha256 is not None and expected_last_record_sha256==previous
    if expected_last_record_sha256 is not None and not anchored:issue=issue or 'external_tail_anchor_mismatch'
    return {'status':'diagnostic_prefix_only' if issue else 'diagnostic_chain_consistent',
            'structurally_consistent_prefix_steps':len(hashes),'last_record_sha256':previous,
            'external_tail_anchor_matches_prefix':anchored,'issue':issue,'checkpoints':checkpoints,
            'native_state_recovered':False,'resume_authorized':False,'files_modified':False}


def allocated_history_candidates(source_text):
    """Conservative AST inventory of self attributes directly allocated by Warp.

    Includes temporary arrays and misses aliases/conditional indirect state. It
    is a review lead, not a complete restart/reset registry.
    """
    candidates={}
    for node in ast.walk(ast.parse(source_text)):
        if not isinstance(node,(ast.Assign,ast.AnnAssign)):continue
        value=node.value
        if not isinstance(value,ast.Call) or not isinstance(value.func,ast.Attribute) or not isinstance(value.func.value,ast.Name) or value.func.value.id!='wp':continue
        if value.func.attr not in ('zeros','zeros_like','empty','empty_like','clone','array','full'):continue
        targets=node.targets if isinstance(node,ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target,ast.Attribute) and isinstance(target.value,ast.Name) and target.value.id=='self':
                candidates.setdefault(target.attr,[]).append({'line':node.lineno,'allocator':'wp.'+value.func.attr})
    return {'candidate_attributes':candidates,'registry_complete':False,'native_reset_validated':False}
