"""Gate image-driven validation before freezing and consuming independent tests."""
from pathlib import Path
import argparse,json,subprocess,sys,time
W=Path(__file__).resolve().parent
a=argparse.ArgumentParser();a.add_argument('--script',required=True);a.add_argument('--checkpoint',type=Path,required=True);a.add_argument('--image-report',type=Path,required=True);a.add_argument('--teacher-proof',type=Path,required=True);a.add_argument('--tag',required=True);a.add_argument('--override',type=Path);args=a.parse_args()
assert json.loads(args.teacher_proof.read_text())['success'],'Physical correction must pass first'
im=json.loads(args.image_report.read_text());assert len(im['rows'])==12 and all(r['accepted'] for r in im['rows']) and max(r['position_error_mm'] for r in im['rows'])<2. and max(r['orientation_error_deg'] for r in im['rows'])<2.
manifest=json.loads((W/'generalization_curriculum_v01.json').read_text());validation=[x['id'] for x in manifest['episodes'] if x['split']=='validation' and x['id'].endswith('_00')];validation.sort(key=lambda x:x!='validation_medium_face180_00')
progress=W/'reports'/(args.tag+'_qualification_progress.json')
def run(phase,command):
 progress.write_text(json.dumps(dict(phase=phase,time=time.time(),script=args.script,checkpoint=str(args.checkpoint))))
 print('START',phase,flush=True)
 with (W/'reports'/(args.tag+'_'+phase+'.log')).open('w') as log:subprocess.run([sys.executable,'-u',*command],cwd=W,stdout=log,stderr=subprocess.STDOUT,check=True)
 print('FINISHED',phase,flush=True)
base=['run_curriculum_v33.py','--script',args.script,'--checkpoint',str(args.checkpoint.resolve())]
if args.override:base+=['--override',str(args.override.resolve())]
run('validation',[*base,'--tag',args.tag+'_validation','--ids',*validation])
rows=json.loads((W/'datasets'/(args.tag+'_validation')/'results.json').read_text());passed=len(rows)==6 and all(r['success'] and not r['teacher'] for r in rows)
if not passed:
 progress.write_text(json.dumps(dict(phase='validation_needs_review',rows=rows,time=time.time()),indent=2));print('Validation needs review. Independent tests remain unseen.',flush=True);sys.exit(2)
blank=W/(args.tag+'_blank_override.json');blank.write_text(json.dumps({**(json.loads(args.override.read_text()) if args.override else {}),'vision_ablation':'blank'}))
run('blank',[*base,'--tag',args.tag+'_blank','--ids','train_short_face0_00','--override',str(blank)])
run('freeze',['freeze_candidate.py','--script',args.script,'--checkpoint',str(args.checkpoint.resolve()),'--validation-tag',args.tag+'_validation','--image-report',str(args.image_report.resolve()),'--ablation',str(W/'datasets'/(args.tag+'_blank')/'train_short_face0_00'),*(['--override',str(args.override.resolve())] if args.override else [])])
test=[x['id'] for x in manifest['episodes'] if x['split']=='test']
run('test',[*base,'--tag',args.tag+'_independent_test','--ids',*test])
rows=json.loads((W/'datasets'/(args.tag+'_independent_test')/'results.json').read_text());coverage={(r['family'],r['face']) for r in rows if r['success']};expected={(x['family'],x['rest_roll_deg']) for x in manifest['episodes'] if x['split']=='test'}
passed=len(rows)==14 and sum(r['success'] for r in rows)>=12 and coverage==expected and not any(any(t in (r['failure'] or '') for t in ['Contact stop','Blade/']) for r in rows)
(W/'reports'/(args.tag+'_independent_test_summary.json')).write_text(json.dumps(dict(gate_passed=passed,completed=len(rows),successes=sum(r['success'] for r in rows),expected=14,all_family_face_coverage=coverage==expected,rows=rows),indent=2));progress.write_text(json.dumps(dict(phase='finished',gate_passed=passed,time=time.time())));print('INDEPENDENT GATE',passed,flush=True)
