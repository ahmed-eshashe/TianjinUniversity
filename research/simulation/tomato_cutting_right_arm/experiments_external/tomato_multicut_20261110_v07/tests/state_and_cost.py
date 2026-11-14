from pathlib import Path
import sys,json,time,resource,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from multicut import MultiCut,full_rectangle,volume_certificates,RejectedEvent,maximum
from reference import block
X=block(8,.0015);R=W/'runs/state';R.mkdir(exist_ok=False);checks={};results={};start=time.monotonic();dt=3.90625e-7
fixed=X[:,2]==X[:,2].min();s=MultiCut(X,fixed=fixed);force=np.zeros_like(X);force[~fixed,1]=.01/(~fixed).sum();records=[]
events=[('root',0,-.0021,[0,.006,-.006,.006]),('root',0,-.0021,[-.006,.006,-.006,.006]),('rootR',0,.0021,[-.006,.006,-.006,.006]),('rootRL',1,.0003,[0,.0021,-.006,.006]),('rootRL',1,.0003,[-.0021,.0021,-.006,.006])]
for i,event in enumerate(events):
    for _ in range(25):s.step(dt,force)
    old=s.metrics();before=s.fingerprint();p=s.propose(*event);assert s.fingerprint()==before;s.commit(p);new=s.metrics()
    checks['support_ledger_'+str(i)]=maximum(new['support_impulse']-old['support_impulse'])<1e-14 and maximum(new['support_moment']-old['support_moment'])<1e-14
    checkpoint=R/(str(i)+'.npz');s.save(checkpoint);r=MultiCut.restore(checkpoint)
    checks['history_'+str(i)]=s.events==r.events and list(s.pieces)==list(r.pieces) and s.cut_count==r.cut_count and s.steps==r.steps and s.time==r.time
    for _ in range(25):s.step(dt,force);r.step(dt,force)
    errors={k:{f:maximum(getattr(v,f)-getattr(r.pieces[k],f)) for f in ['q','vg','x','v','F','support_impulse','support_moment']} for k,v in s.pieces.items()};maxerror=max(v for k in errors.values() for v in k.values());checks['continuation_'+str(i)]=maxerror<1e-10
    checks['volume_'+str(i)]=all(c['passed'] for p in s.pieces.values() for c in volume_certificates(p))
    records.append({'event':event,'pieces':len(s.pieces),'max_restart_error':maxerror,'support_impulse':s.metrics()['support_impulse'].tolist(),'archived_support_impulse':s.archived_support_impulse.tolist(),'insertion':p['insertion'],'partition':p['partition']})
results['loaded_events']=records;checks['nonzero_archived_reactions']=np.linalg.norm(s.archived_support_impulse)>1e-12
# A late invalid substep must roll back the already advanced earlier fragments.
before=s.fingerprint();bad=force.copy();late=list(s.pieces.values())[-1];bad[late.indices,0]=np.nan
try:s.step(dt,bad);checks['step_rollback']=False
except RuntimeError:checks['step_rollback']=s.fingerprint()==before
# A proposal cannot be committed after any fragment has moved.
q=s.propose('rootL',2,.0004,full_rectangle(s.pieces['rootL'],2));s.step(dt,force);before=s.fingerprint()
try:s.commit(q);checks['stale_rejected']=False
except RejectedEvent:checks['stale_rejected']=s.fingerprint()==before
# Two concurrent partial cuts are allowed on distinct connected pieces.
t=MultiCut(X);t.commit(t.propose('root',0,0.,full_rectangle(t.pieces['root'],0)));t.commit(t.propose('rootL',1,.0003,[-.003,0.,-.006,.006]));t.commit(t.propose('rootR',2,.0004,[0.,.006,0.,.006]));checks['independent_partial_cuts']=sum(p.plane is not None for p in t.pieces.values())==2 and len(t.pieces)==2
t.save(R/'two_active_partials.npz');u=MultiCut.restore(R/'two_active_partials.npz');checks['two_partial_history']=t.fingerprint()==u.fingerprint()
# Corrupted event/leaf metadata cannot silently rebuild a different topology.
with np.load(R/'4.npz',allow_pickle=False) as z:arrays={k:z[k].copy() for k in z.files}
meta=json.loads(str(arrays['metadata']));meta['piece_ids']=meta['piece_ids'][1:];arrays['metadata']=np.array(json.dumps(meta));np.savez_compressed(R/'corrupt.npz',**arrays)
try:MultiCut.restore(R/'corrupt.npz');checks['corrupt_checkpoint_rejected']=False
except ValueError:checks['corrupt_checkpoint_rejected']=True
fresh=MultiCut(X);checks['fresh_reset']=fresh.cut_count==0 and not fresh.events and list(fresh.pieces)==['root'] and maximum(fresh.observations()[0]-X)<1e-14
thin=MultiCut(X);thin.commit(thin.propose('root',0,.0057,full_rectangle(thin.pieces['root'],0)));thin.step(dt);tiny=thin.pieces['rootR'];checks['unobserved_fragment_retains_material']=len(tiny.X)==0 and tiny.metrics()['mass']>0 and abs(thin.metrics()['mass']-.001728)<1e-12 and all(c['passed'] for c in volume_certificates(tiny));results['unobserved_fragment']={'observation_points':len(tiny.X),'integration_points':len(tiny.volumes),'mass_kg':tiny.metrics()['mass'],'note':'Mechanically retained even though the old observation cloud contains no point in this fragment. Surface rendering/contact remains separate.'}
# Compare forces and energy on actual loaded final dynamic fields at order seven.
quad=[]
for name in ['partial','full']:
    a=MultiCut.restore(W/'runs/dynamics'/(name+'.npz'));b=MultiCut(X,order=7)
    for e in a.events:b.commit(b.propose(e['piece_id'],e['axis'],e['plane'],e['rectangle']))
    for key,p in a.pieces.items():
        h=b.pieces[key];h.q=p.q.copy();h.vg=p.vg.copy();h.update_state();U,f=p.energy_force(p.q);Uh,fh=h.energy_force(h.q);row={'case':name,'piece':key,'energy_relative':abs(U-Uh)/max(abs(U),1e-12),'force_relative':float(np.linalg.norm(f-fh)/max(np.linalg.norm(f),1e-10)),'force_difference_N':float(np.linalg.norm(f-fh))};quad.append(row)
        checks['quad_'+name+'_'+key]=row['energy_relative']<1e-6 and (row['force_relative']<1e-5 or row['force_difference_N']<1e-10)
results['loaded_quadrature']=quad
# Same-step short cost samples, not full robot/RL throughput.
bench=[];b=MultiCut(X)
for target in [0,1,2,4]:
    tic=time.monotonic()
    while b.cut_count<target:
        pid,axis,plane=[('root',0,-.0021),('rootR',0,.0021),('rootRL',1,.0003),('rootL',2,.0004)][b.cut_count];b.commit(b.propose(pid,axis,plane,full_rectangle(b.pieces[pid],axis)))
    setup=time.monotonic()-tic;tic=time.monotonic()
    for _ in range(64):b.step(dt)
    elapsed=time.monotonic()-tic;bench.append({'cuts':target,'pieces':len(b.pieces),'new_topology_setup_s':setup,'wall_s_64_steps':elapsed,'sim_s':64*dt,'wall_s_per_sim_s':elapsed/(64*dt),'scalar_basis_count':sum(len(p.q) for p in b.pieces.values()),'integration_points':sum(len(p.volumes) for p in b.pieces.values()),'process_peak_RSS_MiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024})
results['cost_samples']=bench
out={'status':'pass_restricted_unit_scope' if all(checks.values()) else 'fail','checks':{k:bool(v) for k,v in checks.items()},'results':results,'wall_s':time.monotonic()-start,'scope':'Carried-state prescribed cuts. No contact/damage ledger exists.'};(W/'state_controls.json').write_text(json.dumps(out,indent=2,allow_nan=False));print(json.dumps(out,indent=2,allow_nan=False));assert all(checks.values()),checks
