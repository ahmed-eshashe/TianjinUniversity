from pathlib import Path
import json,difflib,hashlib,shutil
w=Path(__file__).resolve().parent;prior=w.parent/'disect_mesh_validation_20261108_v02';diag=w.parent/'disect_stability_20261108_v03'
initial=json.loads((diag/'initial_analysis.json').read_text());controls=json.loads((w/'controls_result.json').read_text());short=json.loads((w/'settle_result.json').read_text());low=json.loads((w/'affine_low_signal_failure.json').read_text());affine=json.loads((w/'affine_control.json').read_text())
result={'scope':'Corrected relative hydrostatic damping candidate, intact new FEM mesh only','production':'Paused at 6925; no edits','initial_state_finite':all(initial['initial_fields_finite'].values()),'old_dt_over_damping_limit':initial['old_dt_s']/initial['damping_only_eigen_dt_limit_s'],'correction':'Hydrostatic strain rate uses vj-v0, not absolute vj; coefficient unchanged','controls':controls,'low_signal_affine_control':low,'resolved_signal_affine_control':affine,'short_gravity':{k:v for k,v in short.items() if k!='rows'},'complete_settling':None,'contact_passed':False,'separation_passed':False,'full_force_work_qualified':False,'experimental_validation':'pending'}
if (w/'long_settle_result.json').exists():
 long=json.loads((w/'long_settle_result.json').read_text());result['complete_settling']={k:v for k,v in long.items() if k!='rows'}
(w/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False))
# Original production checkpoint integrity comparison against first study.
base=json.loads((w.parent/'disect_feasibility_20261108_v01/preserved_inputs.json').read_text());ck=next(p for p in base if 'step_006925.npz' in p);assert hashlib.sha256(Path(ck).read_bytes()).hexdigest()==base[ck]
(w/'integrity.json').write_text(json.dumps({'checkpoint':ck,'sha256':base[ck],'matches_original_study':True,'compiled_kernel':{'path':str(w/'DiSECt/dflex/kernels/kernels.so'),'sha256':hashlib.sha256((w/'DiSECt/dflex/kernels/kernels.so').read_bytes()).hexdigest()},'force_source':{'sha256':hashlib.sha256((w/'DiSECt/dflex/sim.py').read_bytes()).hexdigest()},'mesh_sha256':hashlib.sha256((prior/'tomato_fem_mesh.npz').read_bytes()).hexdigest()},indent=2))
print('Diagnosis data and input hashes saved; complete settling is populated only after a real result exists.')
