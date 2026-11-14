"""Offline path-informed fixture to distinguish activation timing from space."""
from pathlib import Path
from datetime import datetime,timezone
import sys,copy,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from deformed_sweep import DeformedSweep
from front_system import FrontSystem,prolongation
from multicut import CutPiece,MultiCut,kron3,volume_certificates
from gpu_backend import GPUReference
B=W.parent/'tomato_deformed_face_20261111_v12';R=W/'runs';checks={};results={};states={};start=time.perf_counter()
def progress(s):
    (W/'status.json').write_text(json.dumps({'updated':datetime.now(timezone.utc).isoformat(),'status':'common_space_running' if s else 'common_space_complete','current':s,'simulation_running':bool(s),'production_changed':False},indent=2));print(s,flush=True)
def check(k,v,details=None):
    checks[k]=bool(v)
    if not v:raise AssertionError((k,details))
def load(name):return DeformedSweep.restore(B/'runs/coupled'/name)
first=load('half_dt_frame1');final=load('half_action_frame4');base=[t.copy() for t in final.cpu.pieces['root'].meta['knots']]
coarse=load('half_dt_frame2');coarse_rect=coarse.histories['root']['rectangles'];fine_mid=load('half_action_frame3').histories['root']['rectangles'];fine_final=final.histories['root']['rectangles']
def common():
    d=load('half_dt_frame1');s=d.cpu;old=s.pieces['root'];p=CutPiece(base,old.X,old.indices,old.order,old.E,old.nu,old.rho,old.fixed)
    p.commit(p.propose(d.histories['root']['rectangles'],old.plane,old.axis))
    A=kron3([prolongation(a,b) for a,b in zip(old.knots,p.knots)]);fullQ=A@(old.T@old.q);fullV=A@(old.T@old.vg);T=p.T.toarray();P=np.linalg.lstsq(T,(A@old.T).toarray(),rcond=None)[0]
    p.q=P@old.q;p.vg=P@old.vg;p.time=old.time;p.steps=old.steps;p.support_impulse=old.support_impulse.copy();p.support_moment=old.support_moment.copy();p.update_state()
    inertia=float(np.linalg.norm(P.T@p.M@P-old.M.toarray())/np.linalg.norm(old.M.toarray()))
    errors={k:float(np.max(abs(getattr(p,k)-getattr(old,k)))) for k in ['x','v','F']};errors.update(energy=p.metrics()['energy']-old.metrics()['energy'],energy_before=old.metrics()['energy'],mass=p.metrics()['mass']-old.metrics()['mass'],inertia_pullback=inertia)
    check('common_initial_fields',errors['x']<1e-11 and errors['v']<1e-10 and errors['F']<1e-10,errors);check('common_initial_energy',abs(errors['energy'])<max(1e-12,abs(errors['energy_before'])*1e-8));check('common_initial_mass',abs(errors['mass'])<1e-12 and inertia<1e-10)
    p.history=copy.deepcopy(old.history);s.pieces={'root':p};results['initial_transfer']=errors;return s
def save(label,s):
    p=s.pieces['root'];np.savez_compressed(R/(label+'.npz'),q=p.q,vg=p.vg,T=p.T.toarray(),knots0=p.knots[0],knots1=p.knots[1],knots2=p.knots[2],x=p.x,v=p.v,F=p.F,time=s.time)
def run(label,native,schedule,dt):
    progress(label);s=load('half_dt_frame1').cpu if native else common();begin=s.metrics();wall=time.perf_counter();records=[]
    for endpoint,rect in schedule:
        gpu=GPUReference(s,dt=dt);gpu.step(round((endpoint-s.time)/dt));gpu.export();before=s.metrics();p=s.pieces['root']
        proposal=s.propose('root',0,p.plane,rect) if native else MultiCut.propose(s,'root',0,p.plane,rect)
        s.commit(proposal);after=s.metrics();records.append({'time_s':s.time,'dofs':len(s.pieces['root'].q),'insertion_energy_J':after['energy']-before['energy'],'insertion':proposal['insertion']})
        check(label+'_volume_'+str(len(records)),all(c['passed'] for c in volume_certificates(s.pieces['root'])))
    end=s.metrics();check(label+'_mass',abs(end['mass']-.001728)<1e-12);check(label+'_energy',abs(end['energy']-begin['energy'])<.05*begin['energy']);save(label,s)
    results[label]={'wall_s':time.perf_counter()-wall,'sim_window_s':.00005,'dt_s':dt,'records':records,'initial_energy_J':begin['energy'],'energy_residual_J':end['energy']-begin['energy'],'dofs':len(s.pieces['root'].q),'mass_condition':s.pieces['root'].audit['mass_condition']};states[label]=s
    if results[label]['wall_s']>300:raise TimeoutError(label)

late=[(.0001,coarse_rect)];early=[(.000075,fine_mid),(.0001,fine_final)]
run('native_late',True,late,3.90625e-7/32)
run('common_late',False,late,3.90625e-7/32)
run('common_early',False,early,3.90625e-7/32)
run('common_late_halfdt',False,late,3.90625e-7/64)
run('common_early_halfdt',False,early,3.90625e-7/64)

def difference(a,b):
    common=[]
    for ta,tb in zip(a.knots,b.knots):
        vals=[]
        for v in sorted(np.r_[ta,tb]):
            if not vals or abs(v-vals[-1])>1e-12:vals.append(float(v))
        common.append(np.array([v for v in vals for _ in range(max(np.count_nonzero(abs(ta-v)<1e-12),np.count_nonzero(abs(tb-v)<1e-12)))]))
    A=kron3([prolongation(a,t) for a,t in zip(a.knots,common)]);B_=kron3([prolongation(b,t) for b,t in zip(b.knots,common)])
    return {f:float(np.linalg.norm(A@(a.T@getattr(a,f))-B_@(b.T@getattr(b,f)),axis=1).max()) for f in ['q','vg']}
for label,sa,sb in [('native_reproduction','native_late',None),('timing_only','common_late','common_early'),('space_only','native_late','common_late'),('late_dt','common_late','common_late_halfdt'),('early_dt','common_early','common_early_halfdt')]:
    a=states[sa].pieces['root'];b=(coarse.cpu if sb is None else states[sb]).pieces['root'];e=difference(a,b);results[label]=e
    if label=='native_reproduction':check(label,e['q']<1e-10 and e['vg']<1e-8,e)
    if label.endswith('_dt'):check(label+'_position',e['q']<.0001);check(label+'_velocity',e['vg']<.005,e)
a,b=states['common_late'].pieces['root'],states['common_early'].pieces['root'];check('same_final_approximation_space',all(np.array_equal(x,y) for x,y in zip(a.knots,b.knots)) and np.max(abs(a.T.toarray()-b.T.toarray()))<1e-12)
out={'status':'offline_diagnosis_complete','checks':checks,'results':results,'wall_s':time.perf_counter()-start,'online_backend':False,'physical_fracture':False,'production_changed':False};(W/'common_space_controls.json').write_text(json.dumps(out,indent=2,allow_nan=False));progress(None);print(json.dumps({k:results[k] for k in ['timing_only','space_only','late_dt','early_dt']},indent=2))
