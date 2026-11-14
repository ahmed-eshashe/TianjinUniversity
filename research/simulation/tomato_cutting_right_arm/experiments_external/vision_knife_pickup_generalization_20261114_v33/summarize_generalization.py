"""Summarize saved outcomes without turning teacher trials into learned tests."""
from pathlib import Path
import json,hashlib,datetime
W=Path(__file__).resolve().parent
rows=[]
for batch in sorted((W/'datasets').iterdir()):
 if not batch.is_dir():continue
 for p in sorted(batch.glob('*/configuration.json')):
  c=json.loads(p.read_text());a=c['args'];out=p.parent
  r=json.loads((out/'result.json').read_text()) if (out/'result.json').exists() else None
  f=(out/'failure.txt').read_text().splitlines()[-1] if (out/'failure.txt').exists() else None
  if r is None and f is None:continue
  s=r['last'] if r else {}
  rows.append(dict(batch=batch.name,episode=out.name,teacher=bool(a.get('teacher_target') or a.get('teacher_along_shift')),success=bool(r and r['success']),failure=f,scope=r.get('scope') if r else None,sim_hold_s=s.get('hold_s'),slip_m=s.get('slip_m'),rotation_drift_rad=s.get('rotation_drift_rad'),support_N=s.get('support_N'),minimum_tool_height_m=s.get('minimum_tool_height_m'),maximum_contact_load_N=r.get('maximum_contact_load_N') if r else None,configuration=str(p),source_sha256=c.get('source_hash')))
preserve={p:hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in json.loads((W/'preserved_baseline.json').read_text()).items()}
assert all(preserve.values())
(W/'reports/all_outcomes.json').write_text(json.dumps(dict(updated=datetime.datetime.now().astimezone().isoformat(),rows=rows,baseline_preservation=preserve),indent=2))
print('Saved',len(rows),'finished episode outcomes, preserving teacher/actor distinction.')
