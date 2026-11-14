from pathlib import Path
from datetime import datetime,timezone
import sys,json,time,resource,os,numpy as np
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from integrated_cut import IntegratedCut,IntegratedBody
from continuous_volume import certificate
from reference import block
R=W/'runs/dynamics';R.mkdir(exist_ok=False);X=block(8,.0015)
dt0=3.90625e-7;duration=.001;plane=.0003;checks={};results={};start=time.monotonic()
yz=np.stack(np.meshgrid(np.linspace(-.006,.006,49),np.linspace(-.006,.006,9),indexing='ij'),axis=-1).reshape(-1,2)
def write(current=None):
    report={'checks':{k:bool(v) for k,v in checks.items()},'results':results,'wall_s':time.monotonic()-start,'current':current,'max_rss_MiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024}
    (W/'dynamics.partial.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    (W/'status.json').write_text(json.dumps({'updated':datetime.now(timezone.utc).isoformat(),'status':'running_short_dynamics' if current else 'short_dynamics_completed','simulation_running':bool(current),'process_id':os.getpid() if current else None,'current':current,'production_changed':False,'adopted':False},indent=2))
def compare(a,b,name):
    dx=float(np.linalg.norm(a[0]-b[0],axis=-1).max());dv=float(np.linalg.norm(a[1]-b[1],axis=-1).max())
    results[name]={'x_m':dx,'v_m_s':dv};checks[name]=dx<1e-4 and dv<.005
def load_run(kind,half=False,order=5):
    name=kind+('_half' if half else '')+('_order7' if order==7 else '')
    fixed=X[:,1]==X[:,1].min() if kind=='intact_load' else None
    b=IntegratedCut(X,order=order,fixed=fixed);dt=dt0/(2 if half else 1)
    f=np.zeros_like(X)
    if kind=='intact_load':
        weight=np.exp(-((X[:,0]-.002)/.002)**2-(X[:,2]/.003)**2)*(X[:,1]==X[:,1].max());f[:,1]=-.02*weight/weight.sum()
    else:
        b.commit(b.propose([0,.006,-.006,.006],plane))
        weight=np.exp(-((X[:,1]-.004)/.002)**2-(X[:,2]/.004)**2);left=X[:,0]<plane;right=~left
        f[right,0]=.02*weight[right]/weight[right].sum();f[left,0]=-.02*weight[left]/weight[left].sum()
    initial=b.metrics();work=0.;rows=[];xs=[];vs=[];max_error=0.;work_scale=0.;ahead=0.;behind=0.;support_drift=0.;balance=0.;bounds=[10.,.1];tic=time.monotonic();write(name)
    n=round(duration/dt);sample=round(.0001/dt)
    for i in range(n):
        f0=f*np.sin(np.pi*i*dt/duration)**2;f1=f*np.sin(np.pi*(i+1)*dt/duration)**2
        old_x=b.x.copy();b.step(dt,f0,f1);work+=float(np.sum(.5*(f0+f1)*(b.x-old_x)));work_scale=max(work_scale,abs(work))
        if (i+1)%sample==0:
            m=b.metrics();residual=m['energy']-initial['energy']-work;max_error=max(max_error,abs(residual));cs=certificate(b);assert all(c['passed'] for c in cs),cs
            bounds=[min(bounds[0],*[c['minJ_lower_bound'] for c in cs]),max(bounds[1],*[c['maxJ_upper_bound'] for c in cs])]
            if kind=='intact_load':support_drift=max(support_drift,float(abs(b.x[fixed]-X[fixed]).max()))
            else:
                jump=b.face_jump(yz);ahead=max(ahead,float(np.linalg.norm(jump[yz[:,0]<=0],axis=1).max()));behind=max(behind,float(np.linalg.norm(jump[yz[:,0]>.001],axis=1).max()));balance=max(balance,float(np.linalg.norm(m['momentum']-initial['momentum'])))
            rows.append({'t':b.time,'energy':m['energy'],'work':work,'residual':residual,'ahead_m':ahead,'behind_m':behind});xs.append(b.x.copy());vs.append(b.v.copy())
        if time.monotonic()-tic>600:raise TimeoutError(name)
    result={'wall_s':time.monotonic()-tic,'sim_s':duration,'energy_work_residual_J':max_error,'work_scale_J':work_scale,'J_bounds':bounds,'ahead_jump_m':ahead,'behind_jump_m':behind,'support_drift_m':support_drift,'momentum_error_N_s':balance,'integral_points':len(b.volumes),'peak_rss_MiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024}
    checks[name+'_energy']=max_error<max(1e-12,.05*work_scale)
    if kind=='partial':checks[name+'_bridge']=ahead<1e-11 and behind>1e-9;checks[name+'_momentum']=balance<1e-9
    else:checks[name+'_support']=support_drift<1e-10
    results[name]=result;(R/(name+'.json')).write_text(json.dumps({'result':result,'rows':rows},indent=2));b.save(R/(name+'.npz'));write(name+' completed');assert all(checks.values()),checks
    return np.array(xs),np.array(vs)
def full_run(half=False,order=5):
    name='full'+('_half' if half else '')+('_order7' if order==7 else '')
    b=IntegratedCut(X,order=order);b.commit(b.propose([-.006,.006,-.006,.006],plane));lk,rk=b.split_knots();left=X[:,0]<plane
    l=IntegratedBody(lk,X[left],order=order);r=IntegratedBody(rk,X[~left],order=order)
    r.q=r.q@np.diag([1,.995,1]);rot=Rotation.from_rotvec([.1,.2,.25]).as_matrix();center=r.q.mean(0);r.q=(r.q-center)@rot.T+center+[.008,.001,0];r.vg[:]=[.02,0,0];r.update_state();b.set_full_piece_state(l,r)
    initial=b.metrics();dt=dt0/(2 if half else 1);n=round(duration/dt);sample=round(.0001/dt);tic=time.monotonic();write(name)
    leak=0.;p_error=0.;a_error=0.;e_error=0.;ind_x=0.;ind_v=0.;rows=[];xs=[];vs=[];bounds=[10.,.1]
    for i in range(n):
        b.step(dt)
        if not half and order==5:l.step(dt);r.step(dt)
        if (i+1)%sample==0:
            m=b.metrics();leak=max(leak,float(np.linalg.norm(b.v[left],axis=1).max()));p_error=max(p_error,float(np.linalg.norm(m['momentum']-initial['momentum'])));a_error=max(a_error,float(np.linalg.norm(m['angular']-initial['angular'])));e_error=max(e_error,abs(m['energy']-initial['energy']));cs=certificate(b);assert all(c['passed'] for c in cs),cs
            bounds=[min(bounds[0],*[c['minJ_lower_bound'] for c in cs]),max(bounds[1],*[c['maxJ_upper_bound'] for c in cs])]
            if not half and order==5:
                ind_x=max(ind_x,float(abs(b.x-np.concatenate([l.x,r.x])).max()));ind_v=max(ind_v,float(abs(b.v-np.concatenate([l.v,r.v])).max()))
            rows.append({'t':b.time,'left_speed_m_s':float(np.linalg.norm(b.v[left],axis=1).max()),'energy':m['energy'],'momentum_error':p_error,'angular_error':a_error});xs.append(b.x.copy());vs.append(b.v.copy())
        if time.monotonic()-tic>600:raise TimeoutError(name)
    result={'wall_s':time.monotonic()-tic,'sim_s':duration,'independent_references_included':not half and order==5,'left_max_speed_m_s':leak,'leak_fraction_of_probe':leak/.02,'linear_momentum_error_N_s':p_error,'angular_momentum_error_N_m_s':a_error,'energy_error_J':e_error,'initial_energy_J':initial['energy'],'independent_position_error_m':ind_x if not half and order==5 else None,'independent_velocity_error_m_s':ind_v if not half and order==5 else None,'J_bounds':bounds,'integral_points':len(b.volumes),'peak_rss_MiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'fixture':'Manufactured 8mm gap and rigidly rotated precompressed piece; no physical cut or contact inferred'}
    checks[name+'_independence']=leak/.02<.01;checks[name+'_linear']=p_error<1e-9;checks[name+'_angular']=a_error<1e-10;checks[name+'_energy']=e_error<max(1e-12,.05*initial['energy'])
    if not half and order==5:checks['independent_two_body_reference']=ind_x<1e-8 and ind_v<1e-8
    results[name]=result;(R/(name+'.json')).write_text(json.dumps({'result':result,'rows':rows},indent=2));b.save(R/(name+'.npz'));write(name+' completed');assert all(checks.values()),checks
    return np.array(xs),np.array(vs)
for kind in ['intact_load','partial']:
    a=load_run(kind);b=load_run(kind,half=True);compare(a,b,kind+'_dt_refinement');assert all(checks.values()),checks
    if kind=='partial':c=load_run(kind,order=7);compare(a,c,'partial_quadrature_refinement');assert all(checks.values()),checks
a=full_run();b=full_run(half=True);compare(a,b,'full_dt_refinement');assert all(checks.values()),checks
c=full_run(order=7);compare(a,c,'full_quadrature_refinement');assert all(checks.values()),checks
np.savez_compressed(R/'full_comparison.npz',x=a[0],v=a[1],x_half=b[0],v_half=b[1],x_order7=c[0],v_order7=c[1])
out={'status':'pass_restricted_unit_scope','checks':{k:bool(v) for k,v in checks.items()},'results':results,'wall_s':time.monotonic()-start,'max_rss_MiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'scope':'Fresh-state integrated mechanics and single off-grid plane prescribed topology; no physical cut'}
(W/'dynamics_controls.json').write_text(json.dumps(out,indent=2));write();print(json.dumps(out,indent=2))
