"""Validate, freeze, then evaluate the image-only candidate on reserved cases."""
from pathlib import Path
import json,subprocess,sys,time
W=Path(__file__).resolve().parent
script='hybrid_pickup_v16.py';checkpoint=W/'policies/grasp_vision_v02_expanded/best.pt'
assert json.loads((W/'datasets/v15_index_search/train_medium_face180_00/result.json').read_text())['success'],'Physical correction must pass first'
image_report=W/'reports/vision_v02_expanded_validation.json';im=json.loads(image_report.read_text())
assert all(r['accepted'] for r in im['rows']) and max(r['position_error_mm'] for r in im['rows'])<2. and max(r['orientation_error_deg'] for r in im['rows'])<2.
manifest=json.loads((W/'generalization_curriculum_v01.json').read_text())
validation=[x['id'] for x in manifest['episodes'] if x['split']=='validation' and x['id'].endswith('_00')]
def run(phase,args):
 (W/'reports/camera_qualification_progress.json').write_text(json.dumps(dict(phase=phase,time=time.time())))
 print('START',phase,flush=True)
 with (W/'reports'/('camera_qualification_'+phase+'.log')).open('w') as log:
  subprocess.run([sys.executable,'-u',*args],cwd=W,stdout=log,stderr=subprocess.STDOUT,check=True)
 print('FINISHED',phase,flush=True)
base=['run_curriculum_v33.py','--script',script,'--checkpoint',str(checkpoint)]
run('validation',[*base,'--tag','v16_validation','--ids',*validation])
rows=json.loads((W/'datasets/v16_validation/results.json').read_text())
assert len(rows)==6 and all(r['success'] and not r['teacher'] for r in rows),'Inspect validation failures before consuming independent tests'
blank=W/'blank_image_override.json';blank.write_text(json.dumps(dict(vision_ablation='blank')))
run('blank',[*base,'--tag','v16_blank','--ids','train_short_face0_00','--override',str(blank)])
run('freeze',['freeze_candidate.py','--script',script,'--checkpoint',str(checkpoint),'--validation-tag','v16_validation','--image-report',str(image_report),'--ablation',str(W/'datasets/v16_blank/train_short_face0_00')])
test=[x['id'] for x in manifest['episodes'] if x['split']=='test']
run('test',[*base,'--tag','v16_independent_test','--ids',*test])
rows=json.loads((W/'datasets/v16_independent_test/results.json').read_text())
coverage={(r['family'],r['face']) for r in rows if r['success']}
expected={(x['family'],x['rest_roll_deg']) for x in manifest['episodes'] if x['split']=='test'}
passed=len(rows)==14 and sum(r['success'] for r in rows)>=12 and coverage==expected and not any(any(t in (r['failure'] or '') for t in ['Contact stop','Blade/']) for r in rows)
(W/'reports/independent_test_summary.json').write_text(json.dumps(dict(gate_passed=passed,completed=len(rows),successes=sum(r['success'] for r in rows),expected=14,all_family_face_coverage=coverage==expected,rows=rows),indent=2))
(W/'reports/camera_qualification_progress.json').write_text(json.dumps(dict(phase='finished',gate_passed=passed,time=time.time())))
print('INDEPENDENT GATE',passed,flush=True)
