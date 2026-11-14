"""Last predeclared intact timestep/cost control; no topology or contact qualification."""
from pathlib import Path
import sys,json,time,numpy as np,warp as wp
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from local_reference import LocalBody
from local_gpu import GPU
rows=[];states={};checks={};start=time.perf_counter()
for dt in [25e-6,12.5e-6]:
 b=LocalBody();b.u[:,1]=-.01*b.grid[:,1];e0=b.metrics()['U'];g=GPU(b,dt);g.step(round(.02/dt));g.export();m=b.metrics();err=abs(m['U']+m['T']-e0)/e0;rows.append({'kind':'12mm intact release','dt_s':dt,'sim_s':.02,'energy_residual_relative':err});checks['energy_'+str(dt)]=err<=.05;states[dt]=b;print(rows[-1],flush=True)
a,b=states.values();diff={k:float(np.max(np.linalg.norm(x-y,axis=-1))) for k,x,y in zip(['x','v','F'],a.fields(),b.fields())};checks['intact_position']=diff['x']<=1e-4;checks['intact_velocity']=diff['v']<=.005
for count in [1,4,8]:
 b=LocalBody(n=10,h=.006);b.u[:,1]=-.01*b.grid[:,1];o=b.clone();ng=len(b.u);o.u=np.tile(b.u,(count,1));o.v=np.tile(b.v,(count,1));o.grid=np.tile(b.grid,(count,1));o.X=np.tile(b.X,(count,1));o.ids=np.concatenate([b.ids+i*ng for i in range(count)]);o.N=np.tile(b.N,(count,1));o.G=np.tile(b.G,(count,1,1));o.V=np.tile(b.V,count);o.codes=np.tile(b.codes,count);o.rebuild()
 g=GPU(o,25e-6);g.graph(64);g.graph(32);snap=[wp.clone(g.u),wp.clone(g.v)];g.step(1);wp.synchronize_device();times=[]
 for _ in range(3):
  wp.copy(g.u,snap[0]);wp.copy(g.v,snap[1]);g.steps=0;wp.synchronize_device();t=time.perf_counter();g.step(800);times.append(time.perf_counter()-t)
 g.export();row={'kind':'intact bulk only, failed angled-cut model','dt_s':25e-6,'batch':count,'sim_s_per_body':.02,'points_per_body':len(b.X),'nodes_per_body':ng,'wall_s':times,'median_s':float(np.median(times)),'equivalent_aggregate_50Hz_transitions_s':count/float(np.median(times)),'backend_array_bytes':g.memory(),'cut_history_contact_robot_policy_included':False};rows.append(row);print(row,flush=True)
out={'checks':checks,'half_dt_difference':diff,'rows':rows,'wall_s':time.perf_counter()-start,'full_RL_qualification':False,'angled_cut_qualification':False};(W/'final_cost_control.json').write_text(json.dumps(out,indent=2));print('COMPLETE',flush=True)
