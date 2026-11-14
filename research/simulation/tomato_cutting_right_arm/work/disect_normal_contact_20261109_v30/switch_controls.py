"""Independent mixed-active/contact-entry cases; CPU only."""
from pathlib import Path
import itertools,json,numpy as np,torch
from normal_operator import NormalContact
W=Path(__file__).resolve().parent
ids=np.array([[0,1],[1,2],[2,2]]);u=np.array([.3,.6,0.])
n=np.eye(3);weights=np.array([.7,.4,1.]);h=3.125e-6;ke=2e6
B=np.zeros((3,9))
for j,(a,b) in enumerate(ids):
 B[j,3*a:3*a+3]+=(1-u[j])*n[j];B[j,3*b:3*b+3]+=u[j]*n[j]
mass=np.linspace(.00003,.00005,9);rng=np.random.default_rng(32);rows=[]
for case in range(12):
 rhs=rng.normal(size=9)*.1;phi=rng.normal(size=3)*2e-7;tool=rng.normal(size=3)*.01
 offset=phi-h*n@tool;answer=None
 for bits in itertools.product([False,True],repeat=3):
  active=np.array(bits);K=np.diag(ke*weights*active)
  v=np.linalg.solve(np.diag(mass)+h*h*B.T@K@B,mass*rhs-h*B.T@K@offset)
  gg=offset+h*B@v
  if np.all(gg[active]<=1e-13) and np.all(gg[~active]>=-1e-13):answer=v;break
 assert answer is not None
 op=NormalContact(ids,u,n,weights,phi,tool,h,ke,device='cpu')
 v=torch.tensor(rhs.reshape(3,3),dtype=torch.float64);M=torch.tensor(mass.reshape(3,3));rhs_t=v.clone()
 for iteration in range(30):
  residual=M*(v-rhs_t)+h*op.apply(v)
  if residual.norm()<1e-15:break
  eye=torch.eye(9,dtype=torch.float64)
  H=torch.stack([(M*e.reshape(3,3)+h*op.hessian(e.reshape(3,3),v)).ravel() for e in eye],dim=1)
  delta=torch.linalg.solve(H,residual.ravel()).reshape(3,3)
  objective=lambda vv:.5*(M*(vv-rhs_t).square()).sum()+h*op.energy(vv)
  old=objective(v);alpha=1.
  while objective(v-alpha*delta)>old and alpha>1e-10:alpha*=.5
  v-=alpha*delta
 error=float(np.max(abs(v.numpy().ravel()-answer)));assert error<1e-10
 rows.append(dict(case=case,active_contacts=int(active.sum()),velocity_error_m_s=error))
out=dict(scope='Independent active-set solutions with entry/exit and mixed unilateral activation',passed=True,cases=rows)
(W/'switch_controls_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
