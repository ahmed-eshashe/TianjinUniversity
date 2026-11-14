"""Audit current pickup campaign against the frozen physical criteria."""
from pathlib import Path
import json,hashlib,math,datetime
W=Path(__file__).resolve().parent
version=json.loads((W/'CURRENT_CANDIDATE.json').read_text())['version']
frozen=json.loads((W/('reports/hybrid_'+version+'_frozen_hashes.json')).read_text())
unchanged={name:hashlib.sha256((W/name).read_bytes()).hexdigest()==sha for name,sha in frozen['hashes'].items()};assert all(unchanged.values())
rows=[]
for folder in sorted((W/'datasets').glob('hybrid_'+version+'*')):
 for ep in sorted(x for x in folder.iterdir() if x.is_dir()):
  if not (ep/'configuration.json').exists():continue
  config=json.loads((ep/'configuration.json').read_text());assert config['source_hash']==frozen['hashes']['hybrid_pickup_'+version+'.py']
  settings=config['args'];assert settings['physics_hz']==1920 and settings['control_hz']==20 and settings['solver']==0 and settings['velocity_iterations']==4
  assert settings['compliant'] and settings['thumb_effort']==.65 and settings['finger_effort']==.10 and settings['hand_damping']==3.
  assert settings['close_seconds']==8. and settings['joint_space_approach'] and settings['policy'] is None
  assert config['criteria']==json.loads((W/'pickup_criteria.json').read_text())
  if (ep/'visual_prediction.json').exists():
   prediction=json.loads((ep/'visual_prediction.json').read_text());assert prediction['checkpoint_sha256']==frozen['hashes']['policies/handle_vision_v01/best.pt']
   assert prediction['ground_truth_pose_input'] is False
  if folder.name.endswith(('_validation','_test')):assert settings['vision_ablation']=='none'
  result=json.loads((ep/'result.json').read_text()) if (ep/'result.json').exists() else {};failure=(ep/'failure.txt').read_text() if (ep/'failure.txt').exists() else ''
  row=dict(dataset=folder.name,id=ep.name,complete=bool(result or failure),success=bool(result.get('success')))
  if failure:row['failure']=failure.splitlines()[-1]
  if result:
   r=result['last'];checks=dict(hold=r['hold_s']>=3.,opposed=r['opposed'],support=r['support_N']<.05,clearance=r['minimum_tool_height_m']>.003,slip=r.get('slip_m',999.)<=.01,rotation=r.get('rotation_drift_rad',999.)<=.261799,max_load=result['maximum_contact_load_N']<=50.)
   if row['success']:assert all(checks.values()),checks
   row.update(checks=checks,slip_m=r.get('slip_m'),hold_s=r['hold_s'],min_height_m=r['minimum_tool_height_m'],max_load_N=result['maximum_contact_load_N'],wall_s=result['wall_s'])
  rows.append(row)
validation=[r for r in rows if r['dataset']=='hybrid_'+version+'_validation' and r['complete']];tests=[r for r in rows if r['dataset']=='hybrid_'+version+'_test' and r['complete']];k=sum(r['success'] for r in tests);n=len(tests);ci=None
if n==8:
 z=1.95996398454;center=(k/n+z*z/(2*n))/(1+z*z/n);half=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/(1+z*z/n);ci=[center-half,center+half]
violations=[r['id'] for r in tests if 'Contact stop' in r.get('failure','') or 'Blade/' in r.get('failure','')]
qualified=len(validation)==3 and all(r['success'] for r in validation) and n==8 and k>=7 and not violations
report=dict(updated=datetime.datetime.now().astimezone().isoformat(),frozen_sources_unchanged=unchanged,validation_successes=sum(r['success'] for r in validation),validation_attempts=len(validation),test_successes=k,test_attempts=n,wilson_95_interval=ci,forbidden_test_violations=violations,limited_curriculum_physical_gate_passed=qualified,scope='Head RGB-D learns handle location/yaw; calibrated flat-rest target and engineered contact-guided motion. Short knife, bounded placement/yaw only. Real contact and no attachment. No full-motion/RL, any-knife/any-rest, or physical-transfer claim.',rows=rows)
(W/('reports/hybrid_'+version+'_campaign.json')).write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k not in ['rows','frozen_sources_unchanged']})
