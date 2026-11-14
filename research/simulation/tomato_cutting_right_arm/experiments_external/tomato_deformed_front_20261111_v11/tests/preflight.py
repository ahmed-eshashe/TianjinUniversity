from pathlib import Path
import sys,json,time,numpy as np
from scipy.interpolate import BSpline
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from front_system import FrontSystem
from deformed_sweep import DeformedSweep
from blade_sweep import pose
from reference import block
from integrated_cut import greville
from planar_chart import PlanarChart
start=time.perf_counter();checks={};results={}
def check(k,v):
    checks[k]=bool(v)
    if not v:raise AssertionError(k)
def set_field(p):
    X=greville(p.knots);vals=[BSpline(t,np.eye(len(t)-3),2)(X[:,i]) for i,t in enumerate(p.knots)];N=np.einsum('pi,pj,pk->pijk',*vals).reshape(len(X),-1)
    y=X.copy();y[:,1]=.99*X[:,1]+2*X[:,1]**2+1.5*X[:,0]**2
    p.q=np.linalg.solve(N,y);p.vg=np.tile([.01,-.02,.03],(len(p.q),1));p.update_state()
def world_y(y):return .99*y+2*y*y+1.5*.0003**2
s=FrontSystem(block(8,.0015));set_field(s.pieces['root']);d=DeformedSweep(s,pose([.0003,world_y(.0061),0]))
before=d.cpu.observations();energy=d.cpu.metrics()['energy'];fp=d.fingerprint()
p=d.propose(pose([.0003,world_y(.00595),0]));check('preview_immutable',fp==d.fingerprint());d.commit(p)
b=d.cpu.pieces['root'];check('fifty_micron_depth_activates_partial',b.plane is not None and len(d.cpu.pieces)==1)
check('fields_preserved',max(np.max(abs(a-c)) for a,c in zip(before,d.cpu.observations()))<1e-10)
check('energy_preserved',abs(d.cpu.metrics()['energy']-energy)<max(1e-12,abs(energy)*1e-8))
check('front_inversion',abs(d.commands[-1]['charts'][0]['front']-.00595)<1e-11)
check('rank_condition',b.audit['mass_condition']<1e8)
q=b.q.copy();b.q[b.base_ng:,0]+=1e-8;b.update_state();pts=np.array([[.005925,0],[.00595,0],[.005975,0]])
jump=b.face_jump(pts);check('intact_ahead_and_at_front',np.max(abs(jump[:2]))<1e-11);check('opening_mode_behind_front',np.linalg.norm(jump[2])>1e-10);b.q=q;b.update_state()
results={'condition':b.audit,'dofs':len(b.q),'transfer':d.commands[-1]['changes'][0]['transfer'],'chart':d.commands[-1]['charts'][0],'jump_probe_m':jump.tolist(),'wall_s':time.perf_counter()-start}
d.save(W/'runs/shallow_preflight')
restored=DeformedSweep.restore(W/'runs/shallow_preflight');check('checkpoint_exact',restored.fingerprint()==d.fingerprint())
out={'status':'pass_shallow_preflight','checks':checks,'results':results};(W/'preflight.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
