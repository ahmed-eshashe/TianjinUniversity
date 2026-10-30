"""Summarize measured contact-only reposition tests, including rejected attempts."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'docs/rl'
read=lambda p:json.loads(p.read_text()) if p.exists() else None
cases=[]
for run in sorted((ROOT/'runs/rl/phase3').glob('in_place_tilt_[0-9][0-9]')):
    result=read(run/'result.json');cfg=read(run/'run_configuration.json')
    trajectory=read(run/'trajectory.json') or []
    samples=[x for x in trajectory if x['control_step']>=30]
    failure=read(run/'failure.json') or {}
    stopped=(failure.get('substep_event') or {}).get('contacts',[])
    initial=samples[0]['handle_height_m'] if samples else 0.
    cases.append({'run':str(run.relative_to(ROOT)),'result':result,
        'mode':cfg.get('in_place_tilt') if cfg else None,
        'candidate':cfg.get('candidate') if cfg else None,
        'memory':read(run/'memory_report.json'),
        'max_handle_rise_m':max((s['handle_height_m']-initial for s in samples),default=None),
        'last_handle_rise_m':samples[-1]['handle_height_m']-initial if samples else None,
        'max_measured_rotation_deg':max((s['in_place_motion']['rotation_deg'] for s in samples if 'in_place_motion' in s),default=None),
        'max_measured_centre_shift_m':max((s['in_place_motion']['centre_xy_shift_m'] for s in samples if 'in_place_motion' in s),default=None),
        'min_measured_footprint_margin_m':min((s['in_place_motion']['footprint_margin_m'] for s in samples if 'in_place_motion' in s),default=None),
        'tilt_control_samples':sum(s['phase']=='supported_in_place_tilt' for s in samples),
        'stop_contacts_above_limit':[x for x in stopped if x['force_n']>(10 if '/right_rh_' in x['body'] and x['other'].endswith(('Board','10')) else 50)],
        'motion_limit_event':read(run/'motion_limit_event.json')})
audit=read(DOC/'phase1_inventory.json')
preservation={'source_robot_unchanged':hashlib.sha256(Path(audit['source']).read_bytes()).hexdigest()==audit['source_sha256'],
    'accepted_baselines_unchanged':all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in audit['baseline_sha256'].items()),
    'frozen_criteria_unchanged':hashlib.sha256((DOC/'phase3_grasp_criteria.json').read_bytes()).hexdigest()==read(DOC/'phase3_summary.json')['criteria_sha256']}
assert all(preservation.values())
memory=[c['memory'] for c in cases if c['memory']]
summary={'date_local':'2026-10-19','controller':'Scripted contact-only native physical feasibility diagnostic; no vision policy',
    'firm_grasp_passed':any(c['result'] and c['result'].get('passed') for c in cases),
    'phase3_complete':False,'full_training_started':False,'attachment_created':False,'in_episode_knife_pose_commands':0,
    'command_limits':{'pitch_deg':8,'roll_deg':12,'latest_hand_preclearance_m':.003},
    'measured_limits':{'whole_knife_footprint_margin_m':.005,'centre_translation_m':.03,'rotation_deg':20},
    'preservation':preservation,'cases':cases,
    'memory':{'thresholds_weakened':False,'midrun_memory_warnings':sum(m['warning_requested'] for m in memory),
        'peak_process_ram_gb':max((m['peak_rss_gb'] for m in memory),default=0),
        'min_available_ram_gb':min((m['min_available_ram_gb'] for m in memory),default=0),
        'peak_total_gpu_used_mib':max((m['peak_gpu_used_mib'] for m in memory),default=0)}}
(DOC/'in_place_tilt_results.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({k:summary[k] for k in ['firm_grasp_passed','preservation','memory']},indent=2))
for c in cases:print(c['run'],c['result'],c['max_handle_rise_m'])
