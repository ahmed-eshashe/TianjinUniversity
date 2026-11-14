from pathlib import Path
import json,time,datetime
W=Path(__file__).resolve().parent;O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');last=None
phases={
'waiting_for_coarse_hold':('Full split-assembly settling test','settle_contact',1.,'settling'),
'settle_contact_refined':('Independent smaller-step settling test','settle_contact_refined',1.,'settling'),
'settling_qualification':('Comparing complete assembled holds',None,1.,'settling'),
'plan_indent':('Preparing original-CAD contact on the settled assembly',None,.045,'contact'),
'indent':('Nonfracturing blade load and horizontal withdrawal','indent',.045,'contact'),
'indent_refined':('Smaller-step blade load and horizontal withdrawal','indent_refined',.045,'contact'),
'compare_contact':('Comparing blade force and moment',None,.045,'contact'),
'physical_checks_complete_pending_review':('Physical checks complete · review pending',None,1.,'settling'),
'stopped_at_gate':('Physical qualification stopped at a failed check',None,1.,'settling')}
while True:
 try:
  state=json.loads((W/'qualification_progress.json').read_text());phase=state['phase']
  if phase!=last:
   d=json.loads((O/'disect-execution-checklist.json').read_text());title,name,duration,kind=phases[phase]
   d['current_work']['title']=title;d['current_work']['description']=state.get('reason','Speed deferred by user; physical thresholds unchanged. Results are not section-level passes until comparisons and review complete.')
   d['updated']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds');d['live']=None
   if name:
    for suffix in ['progress','result']:
     p=O/(name+'-live-'+suffix+'.json')
     if not p.is_symlink() and not p.exists():p.symlink_to(W/(name+'_'+suffix+'.json'))
    d['live']=dict(label=title,progress=name+'-live-progress.json',result=name+'-live-result.json',duration_s=duration,kind=kind)
   p=O/'disect-execution-checklist.tmp';p.write_text(json.dumps(d,indent=2));p.replace(O/'disect-execution-checklist.json');last=phase
   if phase in ['stopped_at_gate','physical_checks_complete_pending_review']:break
 except (FileNotFoundError,json.JSONDecodeError):pass
 time.sleep(3)
