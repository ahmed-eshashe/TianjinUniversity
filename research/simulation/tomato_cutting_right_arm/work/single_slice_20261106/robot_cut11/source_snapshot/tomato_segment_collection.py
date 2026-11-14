"""Read-only diagnostic collection; coupon intervals never become cut evidence."""
import hashlib
import math
from pathlib import Path
from tomato_journal_verify import reconcile,read_json


def collect(root,trajectory_path,*,identity_sha256,trajectory_sha256,tail_sha256=None):
    root=Path(root)
    trajectory,h=read_json(Path(trajectory_path))
    if h!=trajectory_sha256:raise ValueError('Trajectory anchor mismatch')
    dt=trajectory.get('dt_s');stages=trajectory.get('stages')
    if type(dt) not in (float,int) or not math.isfinite(dt) or dt<=0 or not isinstance(stages,list) or not stages:
        raise ValueError('Explicit finite trajectory cadence/stages required')
    bounds=[];cursor=0.;names=[]
    for row in stages:
        if not isinstance(row,list) or len(row)!=2:raise ValueError('Named duration pair required')
        name,duration=row
        if not isinstance(name,str) or not name or name in names or type(duration) not in (float,int) or not math.isfinite(duration) or duration<=0:
            raise ValueError('Unique stages with positive finite duration required')
        names.append(name);end=cursor+duration;bounds.append((name,cursor,end));cursor=end
    chain=reconcile(root,expected_identity_sha256=identity_sha256,expected_last_record_sha256=tail_sha256)
    result={'status':'inconclusive_diagnostic_only','journal':chain,'intervals':[],
        'evaluator_records':[],'native_runtime_validated':False,'work_ledger_admissible':False,
        'reason':'coupon_protocol_has_no_cut_draw_down_or_one_second_release_and_no_independent_audits',
        'files_modified':False,'trajectory_sha256':h}
    if chain['issue'] is not None:return result
    for step in range(chain['structurally_consistent_prefix_steps']):
        row,_=read_json(root/f'step{step:06d}.json');d=row['diagnostic']
        start=step*dt;end=(step+1)*dt
        if d.get('start_s')!=start or d.get('dt_s')!=dt or end>cursor:raise ValueError('Missing/overlapping/out-of-trajectory interval')
        m=d.get('endpoint_reaction_metadata',{})
        if any(m.get(k)!=d.get(k) for k in ('step','start_s','dt_s')) or m.get('temporal_semantics')!='end_of_step_force_not_step_average' or m.get('work_ledger_admissible') is not False:
            raise ValueError('Endpoint work semantics or metadata interval mismatch')
        # Preserve straddled stages; never relabel a boundary interval as a complete stage.
        touched=[name for name,a,b in bounds if start<b and end>a]
        result['intervals'].append({'step':step,'start_s':start,'end_s':end,'coupon_stages_touched':touched,
            'crosses_stage_boundary':len(touched)>1,'physical_audits_available':False})
    result['recorded_duration_s']=len(result['intervals'])*dt
    result['full_prescribed_trajectory_covered']=bool(result['intervals']) and result['intervals'][-1]['end_s']==cursor
    return result
