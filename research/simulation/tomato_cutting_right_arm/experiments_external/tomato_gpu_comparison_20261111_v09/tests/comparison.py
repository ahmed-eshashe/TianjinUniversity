from pathlib import Path
from datetime import datetime, timezone
import sys, json, time, resource, subprocess, hashlib
import numpy as np

W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
BASE=Path('/home/omen/Documents/Codex/experiments/tomato_multicut_20261110_v07')
from multicut import MultiCut,full_rectangle,volume_certificates,maximum
from reference import block
from gpu_backend import GPUReference,wp

X=block(8,.0015);DT=3.90625e-7
checks={};results={};begin=time.perf_counter()
R=W/'runs/comparison';R.mkdir(exist_ok=False)


def progress(current):
    record={'updated':datetime.now(timezone.utc).isoformat(),'status':'gpu_comparison_running' if current else 'gpu_comparison_complete','current':current,'simulation_running':bool(current),'production_changed':False,'checks_passed':sum(checks.values())}
    (W/'status.json').write_text(json.dumps(record,indent=2))
    (W/'comparison.partial.json').write_text(json.dumps({'checks':checks,'results':results,'wall_s':time.perf_counter()-begin,'current':current},indent=2,allow_nan=False))
    print(current,flush=True)


def check(key,value,detail=None):
    checks[key]=bool(value)
    if not value:
        progress('STOP: '+key)
        raise AssertionError((key,detail))


def make(cuts=0,fixed=False):
    s=MultiCut(X,fixed=X[:,2]==X[:,2].min() if fixed else None)
    for pid,axis,plane in [('root',0,-.0021),('rootR',0,.0021),('rootRL',1,.0003),('rootL',2,.0004)][:cuts]:
        s.commit(s.propose(pid,axis,plane,full_rectangle(s.pieces[pid],axis)))
    return s


def saved_initial(kind,half=False):
    name=kind+('_half' if half else '')
    s=MultiCut.restore(BASE/'runs/dynamics'/(name+'.npz'))
    z=np.load(BASE/'runs/dynamics'/(name+'_trace.npz'),allow_pickle=False)
    for key,p in s.pieces.items():
        p.q=z[key+'_q'][0].copy();p.vg=z[key+'_vg'][0].copy();p.time=0.;p.steps=0
        p.support_impulse[:]=0.;p.support_moment[:]=0.;p.update_state()
    s.time=0.;s.steps=0;s.archived_support_impulse[:]=0.;s.archived_support_moment[:]=0.
    return s,z


def compare_states(a,b):
    out={name:max(maximum(getattr(p,name)-getattr(b.pieces[key],name)) for key,p in a.pieces.items()) for name in ['q','vg','x','v','F','support_impulse','support_moment']}
    return out


def state_ok(v):
    return v['x']<1e-7 and v['q']<1e-7 and v['v']<1e-5 and v['vg']<1e-5 and v['F']<1e-6 and v['support_impulse']<1e-10 and v['support_moment']<1e-11


def fields():
    rows=[];rng=np.random.default_rng(42)
    for name in ['intact','one','two','four','partial_saved','full_saved','supported','thin']:
        progress('field parity '+name)
        if name.endswith('_saved'):
            s=MultiCut.restore(BASE/'runs/dynamics'/(name.split('_')[0]+'.npz'))
        else:
            s=make({'one':1,'two':2,'four':4}.get(name,0),fixed=name=='supported')
            if name=='thin':s.commit(s.propose('root',0,.0057,full_rectangle(s.pieces['root'],0)))
            if name!='supported':
                for p in s.pieces.values():
                    p.q=p.q@np.diag([1,.995,1.001]);p.vg=rng.normal(size=p.q.shape)*.001;p.update_state()
        f=rng.normal(size=X.shape)*1e-5
        g=GPUReference(s,f);v=g.field_values();uf=[];ff=[];aa=[];rr=[]
        for p in s.pieces.values():
            u,force=p.energy_force(p.q);acc,reaction=p.acceleration(p.q,f[p.indices]);uf.append(u);ff.append(force+p.O.T@f[p.indices]);aa.append(acc);rr.append(reaction)
        force=np.concatenate(ff);acc=np.concatenate(aa);reaction=np.concatenate(rr)
        fn=float(np.linalg.norm(v['force']-force));an=float(np.linalg.norm(v['acceleration']-acc));un=abs(v['strain_energy']-sum(uf));rn=float(np.linalg.norm(v['reaction']-reaction))
        row={'case':name,'force_error_N':fn,'force_relative':fn/max(np.linalg.norm(force),1e-10),'acceleration_error_m_s2':an,'acceleration_relative':an/max(np.linalg.norm(acc),1e-7),'energy_error_J':un,'reaction_error_N':rn,'mass_solve_relative':v['mass_residual'],'mass_inverse_residuals':g.inverse_residuals,'device_array_MiB':g.memory()/2**20,'cpu_preparation_s':g.preparation_s,'upload_and_sparse_packing_s':g.upload_s}
        rows.append(row);results['fields']=rows
        check(name+'_force',fn<max(1e-10,1e-7*np.linalg.norm(force)),row)
        check(name+'_acceleration',an<max(1e-7,1e-7*np.linalg.norm(acc)),row)
        check(name+'_energy',un<max(1e-12,1e-8*abs(sum(uf))),row)
        check(name+'_mass_residual',v['mass_residual']<1e-7,row)
        check(name+'_reaction',rn<max(1e-10,1e-7*np.linalg.norm(reaction)),row)


def loaded_history():
    progress('loaded supports and topology upload')
    a=make(fixed=True);b=make(fixed=True);f=np.zeros_like(X);fixed=X[:,2]==X[:,2].min();f[~fixed,1]=.01/(~fixed).sum();rows=[]
    events=[('root',0,-.0021,[0,.006,-.006,.006]),('root',0,-.0021,[-.006,.006,-.006,.006]),('rootR',0,.0021,[-.006,.006,-.006,.006]),('rootRL',1,.0003,[0,.0021,-.006,.006]),('rootRL',1,.0003,[-.0021,.0021,-.006,.006])]
    for i,e in enumerate(events):
        for _ in range(25):a.step(DT,f)
        g=GPUReference(b,f);g.step(25);b=g.export();pre=compare_states(a,b);check('loaded_before_'+str(i),state_ok(pre),pre)
        a.commit(a.propose(*e));b.commit(b.propose(*e));g=GPUReference(b,f);g.step(25);b=g.export()
        for _ in range(25):a.step(DT,f)
        err=compare_states(a,b);check('loaded_after_'+str(i),state_ok(err),err)
        for label,s in [('cpu',a),('gpu',b)]:s.save(R/(label+'_event'+str(i)+'.npz'))
        restored=MultiCut.restore(R/('gpu_event'+str(i)+'.npz'));check('checkpoint_'+str(i),restored.fingerprint()==b.fingerprint())
        check('loaded_volume_'+str(i),all(c['passed'] for p in b.pieces.values() for c in volume_certificates(p)))
        rows.append({'event':e,'difference':err,'pieces':len(b.pieces),'gpu_constructor_s':g.preparation_s+g.upload_s})
    results['loaded_history']=rows
    # Trial failure must restore the complete GPU chunk, including clock/ledgers.
    old={n:getattr(g,n).numpy().copy() for n in ['q','v','impulse','moment','clock']};count=g.steps
    g.load.assign(np.full((g.ng,3),np.nan))
    rejected=False
    try:g.step(3)
    except RuntimeError:rejected=True
    check('bad_load_rejected',rejected)
    check('whole_chunk_rollback',count==g.steps and all(np.array_equal(v,getattr(g,n).numpy()) for n,v in old.items()))
    # An inadmissible predicted deformation is detected by the same volume guard.
    h=GPUReference(make());h.q.assign(h.q.numpy()@np.diag([1,.05,1]));bad=False
    try:h.step(1)
    except RuntimeError:bad=True
    check('volume_stop_detected',bad)
    # Direct launches and graph capture must perform the same numerical update.
    l=GPUReference(make(2));r=GPUReference(make(2));l.step(8,graph=False);r.step(8,graph=True)
    err=compare_states(l.export(),r.export());check('graph_equivalence',state_ok(err),err)


def trajectories():
    rows=[]
    for kind,half in [('partial',False),('full',False),('partial',True),('full',True)]:
        name=kind+('_half' if half else '');progress('saved trajectory '+name)
        s,z=saved_initial(kind,half);dt=DT/(2 if half else 1);f=np.zeros_like(X)
        if kind=='partial':
            selected=np.zeros(len(X),bool);selected[s.pieces['rootRL'].indices]=True;low=selected&(X[:,1]<.0003);high=selected&~low
            weights=np.exp(-((X[:,0]-.001)/.001)**2-(X[:,2]/.004)**2)
            f[high,1]=.02*weights[high]/weights[high].sum();f[low,1]=-.02*weights[low]/weights[low].sum()
        g=GPUReference(s,f,mode=int(kind=='partial'),dt=dt);g.graph(32)
        n=round(.0001/dt);warm_s=g.graph_build_s+g.module_load_s
        initial=s.metrics();work=0.;workscale=0.;maxenergy=0.;maxP=0.;maxL=0.;errors=[];states=[];bridge=0.;opened=0.;idle=0.;start=time.perf_counter();gpu_wall=0.;host_check=0.;bounds=[10.,.1]
        # Work parity uses the exact reference's saved sample ledger as well as state/energy parity.
        ref=json.loads((BASE/'runs/dynamics'/(name+'.json')).read_text());checkpoints=[]
        for sample in range(1,11):
            tick=time.perf_counter();g.step(n);gpu_wall+=time.perf_counter()-tick
            tick=time.perf_counter();s=g.export();snap={};err={k:0. for k in ['q','vg','x','v','F']}
            for key,p in s.pieces.items():
                qr,vr=z[key+'_q'][sample],z[key+'_vg'][sample]
                reference={'q':qr,'vg':vr,'x':p.O@qr,'v':p.O@vr,'F':np.stack([a@qr for a in p.H],axis=2)}
                for field,val in reference.items():err[field]=max(err[field],maximum(getattr(p,field)-val))
                snap[key+'_q']=p.q.copy();snap[key+'_vg']=p.vg.copy()
            m=s.metrics();row=ref['rows'][sample-1];energy_difference=abs(m['energy']-row['energy']);scale=max(abs(row['energy']),1e-12)
            check(name+'_state_'+str(sample),err['x']<1e-7 and err['q']<1e-7 and err['v']<1e-5 and err['vg']<1e-5 and err['F']<1e-6,err)
            check(name+'_energy_'+str(sample),energy_difference<max(1e-12,1e-5*scale),energy_difference)
            cs=[c for p in s.pieces.values() for c in volume_certificates(p)];check(name+'_volume_'+str(sample),all(c['passed'] for c in cs))
            bounds=[min(bounds[0],*[c['minJ_lower_bound'] for c in cs]),max(bounds[1],*[c['maxJ_upper_bound'] for c in cs])]
            active='rootRL' if kind=='partial' else 'rootRLR';idle=max(idle,*[float(np.linalg.norm(p.v,axis=1).max()) for key,p in s.pieces.items() if key!=active])
            if kind=='partial':
                pts=np.stack(np.meshgrid(np.linspace(-.0021,.0021,41),np.linspace(-.006,.006,7),indexing='ij'),axis=-1).reshape(-1,2);jump=s.pieces['rootRL'].face_jump(pts);bridge=max(bridge,float(np.linalg.norm(jump[pts[:,0]<=0],axis=1).max()));opened=max(opened,float(np.linalg.norm(jump[pts[:,0]>.0005],axis=1).max()))
            maxP=max(maxP,float(np.linalg.norm(m['momentum']-initial['momentum'])));maxL=max(maxL,float(np.linalg.norm(m['angular']-initial['angular'])))
            errors.append({'t':s.time,**err,'energy_difference_J':energy_difference});states.append(snap);host_check+=time.perf_counter()-tick
            if time.perf_counter()-start>600:raise TimeoutError(name)
        wall=time.perf_counter()-start
        check(name+'_independence',idle/.02<.01,idle);check(name+'_momentum',maxP<1e-9,maxP)
        if kind=='partial':check(name+'_bridge',bridge<1e-11 and opened>1e-9,(bridge,opened))
        else:check(name+'_angular',maxL<1e-10,maxL)
        s.save(R/(name+'_gpu.npz'));np.savez_compressed(R/(name+'_gpu_trace.npz'),**{k:np.stack([r[k] for r in states]) for k in states[0]})
        row={'case':name,'sim_s':.001,'gpu_checked_step_wall_s':gpu_wall,'export_comparison_and_certificate_s':host_check,'checked_total_wall_s':wall,'saved_CPU_checked_wall_s':ref['result']['wall_s'],'speedup_vs_saved_CPU_checked':ref['result']['wall_s']/wall,'setup_s':g.preparation_s+g.upload_s,'graph_module_warmup_s':warm_s,'device_array_MiB':g.memory()/2**20,'maximum_differences':{k:max(e[k] for e in errors) for k in errors[0] if k!='t'},'idle_speed_m_s':idle,'ahead_jump_m':bridge,'behind_jump_m':opened,'momentum_error_N_s':maxP,'angular_error_N_m_s':maxL,'J_bounds':bounds,'fixture':'Same v07 prescribed topology/manufactured gaps; no contact/physical cut','samples':errors}
        rows.append(row);results['trajectories']=rows;progress(name+' completed')


def costs():
    rows=[]
    for cuts in [0,1,2,4]:
        progress('paired cost sample '+str(cuts)+' cuts');s=make(cuts);gpu=GPUReference(make(cuts));gpu.graph(32);gpu.graph(64)
        cpu_times=[];gpu_times=[];raw=[]
        for _ in range(3):
            start=time.perf_counter()
            for i in range(64):s.step(DT)
            cpu_times.append(time.perf_counter()-start)
            start=time.perf_counter();gpu.step(64);gpu_times.append(time.perf_counter()-start)
        # Raw graph timing excludes transactional backup and the host flag read.
        # It is measured separately; only checked timings support the reported speedup.
        for _ in range(3):
            wp.synchronize_device(gpu.device);start=time.perf_counter();wp.capture_launch(gpu.graphs[64]);wp.synchronize_device(gpu.device);raw.append(time.perf_counter()-start)
            check('raw_guard_'+str(cuts)+'_'+str(_),int(gpu.bad.numpy()[0])==0)
            gpu.steps+=64
        row={'cuts':cuts,'pieces':len(s.pieces),'scalar_basis_count':gpu.ng,'integration_samples':gpu.nq,'step_s':DT,'steps_per_sample':64,'CPU_checked_wall_samples_s':cpu_times,'GPU_checked_wall_samples_s':gpu_times,'GPU_raw_graph_wall_samples_s':raw,'CPU_median_wall_s_per_sim_s':float(np.median(cpu_times)/(64*DT)),'GPU_median_wall_s_per_sim_s':float(np.median(gpu_times)/(64*DT)),'checked_median_speedup':float(np.median(cpu_times)/np.median(gpu_times)),'CPU_topology_and_gpu_operator_preparation_s':gpu.preparation_s,'sparse_packing_upload_s':gpu.upload_s,'graph_build_s':gpu.graph_build_s,'device_array_MiB':gpu.memory()/2**20,'memory_note':'Exact owned arrays including rollback copies; excludes CUDA context/graphs/allocator.'}
        rows.append(row);results['costs']=rows;progress('cost sample completed')


try:
    fields();loaded_history();trajectories();costs()
    out={'status':'pass_restricted_GPU_comparison','checks':checks,'results':results,'wall_s':time.perf_counter()-begin,'peak_host_RSS_MiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'physical_slice':False,'rl_qualified':False,'source_sha256':{str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'src').glob('*.py')}}
    (W/'comparison.json').write_text(json.dumps(out,indent=2,allow_nan=False));progress(None)
    print(json.dumps({'status':out['status'],'checks':len(checks),'wall_s':out['wall_s'],'costs':results['costs']},indent=2),flush=True)
except Exception as e:
    (W/'failure.json').write_text(json.dumps({'error':repr(e),'checks':checks,'results':results,'wall_s':time.perf_counter()-begin},indent=2,allow_nan=False));progress('failed: '+repr(e));raise
