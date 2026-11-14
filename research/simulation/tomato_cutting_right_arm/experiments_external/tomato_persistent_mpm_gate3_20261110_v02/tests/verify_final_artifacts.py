from pathlib import Path
import json,sys,hashlib,ast,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from contact_geometry import Cells,CAD
from volume_guard import certificate
checks={};data={}
for p in W.rglob('*.json'):
 if 'cache' not in p.parts:json.loads(p.read_text())
checks['json_readable']=True
for p in (W/'src').glob('*.py'):ast.parse(p.read_text())
for p in (W/'tests').glob('*.py'):ast.parse(p.read_text())
checks['python_syntax']=True
manifest=json.loads((W/'manifest.json').read_text());bad=[p for p,h in manifest['protected_sha256'].items() if not Path(p).is_file() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h];checks['protected_files_unchanged']=not bad;data['protected_count']=len(manifest['protected_sha256'])
f=np.load(W/'runs/paid_cut_refined_guard/final.npz');cells=Cells(f['X'],f['codes'],contact_face_spacing=.0000625);volume=certificate(cells,f['x']);checks['last_saved_state_volume_admissible']=volume['passed'];checks['no_physical_code_change']=bool(np.all(f['codes']==0));data['saved_volume_certificate']=volume
cad=CAD();t=float(f['sim_time']);T=np.array([0,.00605-.0016*.5*(1-np.cos(np.pi*t/.05)),0]);geometry=cells.certificate(f['x'],cad,T);checks['last_saved_state_penetration_certified']=geometry['passed'];data['saved_blade_certificate']=geometry
control=json.loads((W/'contact_fracture_controls.json').read_text());checks['gate_not_falsely_complete']=not control['gate_complete'] and not control['physical_cut_achieved'];data['failed_trial_J']=json.loads((W/'runs/paid_cut_refined_guard/result.json').read_text())['last_volume_certificate']['observed_minJ']
# Prove old milestone data, not just counts, survived the status-banner addition.
import re
D=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs')
for name in ['disect-checklist.html','learning-roadmap.html']:
 before=(W/'reports/checklist_before'/name).read_text();after=(D/name).read_text();stripped=re.sub(r'\n<aside id="mpm-gate3-status".*?</aside>\n','',after,flags=re.S);checks[name+'_only_status_banner_changed']=stripped==before
out={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'results':data};(W/'final_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert all(checks.values())
