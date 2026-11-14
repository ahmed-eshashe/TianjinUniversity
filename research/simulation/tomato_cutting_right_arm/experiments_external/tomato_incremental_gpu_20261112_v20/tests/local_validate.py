from pathlib import Path
import sys,time,json,traceback,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body as Ref
from local_geometry import Body as Local
from aggregation import Aggregate as RefAgg
from fast_aggregation import Aggregate as FastAgg,vertex_fields
rows=[];checks={}
def same(a,b):
 errors={}
 for k in ['grid','ids','inv','G','V','X','N','codes','u','v','mass']:
  x,y=getattr(a,k),getattr(b,k)
  if x.shape!=y.shape:return {'shape_failure':k},False
  errors[k]=float(np.max(abs(x-y)))
 if len(a.polys)!=len(b.polys):return {'poly_count_failure':True},False
 errors['poly_vertices']=max(float(np.max(abs(x-y))) if x.shape==y.shape else float('inf') for x,y in zip(a.polys,b.polys))
 return errors,all(errors[k]<= (0 if k in ['ids','codes'] else 1e-10) for k in errors)
try:
 cases=[('oblique',[1,.27,.13],.001,None,False),('corner',[1,1,1],1e-6,None,False),('aligned',[1,0,0],0,None,False),('partial',[1,.27,.13],.001,([0,-1,0],0),False),('world',[1,.27,.13],.001,([0,-1,0],.002),True),('tangent',[1,0,0],.012,None,False),('outside',[1,0,0],.1,None,False),('tiny',[1,-1,1],1e-7,None,False)]
 for name,n,d,front,world in cases:
  a=Ref(n=4);b=Local(n=4)
  for x in [a,b]:x.u[:,1]=-.01*x.grid[:,1];x.u[:,0]=.005*x.grid[:,2];x.v[:]=np.sin(x.grid*50)*.002
  t=time.perf_counter();a.split(n,d,front=front,world=world);ref=time.perf_counter()-t;t=time.perf_counter();b.split(n,d,front=front,world=world);local=time.perf_counter()-t
  err,ok=same(a,b);checks[name+'_split']=ok;ra=RefAgg(a);fa=FastAgg(b);de=float(abs(ra.E-fa.E).max());dm=float(abs(ra.M-fa.M).max());dq=float(np.max(abs(ra.q-fa.q)));dv=float(np.max(abs(ra.v-fa.v)));checks[name+'_aggregation']=de<=1e-10 and dm<=1e-12 and dq<=1e-10 and dv<=1e-10
  rows.append({'case':name,'ref_s':ref,'local_s':local,'difference':err,'aggregation_errors':{'E':de,'M':dm,'q':dq,'v':dv},'update':b.last_update});print(name,ok,flush=True)
 # Partial-to-complete, then history capacity across four planes.
 a=Ref(n=4);b=Local(n=4)
 for x in [a,b]:x.u[:,0]=.003*x.grid[:,2];x.v[:,1]=.001*np.sin(x.grid[:,0]*100)
 sequence=[([1,.2,.1],.001,0,([0,1,0],0)),([1,.2,.1],.001,0,None),([0,1,.1],.002,1,None),([0,0,1],.003,2,None),([1,1,0],-.004,3,None)]
 for j,(n,d,i,f) in enumerate(sequence):
  a.split(n,d,i,front=f);b.split(n,d,i,front=f);err,ok=same(a,b);checks[f'history_{j}']=ok;rows.append({'case':f'history_{j}','difference':err,'components':len(np.unique(b.components()[0])),'update':b.last_update})
 b.save(W/'states/local_restart.npz');r=Local.restore(W/'states/local_restart.npz');err,ok=same(b,r);checks['restart']=ok
 try:b.split([1,0,0],0,4);checks['capacity_stop']=False
 except ValueError:checks['capacity_stop']=True
 # Measured cost at 60 mm, no profiler instrumentation.
 for name,n,d in [('oblique',[1,.27,.13],.001),('corner',[1,1,1],1e-6)]:
  a=Ref(n=10);b=Local(n=10);t=time.perf_counter();b.prepare_geometry_cache();prepare=time.perf_counter()-t;t=time.perf_counter();a.split(n,d);ref=time.perf_counter()-t;t=time.perf_counter();b.split(n,d);local=time.perf_counter()-t;err,ok=same(a,b);checks['bulk_'+name]=ok
  t=time.perf_counter();ra=RefAgg(a);refagg=time.perf_counter()-t;t=time.perf_counter();fa=FastAgg(b);fastagg=time.perf_counter()-t
  checks['bulk_'+name+'_aggregate']=float(abs(ra.E-fa.E).max())<=1e-10 and float(abs(ra.M-fa.M).max())<=1e-12
  rows.append({'case':'bulk_'+name,'ref_s':ref,'local_s':local,'one_off_geometry_cache_s':prepare,'ref_aggregation_s':refagg,'fast_aggregation_s':fastagg,'difference':err,'update':b.last_update});print(rows[-1],flush=True)
 result={'status':'pass' if all(checks.values()) else 'failed','checks':{k:bool(v) for k,v in checks.items()},'rows':rows}
except Exception as e:traceback.print_exc();result={'status':'exception','exception':repr(e),'checks':{k:bool(v) for k,v in checks.items()},'rows':rows}
(W/'local_validation.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)
