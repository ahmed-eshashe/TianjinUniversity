from pathlib import Path
import sys,time,json,traceback,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from linear_reference import Body,strain_audit
from linear_gpu import GPU
start=time.perf_counter();checks={};rows=[]
def check(k,v,d=None):
 checks[k]=bool(v)
 if not v:raise AssertionError((k,d))
try:
 b=Body();b.u[:,1]=-.01*b.grid[:,1];b.u[:,0]=.003*b.grid[:,2];b.v=np.cross([.1,.2,.3],b.grid)
 cases=[('partial',[1,0,0],-.002,0,([0,-1,0],0),1),('completed',[1,0,0],-.002,0,None,2),('parallel',[1,0,0],.002,1,None,3),('cross',[0,1,0],0,2,None,6),('fourth',[0,0,1],0,3,None,12)]
 for name,n,d,slot,front,ncomp in cases:
  old=b.clone();err=b.split(n,d,cut_id=slot,front=front);a=strain_audit(b);row={'name':name,'transfer':err,'audit':a};rows.append(row);print(row,flush=True);check(name+'_rank',a['rank']==a['expected_rank'],a);check(name+'_components',a['components']==ncomp,a)
  g=GPU(b,dt=1e-6);g.step(20);g.export();b.save(W/'states'/f'multicut_{name}.npz')
 before=b.clone();rejected=False
 try:b.split([1,0,0],0,cut_id=4)
 except ValueError:rejected=True
 check('capacity_stop_preserves_state',rejected and np.array_equal(b.ids,before.ids) and np.array_equal(b.u,before.u) and b.history==before.history)
 # A translated, affine-deformed block receives a plane in current coordinates.
 b=Body();b.u=b.grid@np.array([[.0,.01,0],[.0,-.01,.0],[.0,0,.002]]).T+[.013,.007,-.004];err=b.split([1,.27,.13],.013+.27*.007+.13*(-.004)+.001,world=True);a=strain_audit(b);check('current_frame_rank',a['rank']==a['expected_rank'] and a['components']==2,a);rows.append({'name':'current_frame','transfer':err,'audit':a})
 # Long enough to excite fast local sliver modes; CPU and GPU start afresh.
 for name,n,d,dt in [('intact',None,0,12.5e-6),('oblique',[1,.27,.13],.001,6.25e-6),('sliver1um',[1,1,1],1e-6,1.5625e-6)]:
  b=Body();b.u[:,1]=-.01*b.grid[:,1];b.u[:,0]=.005*b.grid[:,2]
  if n is not None:b.split(n,d)
  c=b.clone();g=GPU(b.clone(),dt);nsteps=round(.002/dt);t=time.perf_counter()
  for _ in range(nsteps):c.step(dt)
  g.step(nsteps);g.export();diff={k:float(np.max(abs(a-z))) for k,a,z in zip(['x','v','F'],c.fields(),g.body.fields())};row={'name':name,'CPU_GPU_2ms':diff,'dt_s':dt,'wall_s':time.perf_counter()-t};rows.append(row);print(row,flush=True);check(name+'_CPU_GPU_2ms',diff['x']<=1e-6 and diff['v']<=1e-4 and diff['F']<=1e-4,row)
 result={'status':'pass_history_and_reference_components','checks':checks,'rows':rows,'wall_s':time.perf_counter()-start,'physical_cut':False}
except Exception as e:traceback.print_exc();result={'status':'failed','exception':repr(e),'checks':checks,'rows':rows,'wall_s':time.perf_counter()-start,'physical_cut':False}
(W/'history_and_cpu.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True);sys.exit(0 if result['status'].startswith('pass') else 1)
