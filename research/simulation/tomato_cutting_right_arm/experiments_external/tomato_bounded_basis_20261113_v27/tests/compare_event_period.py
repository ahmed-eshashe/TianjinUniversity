from pathlib import Path
import sys,os,json,itertools,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
from compiled_body import Body
paths=[Path('/home/omen/Documents/Codex/experiments/tomato_local_continuity_20261113_v26/runs/continue_paid_r6'),W/'runs/event_250us_r1'];reports=[json.loads((p/'result.json').read_text()) for p in paths];bodies=[Body.restore(p/'last_accepted.npz') for p in paths];a,b=bodies;upper=[];vupper=[];weighted_bounds=[];pairs=0;groups={}
for j in range(len(b.X)):groups.setdefault(tuple(b.inv[j].ravel()),[]).append(j)
for i,poly in enumerate(a.polys):
 candidates=[j for j in groups[tuple(a.inv[i].ravel())] if np.all(poly.max(0)+1e-14>=b.polys[j].min(0)) and np.all(b.polys[j].max(0)+1e-14>=poly.min(0))];assert candidates;N=np.c_[np.ones(len(poly)),poly]@a.inv[i];u=N@a.u[a.ids[i]];v=N@a.v[a.ids[i]];pe=ve=0.
 for j in candidates:
  lo=np.maximum(poly.min(0),b.polys[j].min(0));hi=np.minimum(poly.max(0),b.polys[j].max(0));box=np.array(list(itertools.product(*zip(lo,hi))));Ni=np.c_[np.ones(8),box]@a.inv[i];Nj=np.c_[np.ones(8),box]@b.inv[j];pe=max(pe,float(np.linalg.norm(Ni@a.u[a.ids[i]]-Nj@b.u[b.ids[j]],axis=1).max()));pair_velocity=float(np.linalg.norm(Ni@a.v[a.ids[i]]-Nj@b.v[b.ids[j]],axis=1).max());ve=max(ve,pair_velocity);weighted_bounds.append(min(a.V[i],b.V[j])*pair_velocity**2);pairs+=1
 upper.append(pe);vupper.append(ve)
# Bound each common region using its enclosing intersected boxes, then
# bound overlap volume by min(Va,Vb). Summing ALL potentially overlapping pairs
# overcounts volume but cannot underestimate weighted error; no sampling.
position=max(upper);velocity=float(np.sqrt(sum(weighted_bounds)/a.V.sum()));cases={}
for field,floor in [('contact_N',1e-4),('cutting_N',1e-4),('gap_m',.0001)]:
 x=np.array([r[field] for r in reports[0]['rows']]);y=np.array([r[field] for r in reports[1]['rows']]);assert x.shape==y.shape;cases[field]=float(np.max(abs(x-y))/max(np.max(abs(y)),floor))
work=abs(reports[0]['paid_fracture_work_J']-reports[1]['paid_fracture_work_J'])/max(reports[1]['paid_fracture_work_J'],1e-8);checks=dict(position=position<=.0001,weighted_velocity=velocity<=.005,contact_force=cases['contact_N']<=.05,cutting_force=cases['cutting_N']<=.05,fracture_work=work<=.05,all_events=all(all(e['checks'].values()) for r in reports for e in r['events']),same_separation=reports[0]['physical_slice']==reports[1]['physical_slice']);out=dict(passed=all(checks.values()),checks={k:bool(v) for k,v in checks.items()},position_bound_m=position,weighted_velocity_bound_m_s=velocity,maximum_velocity_bound_m_s=max(vupper),force_relative=cases,fracture_work_relative=work,region_pairs=pairs,events=[len(r['events']) for r in reports],scope='0.9 ms continuation of one physically paid shallow crack, original versus bounded local basis, both dt 6.25 microseconds. Not a full cut, tomato or RL gate.');(W/'reports/event_250us_comparison.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
