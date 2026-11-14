from cohesive_transfer import Transfer
import numpy as np,json,time
from pathlib import Path
from scipy.spatial.transform import Rotation
s=Transfer();x=s.mesh['x'].copy();plus=np.unique(s.mesh['tets'][s.mesh['tet_side']>0]);rng=np.random.default_rng(17)
x[plus,0]+=2e-4;x[plus,1]+=5e-5
x+=rng.normal(size=x.shape)*1e-7
r=s.evaluate(x);f=r['force'];d=rng.normal(size=x.shape);d/=np.linalg.norm(d);eps=1e-7
fd=(s.evaluate(x+eps*d)['stored_energy_j']-s.evaluate(x-eps*d)['stored_energy_j'])/(2*eps)
force_error=abs(fd+np.sum(f*d))/max(abs(fd),1e-12)
R=Rotation.from_rotvec([.2,-.3,.4]).as_matrix();rot=s.evaluate(x@R.T+[.2,-.1,.3]);rot_error=np.linalg.norm(rot['force']-f@R.T)/np.linalg.norm(f)
net=np.linalg.norm(f.sum(0));torque=np.linalg.norm(np.cross(x,f).sum(0))
original=s.history.copy();opened=s.mesh['x'].copy();opened[plus,0]+=.005
frozen=s.evaluate(opened);released=s.evaluate(opened,np.ones(47,bool));unmutated=np.array_equal(original,s.history);s.commit(released['trial_history']);after=s.evaluate(x)
out={'scope':'Original 47-patch objective reference force transfer to FEM nodes; no coupled dynamics, closure or eligibility-detector pass','virtual_work_relative_error':force_error,'rotation_force_relative_error':rot_error,'net_force_N':net,'net_torque_Nm':torque,'ineligible_damage_max':float(frozen['trial_history'][:,1].max()),'eligible_full_open_damage_min':float(released['trial_history'][:,1].min()),'trial_does_not_mutate_history':unmutated,'released_force_norm_N':float(np.linalg.norm(after['force'])),'original_fracture_budget_J':sum(p['fracture_budget_j'] for p in s.registry['patches'])}
out['passed']=bool(force_error<1e-5 and rot_error<1e-8 and net<1e-8 and torque<1e-8 and out['ineligible_damage_max']==0 and out['eligible_full_open_damage_min']==1 and unmutated and out['released_force_norm_N']==0)
Path(__file__).with_name('transfer_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
