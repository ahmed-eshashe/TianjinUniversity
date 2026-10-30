"""Summarize physical contact-seating diagnostics without treating supported tilt as pickup."""
import hashlib,json,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DOC=ROOT/'docs/rl'
def read(p):return json.loads(p.read_text()) if p.exists() else None
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prefix',default='contact_seating');parser.add_argument('--stem',default='contact_seating');args=parser.parse_args()
cases=[]
for run in sorted((ROOT/'runs/rl/phase3').glob(args.prefix+'_[0-9][0-9]')):
 result=read(run/'result.json')
 if result is None:continue
 samples=read(run/'trajectory.json') or [];seating=[s for s in samples if s['phase']=='contact_preserving_seating']
 digit_stats={}
 for part in ['middle','ring','pinky']:
  forces=[sum(c['force_n'] for c in s['contacts'] if c['part']==part and c['on_handle']) for s in seating];streak=longest=0
  for f in forces:
   streak=streak+1 if f>.3 else 0;longest=max(longest,streak)
  digit_stats[part]={'peak_normal_force_n':max(forces,default=0),'longest_contact_over_0_3n_s':longest*.05}
 progress=read(run/'seating_progress.json');stop=read(run/'contact_path_tracking_stop.json')
 cases.append({'run':str(run.relative_to(ROOT)),'result':result,'memory':read(run/'memory_report.json'),
 'provisional_contact_patch':(read(run/'run_configuration.json') or {}).get('provisional_contact_patch'),
 'completed_seating_fraction':progress.get('fraction') if progress else None,'rolling_progress':({k:v for k,v in read(run/'rolling_progress.json').items() if k!='sample'} if read(run/'rolling_progress.json') else None),
 'seating_samples':len(seating),'new_digit_contacts':digit_stats,'tracking_stop':stop.get('contact_path_tracking') if stop else None,
 'palm_contact_seen':any(any(c['part']=='palm' and c['on_handle'] for c in s['contacts']) for s in samples),
 'max_oracle_wrapping_fingers':max((len(s.get('metric',{}).get('fingers',[])) for s in samples),default=0),
 'max_unsupported_hold_s':max((s.get('metric',{}).get('hold_s',0) for s in samples),default=0),
 'lift_phase_reached':any(s['phase']=='lift' for s in samples),
 'substep_trace_saved':(run/'seating_substeps.json').exists()})
audit=read(DOC/'phase1_inventory.json');criteria=hashlib.sha256((DOC/'phase3_grasp_criteria.json').read_bytes()).hexdigest()
preservation={'source_robot_unchanged':hashlib.sha256(Path(audit['source']).read_bytes()).hexdigest()==audit['source_sha256'],
 'accepted_baselines_unchanged':all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==v for p,v in audit['baseline_sha256'].items()),
 'frozen_criteria_unchanged':criteria==read(DOC/'phase3_summary.json')['criteria_sha256']}
assert all(preservation.values())
mem=[c['memory'] for c in cases if c['memory']]
out={'controller':'Scripted native contact-only diagnostic; no vision policy or task training',
 'firm_grasp_passed':any(c['result'].get('passed') for c in cases),'phase3_complete':False,'full_training_started':False,
 'attachments_created':False,'knife_pose_commands_during_episode':0,
 'startup_refusals':[{'run':str(p.parent.relative_to(ROOT)),**read(p)} for p in sorted((ROOT/'runs/rl/phase3').glob(args.prefix+'_[0-9][0-9]/startup_refusal.json'))],'preservation':preservation,'cases':cases,
 'memory':{'reserves_weakened':False,'warnings':sum(m['warning_requested'] for m in mem),
 'peak_process_ram_gb':max((m['peak_rss_gb'] for m in mem),default=0),
 'min_available_ram_gb':min((m['min_available_ram_gb'] for m in mem),default=0),
 'peak_total_gpu_mib':max((m['peak_gpu_used_mib'] for m in mem),default=0)}}
(DOC/(args.stem+'_results.json')).write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
