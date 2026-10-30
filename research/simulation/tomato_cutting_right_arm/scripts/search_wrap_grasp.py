"""Offline geometry screen for a palm-seated wrap, using the original hand and handle."""
import sys,json,itertools
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom,UsdPhysics
from reach_kinematics import ArmKinematics
ROOT=Path(__file__).resolve().parents[1]
s=Usd.Stage.Open(str(ROOT/'work/kitchen_reach.usda'));k=ArmKinematics(s);xc=UsdGeom.XformCache()
mesh=[]
for p in Usd.PrimRange(s.GetPrimAtPath(k.hand_path)):
 if not p.IsA(UsdGeom.Mesh):continue
 body=p
 while not body.HasAPI(UsdPhysics.RigidBodyAPI):body=body.GetParent()
 rel=np.linalg.inv(np.array(xc.GetLocalToWorldTransform(body)).T)@np.array(xc.GetLocalToWorldTransform(p)).T
 v=np.array(UsdGeom.Mesh(p).GetPointsAttr().Get());v=v@rel[:3,:3].T+rel[:3,3]
 mesh.append((str(body.GetPath()),v[ConvexHull(v).vertices]))
def geometry(finger,yaw,pitch):
 vals={'right_rh_thumb_cmc_yaw':yaw,'right_rh_thumb_cmc_pitch':pitch,'right_rh_thumb_ip':1.86*pitch}
 for f in ['index','middle','ring','pinky']:
  flex=finger[f] if isinstance(finger,dict) else finger
  vals['right_rh_'+f+'_mcp_pitch']=flex;vals['right_rh_'+f+'_dip']=.89*flex
 tf={k.hand_path:np.eye(4)}
 def tr(path):
  if path in tf:return tf[path]
  parent,child,a,b,axis,name=k.by_child[path];rot=np.eye(4)
  if axis is not None:rot[:3,:3]=Rotation.from_rotvec(axis*np.deg2rad(vals.get(name,0))).as_matrix()
  tf[path]=tr(parent)@a@rot@b;return tf[path]
 return [(p.split('/')[-1],v@tr(p)[:3,:3].T+tr(p)[:3,3]) for p,v in mesh]
knife=s.GetPrimAtPath('/Indoor/RZ/SM_kitchen_knife_02');m=UsdGeom.Mesh(knife)
co=np.array(m.GetFaceVertexCountsAttr().Get());ind=np.array(m.GetFaceVertexIndicesAttr().Get());off=np.r_[0,np.cumsum(co)]
f=np.array(UsdGeom.Subset(s.GetPrimAtPath(str(knife.GetPath())+'/Section2')).GetIndicesAttr().Get());ids=np.unique(np.concatenate([ind[off[i]:off[i+1]] for i in f]))
meta=json.loads((ROOT/'work/kitchen_reach_metadata.json').read_text());km=np.array(xc.GetLocalToWorldTransform(knife)).T
world_vectors=(np.array(m.GetPointsAttr().Get())[ids]-meta['knife_handle_local'])@km[:3,:3].T
old=np.array(json.loads((ROOT/'work/reach_seed.json').read_text())['orientation'])
if __name__=='__main__':
 centers=np.array(list(itertools.product(np.linspace(.024,.050,27),[-.05,-.035,-.02],np.linspace(.07,.102,33))))
 results=[]
 for tilt in [15,30,55]:
  rot=old@Rotation.from_euler('y',tilt,degrees=True).as_matrix();kv=world_vectors@rot;kv=kv[ConvexHull(kv).vertices];cache={}
  for finger,pitch,yaw in itertools.product([75,80,85,90],[0,10,20,30,33],[0,20,40,60,77]):
   ds=[];ns=[];mins=[];vs=geometry(finger,yaw,pitch)
   for name,v in vs:
    key=(name,pitch,yaw) if 'thumb' in name else (name,finger)
    if key not in cache:
     eq=ConvexHull((v[:,None,:]-kv[None,:,:]).reshape(-1,3)).equations
     dd=centers@eq[:,:3].T+eq[:,3];ii=dd.argmax(1)
     cache[key]=(dd[np.arange(len(centers)),ii],eq[ii,:3],(v@rot[2]).min()-centers@rot[2])
    d,n,mm=cache[key];ds.append(d);ns.append(n);mins.append(mm)
   ds=np.array(ds);names=[n for n,_ in vs]
   ix=lambda n:names.index('right_rh_'+n)
   prox=ds[[ix(f+'_proximal') for f in ['index','middle','ring','pinky']]]
   dist=ds[[ix(f+'_distal') for f in ['index','middle','ring','pinky']]]
   palm=ds[ix('hand_base_link')];thumb=ds[ix('thumb_distal')]
   # Seek deep finger contact and palm support; reject penetrations and table intrusion.
   cost=np.maximum(-.0003-ds,0).sum(0)*200
   cost+=(np.sort(np.abs(prox),axis=0)[:2]**2).sum(0)*2e4
   cost+=(np.sort(np.abs(dist),axis=0)[:2]**2).sum(0)*1e4
   cost+=(palm**2+thumb**2)*1e4
   minimum=np.min(mins,axis=0);cost+=np.maximum(-.027-minimum,0)*1000
   j=cost.argmin();results.append({'cost':float(cost[j]),'finger':finger,'pitch':pitch,'yaw':yaw,'tilt':tilt,'center_xyz':centers[j].tolist(),'minimum_relative_height':float(minimum[j]),'gaps':dict(zip(names,ds[:,j].tolist()))})
  print('TILT',tilt,'BEST',min(results,key=lambda x:x['cost']),flush=True)
 results.sort(key=lambda x:x['cost']);(ROOT/'work/wrap_grasp_candidates.json').write_text(json.dumps(results[:80],indent=2))
 print('BEST',json.dumps(results[:3]),flush=True)
