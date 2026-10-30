"""Approximate planar thumb/finger grasp search; collision and lift require physics validation."""
import sys,json
sys.path.insert(0,'scripts')
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom,UsdPhysics
from reach_kinematics import ArmKinematics
s=Usd.Stage.Open('work/kitchen_reach.usda');k=ArmKinematics(s);xc=UsdGeom.XformCache()
mesh=[]
for p in Usd.PrimRange(s.GetPrimAtPath(k.hand_path)):
 if not p.IsA(UsdGeom.Mesh):continue
 body=p
 while not body.HasAPI(UsdPhysics.RigidBodyAPI):body=body.GetParent()
 rel=np.linalg.inv(np.array(xc.GetLocalToWorldTransform(body)).T)@np.array(xc.GetLocalToWorldTransform(p)).T
 v=np.array(UsdGeom.Mesh(p).GetPointsAttr().Get());v=v@rel[:3,:3].T+rel[:3,3]
 mesh.append((str(body.GetPath()),v))
def geometry(mcp,yaw,pitch):
 vals={n:0. for n in k.home};vals.update({'right_rh_thumb_cmc_yaw':yaw,'right_rh_thumb_cmc_pitch':pitch,'right_rh_thumb_ip':1.86*pitch})
 for f in ['index','middle','ring','pinky']:
  angle=mcp.get(f,90) if isinstance(mcp,dict) else mcp
  vals['right_rh_'+f+'_mcp_pitch']=angle;vals['right_rh_'+f+'_dip']=.89*angle
 tf={k.hand_path:np.eye(4)}
 def tr(path):
  if path in tf:return tf[path]
  parent,child,a,b,axis,name=k.by_child[path];rot=np.eye(4)
  if axis is not None:rot[:3,:3]=Rotation.from_rotvec(axis*np.deg2rad(vals.get(name,0))).as_matrix()
  tf[path]=tr(parent)@a@rot@b;return tf[path]
 return [(p.split('/')[-1],v@tr(p)[:3,:3].T+tr(p)[:3,3]) for p,v in mesh]

from scipy.spatial import ConvexHull
import itertools
centers=np.array(list(itertools.product(np.linspace(.025,.075,61),np.linspace(.05,.15,101))))
results=[]
for finger in [30,40,50,60,70,80,90]:
 for pitch in [0,10,20,30,33]:
  for yaw in [0,20,40,60,77]:
   vs=geometry(finger,yaw,pitch);dists=[];normals=[];max_proj=[]
   for name,v in vs:
    v2=v[:,[0,2]];h=ConvexHull(v2);eq=h.equations
    ds=centers@eq[:,:2].T+eq[:,2];i=ds.argmax(1);d=ds[np.arange(len(centers)),i];dists.append(d);normals.append(eq[i,:2])
   di=next(i for i,(n,v) in enumerate(vs) if 'index_distal' in n);dt=next(i for i,(n,v) in enumerate(vs) if 'thumb_distal' in n)
   dists=np.array(dists);opp=np.sum(normals[di]*normals[dt],axis=1)
   base_cost=((dists[di]-.012)**2+(dists[dt]-.012)**2)*1e4+np.maximum(.010-dists,0).sum(0)*100+np.maximum(opp+.5,0)*2
   allv=np.concatenate([v[:,[0,2]] for _,v in vs])
   for tilt in [0,15,30,45,60]:
    n=np.array([np.cos(np.deg2rad(tilt)),np.sin(np.deg2rad(tilt))]);below=(allv@n).max()-centers@n
    cost=base_cost+np.maximum(below-.010,0)*100
    j=cost.argmin();results.append({'cost':float(cost[j]),'finger':finger,'pitch':pitch,'yaw':yaw,'tilt':tilt,'center_xz':centers[j].tolist(),'below':float(below[j]),'d_index':float(dists[di,j]),'d_thumb':float(dists[dt,j]),'opposition':float(opp[j])})
results.sort(key=lambda x:x['cost']);json.dump(results[:30],open('work/grasp_geometry_candidates.json','w'),indent=2)
for r in results[:10]:print(r)
