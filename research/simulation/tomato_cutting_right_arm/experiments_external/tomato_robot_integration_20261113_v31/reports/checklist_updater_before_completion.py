from pathlib import Path
import json,shutil,re,datetime
W=Path(__file__).resolve().parent;O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');backup=W/'reports/checklist_before';backup.mkdir(exist_ok=True)
for name in ['learning-roadmap.html','isaac-sim-progress.html','disect-checklist.html','learning-roadmap.json','approximate-training-status.json']:
 if not(backup/name).exists():shutil.copy2(O/name,backup/name)
status={'status':'native_contact_testing','dry_route_passed':True,'mounted_cut_passed':False,'existing_sources_unchanged':True,'original_handle_and_grip':True,'visible_tested_straight_blade':True,'fixed_mount':True,'retracting_pickup_cradle':True,'scripted':True,'policy_trained':False,'real_tomato_validation':'pending','report':str(W/'reports/native_checks_progress.json')}
p=O/'approximate-training-status.json';d=json.loads(p.read_text());d['robot_integration']=status;p.write_text(json.dumps(d,indent=2))
p=O/'learning-roadmap.json';d=json.loads(p.read_text());stage=next(s for s in d['stages']if s['id']==9);stage['items']=[x for x in stage['items']if x['id']!='9.9'];stage['items'].append({'id':'9.9','text':'Integrate the approximate tomato with the original robot, kitchen and fixed grip in a separate version.','status':'in_progress','evidence':'Actual dry route passed; original handle retained with a visible straight blade. Empty cradle retracts after pickup. Coupled contact and cutting tests are in progress.'});d.setdefault('approximate_training',{})['robot_integration']=status;p.write_text(json.dumps(d,indent=2))
paragraph='<p id="v31-status"><strong>Robot integration in progress:</strong> original kitchen, robot and handle grip retained in a separate version, with the tested straight blade visibly fitted. Full dry route and horizontal withdrawal passed. Contact feedback and cutting tests are running. Original research files remain unchanged.</p>'
for name in ['learning-roadmap.html','isaac-sim-progress.html','disect-checklist.html']:
 p=O/name;s=p.read_text();s=re.sub(r'<p id="v31-status">.*?</p>','',s,flags=re.S);a=s.index('<section id="v28-live"');b=s.index('</section>',a);s=s[:b]+paragraph+s[b:];p.write_text(s)
print('Checklist updated with verified dry-route pass; coupled cut still pending.')
