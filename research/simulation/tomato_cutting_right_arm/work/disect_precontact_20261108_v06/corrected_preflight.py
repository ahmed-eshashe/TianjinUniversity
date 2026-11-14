from pathlib import Path
import sys,json,numpy as np
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parent;V=W/'backend';sys.path.insert(0,str(V))
from numerics import load_arrays,numpy_force,Bulk,tensor
z=load_arrays();x=z['x'];zero=np.zeros_like(x);center=x.mean(0);rng=np.random.default_rng(812);xd=x+rng.normal(size=x.shape)*1e-6;out={'scope':'static constitutive preflight, no dynamics, contact or topology changes','rows':[]}
b=Bulk();f0=numpy_force(z,xd,zero)
for deg in [15,45,90]:
    R=Rotation.from_euler('y',deg,degrees=True).as_matrix();xr=(x-center)@R.T+center;f=numpy_force(z,xr,zero);dr=(xd-center)@R.T+center;fd=numpy_force(z,dr,zero);reference=f0@R.T;error=float(np.linalg.norm(fd-reference));relative=error/max(np.linalg.norm(reference),1e-9)
    b.x.copy_(tensor(xr));b.v.zero_();gpu=b.material().cpu().numpy().copy()
    row={'rotation_deg':deg,'rest_force_norm_N':float(np.linalg.norm(f)),'cuda_rest_force_norm_N':float(np.linalg.norm(gpu)),'independent_cuda_error_N':float(np.linalg.norm(gpu-f)),'covariance_reference_force_norm_N':float(np.linalg.norm(reference)),'covariance_force_error_N':error,'covariance_relative_error':relative,'passed':bool(np.linalg.norm(f)<=1e-9 and relative<=1e-8)};out['rows'].append(row)
out['passed']=all(r['passed'] for r in out['rows']);out['preserved_failure_cause']='Source Ic sums only squared diagonal entries of F; the intended first invariant is tr(F.T F), the sum of all nine squared entries. This changes under rigid rotations in the current code.';out['primary_reference']='https://graphics.pixar.com/library/StableElasticity/paper.pdf';(W/'corrected_preflight_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
