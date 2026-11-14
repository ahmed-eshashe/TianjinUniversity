"""Bounded complete-body mechanics/history cost diagnostic, not an RL rollout."""
from pathlib import Path
import sys,json,time,numpy as np,warp as wp,cProfile,pstats,io
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from linear_reference import Body
from linear_gpu import GPU
rows=[];start=time.perf_counter()
def record(row):
 rows.append(row);print(row,flush=True);(W/'cost.partial.json').write_text(json.dumps({'rows':rows,'wall_s':time.perf_counter()-start},indent=2))
def batch(b,n):
 o=b.clone();ng=len(b.u);o.u=np.tile(b.u,(n,1));o.v=np.tile(b.v,(n,1));o.grid=np.tile(b.grid,(n,1));o.ids=np.concatenate([b.ids+i*ng for i in range(n)])
 for k in ['X','G','N','inv']:setattr(o,k,np.tile(getattr(b,k),(n,)+(1,)*(getattr(b,k).ndim-1)))
 o.V=np.tile(b.V,n);o.codes=np.tile(b.codes,n);o.polys=[p.copy() for _ in range(n) for p in b.polys];o.rebuild();return o

assert json.loads((W/'refinement.json').read_text())['status']=='pass_dynamic_components'
assert json.loads((W/'history_and_cpu.json').read_text())['status']=='pass_history_and_reference_components'
base=Body(n=10);base.u[:,1]=-.01*base.grid[:,1];base.u[:,0]=.005*base.grid[:,2]
for dt in [12.5e-6,6.25e-6,1.5625e-6]:
 for count in [1,4,8]:
  b=batch(base,count);g=GPU(b,dt);steps=round(.02/dt);block=64;g.graph(block)
  if steps%block:g.graph(steps%block)
  snap=[wp.clone(g.u),wp.clone(g.v)];g.step(1);times=[]
  for rep in range(3):
   wp.copy(g.u,snap[0]);wp.copy(g.v,snap[1]);g.steps=0;wp.synchronize_device();t=time.perf_counter();g.step(steps);times.append(time.perf_counter()-t)
  g.export();record({'kind':'fixed_topology_bulk_ceiling_only','batch':count,'regions_per_body':len(base.X),'nodes_per_body':len(base.u),'dt_s':dt,'sim_s_each':.02,'wall_s':times,'median_s':float(np.median(times)),'equivalent_50Hz_transitions_s':count/float(np.median(times)),'array_bytes':g.memory(),'history_contact_robot_policy_included':False})

# One bounded history event profile, at an accepted loaded state. The event is
# a prescribed geometric partial/full plane fixture, not paid physical fracture.
for count in [1,4,8]:
 b=batch(base,count);dt=1.5625e-6;g=GPU(b,dt);g.step(640);g.export();initial=b.metrics();times=[]
 for j,front in enumerate([([0,-1,0],0),None]):
  profile=cProfile.Profile() if count==1 and j==0 else None
  if profile:profile.enable()
  t=time.perf_counter();err=b.split([1,.27,.13],.001,cut_id=0,front=front);elapsed=time.perf_counter()-t
  if profile:
   profile.disable();profile.dump_stats(str(W/'reports/history_profile.pstats'));buf=io.StringIO();pstats.Stats(profile,stream=buf).sort_stats('cumulative').print_stats(18);(W/'reports/history_profile.txt').write_text(buf.getvalue())
  # Upload/capture a new topology then evolve for 1ms. Time all rebuild work.
  t=time.perf_counter();g=GPU(b,dt);g.step(640);g.export();continuation=time.perf_counter()-t;times.append(elapsed+continuation);record({'kind':'evolving_geometric_history','batch':count,'event':'partial' if j==0 else 'complete','dt_s':dt,'sim_s_after_event_each':.001,'regions_total':len(b.X),'nodes_total':len(b.u),'history_update_wall_s':elapsed,'GPU_rebuild_capture_and_1ms_wall_s':continuation,'transfer_errors':err,'includes_contact_robot_policy':False})
 total=sum(times);record({'kind':'two_geometric_events_total','batch':count,'wall_s':total,'sim_s_after_events_each':.002,'equivalent_50Hz_transitions_s':50*count*.002/total,'note':'dense event diagnostic, not normal episode average; mechanics+history only'})

(W/'cost.json').write_text(json.dumps({'rows':rows,'wall_s':time.perf_counter()-start,'physical_contact_or_RL_qualified':False},indent=2));print('COMPLETE',flush=True)
