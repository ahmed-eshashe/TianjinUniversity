"""Fit the existing knife diagonally across the fixed-linkage hand; geometry screen only."""
import json,itertools
import numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from search_wrap_grasp import ROOT,old,world_vectors,geometry
centers=np.array(list(itertools.product(np.linspace(.022,.052,31),[-.035],np.linspace(.06,.11,51))))
results=[]
for tilt,skew in itertools.product([0,15,55,75,90],[-20,-10,0,10,20]):
 r=old@Rotation.from_euler('y',tilt,degrees=True).as_matrix()@Rotation.from_euler('x',-5,degrees=True).as_matrix()@Rotation.from_euler('z',skew,degrees=True).as_matrix()
 kv=world_vectors@r;kv=kv[ConvexHull(kv).vertices];cache={}
 for finger,pitch,yaw in itertools.product([75,85,90],[20,30],[20,60]):
  ds=[];mins=[];vs=geometry(finger,yaw,pitch);names=[n for n,_ in vs]
  for name,v in vs:
   key=(name,pitch,yaw) if 'thumb' in name else (name,finger)
   if key not in cache:
    eq=ConvexHull((v[:,None,:]-kv[None,:,:]).reshape(-1,3)).equations;cache[key]=((centers@eq[:,:3].T+eq[:,3]).max(1),(v@r[2]).min()-centers@r[2])
   d,m=cache[key];ds.append(d);mins.append(m)
  ds=np.array(ds);ix=lambda n:names.index('right_rh_'+n)
  prox=ds[[ix(f+'_proximal') for f in ['index','middle','ring','pinky']]];dist=ds[[ix(f+'_distal') for f in ['index','middle','ring','pinky']]]
  palm=ds[ix('hand_base_link')];thumb=np.minimum(np.abs(ds[ix('thumb_distal')]),np.abs(ds[ix('thumb_metacarpals')]))
  cost=np.maximum(-.0005-ds,0).sum(0)*300
  cost+=(np.sort(np.abs(prox),axis=0)[:2]**2).sum(0)*3e4
  cost+=(np.sort(np.minimum(np.abs(prox),np.abs(dist)),axis=0)[:3]**2).sum(0)*1e4
  cost+=(palm**2+thumb**2)*2e4
  minimum=np.min(mins,axis=0);cost+=np.maximum(-.027-minimum,0)*1000
  j=cost.argmin();results.append({'cost':float(cost[j]),'finger':finger,'pitch':pitch,'yaw':yaw,'tilt':tilt,'skew_deg':skew,'roll_deg':-5,'center_xyz':centers[j].tolist(),'minimum_relative_height':float(minimum[j]),'orientation':r.tolist(),'gaps':dict(zip(names,ds[:,j].tolist()))})
 print(tilt,skew,'best',min(results,key=lambda x:x['cost'])['cost'],flush=True)
 results.sort(key=lambda x:x['cost']);(ROOT/'work/diagonal_wrap_candidates.json').write_text(json.dumps(results[:60],indent=2))
print('BEST',json.dumps(results[:3]),flush=True)
