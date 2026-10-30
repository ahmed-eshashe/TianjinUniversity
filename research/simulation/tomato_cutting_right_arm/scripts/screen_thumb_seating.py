"""Find a thumb preshape clear of the settled knife and worktop before finger closure."""
import json,itertools
import numpy as np
from scipy.spatial import ConvexHull
from search_wrap_grasp import ROOT,geometry,world_vectors,km
seed=json.loads((ROOT/'work/grasp_stance_top.json').read_text());r=np.array(seed['orientation'])
line=next(x for x in (ROOT/'logs/wrap_trial12.log').read_text().splitlines() if x.startswith('SETTLED_SCENE '));settled=json.loads(line.removeprefix('SETTLED_SCENE '));actual=np.array(settled['knife_rotation_world']);original=km[:3,:3]/np.linalg.norm(km[:3,:3],axis=0)
kv=world_vectors@original@actual.T@r;kv=kv[ConvexHull(kv).vertices]
centers=np.array(list(itertools.product([.035,.04,.045,.05],[-.015],[.08,.09,.10,.11])))
results=[]
for yaw,pitch in itertools.product([0,20,40,60,77],[0,10,20,30,33]):
 gaps=[];mins=[];names=[]
 for name,v in geometry(0,yaw,pitch):
  eq=ConvexHull((v[:,None,:]-kv[None,:,:]).reshape(-1,3)).equations;gaps.append((centers@eq[:,:3].T+eq[:,3]).max(1));mins.append((v@r[2]).min()-centers@r[2]);names.append(name)
 gaps=np.array(gaps);minimum=np.min(mins,axis=0);clearance=np.min(gaps,axis=0)
 for i,c in enumerate(centers):
  results.append({'yaw':yaw,'pitch':pitch,'center_xyz':c.tolist(),'knife_clearance_m':float(clearance[i]),'minimum_relative_height_m':float(minimum[i]),'gaps':dict(zip(names,gaps[:,i].tolist())),'clear':bool(clearance[i]>.002 and minimum[i]>-.027)})
results.sort(key=lambda x:(not x['clear'],abs(x['center_xyz'][2]-.1)+abs(x['center_xyz'][0]-.045)))
(ROOT/'work/thumb_seating_candidates.json').write_text(json.dumps(results,indent=2))
for x in results[:12]:print({k:v for k,v in x.items() if k!='gaps'},flush=True)
for x in results:
 if x['yaw']==0 and x['pitch']==20 and x['center_xyz']==[.035,-.015,.1]:print('TRIAL12',x,flush=True)
