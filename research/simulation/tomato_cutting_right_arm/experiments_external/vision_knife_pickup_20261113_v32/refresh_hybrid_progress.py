"""Publish saved hybrid outcomes without promoting untested scope."""
from pathlib import Path
import json,datetime,hashlib
W=Path(__file__).resolve().parent
rows=[]; active=[]
for folder in sorted((W/'datasets').glob('hybrid_v*')):
 progress=folder/'collection_progress.json'
 if progress.exists():
  current=json.loads(progress.read_text()).get('current')
  if current:active.append(str(folder.name+'/'+current))
 for p in sorted(folder.glob('*/visual_prediction.json')):
  ep=p.parent; result=json.loads((ep/'result.json').read_text()) if (ep/'result.json').exists() else {}
  failure=(ep/'failure.txt').read_text() if (ep/'failure.txt').exists() else None
  pred=json.loads(p.read_text());row=dict(dataset=folder.name,episode=ep.name,success=bool(result.get('success')),complete=bool(result or failure),vision_accepted=pred['accepted'],ablation=pred['vision_ablation'])
  if result:
   last=result['last'];row.update(hold_s=last['hold_s'],slip_m=last.get('slip_m'),min_tool_height_m=last['minimum_tool_height_m'],support_N=last['support_N'],maximum_contact_load_N=result['maximum_contact_load_N'],wall_s=result['wall_s'])
  if failure:row['failure']=failure.splitlines()[-1]
  rows.append(row)
validation=[r for r in rows if r['dataset']=='hybrid_v03_validation' and r['complete']]
tests=[r for r in rows if r['dataset']=='hybrid_v03_test' and r['complete']]
vs=sum(r['success'] for r in validation);ts=sum(r['success'] for r in tests)
summary=f'Balanced-grip controller v03, learned head-RGB-D grasp targeting plus engineered motion: {vs}/{len(validation)} completed validation pickups and {ts}/{len(tests)} independent test pickups passed. Real finger contact; no attachment. Short knife and bounded flat-rest placements only.'
now=datetime.datetime.now().astimezone().isoformat()
(W/'reports/hybrid_live_results.json').write_text(json.dumps(dict(updated=now,summary=summary,active=active,rows=rows),indent=2))
status=json.loads((W/'STATUS.json').read_text());status.update(updated_local=now,status='validating_hybrid_pickup' if active else 'hybrid_results_available',active_simulation=bool(active),latest_trial=active or (rows[-1]['episode'] if rows else None),latest_result=summary,learned_pickup_verified=bool(vs),learned_pickup_scope='Learned grasp target, engineered motion; bounded short-knife flat-rest curriculum only',hybrid_validation_passes=vs,hybrid_validation_attempts=len(validation),hybrid_test_passes=ts,hybrid_test_attempts=len(tests),pending_decision=None)
(W/'STATUS.json').write_text(json.dumps(status,indent=2))
p=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs/learning-roadmap.json');d=json.loads(p.read_text());s=next(x for x in d['stages'] if x['id']==10);s['phase']='Testing learned grasp selection with real contact pickup' if active else 'Learned grasp selection: see verified test results';s['items'][5].update(status='in_progress',evidence=summary+' Full image-to-joint students remain failed; full motion learning deferred by user.');d['updated']=now;d['latest_progress']['learning']=summary;tmp=p.with_suffix('.json.tmp');tmp.write_text(json.dumps(d,indent=2));tmp.replace(p)
preserved=json.loads((W/'preserved_sources.json').read_text());(W/'reports/hybrid_source_preservation.json').write_text(json.dumps({name:hashlib.sha256(Path(name).read_bytes()).hexdigest()==sha for name,sha in preserved.items()},indent=2));print(summary)
