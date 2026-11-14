from numerics import *
import resource
start=time.perf_counter();b=Bulk();torch.cuda.synchronize();setup=time.perf_counter()-start
z=b.z;x=z['x'];n=len(x);out={'scope':'forward intact-bulk numerical controls only','setup_and_compile_wall_s':setup}
f0=b.geometry().cpu().numpy().copy();ref0=numpy_force(z,x,np.zeros_like(x))
out['rest_force']={'cuda_norm_N':float(np.linalg.norm(f0)),'numpy_norm_N':float(np.linalg.norm(ref0)),'difference_N':float(np.linalg.norm(f0-ref0))}
rng=np.random.default_rng(713);xd=x+rng.normal(size=x.shape)*1e-6;vd=rng.normal(size=x.shape)*1e-4
b.x.copy_(tensor(xd));b.v.copy_(tensor(vd));actual=b.material().cpu().numpy();ref=numpy_force(z,xd,vd);err=np.linalg.norm(actual-ref)
out['independent_constitutive']={'reference_norm_N':float(np.linalg.norm(ref)),'error_N':float(err),'relative_error':float(err/np.linalg.norm(ref)),'passed':bool(err<=max(1e-10,.001*np.linalg.norm(ref)))}
b.reset();b.geometry();out['small_force_controls']=[]
for rate in [1e-6,1e-4,.01,1.]:
    v=-rate*(x-x.mean(0));actual=-b.damping(tensor(v)).cpu().numpy().copy();ref=numpy_force(z,x,v)-ref0;err=float(np.linalg.norm(actual-ref));norm=float(np.linalg.norm(ref));out['small_force_controls'].append({'strain_rate_s_inv':rate,'reference_norm_N':norm,'error_N':err,'relative_error':err/max(norm,1e-30),'power_W':float(np.sum(actual*v)),'passed':bool(err<=max(1e-10,.001*norm) and np.sum(actual*v)<=0)})
v=np.tile([.1,-.2,.3],(n,1));fd=b.damping(tensor(v)).cpu().numpy().copy();out['common_translation_nullspace']={'norm_N':float(np.linalg.norm(fd)),'passed':bool(np.linalg.norm(fd)<1e-10)}

# Exercise the SAME CUDA integration kernel used by the corrected bulk adapter.
q0=np.array([[.08,.12,-.11],[.03,.04,.05]],dtype=float);q=tensor(q0);v=tensor([[.017,-.013,.011],[0,0,0]]);initial_v=v.cpu().numpy().copy();f=torch.zeros_like(q);im=tensor([1.,0.]);g=tensor([0.,0.,0.]);h=1.5e-7;steps=100000;T=h*steps
for _ in range(steps):b.k.step(q,v,f,im,g,h)
torch.cuda.synchronize();qa=q.cpu().numpy();va=v.cpu().numpy();e=float(np.max(np.abs(qa-(q0+initial_v*T))));ve=float(np.max(np.abs(va-initial_v)))
out['translation_integration']={'steps':steps,'dt_s':h,'sim_s':T,'position_error_m':e,'velocity_error_m_s':ve,'fixed_error_m':float(np.max(abs(qa[1]-q0[1]))),'passed':bool(e<1e-10 and ve<1e-8 and np.array_equal(qa[1],q0[1]))}
q=tensor(q0);v=torch.zeros_like(q);g=tensor([0.,-9.80665,0.])
for _ in range(steps):b.k.step(q,v,f,im,g,h)
qa=q.cpu().numpy();va=v.cpu().numpy();exact=q0.copy();exact[0]+=np.array([0,-9.80665,0])*.5*T*T;ev=np.zeros_like(q0);ev[0]=np.array([0,-9.80665,0])*T;e=float(np.max(abs(qa-exact)));ve=float(np.max(abs(va-ev)))
out['freefall_integration']={'position_error_m':e,'velocity_error_m_s':ve,'expected_euler_position_error_m':.5*9.80665*h*T,'passed':bool(e<1e-5 and ve<1e-8 and np.array_equal(qa[1],q0[1]))}

# Analytic underdamped oscillator x''+4x'+100x=0, x(0)=.001, v(0)=0.
q=tensor([[.001,0.,0.],[0.,0.,0.]]);v=torch.zeros_like(q);g=tensor([0.,0.,0.]);h=1e-5;T=.1
for _ in range(round(T/h)):
    f=-100*q-4*v;b.k.step(q,v,f,im,g,h)
wd=np.sqrt(96.);ex=.001*np.exp(-2*T)*(np.cos(wd*T)+2/wd*np.sin(wd*T));ev=-.001*np.exp(-2*T)*100/wd*np.sin(wd*T);ep=abs(q[0,0].item()-ex);evv=abs(v[0,0].item()-ev)
out['analytic_oscillator']={'position_error_m':ep,'velocity_error_m_s':evv,'passed':bool(ep<1e-5 and evv<.0001)}

b.reset()
for _ in range(40):b.explicit(1.5e-7)
first=b.arrays();b.guess.fill_(999);b.reset()
for _ in range(40):b.explicit(1.5e-7)
second=b.arrays();er=max(float(np.max(abs(a-c))) for a,c in zip(first,second));guess_zero=bool((b.guess==0).all().item());b.reset();fresh=Bulk();fresh_error=max(float(torch.max(abs(getattr(b,a)-getattr(fresh,a))).item()) for a in ['x','v','guess','f','g','j','diag','tmp'])
out['reset']={'repeat_max_error':er,'fresh_max_error':fresh_error,'cleared_guess':guess_zero,'passed':bool(er<1e-12 and fresh_error==0 and guess_zero)}
out['peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
out['peak_torch_allocated_bytes']=torch.cuda.max_memory_allocated();out['elapsed_wall_s']=time.perf_counter()-start
out['passed']=all(out[k]['passed'] for k in ['independent_constitutive','common_translation_nullspace','translation_integration','freefall_integration','analytic_oscillator','reset']) and all(a['passed'] for a in out['small_force_controls'])
(W/'controls_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
