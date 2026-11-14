"""Read-only local linearization of saved states, not a new dynamics branch."""
from pathlib import Path
import sys,json,time,numpy as np
from scipy.sparse import kron,eye
from scipy.sparse.linalg import LinearOperator,eigsh
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from fixtures import make
from front_system import FrontSystem
start=time.perf_counter();rows={}
for label,s in [('intact',make().cpu),('front_50um',FrontSystem.restore(W/'runs/gpu/initial.npz')),('front_25um',FrontSystem.restore(W/'runs/gpu/spatial_initial.npz'))]:
    p=s.pieces['root'];q=p.q.copy();n=q.size;calls=[0]
    def K(v):
        calls[0]+=1;h=1e-9/max(np.linalg.norm(v),1e-30);d=v.reshape(q.shape)
        return (-(p.energy_force(q+h*d)[1]-p.energy_force(q-h*d)[1])/(2*h)).ravel()
    op=LinearOperator((n,n),matvec=K,dtype=float);M=kron(p.M,eye(3),format='csr');inv=LinearOperator((n,n),matvec=lambda x:p.factor.solve(x.reshape(q.shape)).ravel(),dtype=float)
    t=time.perf_counter();lam,V=eigsh(op,k=1,M=M,Minv=inv,which='LA',tol=1e-5,maxiter=100,ncv=12,v0=np.random.default_rng(71).normal(size=n));v=V[:,0];r=np.linalg.norm(K(v)-lam[0]*(M@v))/max(np.linalg.norm(K(v)),1e-30);omega=float(np.sqrt(lam[0]));dt=3.90625e-7
    rows[label]={'largest_linearized_angular_frequency_rad_s':omega,'mode_period_s':2*np.pi/omega,'linear_Verlet_stability_limit_s':2/omega,'primary_dt_omega':dt*omega,'primary_steps_per_fast_period':2*np.pi/(dt*omega),'eigen_residual_relative':float(r),'matvec_calls':calls[0],'wall_s':time.perf_counter()-t,'dofs':len(q)}
    print(label,rows[label],flush=True)
out={'results':rows,'wall_s':time.perf_counter()-start,'scope':'Tangent stiffness finite differences with full consistent mass at saved initial fields. Largest linearized mode only; not a proof of nonlinear stability or force convergence. No material, timestep or trajectory changed.'}
(W/'mode_audit.json').write_text(json.dumps(out,indent=2,allow_nan=False))
