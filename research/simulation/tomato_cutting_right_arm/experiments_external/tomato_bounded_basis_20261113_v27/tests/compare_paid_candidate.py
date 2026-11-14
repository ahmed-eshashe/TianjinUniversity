from pathlib import Path
import sys,os,json,itertools,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
from compiled_body import Body
from scipy.spatial import ConvexHull
import argparse
p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--reference',default='event_250us_sparse');args=p.parse_args()
paths=[W/'runs'/args.reference,W/'runs'/args.candidate];reports=[json.loads((p/'result.json').read_text()) for p in paths];bodies=[Body.restore(p/'last_accepted.npz') for p in paths];a,b=bodies;upper=[];vupper=[];weighted_bounds=[];pairs=0;groups={}
for j in range(len(b.X)):groups.setdefault(tuple(b.inv[j].ravel()),[]).append(j)
for i,poly in enumerate(a.polys):
 candidates=[j for j in groups[tuple(a.inv[i].ravel())] if np.all(poly.max(0)+1e-14>=b.polys[j].min(0)) and np.all(b.polys[j].max(0)+1e-14>=poly.min(0))];assert candidates;N=np.c_[np.ones(len(poly)),poly]@a.inv[i];u=N@a.u[a.ids[i]];v=N@a.v[a.ids[i]];pe=ve=0.
 for j in candidates:
  lo=np.maximum(poly.min(0),b.polys[j].min(0));hi=np.minimum(poly.max(0),b.polys[j].max(0));box=np.array(list(itertools.product(*zip(lo,hi))));Ni=np.c_[np.ones(8),box]@a.inv[i];Nj=np.c_[np.ones(8),box]@b.inv[j];pe=max(pe,float(np.linalg.norm(Ni@a.u[a.ids[i]]-Nj@b.u[b.ids[j]],axis=1).max()));pair_velocity=float(np.linalg.norm(Ni@a.v[a.ids[i]]-Nj@b.v[b.ids[j]],axis=1).max());ve=max(ve,pair_velocity);weighted_bounds.append(min(a.V[i],b.V[j])*pair_velocity**2);pairs+=1
 upper.append(pe);vupper.append(ve)
# Bound each common region using its enclosing intersected boxes, then
# bound overlap volume by min(Va,Vb). Summing ALL potentially overlapping pairs
# overcounts volume but cannot underestimate weighted error; no sampling.
def crack_rank(body):
 E=body._valid_basis;jumps=[]
 for r in np.flatnonzero(body.codes%3==1):
  for q in np.flatnonzero(body.codes%3==2):
   if not np.array_equal(body.inv[r],body.inv[q]):continue
   hull=ConvexHull(body.polys[q]);mask=np.max(body.polys[r]@hull.equations[:,:3].T+hull.equations[:,3],axis=1)<1e-12
   for point in body.polys[r][mask]:
    N=np.r_[1.,point]@body.inv[r];jumps.append(N@E[body.ids[r]].toarray()-N@E[body.ids[q]].toarray())
 return int(np.linalg.matrix_rank(np.array(jumps),tol=1e-10)) if jumps else 0
ranks=[crack_rank(x) for x in bodies]
position=max(upper);velocity=float(np.sqrt(sum(weighted_bounds)/a.V.sum()));cases={}
for field,floor in [('contact_N',1e-4),('cutting_N',1e-4)]:
 x=np.array([r[field] for r in reports[0]['rows']]);y=np.array([r[field] for r in reports[1]['rows']]);assert x.shape==y.shape;cases[field]=float(np.max(abs(x-y))/max(np.max(abs(y)),floor))
work=abs(reports[0]['paid_fracture_work_J']-reports[1]['paid_fracture_work_J'])/max(reports[1]['paid_fracture_work_J'],1e-8);checks=dict(position=position<=.0001,weighted_velocity=velocity<=.005,contact_force=cases['contact_N']<=.05,cutting_force=cases['cutting_N']<=.05,fracture_work=work<=.05,all_events=all(all(e['checks'].values()) for r in reports for e in r['events']),opening_modes_retained=ranks[1]>=ranks[0]>0,all_observed_openings_positive=all(row.get("opening_rank") is None or row["opening_rank"]>0 for row in reports[1]["rows"]));out=dict(passed=all(checks.values()),checks={k:bool(v) for k,v in checks.items()},position_bound_m=position,weighted_velocity_bound_m_s=velocity,maximum_velocity_bound_m_s=max(vupper),force_relative=cases,fracture_work_relative=work,region_pairs=pairs,opening_ranks=ranks,events=[len(r['events']) for r in reports],scope='Matched physical continuation of one shallow crack; input names and duration recorded explicitly. Not a full cut, tomato or RL gate.',reference=args.reference,candidate=args.candidate,duration_s=reports[1]['simulation_advanced_s']);(W/'reports'/(args.candidate+'_comparison.json')).write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
