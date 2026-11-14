from pathlib import Path
import itertools,json,numpy as np,torch
from normal_operator import NormalContact
W=Path(__file__).resolve().parent
rng=np.random.default_rng(30);dtype=torch.float64
ids=np.array([[0,1],[1,2],[2,2]]);u=np.array([.3,.6,0.]);weights=np.array([.7,.4,1.])
n=rng.normal(size=(3,3));n/=np.linalg.norm(n,axis=1)[:,None]
phi=np.array([-2e-5,-3e-5,-4e-5]);tool=np.array([.01,-.02,.03]);h=3.125e-6;ke=2e6
v=torch.tensor(rng.normal(size=(3,3))*.02,dtype=dtype);p=torch.tensor(rng.normal(size=(3,3)),dtype=dtype)
op=NormalContact(ids,u,n,weights,phi,tool,h,ke,device='cpu')
B=np.zeros((3,9))
for j,(a,b) in enumerate(ids):
 B[j,3*a:3*a+3]+=(1-u[j])*n[j];B[j,3*b:3*b+3]+=u[j]*n[j]
offset=phi-h*np.einsum('ij,j->i',n,tool)
gap=offset+h*B@v.numpy().ravel();expected=(B.T@(ke*weights*np.minimum(gap,0))).reshape(3,3)
H=B.T@np.diag(ke*h*weights*(gap<0))@B
checks={}
checks['force_error_N']=float(np.max(abs(op.apply(v).numpy()-expected)))
checks['hessian_error']=float(np.max(abs(op.hessian(p,v).numpy().ravel()-H@p.numpy().ravel())))
checks['diagonal_error']=float(np.max(abs(op.diagonal(v).numpy().ravel()-np.diag(H))))
vv=v.clone().requires_grad_();grad=torch.autograd.grad(op.energy(vv),vv)[0]
checks['energy_gradient_error_N']=float((grad-op.apply(v)).abs().max())
initial={k:x.clone() for k,x in vars(op).items() if isinstance(x,torch.Tensor)}
for _ in range(4):op.apply(v+p);op.energy(v-p);op.hessian(p,v)
checks['trial_purity']=all(torch.equal(getattr(op,k),x) for k,x in initial.items())
reset=NormalContact(ids,u,n,weights,phi,tool,h,ke,device='cpu')
checks['fresh_reset']=torch.equal(op.apply(v),reset.apply(v))
# Independent dense enumeration of all unilateral active sets. This solves
# a mass-only frozen-contact implicit step exactly, without the operator.
mass=np.linspace(.03,.05,9);rhs=rng.normal(size=9)*.02
solution=None
for bits in itertools.product([False,True],repeat=3):
 active=np.array(bits);K=np.diag(ke*weights*active)
 sol=np.linalg.solve(np.diag(mass)+h*h*B.T@K@B,mass*rhs-h*B.T@K@offset)
 gg=offset+h*B@sol
 if np.all(gg[active]<=1e-12) and np.all(gg[~active]>=-1e-12):solution=sol;break
assert solution is not None
tv=torch.tensor(rhs.reshape(3,3),dtype=dtype);M=torch.tensor(mass.reshape(3,3),dtype=dtype)
for iteration in range(20):
 residual=M*(tv-torch.tensor(rhs.reshape(3,3)))+h*op.apply(tv)
 if residual.norm()<1e-14:break
 eye=torch.eye(9,dtype=dtype);matrix=torch.stack([(M*eye[j].reshape(3,3)+h*op.hessian(eye[j].reshape(3,3),tv)).ravel() for j in range(9)],dim=1)
 tv-=torch.linalg.solve(matrix,residual.ravel()).reshape(3,3)
checks['independent_dense_velocity_error_m_s']=float(np.max(abs(tv.numpy().ravel()-solution)))
# Covariance, force and moment use embedded sample positions independently.
Q,_=np.linalg.qr(rng.normal(size=(3,3)));Q[:,0]*=np.linalg.det(Q)
rot=NormalContact(ids,u,n@Q.T,weights,phi,tool@Q.T,h,ke,device='cpu')
rf=rot.apply(torch.tensor(v.numpy()@Q.T,dtype=dtype)).numpy()
checks['rigid_force_error_N']=float(np.max(abs(rf-op.apply(v).numpy()@Q.T)))
q=rng.normal(size=(3,3));sample=(1-u[:,None])*q[ids[:,0]]+u[:,None]*q[ids[:,1]]
sf=(ke*weights*np.minimum(gap,0))[:,None]*n
checks['wrench_error_Nm']=float(np.max(abs(np.cross(q,op.apply(v).numpy()).sum(0)-np.cross(sample,sf).sum(0))))
outside=NormalContact(ids,u,n,weights,np.ones(3),tool,h,ke,device='cpu')
checks['no_adhesion']=bool(torch.equal(outside.apply(v),torch.zeros_like(v)))
# Static independently constrained benchmark: elastic support K at q0<wall,
# admissible q>=wall. KKT solution is q=wall, reaction=K*(wall-q0).
# This chooses penalty accuracy independently of tomato damage or appearance.
K=100.;q0=-.001;target_force=.1;levels=[]
for stiffness in [2e4,2e5,2e6]:
 q=K*q0/(K+stiffness);force=-stiffness*q
 levels.append({'stiffness_N_per_m':stiffness,'penetration_m':-q,'force_N':force,'constrained_force_N':target_force,'relative_force_error':abs(force-target_force)/target_force})
last,prev=levels[-1],levels[-2]
converged=abs(last['penetration_m']-prev['penetration_m'])<=1e-4 and abs(last['force_N']-prev['force_N'])/last['force_N']<=.05 and last['penetration_m']<=1e-4 and last['relative_force_error']<=.05
passed=all(vv is True if isinstance(vv,bool) else vv<1e-10 for vv in checks.values()) and converged
out={'scope':'Independent normal-contact operator/velocity-step/benchmark controls only; no tomato contact or fracture pass','checks':checks,'stiffness_benchmark':levels,'selected_stiffness_N_per_m':last['stiffness_N_per_m'] if converged else None,'benchmark_converged':converged,'passed':passed}
(W/'controls_result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));assert passed
