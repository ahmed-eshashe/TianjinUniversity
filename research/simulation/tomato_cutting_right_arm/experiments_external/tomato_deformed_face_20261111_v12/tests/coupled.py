from pathlib import Path
from datetime import datetime,timezone
import sys,json,time,numpy as np
from scipy.interpolate import BSpline
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from fixtures import make,world_y
from deformed_sweep import DeformedSweep,field_snapshot
from coupled_sweep import CoupledSweep
from front_system import prolongation
from multicut import kron3,volume_certificates
from blade_sweep import pose
from face_chart import edge_rectangle
R=W/'runs/coupled';R.mkdir(exist_ok=False);checks={};results={};states={};start=time.perf_counter()
assert all(json.loads((W/'time_controls.json').read_text())['checks'].values())
def progress(label):
    (W/'status.json').write_text(json.dumps({'updated':datetime.now(timezone.utc).isoformat(),'status':'coupled_validation_running' if label else 'coupled_validation_finished','current':label,'simulation_running':bool(label),'production_changed':False},indent=2));print(label,flush=True)
def check(k,v):checks[k]=bool(v)
def evaluate(p,X,field='q'):
    V=[BSpline(t,np.eye(len(t)-3),2)(X[:,i]) for i,t in enumerate(p.knots)]
    return np.einsum('pi,pj,pk->pijk',*V).reshape(len(X),-1)@(p.T@getattr(p,field))
def coverage_witness(segments,chart,blade):
    rng=np.random.default_rng(173);n=400;r=chart['rectangle'];X=np.empty((n,3));X[:,chart['axis']]=chart['plane'];others=[i for i in range(3) if i!=chart['axis']]
    for j,axis in enumerate(others):X[:,axis]=rng.uniform(r[2*j],r[2*j+1],n)
    seen=np.zeros(n,bool);lo,hi,half=edge_rectangle(blade)
    for old,new,op,np_ in segments:
        a=(evaluate(old,X)-op[:3,3])@op[:3,:3];b=(evaluate(new,X)-np_[:3,3])@np_[:3,:3]
        den=b[:,1]-a[:,1];t=np.full(n,-1.);np.divide(-a[:,1],den,out=t,where=abs(den)>1e-15);hit=a+t[:,None]*(b-a)
        seen|=(t>=-1e-8)&(t<=1+1e-8)&(hit[:,0]>=lo-1e-10)&(hit[:,0]<=hi+1e-10)&(abs(hit[:,2])<=half+1e-10)
    return bool(seen.all())

for label,dt,subdivision in [('primary',3.90625e-7/16,1),('half_dt',3.90625e-7/32,1),('half_action',3.90625e-7/32,2)]:
    progress(label+' freely deforming blade advance');d=make();c=CoupledSweep(d,dt);rows=[];segments=[];failure=None;initial=d.cpu.metrics();tic=time.perf_counter()
    targets=[world_y(.0061),world_y(.00595),world_y(.00590)]
    for action_index in range(2):
        for j in range(1,subdivision+1):
            old_cpu=d.cpu;old=field_snapshot(old_cpu)['root'];op=d.pose.copy();end=pose([.0003,targets[action_index]+(targets[action_index+1]-targets[action_index])*j/subdivision,0]);before=d.fingerprint()
            try:row=c.advance(end,round(.00005/subdivision/dt))
            except Exception as e:
                failure={'action':action_index+1,'subaction':j,'exception':repr(e),'detail':getattr(e,'detail',{}),'rollback_exact':before==d.fingerprint()};break
            segments.append((old,field_snapshot(old_cpu)['root'],op,end.copy()));rows.append(row);chart=d.commands[-1]['charts'][0] if d.commands[-1]['charts'] else None
            visited=any(cmd['new_reference_area_m2']>1e-18 for cmd in d.commands)
            check(label+'_topology_matches_coverage_'+str(len(rows)),len(d.cpu.pieces)==1 and (d.cpu.pieces['root'].plane is not None)==visited)
            check(label+'_volume_'+str(len(rows)),all(v['passed'] for p in d.cpu.pieces.values() for v in volume_certificates(p)))
            if chart:check(label+'_coverage_'+str(len(rows)),coverage_witness(segments,chart,d.blade))
            d.save(R/(label+'_frame'+str(len(rows))))
        if failure:break
    check(label+'_all_actions_accepted',failure is None)
    final=d.cpu.metrics();results[label]={'failure':failure,'records':rows,'wall_s':time.perf_counter()-tic,'sim_s':d.cpu.time,'mass_kg':final['mass'],'energy_residual_J':final['energy']-initial['energy'],'cut_count':d.cpu.cut_count,'initial_energy_J':initial['energy'],'final_charts':[q for cmd in d.commands for q in cmd['charts']]};states[label]=d
    if failure:break
    check(label+'_energy',abs(final['energy']-initial['energy'])<max(1e-12,.05*initial['energy']));check(label+'_mass',abs(final['mass']-.001728)<1e-12)

def shared_coeff_difference(a,b):
    # Exact spline prolongation onto a union knot grid is only an analysis
    # basis, never a new physical mesh or mass solve.
    common=[]
    for ta,tb in zip(a.knots,b.knots):
        groups=[]
        for v in sorted(np.r_[ta,tb]):
            if not groups or abs(v-groups[-1][0])>1e-12:groups.append([float(v)])
            else:groups[-1].append(float(v))
        t=[]
        for group in groups:
            v=group[0];count=max(np.count_nonzero(abs(ta-v)<1e-12),np.count_nonzero(abs(tb-v)<1e-12));t.extend([v]*count)
        common.append(np.array(t))
    A=kron3([prolongation(x,t) for x,t in zip(a.knots,common)]);B=kron3([prolongation(x,t) for x,t in zip(b.knots,common)])
    return {f:float(np.linalg.norm(A@(a.T@getattr(a,f))-B@(b.T@getattr(b,f)),axis=1).max()) for f in ['q','vg']}
if all(k in states and results[k]['failure'] is None for k in ['primary','half_dt','half_action']):
    for name in ['half_dt','half_action']:
        e=shared_coeff_difference(states['primary'].cpu.pieces['root'],states[name].cpu.pieces['root']);check(name+'_continuous_position',e['q']<.0001);check(name+'_continuous_velocity',e['vg']<.005)
        results[name+'_comparison']={'position_convex_hull_bound_m':e['q'],'velocity_convex_hull_bound_m_s':e['vg'],'plane_difference_m':abs(states['primary'].cpu.pieces['root'].plane-states[name].cpu.pieces['root'].plane)}
    # Loaded cut-history restart from an accepted action, with the current clock.
    progress('loaded deformed-history restart');d=DeformedSweep.restore(R/'primary_frame1');c=CoupledSweep(d,3.90625e-7/16);c.advance(pose([.0003,world_y(.00590),0]),2048)
    e=shared_coeff_difference(d.cpu.pieces['root'],states['primary'].cpu.pieces['root']);check('restart_exact_fields',max(e.values())<1e-9)
    results['restart']=e
out={'status':'pass_short_deformed_motion_components' if all(checks.values()) else 'coupled_accuracy_or_coverage_failed','checks':checks,'results':results,'wall_s':time.perf_counter()-start,'physical_fracture':False,'actual_blade_contact':False,'production_changed':False}
(W/'coupled_controls.json').write_text(json.dumps(out,indent=2,allow_nan=False));progress(None);print(json.dumps({'status':out['status'],'checks':len(checks),'failures':[k for k,v in checks.items() if not v],'wall_s':out['wall_s']},indent=2))
