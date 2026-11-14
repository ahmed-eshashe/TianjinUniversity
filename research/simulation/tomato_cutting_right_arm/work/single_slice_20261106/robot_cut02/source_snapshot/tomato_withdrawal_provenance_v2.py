"""Fail-closed provenance for a separate spectral withdrawal diagnostic."""
import hashlib,math
from pathlib import Path

ANCHOR_BACKEND='triangle_spectral_evolving_v1'
BACKEND='triangle_spectral_withdrawal_v1'

def validate_transition(old,new_hashes,depth):
    if not old.get('passed') or old.get('backend') not in (ANCHOR_BACKEND,BACKEND):raise ValueError('Unsupported or unaccepted predecessor')
    if not math.isfinite(depth) or not -.25000001<=depth-old['depth_mm']<=0:raise ValueError('Only nonpositive withdrawal steps <=0.25mm')
    if old['backend']==ANCHOR_BACKEND:
        if depth!=old['depth_mm']:raise ValueError('Source transition requires same-depth hold')
        if not all(new_hashes.get(n)==h for n,h in old['source_hashes'].items()):raise ValueError('Anchor source mismatch')
    elif old['source_hashes']!=new_hashes:raise ValueError('Withdrawal source mismatch')

def verify_files(root,folder,state):
    root,folder=Path(root),Path(folder)
    for base,mapping in [(root,state['source_hashes']),(folder,state['state_hashes'])]:
        for name,h in mapping.items():
            if hashlib.sha256((base/name).read_bytes()).hexdigest()!=h:raise ValueError('Saved source/state hash mismatch')

def unchanged_history(old,new):
    # A diagnostic acceptance condition; never clamps or freezes the damage law.
    return old['damage_states']==new['damage_states']

def withdrawal_anchor(folder,summary,digest):
    if summary['backend']==ANCHOR_BACKEND:
        return {'checkpoint':folder,'summary_sha256':digest,'energy_j':summary['energy_j'],'fracture_dissipation_j':summary['fracture_dissipation_j'],'cumulative_blade_work_j':summary['cumulative_blade_work_j']}
    if summary['backend']!=BACKEND:raise ValueError('Unsupported withdrawal anchor')
    return dict(summary['withdrawal_anchor'])


def warm_active_rows(live,multipliers):
    """Map full stored facet IDs into the solver's compressed live-row IDs."""
    if len(live)!=len(multipliers):raise ValueError('Contact indexing length mismatch')
    return [local for local,full in enumerate(i for i,flag in enumerate(live) if flag) if multipliers[full]>1e-9]
