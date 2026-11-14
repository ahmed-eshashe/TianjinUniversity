from pathlib import Path
import sys,time,json,copy,numpy as np,warp as wp
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from local_reference import LocalBody
from local_gpu import GPU
checks={};rows=[];states={};start=time.perf_counter()
def batch(b,n):
 out=b.clone();ng=len(b.u);np_=len(b.X)
 out.u=np.tile(b.u,(n,1));out.v=np.tile(b.v,(n,1));out.grid=np.tile(b.grid,(n,1));out.X=np.tile(b.X,(n,1));out.ids=np.concatenate([b.ids+i*ng for i in range(n)]);out.N=np.tile(b.N,(n,1));out.G=np.tile(b.G,(n,1,1));out.V=np.tile(b.V,n);out.codes=np.tile(b.codes,n);out.rebuild();return out

def log():
 (W/'intact_cost.partial.json').write_text(json.dumps({'checks':checks,'rows':rows,'wall_s':time.perf_counter()-start,'angled_cut_not_qualified':True},indent=2));print(rows[-1] if rows else checks,flush=True)
for dt in [12.5e-6,6.25e-6]:
 b=LocalBody(n=2,h=.006);b.u[:,1]=-.01*b.grid[:,1];m=b.metrics();g=GPU(b,dt=dt);t=time.perf_counter();g.step(round(.002/dt));g.export();end=b.metrics();states[dt]=b;checks['energy_'+str(dt)]=abs((end['U']+end['T'])-(m['U']+m['T']))<=.05*(m['U']+m['T']);rows.append({'kind':'12mm intact release','dt':dt,'sim_s':.002,'wall_s':time.perf_counter()-t,'energy_residual_relative':abs(end['U']+end['T']-m['U']-m['T'])/(m['U']+m['T'])});log()
a,b=states.values();af,bf=a.fields(),b.fields();diff={k:float(np.max(np.linalg.norm(x-y,axis=-1))) for k,x,y in zip(['x','v','F'],af,bf)};checks['intact_dt_position']=diff['x']<1e-4;checks['intact_dt_velocity']=diff['v']<.005
(W/'intact_dt.json').write_text(json.dumps({'checks':checks,'difference':diff},indent=2))
for count in [1,4,8]:
 b=LocalBody(n=10,h=.006);b.u[:,1]=-.01*b.grid[:,1];body=batch(b,count);g=GPU(body,dt=12.5e-6);g.step(1);snap=[wp.clone(g.u),wp.clone(g.v)];g.graph(64);wp.synchronize_device();times=[]
 for rep in range(3):
  wp.copy(g.u,snap[0]);wp.copy(g.v,snap[1]);g.steps=0;wp.synchronize_device();t=time.perf_counter();g.step(256);times.append(time.perf_counter()-t)
 g.export();r={'kind':'60mm intact bulk diagnostic only','batch':count,'material_points_per_body':len(b.X),'nodes_per_body':len(b.u),'sim_s_per_body':256*12.5e-6,'wall_s':times,'median_s':float(np.median(times)),'equivalent_transitions_s':50*count*256*12.5e-6/float(np.median(times)),'backend_array_bytes':g.memory(),'topology_qualified':False};rows.append(r);log()
(W/'intact_cost.json').write_text(json.dumps({'checks':checks,'rows':rows,'wall_s':time.perf_counter()-start,'angled_cut_not_qualified':True},indent=2));print('DIAGNOSTIC COMPLETE',flush=True)
