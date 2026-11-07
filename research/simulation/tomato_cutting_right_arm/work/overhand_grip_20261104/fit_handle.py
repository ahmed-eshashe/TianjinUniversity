from pathlib import Path
import sys,json,numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import least_squares
from pxr import Usd,UsdGeom
r=Path(__file__).resolve().parents[2];w=Path(__file__).resolve().parent;sys.path.insert(0,str(r/'scripts'));import search_wrap_grasp as g
p=json.loads((w/'overhand_plan_v05.json').read_text());m=np.array(p['mount_hand_from_knife']);s=Usd.Stage.Open(str(r/'rl/scene/phase3.usda'));meta=json.loads((r/'rl/scene/manifest.json').read_text());h=np.array(UsdGeom.Mesh(s.GetPrimAtPath(meta['knife_path']+'/CollisionHandle')).GetPointsAttr().Get());hc=(h.min(0)+h.max(0))/2;kv=(h-hc)@m[:3,:3].T
meshes=g.geometry(75,np.rad2deg(.86),np.rad2deg(.49));names=[n for n,v in meshes];eq=[ConvexHull((v[:,None,:]-kv[None,:,:]).reshape(-1,3)).equations for n,v in meshes];c=m[:3,:3]@hc+m[:3,3]
def gaps(x):return np.array([max(e[:,:3]@x+e[:,3]) for e in eq])
sel=[i for i,n in enumerate(names) if 'distal' in n or 'hand_base' in n]
def res(x):
 d=gaps(x);return np.r_[30*np.maximum(.0005-d,0),d[sel]-.001,.01*(x-c)]
f=least_squares(res,c,max_nfev=200);print('center',f.x);print(dict(zip(names,gaps(f.x))));(w/'handle_fit.json').write_text(json.dumps({'center':f.x.tolist(),'gaps':dict(zip(names,gaps(f.x).tolist()))},indent=2))
