from pathlib import Path
import json,datetime,hashlib,subprocess
W=Path(__file__).resolve().parent
version=json.loads((W/'CURRENT_CANDIDATE.json').read_text())['version']
results=[];active=[]
process_lines=subprocess.check_output(['ps','-eo','args'],text=True).splitlines()
for folder in sorted((W/'datasets').glob('hybrid_'+version+'*')):
 if (folder/'collection_progress.json').exists():
  current=json.loads((folder/'collection_progress.json').read_text()).get('current')
  if current and any(str(folder/current) in line and ('hybrid_pickup_'+version+'.py') in line for line in process_lines):active.append(folder.name+'/'+current)
 for ep in sorted(p for p in folder.iterdir() if p.is_dir()):
  r=json.loads((ep/'result.json').read_text()) if (ep/'result.json').exists() else {};fail=(ep/'failure.txt').read_text() if (ep/'failure.txt').exists() else ''
  if not (r or fail):
   if any(str(ep) in line and ('hybrid_pickup_'+version+'.py') in line for line in process_lines):active.append(folder.name+'/'+ep.name)
   continue
  row=dict(dataset=folder.name,id=ep.name,success=bool(r.get('success')))
  if r:row.update(hold_s=r['last']['hold_s'],slip_m=r['last'].get('slip_m'),min_height_m=r['last']['minimum_tool_height_m'],support_N=r['last']['support_N'],max_contact_load_N=r['maximum_contact_load_N'],wall_s=r['wall_s'])
  if fail:row['failure']=fail.splitlines()[-1]
  results.append(row)
counts={}
for name in ['development','regression','validation','test']:
 rows=[x for x in results if x['dataset']=='hybrid_'+version+'_'+name];counts[name]={'successes':sum(x['success'] for x in rows),'attempted':len(rows)}
v=counts['validation'];t=counts['test'];reg=counts['regression'];summary=f"Contact-guided closure {version}: {reg['successes']}/{reg['attempted']} regression cases, {v['successes']}/{v['attempted']} validation pickups and {t['successes']}/{t['attempted']} fresh test pickups passed. Learned visual grasp selection, engineered motion, real finger contact and no attachment. Prior v03 gate failed (2/4 original test attempts)."
active=list(dict.fromkeys(active))
now=datetime.datetime.now().astimezone().isoformat();report=dict(updated=now,summary=summary,counts=counts,active=active,rows=results);(W/('reports/hybrid_'+version+'_progress.json')).write_text(json.dumps(report,indent=2))
status=json.loads((W/'STATUS.json').read_text());status.update(updated_local=now,status='validating_contact_guided_pickup' if active else 'contact_guided_pickup_results_available',active_simulation=bool(active),latest_trial=active or (results[-1]['id'] if results else None),latest_result=summary,current_candidate='hybrid_pickup_'+version+'.py',generalization_qualified=False,hybrid_validation_passes=v['successes'],hybrid_validation_attempts=v['attempted'],hybrid_test_passes=t['successes'],hybrid_test_attempts=t['attempted']);(W/'STATUS.json').write_text(json.dumps(status,indent=2))
p=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs/learning-roadmap.json');d=json.loads(p.read_text());s=next(x for x in d['stages'] if x['id']==10);s['phase']='Checking contact-guided closure across new placements';s['items'][5].update(status='in_progress',evidence=summary);d['updated']=now;d['latest_progress']['learning']=summary;tmp=p.with_suffix('.json.tmp');tmp.write_text(json.dumps(d,indent=2));tmp.replace(p);print(summary)
