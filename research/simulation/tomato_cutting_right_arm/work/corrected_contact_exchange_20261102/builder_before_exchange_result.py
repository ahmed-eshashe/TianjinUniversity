from pathlib import Path
import json,html
out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
data=json.loads((out/'isaac-sim-progress-checklist.json').read_text())
groups=[('Computer & startup',1,4,'Isaac Sim launches and the isolated rest checks pass.'),('Contact diagnostics',5,10,'Completed checks cover specific fixtures, not full cutting readiness.'),('Blade contact',11,12,'Contact generation and transfer pass for the current short diagnostics. Full-cut checks are later milestones.'),('Physics & materials',13,18,'Verify forces, coupling and separation.'),('Robot & scene',19,22,'Check placement, motion and reliable resets.'),('First controlled cut',23,26,'Establish a stable, repeatable single-blade baseline.'),('Dual-arm extension',27,29,'Add coordinated support and cutting.'),('Learning & experiments',30,32,'Later: validate the environment before longer training.')]
sections=[]
for index,(title,start,end,subtitle) in enumerate(groups,1):
 items=[x for x in data['items'] if start<=x['id']<=end]
 done=sum(x['status']=='done' for x in items); issue=any(x['status']=='open' for x in items)
 label=f'{done}/{len(items)} done' if not issue else f'{done} done · {sum(x["status"]=="open" for x in items)} pending'
 rows=[]
 for item in items:
  status=item['status']; icon={'done':'✓','open':'!','todo':'○'}[status]
  extra=f'<small>{html.escape(item.get("progress", ""))}</small>' if item['id']==data.get('current_next_step') or 13<=item['id']<=32 else ''
  extra+=''.join('<small>'+html.escape(c)+'</small>' for c in item.get('checks',[]))
  if item['id']==11: extra='<small>Complete · Six native fixtures pass with separate references. Historical combined comparison failure preserved.</small>'
  if item['id']==12: extra='<small>'+html.escape(item.get('progress',''))+'</small>'+''.join('<small>'+html.escape(c)+'</small>' for c in item.get('checks',[]))
  rows.append(f'<li class="{status}"><span class="mark" aria-label="{status}">{icon}</span><div><span class="number">{item["id"]:02}</span> {html.escape(item["title"])}{extra}</div></li>')
 sections.append(f'''<details class="stage {'active' if issue else ''}" {'open' if issue or start in (13,19) or start<=data.get('current_next_step',0)<=end else ''}>
 <summary><span class="stage-no">{index:02}</span><span class="stage-title">{html.escape(title)}<small>{html.escape(label)}</small></span><span class="chevron" aria-hidden="true">⌄</span></summary>
 <div class="stage-track"><span style="width:{done/len(items)*100}%"></span></div>
 <div class="stage-body"><p>{subtitle}</p><ul>{''.join(rows)}</ul></div></details>''')
checkpoints=data.get('integration_checkpoints',[])
checkpoint_cards=[]
for point in checkpoints:
 status=point['status'];icon={'done':'✓','open':'…','todo':'○'}[status]
 checkpoint_cards.append(f'<div class="checkpoint {status}" role="listitem"><span class="checkpoint-icon" aria-label="{status}">{icon}</span><div><strong>{html.escape(point["title"])}</strong><small>{html.escape(point["detail"])}</small></div></div>')
verified=sum(p['status']=='done' for p in checkpoints)
integration_html=f'<details class="integration" open><summary><span class="stage-title">Integration checks<small>{verified} component checks verified · full cutting remains unqualified</small></span><span class="chevron" aria-hidden="true">⌄</span></summary><div class="checkpoint-grid" role="list">'+''.join(checkpoint_cards)+'</div><p class="checkpoint-caption">These are parts of the open milestones below.</p></details>' if checkpoints else ''
page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cutting project · Progress</title>
<style>
:root{color-scheme:light dark;--bg:light-dark(#f5f6f8,#12151c);--panel:light-dark(#fff,#1b202b);--text:light-dark(#192132,#edf0f7);--muted:light-dark(#586377,#a9b3c6);--line:light-dark(#e2e6ed,#323b4c);--green:light-dark(#13744d,#68d8a1);--amber:light-dark(#8d5705,#f6c36d);--soft:light-dark(#edf7f1,#1e332b);--warm:light-dark(#fff7e7,#352d1f);--blue:light-dark(#335fa3,#8fb5fa)}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 system-ui,sans-serif}main{max-width:760px;margin:auto;padding:28px 20px 40px}.eyebrow{font-size:11px;font-weight:650;letter-spacing:1.8px;color:var(--muted);text-transform:uppercase}h1{font-size:29px;line-height:1.2;margin:8px 0}header p{color:var(--muted);margin:0 0 22px}.counts{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.stat{background:var(--panel);padding:14px;border-radius:12px}.stat b{display:block;font-size:30px;line-height:1.2}.stat span{font-size:12px;color:var(--muted)}.stat.done b{color:var(--green)}.stat.open b{color:var(--amber)}.overall{height:7px;background:var(--line);border-radius:8px;overflow:hidden;display:flex;margin-top:16px}.overall span:first-child{width:31.25%;background:var(--green)}.overall span:last-child{width:6.25%;background:var(--amber)}.caption{font-size:12px;color:var(--muted);margin:8px 0 20px}.focus{background:var(--warm);border-left:3px solid var(--amber);padding:15px 17px;border-radius:0 10px 10px 0;margin-bottom:24px}.focus h2{font-size:16px;margin:3px 0}.focus p{margin:4px 0 0;color:var(--muted);font-size:13px}.toolbar{display:flex;gap:8px;align-items:center;justify-content:space-between;margin-bottom:10px}.toolbar h2{font-size:16px;margin:0}button{font:inherit;font-size:12px;color:var(--text);background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:7px 10px;cursor:pointer}button:focus-visible,summary:focus-visible{outline:2px solid var(--blue);outline-offset:3px}.stage{background:var(--panel);border:1px solid var(--line);border-radius:12px;margin:10px 0;overflow:hidden}.stage.active{border-color:var(--amber)}summary{list-style:none;display:flex;align-items:center;gap:12px;padding:14px 16px;cursor:pointer}summary::-webkit-details-marker{display:none}.stage-no{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}.stage-title{flex:1;font-weight:600}.stage-title small{display:block;color:var(--muted);font-weight:400;font-size:12px}.active .stage-title small{color:var(--amber)}.chevron{color:var(--muted);transition:transform .15s}details[open] .chevron{transform:rotate(180deg)}.stage-track{height:3px;background:var(--line)}.stage-track span{display:block;background:var(--green);height:100%}.stage-body{padding:0 16px 10px}.stage-body p{font-size:12px;color:var(--muted);margin:12px 0}ul{list-style:none;padding:0;margin:0}li{display:flex;gap:11px;align-items:flex-start;padding:12px 0;border-top:1px solid var(--line);font-size:14px}.mark{flex:none;width:23px;height:23px;display:grid;place-items:center;border-radius:50%;font-size:13px;color:var(--muted);background:var(--bg)}.done .mark{color:var(--green);background:var(--soft)}.open .mark{color:var(--amber);background:var(--warm);font-weight:700}.number{font-size:11px;color:var(--muted);font-variant-numeric:tabular-nums;margin-right:3px}li small{display:block;color:var(--muted);font-size:12px;margin-top:5px}footer{font-size:12px;color:var(--muted);margin-top:22px}footer p{margin:5px 0}@media(max-width:380px){main{padding:20px 12px}.stat{padding:12px 10px}.stat b{font-size:26px}h1{font-size:25px}}@media(prefers-reduced-motion:reduce){*{transition:none!important}}
.integration{background:var(--panel);border:1px solid var(--line);border-radius:12px;margin:0 0 24px}.checkpoint-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;padding:0 14px}.checkpoint{display:flex;gap:8px;padding:11px;border-radius:9px;background:var(--bg);min-width:0}.checkpoint-icon{color:var(--muted);font-weight:700;flex:none}.checkpoint.done .checkpoint-icon{color:var(--green)}.checkpoint.open .checkpoint-icon{color:var(--amber)}.checkpoint strong{font-size:12px;line-height:1.4;display:block}.checkpoint small{font-size:11px;line-height:1.45;color:var(--muted);display:block;margin-top:4px}.checkpoint-caption{font-size:11px;color:var(--muted);padding:0 14px 10px;margin:10px 0 0}@media(max-width:430px){.checkpoint-grid{grid-template-columns:1fr}.checkpoint{padding:9px 11px}}
</style></head><body><main>
<header><div class="eyebrow">Dual-arm robotic cutting</div><h1>Project progress</h1><p>From a working simulator to a repeatable cut.</p></header>
<div class="counts" aria-label="10 completed, 2 open issues, 20 upcoming"><div class="stat done"><b>10</b><span>Completed</span></div><div class="stat open"><b>2</b><span>Pending checks</span></div><div class="stat"><b>20</b><span>Upcoming</span></div></div>
<div class="overall" aria-hidden="true"><span></span><span></span></div><p class="caption">10 of 32 milestones completed · Counts reflect steps, not time remaining.</p>
<aside class="focus"><div class="eyebrow">We are here</div><h2>Integration underway · fixed mount</h2><p>Mounted-robot elastic contact and the new material-force candidate pass their component checks. Sustained tomato support and full cutting mechanics remain open.</p><p><a href="integration-progress-20261102.txt">Current integration evidence →</a></p><p><a href="research-roadmap-review-20261102.html">Read the research review &amp; detailed next-stage plan →</a></p></aside>
<div class="toolbar"><h2>The roadmap</h2><button id="expand" type="button" aria-expanded="false">Expand all</button></div>
'''+''.join(sections)+'''
<footer><p>✓ Completed &nbsp; · &nbsp; ! Pending checks &nbsp; · &nbsp; ○ Upcoming</p><p>Reviewed 2 Nov 2026 · Click any stage to see its checklist.</p><p>Review changed the count from 21 to 18: existing tests still pass; three broader integration gates are partial. Four open checks include the experimental hold.</p><p>This view is updated as we finish steps; it is not a live simulation monitor.</p></footer>
</main><script>const control=document.getElementById('expand');control.addEventListener('click',()=>{const expand=control.getAttribute('aria-expanded')!=='true';document.querySelectorAll('details.stage').forEach(d=>d.open=expand);control.setAttribute('aria-expanded',String(expand));control.textContent=expand?'Collapse all':'Expand all';});</script></body></html>'''
page=page.replace('<div class="toolbar">',integration_html+'<div class="toolbar">',1)
if data.get('dry_motion_review'):
 page=page.replace('<p><a href="integration-progress-20261102.txt">', '<p><a href="live-clear-assembly-20261102.txt">Read the live robot and tomato results →</a></p><p><a href="integration-progress-20261102.txt">',1)
if data.get('integration_recovery'):
 page=page.replace('<p><a href="integration-progress-20261102.txt">', '<p><a href="integration-recovery-decision-20261102.txt">Read the recovery decision &amp; next-step recommendation →</a></p><p><a href="integration-progress-20261102.txt">',1)

focus=data.get('integration_focus')
if focus:
 page=page.replace('Integration underway · fixed mount',html.escape(focus['title'])).replace('Mounted-robot elastic contact and the new material-force candidate pass their component checks. Sustained tomato support and full cutting mechanics remain open.',html.escape(focus['text']))
counts=data['counts']
page=page.replace('<b>10</b>',f"<b>{counts['done']}</b>").replace('<b>2</b>',f"<b>{counts['open']}</b>").replace('<b>20</b>',f"<b>{counts['todo']}</b>")
page=page.replace('10 completed, 2 open issues, 20 upcoming',f"{counts['done']} completed, {counts['open']} pending checks, {counts['todo']} upcoming")
page=page.replace('10 of 32 milestones completed',f"{counts['done']} of {len(data['items'])} milestones completed")
page=page.replace('width:31.25%',f"width:{counts['done']/len(data['items'])*100}%").replace('width:6.25%',f"width:{counts['open']/len(data['items'])*100}%")
(out/'isaac-sim-progress.html').write_text(page)
assert page.count('<details ')==8+bool(checkpoints) and page.count('<li class=')==32
print('Created responsive checklist: 8 stages, 32 milestones, current issues expanded.')
