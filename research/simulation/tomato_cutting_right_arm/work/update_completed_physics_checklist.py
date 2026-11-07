from pathlib import Path
import json
O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');p=O/'isaac-sim-progress-checklist.json';d=json.loads(p.read_text());evidence='physics-materials-integration-20261101.txt'
updates={
12:dict(status='done',progress='Authored-blade contact passes on the full tomato mesh, including force transfer, exact replay and clearing. Longer cuts remain unqualified.',checks=['PASS — original blade geometry and finite-surface coverage','PASS — generated contact forces and exact replay']),
15:dict(status='done',progress='Full tomato force feedback passes with a moving probe and the authored blade. Momentum, state feedback and reset/replay checks pass.',checks=['PASS — full-mesh two-way force exchange','PASS — linear/angular balance and exact replay']),
16:dict(status='done',progress='All 47 material patches pass controlled loading on the full mesh. Supported scope: a fixed material frame and tensile loading.',checks=['PASS — native force, stiffness and damage history','PASS — loading work and bulk-volume protection','LIMIT — general compression/shear and free-fragment closure remain unqualified']),
17:dict(status='open',progress='Pending at your request. The published curve is a provisional reference; independent measurements are still needed.',checks=['PENDING — independent experimental measurements'],evidence='tomato-experiment-data-needed-20261101.txt'),
18:dict(status='done',progress='Small interface and solid coupons pass damage, separation, reclosure and replay. Whole-fruit post-cut behavior remains unqualified.',checks=['PASS — fracture budget and irreversible failure','PASS — small-coupon reclosure and reset/replay'])}
for item in d['items']:
 if item['id'] in updates:item.update(dict(evidence=evidence,**updates[item['id']]) if 'evidence' not in updates[item['id']] else updates[item['id']])
 if item['id']==19:item['progress']='Next: load and check the robot and cutting scene using the tested physics components.'
d['updated']='2026-11-01';d['current_next_step']=19;d['experimental_validation_user_decision']='Keep experimental validation pending — 2026-11-01';d['counts']={s:sum(i['status']==s for i in d['items']) for s in ['done','open','todo']};p.write_text(json.dumps(d,indent=2)+'\n')
(O/'isaac-sim-progress-checklist.txt').write_text('Updated 1 November 2026. Completed checks apply to their stated fixtures. Counts are milestones, not time estimates.\n\n'+''.join(f"{i['id']:02} [{i['status'].upper()}] {i['title']}\n"+(i['progress']+'\n' if i.get('progress') else '') for i in d['items'])+'\nNumerical integration evidence: '+evidence+'\nExperimental validation is pending at the user\'s request.\n')
print(d['counts'])
