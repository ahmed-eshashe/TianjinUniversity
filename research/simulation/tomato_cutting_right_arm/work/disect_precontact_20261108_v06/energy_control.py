from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W/'backend'))
from numerics import load_arrays,numpy_force
z=load_arrays();rng=np.random.default_rng(814);t=z['tet_indices'];dm=z['tet_poses'];V=1/np.linalg.det(dm)/6;mu=z['tet_mu'];la=z['tet_lambda'];alpha=1+.75*mu/la
def energy(x):
    D=(x[t[:,1:]]-x[t[:,0]][:,None]).transpose(0,2,1);F=D@dm;Ic=np.square(F).sum(axis=(1,2));J=np.linalg.det(F)
    return np.sum(V*(.5*mu*(Ic-3)+.5*la*(J-alpha)**2-.5*mu*np.log(Ic+1)))
rows=[]
for scale in [1e-6,1e-5,1e-4]:
    x=z['x']+rng.normal(size=z['x'].shape)*scale;d=rng.normal(size=x.shape);d/=np.linalg.norm(d);force=numpy_force(z,x,np.zeros_like(x));projected=-float(np.sum(force*d));cs=float(energy(x.astype(complex)+1e-20j*d).imag/1e-20);fd=float((energy(x+1e-7*d)-energy(x-1e-7*d))/2e-7);ce=abs(cs-projected);fe=abs(fd-projected);row={'deformation_scale_m':scale,'negative_force_projection_N':projected,'complex_step_energy_derivative_N':cs,'central_difference_derivative_N':fd,'complex_relative_error':ce/max(abs(projected),1e-9),'finite_difference_relative_error':fe/max(abs(projected),1e-9),'passed':bool(ce<=max(1e-10,1e-7*abs(projected)) and fe<=max(1e-9,1e-3*abs(projected)))};rows.append(row)
out={'scope':'Independent energy-gradient check for approved corrected elasticity, no damping in energy','complex_relative_limit':1e-7,'complex_absolute_floor_N':1e-10,'finite_difference_relative_limit':.001,'finite_difference_absolute_floor_N':1e-9,'rows':rows,'passed':all(r['passed'] for r in rows)};(W/'energy_control_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
