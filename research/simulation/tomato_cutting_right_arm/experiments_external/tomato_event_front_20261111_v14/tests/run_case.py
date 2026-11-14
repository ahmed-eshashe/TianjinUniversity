from pathlib import Path
from datetime import datetime,timezone
import sys,json,time,traceback,resource,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from preflight import make
from fixtures import world_y
from blade_sweep import pose
from event_sweep import EventSweep
from multicut import volume_certificates
from integrated_cut import RejectedEvent
name=sys.argv[1];variants={'primary':{},'half_action':{},'half_probe':{'probe':12.5e-6},'half_dt':{'dt':3.90625e-7/32},'half_event':{'event_tol':1.25e-10},'heldout':{},'heldout_half_action':{},'heldout_half_dt':{'dt':3.90625e-7/32},'restart':{}}
start=time.perf_counter();checks={};result={'case':name,'status':'running','production_changed':False,'physical_fracture':False};case=W/'runs'/name;case.mkdir(exist_ok=True)
def check(k,v,details=None):
    checks[k]=bool(v)
    if not v:raise AssertionError((k,details))
def progress(message):
    data={'updated':datetime.now(timezone.utc).isoformat(),'status':message,'case':name,'simulation_running':True,'production_changed':False}
    (W/'status.json').write_text(json.dumps(data,indent=2));print(message,flush=True)
try:
    progress('constructing event-localized case')
    d=make(**variants[name]);initial=d.cpu.metrics();d.save(case/'initial')
    result['initial_energy_J']=initial['energy'];result['dt_s']=d.dt;result['probe_s']=d.probe;result['event_tolerance_s']=d.event_tol;result['initialization_s']=time.perf_counter()-start
    second=.00584 if name.startswith('heldout') else .00590
    route=[(0.,.0061),(50e-6,.00595),(100e-6,second)]
    half=name in ['half_action','heldout_half_action']
    energy=[]
    for index in range(1,len(route)):
        t0,y0=route[index-1];t1,y1=route[index];segments=2 if half or (name=='restart' and index==2) else 1
        # Split the exact SAME world-space command, not a different interpolated curve.
        for j in range(1,segments+1):
            endpoint=t0+(t1-t0)*j/segments;target_y=world_y(y0)+(world_y(y1)-world_y(y0))*j/segments
            progress(f'advancing to {endpoint:.9g} s')
            d.action(pose([.0003,target_y,0]),endpoint-d.cpu.time,wall_limit=300)
            energy.append({'time_s':d.cpu.time,**{k:float(d.cpu.metrics()[k]) for k in ['mass','energy']}})
            check('energy_'+str(endpoint),abs(energy[-1]['energy']-initial['energy'])<.05*initial['energy'])
            check('volume_'+str(endpoint),all(c['passed'] for p in d.cpu.pieces.values() for c in volume_certificates(p)))
            if name=='restart' and index==2 and j==1:
                check('restart_has_cut_history',bool(d.activations));d.save(case/'loaded_midpoint');token=d.fingerprint();d=EventSweep.restore(case/'loaded_midpoint');check('loaded_cut_restart_fingerprint',token==d.fingerprint())
        d.save(case/f'frame{index}')
        if index==1 and name=='restart':
            token=d.fingerprint();d=EventSweep.restore(case/'frame1');check('loaded_restart_fingerprint',token==d.fingerprint())
    p=d.cpu.pieces['root'];m=d.cpu.metrics();check('mass',abs(m['mass']-initial['mass'])<initial['mass']*1e-6);check('clock',abs(d.cpu.time-.0001)<1e-14);check('real_activation',len(d.activations)>0)
    check('bounded_events',all(e['bracket_width_s']<=d.event_tol for e in d.activations));check('unchanged_transfer_energy',all(abs(e['energy_jump_J'])<max(1e-12,initial['energy']*1e-8) for e in d.activations));check('unchanged_transfer_mass',all(abs(e['mass_jump_kg'])<initial['mass']*1e-6 for e in d.activations))
    y=np.linspace(-.006,.005849,65);z=np.linspace(-.006,.006,17);pts=np.array(np.meshgrid(y,z,indexing='ij')).reshape(2,-1).T
    check('uncut_bridge',np.max(abs(p.face_jump(pts)))<1e-11)
    d.save(case/'final');r=EventSweep.restore(case/'final');check('restart_fingerprint',r.fingerprint()==d.fingerprint(),{'original_cpu':str((d.cpu.time,d.cpu.steps,d.cpu.cut_count,d.cpu.events,d.cpu.config)), 'restored_cpu':str((r.cpu.time,r.cpu.steps,r.cpu.cut_count,r.cpu.events,r.cpu.config)),'pieces':{k:[str((p.steps,p.epoch,p.keys,p.plane)),str((r.cpu.pieces[k].steps,r.cpu.pieces[k].epoch,r.cpu.pieces[k].keys,r.cpu.pieces[k].plane))] for k,p in d.cpu.pieces.items()}})
    before=d.fingerprint();bad=d.pose.copy();bad[0,3]+=.001
    try:d.action(bad,10e-6);check('rejected_action',False)
    except RejectedEvent:check('rejected_action',True)
    check('rejected_action_rollback',d.fingerprint()==before)
    result.update(status='completed',activations=d.activations,cost=d.cost,energy=energy,final_dofs=len(p.q),mass_kg=m['mass'],final_energy_J=m['energy'],mass_condition=p.audit['mass_condition'],cut_keys=len(p.keys),simulated_s=d.cpu.time,final_history=d.histories['root'])
except Exception as e:
    result.update(status='failed',exception=repr(e),details=getattr(e,'detail',{}));traceback.print_exc()
finally:
    result.update(checks=checks,wall_s=time.perf_counter()-start,peak_process_RSS_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
    (case/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False));(W/'status.json').write_text(json.dumps({'updated':datetime.now(timezone.utc).isoformat(),'status':result['status'],'case':name,'simulation_running':False,'production_changed':False},indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['activations','final_history']},indent=2),flush=True)
if result['status']!='completed':sys.exit(1)
