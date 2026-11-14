from pathlib import Path
import json,numpy as np
from implicit_blade import ImplicitBlade,m,tensor,torch
from adaptive_blade import AdaptiveBlade
W=Path(__file__).resolve().parent
b=ImplicitBlade();old=AdaptiveBlade();old.adaptive.force_atol=1e-13
z=np.load(W.parent/'disect_section4_loading_20261109_v28/coarse0024_final.npz')
q=z['x'];v=np.zeros_like(q);T=z['blade_translation'];vel=np.zeros(3)
ev,bd=b.contact(q,v,T,vel);ref,_=old.contact(q,v,T,vel)
ratio=b.normal_stiffness/2000.
force_error=float(np.max(abs(ev['force']-ratio*ref['force'])))
energy_error=abs(ev['energy_J']-ratio*ref['energy_J'])
rng=np.random.default_rng(31);direction=rng.normal(size=q.shape);direction/=np.linalg.norm(direction)
eps=1e-8
energies=[b.contact(q+sign*eps*direction,v,T,vel)[0]['energy_J'] for sign in [1,-1]]
gradient_error=abs((energies[0]-energies[1])/(2*eps)+float(np.sum(ev['force']*direction)))
b.x.copy_(tensor(q));b.v.zero_();b.blade_enabled=True;b.blade_translation=T.copy();b.blade_velocity=vel.copy()
b.geometry();history=b.fracture.state_dict()['history'].copy();force=b.blade_sample['force'].copy();b.geometry()
pure=bool(np.array_equal(history,b.fracture.state_dict()['history']) and np.array_equal(force,b.blade_sample['force']))
b.reset();reset=bool(not b.blade_enabled and b.blade_dashpot is None and not b.eligibility.any() and np.all(b.fracture.state_dict()['history']==0))
passed=bool(force_error<1e-6 and energy_error<1e-7 and gradient_error<1e-6 and pure and reset)
out=dict(scope='Read-only actual CAD/edge force scaling, independent material-coordinate energy gradient and trial/reset checks. Old penetrated checkpoint is NOT used as a physical start.',force_scale_error_N=force_error,energy_scale_error_J=energy_error,energy_gradient_error_N=gradient_error,pure=pure,reset=reset,passed=passed)
(W/'adapter_controls_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert passed
