"""Bounded read-only timing study: no accepted physics step or history commit."""
from pathlib import Path
import sys,json,time,hashlib,numpy as np
from scipy.interpolate import PchipInterpolator
W=Path(__file__).resolve().parent;R=W.parents[1];V=W.parent/'disect_bevel_reference_20261109_v33';sys.path.insert(0,str(W.parent/'disect_contact_linesearch_20261109_v32'))
from stable_blade import StableBlade,s,m,closure,torch,tensor
from stable_solver import Bulk
import adaptive_contact,tomato_compiled_blade_query as query_module
sys.path.insert(0,str(W.parent/'disect_section4_completion_20261109_v29'))
from volume_guard_limit_resolution import WholeVolumeGuard
source=V/'centered0080_resume_final.npz';z=np.load(source);h=float(z['dt']);t0=float(z['step'])*h;plan=json.loads((V/'correction_plan.json').read_text());curve=PchipInterpolator(*np.array(plan['front_lateral_path_m']).T)
def pose(t):
 u=t/plan['durations_s'][0];r=10*u**3-15*u**4+6*u**5;dr=30*u*u-60*u**3+30*u**4;d=plan['downward_stroke_m']*r;speed=plan['downward_stroke_m']*dr/plan['durations_s'][0]
 return np.array(plan['selected']['translation_m'])+[float(curve(d)),-d,0],np.array([float(curve.derivative()(d))*speed,-speed,0])
command='bash work/disect_numerics_20261108_v05/run.sh '+str(Path(__file__).resolve())
contract={'scope':'One immutable old-operator saved state; one warm uncommitted solve plus two timed reset solves and one cold/cached volume guard. No candidate adoption, cutting episode, history commit, physical parameter or tolerance change. No new coarser timestep.','source_checkpoint':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_time_s':t0,'maximum_uncommitted_solves':3,'wall_cap_s':180,'command':command,'sources':{str(Path(__file__).resolve()):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
(W/'profile_contract.json').write_text(json.dumps(contract,indent=2)+'\n');start=time.perf_counter();b=StableBlade();b.blade_enabled=True;mapping=dict(np.load(W.parent/'disect_precontact_20261108_v06/board_mapping.npz'));base=b.mask.clone()
def restore():
 b.x.copy_(tensor(z['x']));b.v.copy_(tensor(z['v']));b.fracture.load_state_dict({'history':z['history']});b.blade_translation,b.blade_velocity=pose(t0);b.eligibility_override=None;world=b.x@tensor(mapping['rotation']).T+tensor(mapping['translation']);H=tensor(mapping['halfspaces']);b.mask=base*torch.all(world[:,:2]@H[:,:2].T+H[:,2]<=0,dim=1)
def solve():
 restore();torch.cuda.synchronize();tic=time.perf_counter();info=b.implicit(h);torch.cuda.synchronize();elapsed=time.perf_counter()-tic;return info,elapsed,b.x.cpu().numpy().copy(),b.v.cpu().numpy().copy()
warm=solve();rows=[];phase='step';stats={};damping_events=[]
def add(k,dt,count=1):
 d=stats.setdefault(k,{'wall_s':0.,'calls':0});d['wall_s']+=dt;d['calls']+=count
raw_query=query_module._query
def timed_query(vertices,faces,points):
 tic=time.perf_counter();value=raw_query(vertices,faces,points);add(phase+'_solid_CAD_query',time.perf_counter()-tic);stats[phase+'_solid_CAD_query']['points']=stats[phase+'_solid_CAD_query'].get('points',0)+len(points);return value
query_module._query=timed_query
raw_intersections=adaptive_contact.intersections
def timed_intersections(*args):
 tic=time.perf_counter();value=raw_intersections(*args);add(phase+'_edge_triangle_intersections',time.perf_counter()-tic);return value
adaptive_contact.intersections=timed_intersections
original={}
def wrap(obj,name,label):
 method=getattr(obj,name);original[label]=method
 def timed(*args,**kw):
  torch.cuda.synchronize();tic=time.perf_counter();value=method(*args,**kw);torch.cuda.synchronize();add(label,time.perf_counter()-tic);return value
 setattr(obj,name,timed)
wrap(b,'geometry','geometry_total');wrap(b,'contact','contact_total');wrap(b.fracture,'evaluate','cohesive_evaluation');wrap(closure,'evaluate','compressive_closure')
material=Bulk.geometry
# Bulk.geometry is invoked explicitly by EdgeBlade.geometry.
def timed_bulk(self,*args,**kw):
 torch.cuda.synchronize();tic=time.perf_counter();value=material(self,*args,**kw);torch.cuda.synchronize();add('bulk_elastic_geometry',time.perf_counter()-tic);return value
Bulk.geometry=timed_bulk
raw_damping=b.damping
def timed_damping(*args):
 before=torch.cuda.Event(enable_timing=True);after=torch.cuda.Event(enable_timing=True);before.record();value=raw_damping(*args);after.record();damping_events.append((before,after));return value
b.damping=timed_damping
for repetition in range(2):
 stats={};damping_events=[];info,elapsed,q,v=solve();torch.cuda.synchronize();stats['damping_GPU_events']={'gpu_s':sum(a.elapsed_time(c) for a,c in damping_events)/1000,'calls':len(damping_events)}
 difference={'position_m':float(np.linalg.norm(q-warm[2],axis=1).max()),'velocity_m_s':float(np.linalg.norm(v-warm[3],axis=1).max())};assert difference['position_m']<1e-10 and difference['velocity_m_s']<1e-7;assert info['relative_residual']<=1e-9 and info['inner_max_residual']<=1e-9;assert np.array_equal(z['history'],b.fracture.state_dict()['history'])
 rows.append({'repetition':repetition,'total_s':elapsed,'solver':info,'timings':stats,'difference_from_uninstrumented_trial':difference});assert time.perf_counter()-start<180
phase='volume';stats={};guard=WholeVolumeGuard(b.cad,m['tets']);T,_=pose(t0+h);tic=time.perf_counter();proof=guard.check(q,T,known_inside_depth=b.blade_sample['maximum_penetration_m']);cold=time.perf_counter()-tic;tic=time.perf_counter();again=guard.check(q,T);cached=time.perf_counter()-tic;assert proof['passed'] and again['passed'];volume_stats=stats
phase='io';tic=time.perf_counter();np.savez_compressed(W/'profile_uncommitted_trial_NOT_A_CHECKPOINT.npz',x=q,v=v,history=z['history']);file_wall=time.perf_counter()-tic
assert hashlib.sha256(source.read_bytes()).hexdigest()==contract['source_sha256'];assert np.array_equal(z['history'],b.fracture.state_dict()['history']);out={'scope':contract['scope'],'warm_uninstrumented_solve_s':warm[1],'repetitions':rows,'cold_volume_guard_s':cold,'identical_state_cached_guard_s':cached,'volume_query_timings':volume_stats,'volume_guard_passed':proof['passed'],'compressed_snapshot_write_s':file_wall,'source_checkpoint_unchanged':True,'history_uncommitted_and_unchanged':True,'wall_s':time.perf_counter()-start,'qualified_physical_episode':False}
(W/'profile_result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
