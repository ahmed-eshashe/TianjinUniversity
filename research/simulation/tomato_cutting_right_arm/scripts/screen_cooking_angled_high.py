"""Screen both original blade and handle against an open hand before descending."""
import json,itertools,numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from pxr import UsdGeom
from search_wrap_grasp import ROOT,geometry,s,xc,meta,km
seed=json.load(open(ROOT/'work/grasp_stance_cooking_angled_seed.json'));r=np.array(seed['orientation'])
knife=s.GetPrimAtPath(meta['knife_path']);mesh=UsdGeom.Mesh(knife);v=np.array(mesh.GetPointsAttr().Get());counts=np.array(mesh.GetFaceVertexCountsAttr().Get());ix=np.array(mesh.GetFaceVertexIndicesAttr().Get());off=np.r_[0,np.cumsum(counts)];scale=np.linalg.norm(km[:3,:3],axis=0)
line=next(x for x in (ROOT/'logs/cooking_trial1.log').read_text().splitlines() if x.startswith('SETTLED_SCENE '));kr=np.array(json.loads(line.removeprefix('SETTLED_SCENE '))['knife_rotation_world'])
centers=np.array(list(itertools.product([.045,.05,.055,.06],[0],[.065,.075,.085,.095,.105,.115])))
results=[]
for setup_roll in [180]:
 knife_r=kr@Rotation.from_euler('x',setup_roll,degrees=True).as_matrix();parts=[]
 for sections in [['Section2'],['Section0','Section1']]:
  faces=np.concatenate([np.array(UsdGeom.Subset(s.GetPrimAtPath(meta['knife_path']+'/'+name)).GetIndicesAttr().Get()) for name in sections]);ids=np.unique(np.concatenate([ix[off[f]:off[f+1]] for f in faces]));kv=((v[ids]-meta['knife_handle_local'])*scale)@knife_r.T@r;parts.append(kv[ConvexHull(kv).vertices])
 for yaw,pitch in itertools.product([0,20,40,60,77],[0,10,20,30,33]):
  gaps=[];mins=[]
  for name,vv in geometry(0,yaw,pitch):
   mins.append((vv@r[2]).min()-centers@r[2])
   for kv in parts:
    eq=ConvexHull((vv[:,None,:]-kv[None,:,:]).reshape(-1,3)).equations;gaps.append((centers@eq[:,:3].T+eq[:,3]).max(1))
  clearance=np.min(gaps,axis=0);minimum=np.min(mins,axis=0)
  for i,c in enumerate(centers):
   if clearance[i]>.002 and minimum[i]>-.027:
    results.append({'setup_roll':setup_roll,'yaw':yaw,'pitch':pitch,'center_xyz':c.tolist(),'clearance':float(clearance[i]),'minimum_relative_height':float(minimum[i]),'cost':float(np.linalg.norm(c-np.array([.035,0,.085])))})
results.sort(key=lambda x:x['cost']);(ROOT/'work/cooking_angled_high_candidates.json').write_text(json.dumps(results,indent=2))
print('COUNT',len(results));print(json.dumps(results[:15],indent=2))
