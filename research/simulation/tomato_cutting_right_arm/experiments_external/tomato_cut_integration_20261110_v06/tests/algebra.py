from pathlib import Path
import sys,json,time,numpy as np
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from integrated_cut import IntegratedCut,RejectedEvent
from continuous_volume import certificate,box_certificate
from reference import block
X=block(8,.0015);b=IntegratedCut(X);checks={};results={};start=time.monotonic()
def write():
    for k in checks:checks[k]=bool(checks[k])
    out={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'results':results,'wall_s':time.monotonic()-start,'scope':'Integration and prescribed topology algebra only'}
    (W/'algebra_controls.json').write_text(json.dumps(out,indent=2,allow_nan=False));print(json.dumps(out,indent=2,allow_nan=False))
m=b.rho*b.volumes;expected=.012**3*1000;mass=float(m.sum());com=(m@b.points)/mass;second=b.points.T@(m[:,None]*b.points);target=np.eye(3)*expected*.012**2/12
results['box_integrals']={'mass':mass,'mass_relative_error':abs(mass-expected)/expected,'center_m':com.tolist(),'second_moment_relative_error':float(np.linalg.norm(second-target)/np.linalg.norm(target)),'quadrature_points':len(m),'mass_condition':b.audit['mass_condition']}
checks['box_integrals']=results['box_integrals']['mass_relative_error']<1e-10 and np.max(abs(com))<1e-14 and results['box_integrals']['second_moment_relative_error']<1e-10
U,f=b.energy_force(b.q);checks['rest']=abs(U)<1e-12 and np.max(abs(f))<1e-9
F=np.array([[1.01,.003,0],[0,.99,.002],[0,0,1.005]]);b.q=b.q@F.T;b.update_state();U,f=b.energy_force(b.q);J=np.linalg.det(F);analytic=.012**3*(b.mu/2*(np.sum(F*F)-3)-b.mu*np.log(J)+b.lam/2*np.log(J)**2)
checks['affine_energy']=abs(U-analytic)<max(1e-12,abs(analytic)*1e-10)
rot=Rotation.from_rotvec([.1,.2,.3]).as_matrix();Ur,fr=b.energy_force(b.q@rot.T+[.03,-.01,.02]);checks['objectivity']=abs(Ur-U)<1e-12 and np.max(abs(fr-f@rot.T))<1e-10
checks['force_balance']=np.linalg.norm(b.translation@f)<1e-10 and np.linalg.norm(np.cross(b.q,f).sum(0))<1e-10
rng=np.random.default_rng(114);b.q+=rng.normal(size=b.q.shape)*1e-6;b.vg=rng.normal(size=b.vg.shape)*.001;b.update_state();u,f=b.energy_force(b.q);dq=rng.normal(size=b.q.shape)*.001;eps=1e-6;fd=(b.energy_force(b.q+eps*dq)[0]-b.energy_force(b.q-eps*dq)[0])/(2*eps);exact=-np.sum(f*dq);results['energy_gradient_relative']=float(abs(fd-exact)/max(abs(exact),1e-12));checks['energy_gradient']=results['energy_gradient_relative']<2e-5
high=IntegratedCut(X,order=7);high.q=b.q.copy();high.vg=b.vg.copy();high.update_state();uh,fh=high.energy_force(high.q);results['quadrature_comparison']={'energy_relative':float(abs(u-uh)/max(abs(uh),1e-12)),'force_relative':float(np.linalg.norm(f-fh)/max(np.linalg.norm(fh),1e-12))};checks['quadrature_convergence']=results['quadrature_comparison']['energy_relative']<1e-6 and results['quadrature_comparison']['force_relative']<1e-5
checks['continuous_volume']=all(c['passed'] for c in certificate(b));checks['inversion_control']=not box_certificate(b.knots,b.q@np.diag([1,-1,1]))['passed']
results['offsets']=[]
for plane in [0,.0003,.00075,.0015,.0029,-.0029,.0057,-.0057]:
    c=IntegratedCut(X);c.q=b.q.copy();c.vg=b.vg.copy();c.update_state();before=c.fingerprint()
    p=c.propose([0,.006,-.006,.006],plane);assert c.fingerprint()==before;c.commit(p)
    first=p['transfer'];c.q[c.base_ng:]+=rng.normal(size=(len(c.keys),3))*1e-8;c.update_state()
    p=c.propose([-.006,.006,-.006,.006],plane);c.commit(p)
    results['offsets'].append({'plane':plane,'mass_audit':c.audit,'first_transfer':first,'full_transfer':p['transfer'],'integration_points':len(c.volumes),'volume_bounds':certificate(c)})
    checks['offset_'+str(plane)]=all(v['passed'] for v in results['offsets'][-1]['volume_bounds']) and c.audit['mass_rank']==len(c.q)
c=IntegratedCut(X);before=c.fingerprint()
try:c.propose([-.006,.006,-.006,.006],.006-1e-10);checks['ultrathin_rejection']=False
except RejectedEvent as e:checks['ultrathin_rejection']=c.fingerprint()==before;results['ultrathin_rejection']={'reason':str(e),'detail':e.detail}
write()
assert all(checks.values()),checks
