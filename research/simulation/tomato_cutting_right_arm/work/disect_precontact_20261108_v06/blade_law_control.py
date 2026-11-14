from pathlib import Path
import json,math,numpy as np
from blade_contact import law
W=Path(__file__).resolve().parent;rng=np.random.default_rng(824);phi=np.r_[rng.uniform(-.001,-1e-6,100),rng.uniform(0,.001,100)];n=rng.normal(size=(200,3));n/=np.linalg.norm(n,axis=1)[:,None];v=rng.normal(size=(200,3))*.002;tool=np.array([.0001,-.0003,.0002]);actual=law(phi,n,v,tool);expected=[];power=[]
for d,normal,velocity in zip(phi,n,v):
    if d>=0:expected.append(np.zeros(3));continue
    r=velocity-tool;vn=float(normal@r);vt=r-vn*normal;s=float(np.linalg.norm(vt));fn=2000*(-d);f=(fn+max(-vn,0))*normal
    if s>0:f-=fn*(.5*math.tanh(4*s/2500))*vt/s
    expected.append(f);power.append(float((f-(f@normal)*normal)@vt))
error=float(np.max(abs(actual-np.array(expected))));outside=bool(np.array_equal(actual[phi>=0],np.zeros_like(actual[phi>=0])));opposed=np.array([[1.,0,0],[-1.,0,0]])
out={'scope':'Vectorized exact-geometry adapter force law versus independent scalar legacy functional form; no live indentation','random_cases':len(phi),'maximum_force_error_N':error,'noncontact_force_exact_zero':outside,'maximum_tangential_relative_power_W':max(power),'opposed_load_resultant_N':float(np.linalg.norm(opposed.sum(0))),'opposed_load_sum_magnitudes_N':float(np.linalg.norm(opposed,axis=1).sum()),'parameters':{'normal_ke_N_per_m':2000.,'normal_kd_N_s_per_m':1.,'friction_velocity_scale_m_per_s':2500.,'mu':.5,'mu_static':.5,'source':'v04 DiSECt/dflex/sim.py knife_contact_force; surface coefficients from ansys_prism config'},'limits':['kf is used as a velocity scale in the source Brown formula, not ground viscous kf. These inherited values are uncalibrated.','New adapter collocates at original FEM exterior nodes; it does not claim equivalence to legacy virtual-edge force interpolation.','No angular blade motion or native robot force feedback is tested.'],'passed':bool(error<1e-12 and outside and max(power)<=1e-15)};(W/'blade_law_control_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
