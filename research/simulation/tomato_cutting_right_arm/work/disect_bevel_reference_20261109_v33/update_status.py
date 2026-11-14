from pathlib import Path
import json,datetime,os
W=Path(__file__).resolve().parent;R=W.parents[1];O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');p=O/'disect-execution-checklist.json';d=json.loads(p.read_text());now=datetime.datetime.now(datetime.timezone.utc).isoformat()
d['updated']=now;d['current_work']={'eyebrow':'Section 4 · bounded corrected-reference pilot','title':'Testing a centered cutting-bevel reference','description':'Stronger-contact component controls and equivalent stable-arithmetic controls passed. A fresh settled-target pilot uses the finite bevel midpoint on the fixed initial-interface chart. Original material, 2 N / 0.1 mm stops and prescribed motion remain. No damage/separation pass yet.','href':'disect-section4-current.txt'};d['live']={'progress':'disect-v33-progress.json','result':'disect-v33-result.json','duration_s':.08,'kind':'contact','label':'Fresh centered-bevel loading pilot'};d['current_job_directory']=str(W);d['section4_execution'].update(running=True,last_stop=None,work_directory=str(W));d['stages'][3]['note']='Contact components passed; corrected fixed-reference shallow pilot underway. Genuine damage, refinement, withdrawal and all six full section milestones remain open.'
p.write_text(json.dumps(d,indent=2)+'\n')
for name,target in [('disect-v33-progress.json','centered0080_progress.json'),('disect-v33-result.json','centered0080_result.json')]:
 link=O/name
 if link.is_symlink():link.unlink()
 if not link.exists():link.symlink_to(W/target)
text='SECTION 4 — FRESH CENTERED-BEVEL PILOT\n\nThe prior run stopped numerically at 55.39375 ms, before failed-step history commit; no damage. Stable mathematically equivalent potential increments passed 143 high-precision controls and one-step/two-half-step replay checks, without changing force law or convergence tolerances. The legacy replay converged; the exact abort was not reproduced.\n\nThe old lowest-corner offset alone does not prove a blade miss; the full bevel contacts the interface. Static cut-node force-direction controls motivated a single geometry-derived reference correction: use the finite leading-bevel midpoint and freeze the path from the initial settled interface. No online controller, support fixture, model or safety-limit change. Fresh target start, no loaded-prefix reuse.\n\nPilot: 80 ms horizon, 3600 s sample-checked wall cap; stop on damage or physical/numerical stop. Original 47 fracture laws/energy budgets, fixed grip and 2 N / 0.1 mm stops retained. Actual-damage refinement and controlled withdrawal are still required. All six complete section milestones remain open. Speed deferred, experimental validation pending.\n\nEvidence: '+str(W)+'\n'
(O/'disect-section4-current.txt').write_text(text);(W/'RESULT_INTERIM.txt').write_text(text)
lines=[d['title'],'Updated: '+now,'']
for stage in d['stages']:
 lines.append(stage['title'])
 for item in stage['items']:lines.extend(['['+item['status']+'] '+item['task'],item.get('acceptance_or_limit','')])
 lines.append('')
(O/'disect-execution-checklist.txt').write_text('\n'.join(lines)+'\n')
road=R/'docs/rl/RESEARCH_ROADMAP_REVIEW_20261102.md'
with road.open('a') as f:f.write('\n\n### Stable arithmetic repair and corrected bevel reference — '+now+'\n\n'+text+'\n')
