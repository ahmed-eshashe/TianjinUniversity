"""Summarize bounded physical attempts without treating safe process exit as grasp success."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'docs/rl'
cases=[];resources=[]
for path in sorted((ROOT/'runs/rl/phase3').glob('central_grasp_[0-9][0-9]')):
    read=lambda name:json.loads((path/name).read_text()) if (path/name).exists() else None
    result=read('result.json');failure=read('failure.json');config=read('run_configuration.json');memory=read('memory_report.json')
    records=read('trajectory.json') or []
    post_reset=[s for s in records if s['control_step']>=30]
    initial=post_reset[0]['handle_height_m'] if post_reset else None
    max_lift=max((s['handle_height_m']-initial for s in post_reset),default=None)
    phase=result.get('phase') if result else failure.get('phase') if failure else None
    why=result.get('reason') if result else failure['traceback'].strip().splitlines()[-1] if failure else 'See simulation.log or startup refusal'
    case={'run':str(path.relative_to(ROOT)),'passed':bool(result and result.get('passed')),'phase':phase,'reason':why,
        'recorded_control_steps':len(records),'max_handle_lift_after_settling_m':max_lift,
        'final_board_support_n':post_reset[-1]['support_force_n'] if post_reset else None,
        'manual_stop':(path/'checkpoint_and_stop.request').exists(),
        'training':False,'memory':memory}
    if config:
        c=config['candidate'];case['configuration']={k:c[k] for k in ['roll_deg','finger_deg','thumb_pitch_deg','handle_in_hand_m']}
        case['reset']=config['reset']
    if failure and failure.get('substep_event'):
        event=failure['substep_event'];case['substep_stop_contacts']=event.get('contacts',[])
    cases.append(case)
    if memory:resources.append(memory)
audit=json.loads((DOC/'phase1_inventory.json').read_text())
preservation={'original_robot_unchanged':hashlib.sha256(Path(audit['source']).read_bytes()).hexdigest()==audit['source_sha256'],
 'accepted_demonstrations_unchanged':all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==v for p,v in audit['baseline_sha256'].items())}
criteria_hash=hashlib.sha256((DOC/'phase3_grasp_criteria.json').read_bytes()).hexdigest()
old=json.loads((DOC/'phase3_summary.json').read_text())
preservation['frozen_grasp_criteria_unchanged']=criteria_hash==old['criteria_sha256']
summary={'date_local':'2026-10-19','task':'Firm physical pickup from a flat central knife placement',
 'firm_central_grasp_passed':any(x['passed'] for x in cases),'phase3_complete':False,'training_ready':False,
 'full_training_started':False,'controller':'scripted diagnostic, not a learned policy','vision_based':False,
 'initial_knife':'Existing kitchen knife; full footprint on board; centred flat resets; no edge-overhang setup',
 'attachments_created':False,'knife_teleports_during_episode':0,'self_collision_disabled_to_obtain_pass':False,
 'criteria_sha256':criteria_hash,'preservation':preservation,'cases':cases,
 'memory':{'startup_reserve_refused_once':True,'user_freed_memory_before_retry':True,
   'thresholds_weakened':False,'midrun_memory_warnings':sum(bool(x['warning_requested']) for x in resources),
   'peak_process_ram_gb':max(x['peak_rss_gb'] for x in resources),
   'min_available_ram_gb':min(x['min_available_ram_gb'] for x in resources),
   'peak_total_gpu_used_mib':max(x['peak_gpu_used_mib'] for x in resources)},
 'diagnostic_fixes':['Strict reporting of failed physical outcomes','JSON serialization of nonempty-contact enclosure flag',
   'Pad-facing approach screen and positive closing-load check','Contact safety checks at physics substeps',
   'Preserve individual finger targets when subsequently closing thumb'],
 'remaining_work':['Controlled in-place knife tilt/reposition before final wrap, or another validated acquisition strategy',
    'Validate/refine palm-thumb mechanical collision geometry over the intended joint range',
    'Physical positive wrap, unsupported 5 cm lift, continuous 3 s hold and visual validation']}
assert all(preservation.values())
(DOC/'central_grasp_results.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k in ['firm_central_grasp_passed','memory','preservation']},indent=2))
