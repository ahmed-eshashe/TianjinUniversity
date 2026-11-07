"""Bounded completion-status publisher. No additional simulation is launched."""
from pathlib import Path
import json,time,subprocess,sys,re
w=Path(__file__).parent;r=w.parents[1];deadline=time.monotonic()+86520;p=w/'robot_cut18/endpoint_review.json'
while not p.exists():
 if time.monotonic()>deadline:raise SystemExit('No endpoint review before deadline')
 time.sleep(10)
d=json.loads(p.read_text());status=w/'bodyward_withdrawal_status.json';s=json.loads(status.read_text());s['status']='withdrawal_endpoint_review_required';s['endpoint_assessment_queued']=False
s['progress_note']=f"The withdrawal run has stopped and its saved endpoint was assessed. Route finished: {d.get('route_finished',False)}. Remaining material connections: {d.get('remaining_connections','unknown')}. Full slice is not yet qualified. Review blade clearance and remaining-interface geometry before the finishing stroke. Local timestep comparisons passed; full-trajectory convergence remains unqualified."
status.write_text(json.dumps(s,indent=2));subprocess.run([sys.executable,str(r/'work/integration_20261102/publish_integration_gates.py')],cwd=r,check=True)
o=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');p=o/'learning-roadmap.json';data=json.loads(p.read_text());data['latest_progress']['cutting']=s['progress_note'];p.write_text(json.dumps(data,indent=2));p=o/'learning-roadmap.html';text=p.read_text();text=re.sub(r'<div class="note"><b>Work underway · 7 November</b>.*?</div>','<div class="note"><b>Work underway · 7 November</b>'+s['progress_note']+'</div>',text,count=1);p.write_text(text)
print(s['progress_note'],flush=True)
