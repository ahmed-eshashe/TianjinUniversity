from pathlib import Path
import sys,json,numpy as np,traceback
from scipy.spatial import ConvexHull
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from local_geometry import Body as Reference
from compiled_body import Body
from fast_aggregation import Aggregate
rng=np.random.default_rng(21012);rows=[];checks={}
try:
 for case in range(12):
  n=2+case%3;h=.003 if case%2 else .006;a=Reference(n=n,h=h);b=Body(n=n,h=h)
  theta=.17;R=np.array([[np.cos(theta),-np.sin(theta),0],[np.sin(theta),np.cos(theta),0],[0,0,1]])
  for x in [a,b]:x.u=x.grid@(R@np.diag([1.,.99,1.005])-np.eye(3)).T+np.array([.002,-.001,.003]);x.v=.002*np.sin(x.grid*70)
  for cut in range(2):
   normal=rng.normal(size=3);normal/=np.linalg.norm(normal);offset=float(rng.uniform(-.002,.002));front=(rng.normal(size=3),.0003) if cut==0 else None
   for x in [a,b]:x.split(normal,offset,cut_id=cut,front=front,world=bool(case%2))
   topology=np.array_equal(a.ids,b.ids) and np.array_equal(a.codes,b.codes);surface=0.
   if topology:
    for p,q in zip(a.polys,b.polys):
     if p.shape==q.shape and np.max(abs(p-q))<1e-12:continue
     for target,source in [(p,q),(q,p)]:
      c=target.mean(0);scale=np.max(np.ptp(target,axis=0));eq=ConvexHull((target-c)/scale).equations;surface=max(surface,max(0.,float(np.max(((source-c)/scale)@eq[:,:3].T+eq[:,3])))*scale)
   ua,fa=a.energy_force();ub,fb=b.energy_force();force=float(np.max(abs(fa-fb))) if fa.shape==fb.shape else float('inf');energy=abs(ua-ub)/max(abs(ua),1e-10);mass=abs(a.mass.sum()-b.mass.sum())/a.mass.sum();aa=Aggregate(a);bb=Aggregate(b);same_shape=aa.E.shape==bb.E.shape;E=float(abs(aa.E-bb.E).max()) if same_shape else float('inf')
   ok=topology and surface<=1e-12 and force<=1e-9 and energy<=1e-6 and mass<=1e-6 and E<=1e-10;checks[f'case{case}_cut{cut}']=bool(ok);rows.append({'case':case,'cut':cut,'n':n,'h_m':h,'world':bool(case%2),'topology_equal':topology,'two_way_surface_m':surface,'force_max_N':force,'energy_relative':energy,'mass_relative':mass,'extension_matrix_error':E})
 result={'status':'pass' if all(checks.values()) else 'failed','seed':21012,'checks':checks,'rows':rows,'physical_cut':False}
except Exception as e:traceback.print_exc();result={'status':'exception','exception':repr(e),'checks':checks,'rows':rows}
(W/'geometry_holdout.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
