from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import root
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W/'backend'))
from numerics import load_arrays,numpy_force,tensor
from blade_numerics import BladeContactBulk
z=load_arrays();x=np.array([[0.,.02,0.],[.01,.02,0.],[0.,.03,0.],[0.,.02,.01]]);small={'x':x,'tet_indices':np.array([[0,1,2,3]]),'tet_poses':np.linalg.inv((x[1:]-x[0]).T)[None],'tet_mu':z['tet_mu'][:1],'tet_lambda':z['tet_lambda'][:1],'tet_damping':z['tet_damping'][:1],'tet_activations':np.zeros(1),'physical_mass':np.full(4,.00004),'particle_inv_mass':np.array([0.,25000,25000,25000]),'gravity':np.zeros(3),'contact_mask':np.ones(4),'fixed':np.array([0])}
normal=np.zeros_like(x);normal[1]=np.array([.2,-.96,.2]);normal[1]/=np.linalg.norm(normal[1]);tool=np.tile([.0001,-.05,.0002],(4,1));kd=np.array([0,1,0,0.]);force=.02*normal
class Fixture(BladeContactBulk):
    def geometry(self):super().geometry();self.f.add_(tensor(force));return self.f
b=Fixture(small);b.blade_dashpot={'normal':tensor(normal),'velocity':tensor(tool),'kd':tensor(kd)};b.v.copy_(tensor([[0,0,0],[.001,0,.001],[0,0,0],[0,0,0]]));q0,v0=b.arrays();f0=numpy_force(small,q0,np.zeros_like(x));C=np.empty((12,12))
for j in range(12):
    v=np.zeros_like(x);v.ravel()[j]=1;C[:,j]=-(numpy_force(small,q0,v)-f0).ravel()
h=7.462686567164179e-6;mass=np.repeat(small['physical_mass'],3);A=np.diag(mass)+h*C;rhs=mass*v0.ravel()+h*(f0+force).ravel();free=np.arange(3,12)
def resistance(v):return kd[:,None]*np.minimum(np.sum((v-tool)*normal,axis=1),0)[:,None]*normal
def residual(v):
    a=np.zeros(12);a[free]=v;return (A@a+h*resistance(a.reshape(-1,3)).ravel()-rhs)[free]
sol=root(residual,np.zeros(9),tol=1e-12);ex=np.zeros(12);ex[free]=sol.x;info=b.implicit(h);q,v=b.arrays();error=float(np.max(abs(v.ravel()-ex)));power=float(np.sum(b.last_blade_dashpot.cpu().numpy()*(v-tool)));out={'scope':'Unilateral normal CAD dashpot, implicit coupled solve versus independent NumPy/scipy root','velocity_error_m_s':error,'position_error_m':float(np.max(abs(q-(q0+h*ex.reshape(-1,3))))),'independent_equation_residual':float(np.linalg.norm(residual(sol.x))),'active_dashpot_force_norm_N':float(np.linalg.norm(b.last_blade_dashpot.cpu().numpy())),'relative_dashpot_power_W':power,'solver':info,'passed':bool(error<1e-8 and np.linalg.norm(residual(sol.x))<1e-12 and power<0 and np.linalg.norm(b.last_blade_dashpot.cpu().numpy())>0)};(W/'blade_dashpot_control_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
