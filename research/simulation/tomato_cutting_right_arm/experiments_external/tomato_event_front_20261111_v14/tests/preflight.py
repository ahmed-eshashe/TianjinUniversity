from pathlib import Path
import sys,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from fixtures import assign,world_y
from band_system import BandSystem
from blade_sweep import pose,Blade
from event_sweep import EventSweep,clone_cpu
from reference import block
from gpu_backend import GPUReference
from multicut import volume_certificates
from integrated_cut import RejectedEvent
checks={};results={}
def check(k,v):
    checks[k]=bool(v)
    if not v:raise AssertionError(k)
def make(**kw):
    s=BandSystem(block(8,.0015));assign(s.pieces['root']);p=pose([.0003,world_y(.0061),0]);b=s.current_band(Blade(),p);s.initialize_band(b);return EventSweep(s,p,**kw)
if __name__=='__main__':
    start=time.perf_counter();d=make();results['transfer']=d.cpu.initial_transfer;results['band']=d.cpu.band;p=d.cpu.pieces['root']
    check('band_initially_uncut',p.plane is None and len(p.keys)==0 and not d.cpu.events)
    check('band_mass',abs(d.cpu.metrics()['mass']-.001728)<1e-12)
    check('continuous_volume',all(c['passed'] for c in volume_certificates(p)))
    check('capacity',len(p.q)<=1000);results['dofs']=len(p.q);results['mass_condition']=p.audit['mass_condition']
    for frac in [.27,.73]:
        c=clone_cpu(d.cpu);gcpu=clone_cpu(d.cpu);dt=d.dt*frac;c.step(dt);g=GPUReference(gcpu,dt=dt);g.step(1);g.export()
        err={f:float(np.max(abs(getattr(c.pieces['root'],f)-getattr(gcpu.pieces['root'],f)))) for f in ['q','vg']}
        check('fractional_equivalence_'+str(frac),err['q']<1e-11 and err['vg']<1e-8);results['fraction_'+str(frac)]=err
    before=d.fingerprint();p=d.propose(pose([.0003,world_y(.00594),0]),preview_only=True)
    check('preview_would_release',p['topology_changed']);check('preview_read_only',before==d.fingerprint())
    try:d.commit(p);check('preview_commit_rejected',False)
    except RejectedEvent:check('preview_commit_rejected',True)
    for name,t in [('hold',d.pose),('reverse',pose([.0003,world_y(.0062),0])),('miss',pose([.0003,world_y(.00605),.2]))]:
        p=d.propose(t,preview_only=True);check(name+'_no_release',not p['topology_changed'])
    for name,target in [('off_plane',pose([.0004,world_y(.0059),0])),('outside_band',pose([.0003,world_y(.0056),0]))]:
        old=d.fingerprint()
        try:
            if name=='off_plane':d.guard_pose(target)
            else:d.propose(target,preview_only=True)
            check(name+'_rejected',False)
        except RejectedEvent:check(name+'_rejected',True)
        check(name+'_no_mutation',old==d.fingerprint())
    d.save(W/'runs/preflight');r=EventSweep.restore(W/'runs/preflight');check('initial_restart',d.fingerprint()==r.fingerprint())
    (W/'preflight.json').write_text(json.dumps({'checks':checks,'results':results,'wall_s':time.perf_counter()-start},indent=2));print(json.dumps({'checks':checks,'results':results},indent=2))
