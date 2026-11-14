"""Aggregate frozen v03 physical outcomes and retain all prior failures."""
from pathlib import Path
import json,hashlib,math,datetime
W=Path(__file__).resolve().parent
frozen=json.loads((W/'reports/hybrid_v03_frozen_hashes.json').read_text())
unchanged={f:hashlib.sha256((W/f).read_bytes()).hexdigest()==h for f,h in frozen['hashes'].items()}
assert all(unchanged.values()),'Frozen physical/visual implementation changed during evaluation'
rows=[]
for dataset in sorted((W/'datasets').glob('hybrid_v03*')):
 for ep in sorted(p for p in dataset.iterdir() if p.is_dir()):
  if not (ep/'configuration.json').exists():continue
  cfg=json.loads((ep/'configuration.json').read_text())['args'];result=json.loads((ep/'result.json').read_text()) if (ep/'result.json').exists() else {};failure=(ep/'failure.txt').read_text() if (ep/'failure.txt').exists() else ''
  row=dict(dataset=dataset.name,episode=ep.name,completed=bool(result or failure),success=bool(result.get('success')),physics_hz=cfg['physics_hz'],ablation=cfg['vision_ablation'],scene=cfg['scene'])
  if result:
   last=result['last'];checks=dict(continuous_hold=last['hold_s']>=3.,clear_of_support=last['minimum_tool_height_m']>.003 and last['support_N']<.05,opposed_contact=last['opposed'],slip=last.get('slip_m',float('inf'))<=.01,rotation=last.get('rotation_drift_rad',float('inf'))<=.261799,load=result['maximum_contact_load_N']<=50.)
   if row['success']:assert all(checks.values()),checks
   row.update(checks=checks,hold_s=last['hold_s'],slip_m=last.get('slip_m'),maximum_contact_load_N=result['maximum_contact_load_N'],min_tool_height_m=last['minimum_tool_height_m'],wall_s=result['wall_s'])
  if failure:row['failure']=failure.splitlines()[-1]
  if (ep/'visual_prediction.json').exists():row['vision_accepted']=json.loads((ep/'visual_prediction.json').read_text())['accepted']
  rows.append(row)
validation=[r for r in rows if r['dataset']=='hybrid_v03_validation'];tests=[r for r in rows if r['dataset']=='hybrid_v03_test'];completed_tests=[r for r in tests if r['completed']]
n=len(completed_tests);k=sum(r['success'] for r in completed_tests)
ci=None
if n==8:
 z=1.95996398454;center=(k/n+z*z/(2*n))/(1+z*z/n);half=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/(1+z*z/n);ci=[center-half,center+half]
report=dict(updated=datetime.datetime.now().astimezone().isoformat(),frozen_hashes_unchanged=unchanged,validation_successes=sum(r['success'] for r in validation),validation_completed=sum(r['completed'] for r in validation),test_successes=k,test_completed=n,placement_success_wilson_95=ci,scope='Learned handle position/yaw from head RGB-D, engineered arm and balanced compliant grip; same short knife, bounded flat-rest placements, uncalibrated contact parameters. Not full-motion learning or any-knife/any-rest qualification.',rows=rows)
(W/'reports/hybrid_v03_campaign.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k not in ['rows','frozen_hashes_unchanged']})
