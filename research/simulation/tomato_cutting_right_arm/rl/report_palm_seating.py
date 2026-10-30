"""Report bounded seating diagnostics without conflating clearance with a final grasp."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DOC=ROOT/'docs/rl'
def read(p):return json.loads(p.read_text()) if p.exists() else None
cases=[]
for run in sorted((ROOT/'runs/rl/phase3').glob('palm_seating_[0-9][0-9]')):
 r=read(run/'trajectory.json') or [];samples=[s for s in r if s['control_step']>=30];initial=samples[0]['handle_height_m'] if samples else 0.
 cfg=read(run/'run_configuration.json') or {};failure=read(run/'failure.json') or {};event=failure.get('substep_event') or {}
 cases.append({'run':str(run.relative_to(ROOT)),'mode':cfg.get('seating_mode'),'result':read(run/'result.json'),
  'memory':read(run/'memory_report.json'),'max_handle_rise_m':max((s['handle_height_m']-initial for s in samples),default=None),
  'palm_handle_contact_seen':any(any(c['part']=='palm' and c['on_handle'] for c in s['contacts']) for s in samples),
  'max_oracle_wrapping_fingers':max((len(s.get('metric',{}).get('fingers',[])) for s in samples),default=0),
  'max_final_oracle_hold_s':max((s.get('metric',{}).get('hold_s',0.) for s in samples),default=0.),
  'max_stop_contact_n':max((c['force_n'] for c in event.get('contacts',[])),default=0.),
  'substep_event':event,'latest_seating_progress':read(run/'seating_progress.json'),'hand_frame_audit':read(run/'hand_frame_audit.json')})
audit=read(DOC/'phase1_inventory.json');criteria=hashlib.sha256((DOC/'phase3_grasp_criteria.json').read_bytes()).hexdigest()
preservation={'source_robot_unchanged':hashlib.sha256(Path(audit['source']).read_bytes()).hexdigest()==audit['source_sha256'],
 'accepted_baselines_unchanged':all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==v for p,v in audit['baseline_sha256'].items()),
 'frozen_criteria_unchanged':criteria==read(DOC/'phase3_summary.json')['criteria_sha256']}
assert all(preservation.values())
mem=[c['memory'] for c in cases if c['memory']]
summary={'date_local':'2026-10-19','controller':'Scripted native physical diagnostic; no trained policy or camera perception',
 'firm_grasp_passed':any(c['result'] and c['result'].get('passed') for c in cases),'phase3_complete':False,
 'full_training_started':False,'attachments_created':False,'knife_pose_commands_during_episode':0,
 'criteria_sha256':criteria,'preservation':preservation,'cases':cases,
 'memory':{'reserves_weakened':False,'warnings':sum(m['warning_requested'] for m in mem),
 'peak_process_ram_gb':max((m['peak_rss_gb'] for m in mem),default=0),
 'min_available_ram_gb':min((m['min_available_ram_gb'] for m in mem),default=0),
 'peak_total_gpu_mib':max((m['peak_gpu_used_mib'] for m in mem),default=0)}}
(DOC/'palm_seating_results.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({k:summary[k] for k in ['firm_grasp_passed','memory','preservation']},indent=2))
for c in cases:print(c['run'],c['max_handle_rise_m'],c['result'])
