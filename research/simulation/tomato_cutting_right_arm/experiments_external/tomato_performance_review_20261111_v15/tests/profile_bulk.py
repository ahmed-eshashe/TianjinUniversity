from pathlib import Path
from datetime import datetime,timezone
import sys,time,json,copy,resource,subprocess,os,platform
import numpy as np,scipy,warp as wp
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));B=W.parent/'tomato_event_front_20261111_v14'
from event_sweep import EventSweep,clone_cpu
from gpu_backend import GPUReference
from multicut import volume_certificates
DT=2.44140625e-8;N=256;rows=[];checks={};profiles={};states={};start=time.perf_counter()
def write():
 (W/'bulk_profile.json').write_text(json.dumps({'status':'running','dt_s':DT,'steps_per_timed_sample':N,'rows':rows,'kernel_profiles':profiles,'checks':checks,'wall_s':time.perf_counter()-start},indent=2))
def check(k,v):
 checks[k]=bool(v)
 if not v:raise AssertionError(k)
def mark(s):
 print(s,flush=True);(W/'status.json').write_text(json.dumps({'updated':datetime.now(timezone.utc).isoformat(),'status':s,'simulation_running':True,'production_changed':False},indent=2))
def batch(s,n):
 b=clone_cpu(s);b.X=np.tile(s.X,(n,1));b.fixed=np.tile(s.fixed,n);b.pieces={}
 for env in range(n):
  c=clone_cpu(s)
  for key,p in c.pieces.items():p.indices=p.indices+env*len(s.X);b.pieces[f'env{env}_{key}']=p
 return b

def measure(name,s,batchsize=1,profile=True):
 mark(f'bulk {name}, independent copies {batchsize}');begin=time.perf_counter();cpu=batch(s,batchsize);g=GPUReference(cpu,dt=DT);creation=time.perf_counter()-begin
 snapshots={f:wp.clone(getattr(g,f)) for f in ['q','v','impulse','moment','clock']};wp.synchronize_device()
 def reset():
  for f,a in snapshots.items():wp.copy(getattr(g,f),a)
  g.bad.zero_();g.steps=0;wp.synchronize_device()
 begin=time.perf_counter();g.step(N);wp.synchronize_device();first=time.perf_counter()-begin;warm_graph=g.graph_build_s;reset()
 times=[];answer=None
 for repeat in range(5):
  reset();t=time.perf_counter();g.step(N);wp.synchronize_device();times.append(time.perf_counter()-t)
  fields=(g.q.numpy(),g.v.numpy())
  if answer is None:answer=fields
  else:check(f'{name}_batch{batchsize}_repeat{repeat}_exact',all(np.array_equal(a,b) for a,b in zip(answer,fields)))
 t=time.perf_counter();g.export();export=time.perf_counter()-t
 for p in cpu.pieces.values():check(f'{name}_batch{batchsize}_{p.indices[0]}_volume',all(c['passed'] for c in volume_certificates(p)))
 one=list(cpu.pieces.values())[0];old=list(s.pieces.values())[0]
 check(f'{name}_batch{batchsize}_energy',abs(one.metrics()['energy']-old.metrics()['energy'])<max(1e-12,.05*old.metrics()['energy']))
 if batchsize==1:states[name]=one
 else:
  ref=states[name]
  for i,p in enumerate(cpu.pieces.values()):check(f'{name}_batch{batchsize}_independent{i}',np.max(abs(p.q-ref.q))<1e-11 and np.max(abs(p.vg-ref.vg))<1e-8)
 r={'fixture':name,'batch':batchsize,'basis_modes_per_environment':len(one.q),'quadrature_points_per_environment':len(one.volumes),'observation_points_per_environment':len(one.X),'num_pieces':len(cpu.pieces),'full_mass_nnz_per_environment':one.M.nnz,'inverse_mobility_nnz_total':g.A[2].size,'gradient_nnz_total':g.G[1].size,'state_assembly_and_GPU_constructor_s':creation,'operator_preparation_s':g.preparation_s,'packing_and_upload_s':g.upload_s,'initial_checked_chunk_s':first,'graph_build_s':warm_graph,'cached_module_load_s':g.module_load_s,'warm_checked_sample_s':times,'median_s':float(np.median(times)),'min_s':min(times),'max_s':max(times),'device_export_and_CPU_observations_s':export,'GPU_owned_arrays_bytes':g.memory(),'peak_RSS_so_far_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'simulated_s_per_environment':N*DT}
 r['aggregate_sim_s_per_wall_s']=N*DT*batchsize/r['median_s'];r['optimistic_equivalent_50Hz_transitions_per_wall_s']=50*r['aggregate_sim_s_per_wall_s'];rows.append(r);write();print(json.dumps(r),flush=True)
 if profile:
  reset();g.step(1,graph=False)
  with wp.ScopedTimer('32 uncaptured checked microsteps',print=False,synchronize=True,cuda_filter=wp.TIMING_KERNEL) as timer:g.step(32,graph=False)
  agg={}
  for item in timer.timing_results:agg[item.name]=agg.get(item.name,0)+item.elapsed
  profiles[name]={'microsteps':32,'host_wall_ms':timer.elapsed,'kernel_elapsed_ms':agg,'summed_kernel_ms':sum(agg.values()),'samples':len(timer.timing_results),'note':'Uncaptured kernel diagnostic, not throughput. Actual throughput uses synchronized warm captured graph samples above.'};write()
 return r

for name,path in [('intact',B/'runs/primary/initial'),('one_front',B/'runs/primary/final'),('two_fronts',B/'runs/heldout/final')]:
 s=EventSweep.restore(path).cpu;measure(name,s)
 if name=='one_front':
  for n in [4,8]:measure(name,s,n,False)
result=json.loads((W/'bulk_profile.json').read_text());result.update(status='completed',wall_s=time.perf_counter()-start,checks=checks);(W/'bulk_profile.json').write_text(json.dumps(result,indent=2))
meta={'recorded':datetime.now(timezone.utc).isoformat(),'python':sys.version,'executable':sys.executable,'numpy':np.__version__,'scipy':scipy.__version__,'warp':wp.__version__,'platform':platform.platform(),'OPENBLAS_NUM_THREADS':os.environ.get('OPENBLAS_NUM_THREADS'),'GPU':subprocess.run(['nvidia-smi','--query-gpu=name,driver_version,memory.total,memory.used,utilization.gpu,power.draw','--format=csv'],capture_output=True,text=True).stdout,'compute_processes':subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv'],capture_output=True,text=True).stdout,'power_supplies':{p.name:{n:(p/n).read_text().strip() for n in ['type','online','status','capacity'] if (p/n).exists()} for p in Path('/sys/class/power_supply').glob('*')},'note':'Normal desktop/browser present; no viewer or other compute engine. No installs, clock/power changes or production edits.'}
(W/'environment.json').write_text(json.dumps(meta,indent=2));print('BULK PROFILE COMPLETE',flush=True)
