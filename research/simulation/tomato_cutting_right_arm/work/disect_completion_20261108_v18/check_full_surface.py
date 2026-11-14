from full_surface import FullSurface
from cohesive_transfer import Transfer
from scipy.spatial.transform import Rotation
from pathlib import Path
import numpy as np,json,torch
# CPU one-thread controls; runtime not counted as a simulator benchmark.
torch.set_num_threads(1);s=FullSurface();old=Transfer();x=s.mesh['x'].copy();plus=np.unique(s.mesh['tets'][s.mesh['tet_side']>0]);x[plus]+=[.0002,.00005,.00003];r=s.evaluate(x);reference=old.evaluate(x);energy=abs(r['stored_energy_j']-reference['stored_energy_j'])/reference['stored_energy_j']
q=s.mesh['x'].copy();q[int(s.mesh['ties'][len(s.mesh['ties'])//2,0]),0]-=1e-5;local=s.evaluate(q);coverage=local['stored_energy_j']>0 and np.linalg.norm(local['force'])>0
rng=np.random.default_rng(22);x+=rng.normal(size=x.shape)*1e-7;d=rng.normal(size=x.shape);d/=np.linalg.norm(d);eps=1e-7;r=s.evaluate(x);fd=(s.evaluate(x+eps*d)['stored_energy_j']-s.evaluate(x-eps*d)['stored_energy_j'])/(2*eps);work=abs(fd+np.sum(r['force']*d))/max(abs(fd),1e-12)
R=Rotation.from_rotvec([.2,-.3,.4]).as_matrix();rot=s.evaluate(x@R.T+[.2,-.1,.3]);cov=np.linalg.norm(rot['force']-r['force']@R.T)/np.linalg.norm(r['force']);net=np.linalg.norm(r['force'].sum(0));torque=np.linalg.norm(np.cross(x,r['force']).sum(0))
opened=s.mesh['x'].copy();opened[plus,0]+=.005;release=s.evaluate(opened,np.ones(47,bool));s.commit(release['trial_history']);zero=s.evaluate(x);s.reset();fresh=FullSurface();reset=np.array_equal(s.evaluate(x)['force'],fresh.evaluate(x)['force'])
out=dict(scope='Approved full-surface original-law candidate component checks; no closure or dynamic qualification',uniform_energy_relative_error=energy,sample_interface_node_resisted=bool(coverage),local_opening_energy_J=local['stored_energy_j'],force_energy_relative_error=work,rotation_relative_error=cov,net_force_N=net,net_torque_Nm=torque,released_force_norm_N=float(np.linalg.norm(zero['force'])),reset_matches_fresh=bool(reset));out['passed']=bool(energy<1e-10 and coverage and work<1e-5 and cov<1e-8 and net<1e-8 and torque<1e-8 and out['released_force_norm_N']==0 and reset)
Path(__file__).with_name('full_surface_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
