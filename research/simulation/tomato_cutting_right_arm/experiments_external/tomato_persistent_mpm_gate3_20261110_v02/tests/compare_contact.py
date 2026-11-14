from pathlib import Path
import numpy as np,json
W=Path(__file__).resolve().parents[1];results={};checks={}
for name in ['edge','broad']:
 a=json.loads((W/f'runs/{name}_clock/result.json').read_text());b=json.loads((W/f'runs/{name}_clock_half/result.json').read_text());sa=np.load(W/f'runs/{name}_clock/trajectory.npz');sb=np.load(W/f'runs/{name}_clock_half/trajectory.npz');assert np.allclose(sa['t'],sb['t'],atol=1e-12)
 fa=np.array([r['reaction'] for r in a['rows']]);fb=np.array([r['reaction'] for r in b['rows']]);scale=np.maximum(np.linalg.norm(fb,axis=1),1e-4);rel=np.linalg.norm(fa-fb,axis=1)/scale
 # Compare force only where either signal is meaningful; floor still guards zeros.
 position=np.linalg.norm(sa['x']-sb['x'],axis=-1).max();ja=np.array(a['reaction_impulse_Ns']);jb=np.array(b['reaction_impulse_Ns']);imp=np.linalg.norm(ja-jb)/max(np.linalg.norm(jb),1e-7);work=abs(a['work_J']-b['work_J'])/max(abs(b['work_J']),1e-8)
 residual=max(abs(r['energy_residual']) for r in a['rows']);escale=max(max(abs(r['Wtool']) for r in a['rows']),1e-8)
 r={'position_max_m':float(position),'force_max_relative_or_floor':float(rel.max()),'impulse_relative_or_floor':float(imp),'work_relative_or_floor':float(work),'energy_residual_relative_or_floor':float(residual/escale),'coarse_peak_force_N':a['max_force_N'],'max_impulse_balance_Ns':a['max_impulse_balance_error_Ns'],'coarse_wall_s':a['wall_s'],'refined_wall_s':b['wall_s']};results[name]=r
 checks[name+'_completed']=a['status']==b['status']=='completed';checks[name+'_position']=position<.0001;checks[name+'_force']=rel.max()<.05;checks[name+'_impulse']=imp<.05;checks[name+'_work']=work<.05;checks[name+'_energy']=residual/escale<.05;checks[name+'_loaded']=a['max_force_N']>1e-4;checks[name+'_unloaded']=np.linalg.norm(fa[-1])<1e-4;checks[name+'_balance']=a['max_impulse_balance_error_Ns']<1e-8
out={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'results':results,'scope':'Shared-clock finite CAD load/unload components, fracture disabled'};(W/'contact_comparison.json').write_text(json.dumps(out,indent=2,default=lambda x:x.item()));print(json.dumps(out,indent=2,default=lambda x:x.item()))
