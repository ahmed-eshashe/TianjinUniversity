from pathlib import Path
import sys,json,numpy as np,time
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from cut_reference import CutReference,RejectedEvent
from reference import block
rng=np.random.default_rng(936);X=block(8,.0015);b=CutReference(X);b.q=b.q@np.diag([1,.99,1]).T+rng.normal(size=b.q.shape)*1e-6;b.vg=rng.normal(size=b.q.shape)*.001;b.update_state();checks={};out={};before=b.fingerprint();p=b.propose([0,.006,-.006,.006]);checks['preview_pure']=b.fingerprint()==before;out['partial_proposal']={k:p[k] for k in ['audit','transfer']};b.commit(p);checks['partial_commit']=len(b.keys)==24
for name,rect in [('repeat',[0,.006,-.006,.006]),('reverse',[.003,.006,-.006,.006])]:
 old=b.fingerprint();p=b.propose(rect);checks[name]=p['noop'] and not b.commit(p) and b.fingerprint()==old
# Directly perturb new coefficients only to expose their trace support.
b.q[b.base_ng:]+=rng.normal(size=(len(b.keys),3))*1e-6;b.update_state();yy=np.linspace(-.006,.006,97);zz=np.linspace(-.006,.006,7);yz=np.stack(np.meshgrid(yy,zz,indexing='ij'),axis=-1).reshape(-1,2);j=b.face_jump(yz);ahead=np.linalg.norm(j[yz[:,0]<=0],axis=1).max();behind=np.linalg.norm(j[yz[:,0]>.001],axis=1).max();out['jump_support']={'ahead_max_m':float(ahead),'behind_max_m':float(behind)};checks['finite_front']=ahead<1e-11 and behind>1e-8
# Independent energy directional derivative after topology extension.
E,f=b.energy_force(b.q);dq=rng.normal(size=b.q.shape)*.001;eps=1e-6;fd=(b.energy_force(b.q+eps*dq)[0]-b.energy_force(b.q-eps*dq)[0])/(2*eps);g=-np.sum(f*dq);out['force_gradient_relative']=float(abs(fd-g)/max(abs(g),1e-12));checks['force_gradient']=out['force_gradient_relative']<2e-5
p=b.propose([-.006,.006,-.006,.006]);out['full_proposal']={k:p[k] for k in ['audit','transfer']};b.commit(p);checks['full_release']=len(b.keys)==72;b.save(W/'runs/full_loaded.npz')
# Check full-space support as two independent continuous blocks, not a raw graph of enriched coefficients.
from consistent_reference import ConsistentReference
l=ConsistentReference(X[X[:,0]<0]);r=ConsistentReference(X[X[:,0]>0]);b.set_full_piece_state(l.q,r.q);checks['full_rest']=abs(b.metrics()['energy'])<1e-12
r.q+=np.array([.003,0,0]);r.update_state();b.set_full_piece_state(l.q,r.q);U,f=b.energy_force(b.q);out['rigid_piece_shift_energy']=U;out['rigid_piece_shift_max_force']=float(abs(f).max());checks['rigid_piece_shift_no_elastic_load']=abs(U)<1e-12 and abs(f).max()<1e-9
# Off-grid configuration deliberately reveals unsupported small-support modes; rejection must precede mutation.
c=CutReference(X);before=c.fingerprint()
try:c.commit(c.propose([-.006,.006,-.006,.006],plane=.0003));out['off_grid']={'accepted':True};checks['off_grid_rejected']=False
except RejectedEvent as e:out['off_grid']={'accepted':False,'reason':str(e),'detail':e.detail};checks['off_grid_rejected']=c.fingerprint()==before
out['mass_kg']=b.mass*b.n;checks['mass']=abs(out['mass_kg']-.001728)<1e-15
result={'status':'pass_restricted_unit_scope' if all(checks.values()) else 'fail','checks':checks,'results':out,'scope':'Single aligned finite-front topology fixtures, no physical cutting. Off-grid cut is explicitly unsupported.'};(W/'algebra_controls.json').write_text(json.dumps(result,indent=2,default=lambda v:v.item()));print(json.dumps(result,indent=2,default=lambda v:v.item()))
