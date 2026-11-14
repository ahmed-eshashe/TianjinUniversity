from pathlib import Path
import json,re,html
out=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');p=out/'learning-roadmap.json';d=json.loads(p.read_text());evidence={'1.5':'Approved grip, backward elbow and kitchen preserved in the mounted-robot continuation; fixed attachment remains disclosed.','2.2':'Local material and coupled comparisons passed: maximum tomato difference 0.054 mm, knife 0.014 mm, force 0.86%. Full-cut convergence remains item 2.3.','3.5':'Observation allowlist and checkpoint adapter reject hidden damage/connectivity inputs. All 28 interface and episode component tests passed again.'}
for stage in d['stages']:
 for item in stage['items']:
  if item['id'] in evidence:item.update(status='complete',evidence=evidence[item['id']])
  elif item['id'] in ['2.1','3.2','3.3','3.4','4.3','4.4','5.2']:item['status']='in_progress'
d['scope']='Evidence-based progress: completed preparation is counted separately from unverified cutting and learning gates.';d['updated']='2026-11-07';p.write_text(json.dumps(d,indent=2))
p=out/'learning-roadmap.html';s=p.read_text()
js=r'''
<script id="live-roadmap">
const escapeText=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function renderRoadmap(data){
 const items=data.stages.flatMap(s=>s.items),done=items.filter(i=>i.status==='complete').length,active=items.filter(i=>i.status==='in_progress').length;
 const stats=document.querySelectorAll('.stat');stats[0].innerHTML=`<strong>${done} / ${items.length}</strong><span>Verified checklist items</span>`;stats[1].innerHTML=`<strong>${active}</strong><span>In progress · across ${data.stages.length} stages</span>`;stats[2].innerHTML='<strong>Not started</strong><span>Policy training</span>';
 const open=new Set([...document.querySelectorAll('details[open]')].map(e=>e.id));
 document.getElementById('roadmap-cards').innerHTML=data.stages.map(s=>`<details id="stage-${s.id}" ${open.has('stage-'+s.id)||s.id===1?'open':''}><summary><span class="num">${String(s.id).padStart(2,'0')}</span><span class="title">${escapeText(s.title)}<small>${escapeText(s.phase)}</small></span><span class="count">${s.items.filter(i=>i.status==='complete').length} / ${s.items.length} done</span><span class="chevron">⌄</span></summary><div class="body"><p>${escapeText(s.description)}</p><ul>${s.items.map(i=>`<li class="state-${i.status}"><span class="circle" aria-label="${i.status==='complete'?'Complete':i.status==='in_progress'?'In progress':'Not started'}">${i.status==='complete'?'✓':i.status==='in_progress'?'•':''}</span><div><span class="id">${i.id}</span>${escapeText(i.text)}<span class="status-label">${i.status==='complete'?'Done':i.status==='in_progress'?'In progress':'Not started'}</span>${i.evidence?`<small class="evidence">${escapeText(i.evidence)}</small>`:''}</div></li>`).join('')}</ul></div></details>`).join('');
 document.getElementById('sync-status').textContent='Status refreshed '+new Date().toLocaleTimeString()+' · Full separation remains pending';
}
async function refreshRoadmap(){try{const response=await fetch('learning-roadmap.json',{cache:'no-store'});if(!response.ok)throw Error(response.status);renderRoadmap(await response.json());}catch(e){document.getElementById('sync-status').textContent='Unable to refresh status; showing last loaded snapshot';}}
refreshRoadmap();setInterval(refreshRoadmap,30000);
</script>'''
first=s.index('<details');last=s.rindex('</details>')+len('</details>');s=s[:first]+'<div id="roadmap-cards">'+s[first:last]+'</div>'+s[last:]
s=s.replace('<strong>0 / 39</strong>','<strong>3 / 39</strong>');s=s.replace('</style>','.state-complete .circle{background:#28764c;color:white;border-color:#28764c;text-align:center;font-size:12px}.state-in_progress .circle{border-color:#b87919;color:#b87919;text-align:center}.status-label{display:inline-block;margin-left:10px;font-size:11px;color:#61756a}.state-complete .status-label{color:#28764c;font-weight:700}.state-in_progress .status-label{color:#946010}.evidence{display:block;margin-top:6px;color:#597064;font-size:12px}.sync-status{font-size:12px;color:#597064;margin:16px 0}</style>');s=s.replace('<div class="toolbar">','<p class="sync-status" id="sync-status" role="status">Loading verified progress…</p><div class="toolbar">',1);s=s.replace('</body>',js+'</body>');p.write_text(s)
