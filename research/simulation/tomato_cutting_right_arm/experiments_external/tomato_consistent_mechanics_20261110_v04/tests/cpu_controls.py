from pathlib import Path
import sys,numpy as np,json,time
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from consistent_reference import ConsistentReference
from reference import block
from scipy.spatial.transform import Rotation
from scipy.interpolate import BSpline
from block_basis import block_basis
X=block(8,.0015);rng=np.random.default_rng(781);b=ConsistentReference(X);checks={};out={};t0=time.monotonic()
# Partition, linear reproduction, force/energy directional derivative and objectivity.
R=Rotation.from_rotvec([.3,-.2,.1]).as_matrix();b.initialize(F=np.diag([1,.99,1]));E,f=b.energy_force(b.q);dq=rng.normal(size=b.q.shape)*.001;eps=1e-6;fd=(b.energy_force(b.q+eps*dq)[0]-b.energy_force(b.q-eps*dq)[0])/(2*eps);grad=-float(np.sum(f*dq));err=abs(fd-grad)/max(abs(grad),1e-12);out['gradient_relative_error']=err;checks['force_energy']=err<2e-5
Er,fr=b.energy_force(b.q@R.T);out['objectivity_energy_error']=abs(E-Er);out['objectivity_force_error']=float(abs(fr-f@R.T).max());checks['objectivity']=abs(E-Er)<1e-12 and abs(fr-f@R.T).max()<1e-9
# Physical angular momentum has no added APIC affine energy; full mass is exact particle quadrature.
for name in ['translation','rotated_rest','spin','external','supported']:
 fixed=np.isclose(X[:,1],X[:,1].min()) if name=='supported' else None;b=ConsistentReference(X,fixed=fixed);force=None
 if name=='translation':b.initialize(velocity=np.tile([.01,-.02,.005],(len(X),1)))
 if name=='rotated_rest':b.initialize(F=R)
 if name=='spin':b.initialize(affine_velocity=np.array([[0,-1.,0],[1.,0,0],[0,0,0]]))
 if name in ['external','supported']:force=rng.normal(size=X.shape)*.0001
 initial=b.metrics();x0=b.x.copy();v0=b.v.copy();imp=np.zeros(3);mom=np.zeros(3);dt=12.5e-6
 for i in range(40):
  oldx=b.x.copy();b.step(dt,force)
  if force is not None:imp+=dt*force.sum(0);mom+=.5*dt*np.cross(oldx+b.x,force).sum(0)
 final=b.metrics();pe=float(np.linalg.norm(final['momentum']-initial['momentum']-imp-b.support_impulse));Le=float(np.linalg.norm(final['angular']-initial['angular']-mom-b.support_moment));r={'momentum_residual':pe,'angular_residual':Le,'energy_change':final['energy']-initial['energy']}
 if name in ['translation','rotated_rest']:r['rigid_error']=float(abs(b.x-x0-b.time*v0).max());checks[name+'_position']=r['rigid_error']<1e-10
 if name=='supported':r['support_drift']=float(abs(b.x[fixed]-X[fixed]).max());checks['supported_position']=r['support_drift']<1e-9
 checks[name+'_balance']=pe<1e-9 and Le<1e-10;out[name]=r
# Genuine particle null mode removed once on initialize; represented mode retained, no recurring filter.
b=ConsistentReference(X);A=b.W.toarray();U,s,V=np.linalg.svd(A,full_matrices=False);z=rng.normal(size=X.shape);z-=U@(U.T@z);z*=.02/abs(z).max();b.initialize(velocity=z);out['null_velocity_ratio']=float(np.linalg.norm(b.v)/np.linalg.norm(z));checks['null_filter']=out['null_velocity_ratio']<1e-8
b=ConsistentReference(X);c=rng.normal(size=b.q.shape)*.001;b.initialize(velocity=A@c);out['resolved_velocity_error']=float(abs(b.v-A@c).max());checks['resolved_projection']=out['resolved_velocity_error']<1e-10
# Derive geometry gradients by independent centered evaluation of the continuous basis, not time integration.
b.q+=rng.normal(size=b.q.shape)*1e-6;b.update_state();_,_,_,_,meta=block_basis(X,.0015,.003);Q=b.q.reshape(*meta['dims'],3);Fg=[];eps=1e-8
for point in X[::31]:
 cols=[]
 for j in range(3):
  xx=point.copy();xx[j]+=eps;aa=[BSpline(t,np.eye(len(t)-3),2)(xx[k]) for k,t in enumerate(meta['knots'])];xp=np.einsum('i,j,k,ijkc->c',*aa,Q)
  xx[j]-=2*eps;aa=[BSpline(t,np.eye(len(t)-3),2)(xx[k]) for k,t in enumerate(meta['knots'])];xm=np.einsum('i,j,k,ijkc->c',*aa,Q);cols.append((xp-xm)/(2*eps))
 Fg.append(np.stack(cols,axis=1))
out['geometry_F_fd_error']=float(abs(np.array(Fg)-b.F[::31]).max());checks['geometry_gradient']=out['geometry_F_fd_error']<1e-8
result={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'results':out,'wall_s':time.monotonic()-t0};(W/'cpu_controls.json').write_text(json.dumps(result,indent=2,default=lambda v:v.item()));print(json.dumps(result,indent=2,default=lambda v:v.item()))
