from pathlib import Path
from datetime import datetime,timezone
import sys,time,json,contextlib,resource,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));B=W.parent/'tomato_event_front_20261111_v14'
import event_sweep,multicut
from event_sweep import EventSweep
from gpu_backend import GPUReference
from blade_sweep import pose
records=[];stack=[];trials=[];accepted=[];trial_context=None;checks={};setup=[]
@contextlib.contextmanager
def timed(name,extra=None):
 node={'name':name,'trial_id':trial_context,'child_s':0.,**(extra or {})};stack.append(node);begin=time.perf_counter()
 try:yield node
 finally:
  elapsed=time.perf_counter()-begin;stack.pop();node['inclusive_s']=elapsed;node['exclusive_s']=max(0.,elapsed-node.pop('child_s'));records.append(node)
  if stack:stack[-1]['child_s']+=elapsed

def method(cls,name,label):
 original=getattr(cls,name)
 def wrapper(self,*a,**kw):
  extra={}
  if isinstance(self,GPUReference):extra={'modes':self.ng if hasattr(self,'ng') else None}
  if name=='step' and isinstance(self,GPUReference):extra.update(n=a[0] if a else kw.get('n',1),dt=self.dt)
  if name=='propose':label_here='coverage_preview' if kw.get('preview_only') else 'coverage_and_topology_commit_proposal'
  else:label_here=label
  with timed(label_here,extra):result=original(self,*a,**kw)
  if name=='__init__' and isinstance(self,GPUReference):setup.append({'trial_id':trial_context,'preparation_s':self.preparation_s,'packing_upload_s':self.upload_s,'memory_bytes':self.memory()})
  return result
 setattr(cls,name,wrapper)
for name,label in [('__init__','GPU_constructor'),('step','GPU_checked_chunk'),('graph','graph_lookup_capture'),('export','GPU_export')]:method(GPUReference,name,label)
method(multicut.MultiCut,'step','CPU_fractional_mechanics');method(EventSweep,'propose','coverage');method(EventSweep,'propagate','propagate');method(EventSweep,'save','checkpoint_write')
for module in [event_sweep,multicut]:
 old=module.volume_certificates
 def wrapped_volume(*a,_old=old,**kw):
  with timed('continuous_volume_check'):return _old(*a,**kw)
 module.volume_certificates=wrapped_volume
oldtrial=EventSweep.trial

def wrapper_trial(self,target,duration):
 global trial_context
 tid=len(trials);trials.append({'id':tid,'start_time_s':self.cpu.time,'duration_s':duration});prior=trial_context;trial_context=tid
 try:
  with timed('trial_total',{'duration_s':duration}) as record:t,p=oldtrial(self,target,duration)
  t.review_trial_id=tid;trials[tid].update(would_activate=p['topology_changed'],wall_s=record['inclusive_s']);return t,p
 finally:trial_context=prior
EventSweep.trial=wrapper_trial
oldcommit=EventSweep.commit

def wrapped_commit(self,p):
 with timed('accepted_geometry_commit'):r=oldcommit(self,p)
 if hasattr(self,'review_trial_id'):accepted.append(self.review_trial_id)
 return r
EventSweep.commit=wrapped_commit

(W/'status.json').write_text(json.dumps({'updated':datetime.now(timezone.utc).isoformat(),'status':'profiling one saved activation','simulation_running':True,'production_changed':False},indent=2))
with timed('checkpoint_read'):d=EventSweep.restore(B/'runs/primary/frame1')
before=d.cpu.time;target=np.array(json.loads((B/'runs/primary/final.json').read_text())['pose']);begin=time.perf_counter()
with timed('action_total'):d.action(target,.0001-before,wall_limit=300)
wall=time.perf_counter()-begin
with timed('checkpoint_write_verified'):
 d.save(W/'runs/profiled_activation')
ref=EventSweep.restore(B/'runs/primary/final');checks['exact_final_fingerprint']=d.fingerprint()==ref.fingerprint();checks['same_activations']=d.activations==ref.activations
pa,pb=d.cpu.pieces['root'],ref.cpu.pieces['root'];errors={f:float(np.linalg.norm(pa.T@getattr(pa,f)-pb.T@getattr(pb,f),axis=1).max()) for f in ['q','vg']};checks['fields_identical']=all(v==0 for v in errors.values())
accepted=set(accepted)
for t in trials:t['accepted']=t['id'] in accepted
summary={}
for r in records:
 k=r['name'];m=summary.setdefault(k,{'calls':0,'inclusive_s':0.,'exclusive_s':0.});m['calls']+=1;m['inclusive_s']+=r['inclusive_s'];m['exclusive_s']+=r['exclusive_s']
bygroup={}
for group,mask in [('accepted',True),('discarded',False)]:
 ids={t['id'] for t in trials if t['accepted']==mask};rr=[r for r in records if r['trial_id'] in ids];bygroup[group]={'trials':len(ids),'trial_wall_s':sum(t['wall_s'] for t in trials if t['accepted']==mask),'GPU_microsteps':sum(r['n'] for r in rr if r['name']=='GPU_checked_chunk'),'GPU_chunk_excluding_graph_s':sum(r['exclusive_s'] for r in rr if r['name']=='GPU_checked_chunk'),'GPU_setup_s':sum(r['inclusive_s'] for r in rr if r['name']=='GPU_constructor'),'geometry_preview_s':sum(r['inclusive_s'] for r in rr if r['name']=='coverage_preview')}
result={'status':'completed' if all(checks.values()) else 'failed','simulated_interval_s':.0001-before,'action_wall_s':wall,'summary':summary,'trial_groups':bygroup,'trials':trials,'records':records,'GPU_setup_breakdown':setup,'checks':checks,'field_difference':errors,'peak_RSS_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'note':'Exact saved-case replay with timed wrappers. Categories are nested; exclusive times sum without double counting. Accepted/discarded trial wall sums include their cloning, propagation and preview. Actual commit plus diagnostics sit outside those trials. No mechanics changed.'}
(W/'activation_profile.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['records','trials','GPU_setup_breakdown']},indent=2));assert all(checks.values())
