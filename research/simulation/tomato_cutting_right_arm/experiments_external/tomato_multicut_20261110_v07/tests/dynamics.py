from pathlib import Path
from datetime import datetime,timezone
import sys,json,time,os,resource,numpy as np
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from multicut import MultiCut,full_rectangle,volume_certificates
from reference import block
X=block(8,.0015);R=W/'runs/dynamics';R.mkdir(exist_ok=False);dt0=3.90625e-7;duration=.001;checks={};results={};start=time.monotonic()
def construct(kind,order):
    s=MultiCut(X,order=order)
    s.commit(s.propose('root',0,-.0021,full_rectangle(s.pieces['root'],0)))
    s.commit(s.propose('rootR',0,.0021,full_rectangle(s.pieces['rootR'],0)))
    s.commit(s.propose('rootRL',1,.0003,[0,.0021,-.006,.006] if kind=='partial' else full_rectangle(s.pieces['rootRL'],1)))
    # Manufactured spatial gaps only isolate mechanics; no physical cutting claimed.
    for j,(key,p) in enumerate(s.pieces.items()):
        p.q+=p.translation[:,None]*np.array([.02*j,0,0])[None,:];p.update_state()
    if kind=='full':
        p=s.pieces['rootRLR'];center=p.q.mean(0);rot=Rotation.from_rotvec([.1,.2,.25]).as_matrix();p.q=(p.q-center)@np.diag([1,.995,1])@rot.T+center;p.vg[:]=[.02,0,0];p.update_state()
    return s
def write(current):
    (W/'dynamics.partial.json').write_text(json.dumps({'checks':{k:bool(v) for k,v in checks.items()},'results':results,'wall_s':time.monotonic()-start,'current':current},indent=2))
    (W/'status.json').write_text(json.dumps({'updated':datetime.now(timezone.utc).isoformat(),'status':'multicut_dynamics_running' if current else 'multicut_dynamics_completed','simulation_running':bool(current),'pid':os.getpid() if current else None,'current':current,'production_changed':False,'adopted':False},indent=2))
def run(kind,half=False,order=5):
    s=construct(kind,order);name=kind+('_half' if half else '')+('_order7' if order==7 else '');dt=dt0/(2 if half else 1);n=round(duration/dt);sample=round(.0001/dt);initial=s.metrics();work=0.;workscale=0.;maxenergy=0.;maxP=0.;maxL=0.;leak=0.;ahead=0.;behind=0.;bounds=[10.,.1];tic=time.monotonic();xs=[];vs=[];rows=[];qframes={key:[p.q.copy()] for key,p in s.pieces.items()};vframes={key:[p.vg.copy()] for key,p in s.pieces.items()};times=[0.];write(name)
    if kind=='partial':
        active=s.pieces['rootRL'];indices=active.indices;selected=np.zeros(len(X),bool);selected[indices]=True;low=selected&(X[:,1]<.0003);high=selected&~low
        weights=np.exp(-((X[:,0]-.001)/.001)**2-(X[:,2]/.004)**2);force=np.zeros_like(X);force[high,1]=.02*weights[high]/weights[high].sum();force[low,1]=-.02*weights[low]/weights[low].sum()
        points=np.stack(np.meshgrid(np.linspace(-.0021,.0021,41),np.linspace(-.006,.006,7),indexing='ij'),axis=-1).reshape(-1,2)
        idle=[k for k in s.pieces if k!='rootRL']
    else:idle=[k for k in s.pieces if k!='rootRLR']
    for i in range(n):
        if kind=='partial':
            f0=force*np.sin(np.pi*i*dt/duration)**2;f1=force*np.sin(np.pi*(i+1)*dt/duration)**2;oldx=s.observations()[0];s.step(dt,f0,f1);work+=float(np.sum(.5*(f0+f1)*(s.observations()[0]-oldx)));workscale=max(workscale,abs(work))
        else:s.step(dt)
        if (i+1)%sample==0:
            m=s.metrics();maxenergy=max(maxenergy,abs(m['energy']-initial['energy']-work));maxP=max(maxP,float(np.linalg.norm(m['momentum']-initial['momentum'])));maxL=max(maxL,float(np.linalg.norm(m['angular']-initial['angular'])));leak=max(leak,*[float(np.linalg.norm(s.pieces[k].v,axis=1).max()) for k in idle]);cs=[c for p in s.pieces.values() for c in volume_certificates(p)];assert all(c['passed'] for c in cs),cs;bounds=[min(bounds[0],*[c['minJ_lower_bound'] for c in cs]),max(bounds[1],*[c['maxJ_upper_bound'] for c in cs])]
            if kind=='partial':
                jump=active.face_jump(points);ahead=max(ahead,float(np.linalg.norm(jump[points[:,0]<=0],axis=1).max()));behind=max(behind,float(np.linalg.norm(jump[points[:,0]>.0005],axis=1).max()))
            x,v,F=s.observations();xs.append(x);vs.append(v);times.append(s.time)
            for key,p in s.pieces.items():qframes[key].append(p.q.copy());vframes[key].append(p.vg.copy())
            rows.append({'t':s.time,'energy':m['energy'],'work':work,'energy_error':m['energy']-initial['energy']-work,'idle_speed':leak,'ahead_jump':ahead,'behind_jump':behind})
        if time.monotonic()-tic>600:raise TimeoutError(name)
    scale=workscale if kind=='partial' else initial['energy'];checks[name+'_energy']=maxenergy<max(1e-12,.05*abs(scale));checks[name+'_momentum']=maxP<1e-9;checks[name+'_independence']=leak/.02<.01
    if kind=='partial':checks[name+'_bridge']=ahead<1e-11 and behind>1e-9
    else:checks[name+'_angular']=maxL<1e-10
    result={'wall_s':time.monotonic()-tic,'sim_s':duration,'pieces':len(s.pieces),'cut_count':s.cut_count,'integral_points':sum(len(p.volumes) for p in s.pieces.values()),'energy_error_J':maxenergy,'energy_scale_J':scale,'linear_momentum_error_N_s':maxP,'angular_momentum_error_N_m_s':maxL,'idle_speed_m_s':leak,'idle_fraction_of_0_02_probe':leak/.02,'ahead_jump_m':ahead,'behind_jump_m':behind,'J_bounds':bounds,'peak_RSS_MiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'fixture':'Prescribed reference-axis cuts and manufactured spatial gaps. No blade or physical fracture.'}
    results[name]=result;(R/(name+'.json')).write_text(json.dumps({'result':result,'rows':rows},indent=2));s.save(R/(name+'.npz'));frames={'t':times}
    for k in qframes:frames[k+'_q']=np.asarray(qframes[k]);frames[k+'_vg']=np.asarray(vframes[k])
    np.savez_compressed(R/(name+'_trace.npz'),**frames);write(name+' completed');assert all(checks.values()),checks
    return np.asarray(xs),np.asarray(vs)
def compare(a,b,label):
    dx=float(np.linalg.norm(a[0]-b[0],axis=-1).max());dv=float(np.linalg.norm(a[1]-b[1],axis=-1).max());results[label]={'x_m':dx,'v_m_s':dv};checks[label]=dx<1e-4 and dv<.005;assert checks[label],results[label]
for kind in ['partial','full']:
    a=run(kind);b=run(kind,half=True);compare(a,b,kind+'_dt_refinement');c=run(kind,order=7);compare(a,c,kind+'_quadrature_refinement')
out={'status':'pass_restricted_unit_scope','checks':{k:bool(v) for k,v in checks.items()},'results':results,'wall_s':time.monotonic()-start,'peak_RSS_MiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'scope':'Sequential reference-axis unit cuts; no live blade or paid fracture'};(W/'dynamics_controls.json').write_text(json.dumps(out,indent=2));write(None);print(json.dumps(out,indent=2))
