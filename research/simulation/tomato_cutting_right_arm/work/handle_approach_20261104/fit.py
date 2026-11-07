from pathlib import Path
import json,sys,numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import least_squares
from pxr import Usd,UsdGeom
r=Path(__file__).resolve().parents[2];w=Path(__file__).resolve().parent;sys.path.insert(0,str(r/'scripts'));import search_wrap_grasp as g
p=json.loads((r/'work/pickup_demo_20261104/pickup_plan_v02.json').read_text());s=Usd.Stage.Open(p['scene']);h=np.array(UsdGeom.Mesh(s.GetPrimAtPath(p['tool_path']+'/CollisionHandle')).GetPointsAttr().Get());m=np.array(p['mount_hand_from_knife']);m[1,3]+=.04;A=m[:3,:3];hc=(h.min(0)+h.max(0))/2;c=A@hc+m[:3,3];kv=(h-hc)@A.T
flex={'index':55,'middle':55,'ring':55,'pinky':55}
for cycle in range(1):
 meshes=g.geometry(flex,np.rad2deg(1.2),np.rad2deg(.30));names=[n for n,v in meshes];eq=[ConvexHull((v[:,None,:]-kv[None,:,:]).reshape(-1,3)).equations for n,v in meshes];sel=[i for i,n in enumerate(names)if 'distal'in n or 'hand_base'in n]
 def gaps(xz):
  center=np.array([xz[0],c[1],xz[1]]);return np.array([max(e[:,:3]@center+e[:,3])for e in eq])
 def res(xz):
  ds=gaps(xz);return np.r_[100*np.maximum(.0005-ds,0),ds[sel]-.001]
 fit=least_squares(res,c[[0,2]],bounds=([.02,.06],[.06,.10]));c[[0,2]]=fit.x;points=kv+c
 for finger in flex:
  opts=[]
  for angle in np.arange(50,86,.5):
   ds={}
   for name,v in g.geometry(float(angle),np.rad2deg(1.2),np.rad2deg(.30)):
    if finger not in name:continue
    e=ConvexHull((v[:,None,:]-points[None,:,:]).reshape(-1,3)).equations;ds[name]=float(max(e[:,3]))
   if min(ds.values())>=.00035:opts.append((ds['right_rh_'+finger+'_distal'],float(angle)))
  if not opts:raise ValueError(('No nonpenetrating flex',finger))
  flex[finger]=min(opts)[1]
m[:3,3]=c-A@hc;regions={};gaps={}
for name,v in g.geometry(flex,np.rad2deg(1.2),np.rad2deg(.30)):
 local=(v-m[:3,3])@A;regions[name]=[float(local[:,0].min()),float(local[:,0].max())];e=ConvexHull((v[:,None,:]-(kv+c)[None,:,:]).reshape(-1,3)).equations;gaps[name]=float(max(e[:,3]))
report=dict(mount=m.tolist(),flex=flex,regions_knife_x=regions,thumb_yaw=1.2,thumb_pitch=.30,handle_x_limits=[-.17229162,.00028486],gaps_m=gaps)
(w/'grip_fit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
