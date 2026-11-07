exec(open(__file__.replace('refine_fit.py','fit_handle.py')).read().split('meshes=g.geometry')[0])
from scipy.spatial.transform import Rotation
orig=json.loads((r/'work/exploratory_demo_20261104/grip_candidate.json').read_text());base=np.array(orig['mount_hand_from_knife'])[:3,:3];results=[]
for roll in [45,60,75,90]:
 A=base@Rotation.from_euler('x',roll,degrees=True).as_matrix()@Rotation.from_euler('y',180,degrees=True).as_matrix();kv=(h-hc)@A.T
 for flex in [60,65,70,75,80]:
  meshes=g.geometry(flex,np.rad2deg(.86),np.rad2deg(.49));names=[n for n,v in meshes];eq=[ConvexHull((v[:,None,:]-kv[None,:,:]).reshape(-1,3)).equations for n,v in meshes];sel=[i for i,n in enumerate(names) if 'distal' in n or 'hand_base' in n]
  def gaps(x):return np.array([max(e[:,:3]@x+e[:,3]) for e in eq])
  def res(x):
   d=gaps(x);return np.r_[100*np.maximum(.0005-d,0),d[sel]-.001]
  best=None
  for seed in [[.028,-.03,.075],[.035,0,.08],[.04,-.05,.085]]:
   f=least_squares(res,seed,bounds=([.015,-.075,.05],[.065,.025,.12]),max_nfev=120)
   if best is None or np.linalg.norm(f.fun)<np.linalg.norm(best.fun):best=f
  results.append(dict(roll=roll,flex=flex,center=best.x.tolist(),cost=float(np.linalg.norm(best.fun)),gaps=dict(zip(names,gaps(best.x).tolist())),A=A.tolist()))
results.sort(key=lambda x:x['cost']);(w/'fit_candidates.json').write_text(json.dumps(results,indent=2));print(json.dumps(results[:2],indent=2))
