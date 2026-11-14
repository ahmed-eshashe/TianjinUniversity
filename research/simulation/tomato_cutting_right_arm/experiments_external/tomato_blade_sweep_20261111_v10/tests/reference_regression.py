from pathlib import Path
import sys,json,time,numpy as np
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from multicut import MultiCut,full_rectangle,volume_certificates,RejectedEvent
from integrated_cut import IntegratedCut
from reference import block
X=block(8,.0015);s=MultiCut(X);checks={};results={};start=time.monotonic();rng=np.random.default_rng(217)
ref=IntegratedCut(X)
for _ in range(20):s.step(3.90625e-7);ref.step(3.90625e-7)
checks['uncut_equivalence']=all(np.array_equal(a,b) for a,b in zip(s.observations(),[ref.x,ref.v,ref.F]))
p=s.pieces['root'];p.q=p.q@np.diag([1,.99,1.002])+rng.normal(size=p.q.shape)*2e-7;p.vg=rng.normal(size=p.vg.shape)*.001;p.update_state()
records=[]
def event(pid,axis,plane,rectangle):
    before=s.fingerprint();oldobs=s.observations();old=s.metrics();proposal=s.propose(pid,axis,plane,rectangle);assert before==s.fingerprint();s.commit(proposal);m=s.metrics()
    diffs=[float(np.max(abs(a-b),initial=0)) for a,b in zip(oldobs,s.observations())];record={'piece':pid,'axis':axis,'plane':plane,'insertion':proposal.get('insertion'),'partition':proposal.get('partition'),'observed_transfer':diffs,'global_energy_change_J':m['energy']-old['energy'],'mass':m['mass'],'piece_ids':list(s.pieces)};records.append(record)
    assert max(diffs)<1e-10 and abs(m['energy']-old['energy'])<max(1e-12,abs(old['energy'])*1e-8)
    return proposal
event('root',0,-.0021,[0,.006,-.006,.006]);checks['first_partial_connected']=list(s.pieces)==['root']
p=s.pieces['root'];yy=np.linspace(-.006,.006,49);zz=np.linspace(-.006,.006,7);points=np.stack(np.meshgrid(yy,zz,indexing='ij'),axis=-1).reshape(-1,2);p.q[p.base_ng:,0]+=rng.normal(size=len(p.keys))*1e-7;p.update_state();jump=p.face_jump(points);checks['first_bridge']=np.linalg.norm(jump[points[:,0]<=0],axis=1).max()<1e-11 and np.linalg.norm(jump[points[:,0]>.001],axis=1).max()>1e-9
before=s.fingerprint();checks['repeat_noop']=s.propose('root',0,-.0021,[0,.006,-.006,.006])['noop'] and s.fingerprint()==before
try:s.propose('root',1,.0003,[-.006,.006,-.006,.006]);checks['overlapping_partial_rejected']=False
except RejectedEvent:checks['overlapping_partial_rejected']=s.fingerprint()==before
event('root',0,-.0021,full_rectangle(p,0));checks['first_complete_two_pieces']=len(s.pieces)==2
untouched=s.pieces['rootL'].fingerprint();event('rootR',0,.0021,full_rectangle(s.pieces['rootR'],0));checks['two_parallel_three_pieces']=len(s.pieces)==3 and s.pieces['rootL'].fingerprint()==untouched
middle=s.pieces['rootRL'];R=Rotation.from_rotvec([.15,.2,.1]).as_matrix();middle.q=middle.q@R.T+[.02,.01,.004];middle.vg=middle.vg@R.T+[.02,0,0];middle.update_state();outside={key:p.fingerprint() for key,p in s.pieces.items() if key!='rootRL'}
event('rootRL',1,.0003,[0,.0021,-.006,.006]);middle=s.pieces['rootRL'];checks['cross_partial_keeps_piece']=len(s.pieces)==3
xx=np.linspace(-.0021,.0021,37);points=np.stack(np.meshgrid(xx,zz,indexing='ij'),axis=-1).reshape(-1,2);middle.q[middle.base_ng:,1]+=rng.normal(size=len(middle.keys))*1e-8;middle.update_state();jump=middle.face_jump(points);checks['cross_bridge']=np.linalg.norm(jump[points[:,0]<=0],axis=1).max()<1e-11 and np.linalg.norm(jump[points[:,0]>.0005],axis=1).max()>1e-10
event('rootRL',1,.0003,full_rectangle(middle,1));checks['cross_four_pieces']=len(s.pieces)==4 and all(s.pieces[k].fingerprint()==v for k,v in outside.items())
checks['volumes']=all(c['passed'] for p in s.pieces.values() for c in volume_certificates(p))
s.save(W/'runs/three_cut_loaded.npz')
event('rootL',2,.0004,full_rectangle(s.pieces['rootL'],2));checks['four_cut_capacity']=s.cut_count==4 and len(s.pieces)==5
before=s.fingerprint()
try:s.propose('rootRR',1,.0006,full_rectangle(s.pieces['rootRR'],1));checks['overflow_rejected']=False
except RejectedEvent:checks['overflow_rejected']=s.fingerprint()==before
checks['mass_conserved']=abs(s.metrics()['mass']-.001728)<1e-12
results['events']=records;results['final_mass_kg']=s.metrics()['mass'];results['final_piece_count']=len(s.pieces);results['basis_counts']={k:len(p.q) for k,p in s.pieces.items()};results['mass_conditions']={k:p.audit['mass_condition'] for k,p in s.pieces.items()}
out={'status':'pass_restricted_unit_scope' if all(checks.values()) else 'fail','checks':{k:bool(v) for k,v in checks.items()},'results':results,'wall_s':time.monotonic()-start,'scope':'Reference-axis sequential prescribed cuts, one active partial per connected fragment. No contact or physical fracture.'};(W/'algebra_controls.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert all(checks.values()),checks
