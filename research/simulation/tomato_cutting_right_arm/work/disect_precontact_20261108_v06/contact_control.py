from pathlib import Path
import json,sys,numpy as np
from scipy.optimize import root
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W/'backend'))
from numerics import load_arrays,numpy_force,tensor
from contact_numerics import ContactBulk
z=load_arrays();x=np.array([[0.,.0009,0.],[.01,.0009,0.],[0.,.0109,0.],[0.,.0009,.01]]);dm=np.linalg.inv((x[1:]-x[0]).T)[None];small={'x':x,'tet_indices':np.array([[0,1,2,3]]),'tet_poses':dm,'tet_mu':z['tet_mu'][:1],'tet_lambda':z['tet_lambda'][:1],'tet_damping':z['tet_damping'][:1],'tet_activations':np.zeros(1),'physical_mass':np.full(4,.00004),'particle_inv_mass':np.array([0.,25000,25000,25000]),'gravity':z['gravity'],'contact_mask':np.ones(4),'fixed':np.array([0])}
b=ContactBulk(small);b.v.copy_(tensor([[0,0,0],[.002,0,-.002],[.0002,0,.0004],[-.002,0,.002]]));qx,vx=b.arrays();f0=numpy_force(small,qx,np.zeros_like(qx));C=np.empty((12,12))
for j in range(12):
    v=np.zeros((4,3));v.ravel()[j]=1;C[:,j]=-(numpy_force(small,qx,v)-f0).ravel()
h=7.462686567164179e-6;mass=np.repeat(small['physical_mass'],3);normal=np.zeros_like(x);normal[:,1]=1000*np.maximum(.001-x[:,1],0);limit=np.zeros_like(x);limit[:,[0,2]]=.2*normal[:,1,None];kf=np.zeros_like(x);kf[x[:,1]<.001,0]=1000;kf[x[:,1]<.001,2]=1000;A=np.diag(mass)+h*C;rhs=mass*vx.ravel()+h*(f0+normal+small['physical_mass'][:,None]*small['gravity']).ravel();free=np.arange(3,12)
def residual(v):
    a=np.zeros(12);a[free]=v;return (A@a+h*np.clip(kf.ravel()*a,-limit.ravel(),limit.ravel())-rhs)[free]
def jac(v):
    a=np.zeros(12);a[free]=v;return (A+np.diag(h*kf.ravel()*(abs(kf.ravel()*a)<=limit.ravel())))[free][:,free]
sol=root(residual,np.zeros(9),jac=jac,tol=1e-12);ex=np.zeros(12);ex[free]=sol.x;info=b.implicit(h);q,v=b.arrays();ve=float(np.max(abs(v.ravel()-ex)));qe=float(np.max(abs(q-(qx+h*ex.reshape(-1,3)))));power=float(np.sum(-np.clip(kf*v,-limit,limit)*v));ind_res=float(np.linalg.norm(residual(sol.x)));b.reset();cleared=bool(np.max(abs(b.arrays()[1]))==0)
out={'scope':'Independent four-node monolithic implicit-friction root reference','independent_root_success':bool(sol.success),'independent_residual_norm':ind_res,'position_error_m':qe,'velocity_error_m_s':ve,'friction_power_W':power,'solver':info,'reset_velocity_cleared':cleared,'passed':bool(ind_res<1e-12 and qe<1e-10 and ve<1e-8 and power<=0 and cleared)};(W/'contact_control_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
