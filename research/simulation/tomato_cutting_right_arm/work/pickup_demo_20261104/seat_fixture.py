from pathlib import Path
import json,numpy as np,sys
from pxr import Usd,UsdGeom
r=Path(__file__).resolve().parents[2];w=Path(__file__).resolve().parent;sys.path.insert(0,str(r/'rl'));from tomato_fixed_mount_scene import matrix
p=json.loads((w/'pickup_plan.json').read_text());s=Usd.Stage.CreateNew(str(w/'pickup_scene_v02.usda'));s.GetRootLayer().subLayerPaths=[p['scene']];UsdGeom.SetStageUpAxis(s,'Z');UsdGeom.SetStageMetersPerUnit(s,1.)
mesh=UsdGeom.Mesh(s.GetPrimAtPath(p['tool_path']));v=np.array(mesh.GetPointsAttr().Get());idx=np.array(mesh.GetFaceVertexIndicesAttr().Get());counts=np.array(mesh.GetFaceVertexCountsAttr().Get());offset=np.r_[0,np.cumsum(counts)];rk=np.array(p['knife_rotation']);o=np.array(p['knife_origin_route_m'][0]);report=[]
def clip(poly,bound,sign):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=sign*(a[0]-bound);db=sign*(b[0]-bound)
  if da>=0:out.append(a)
  if (da>=0)!=(db>=0):out.append(a+(b-a)*(da/(da-db)))
 return out
for i,x in enumerate([-.025,-.25]):
 pts=[]
 for j in range(len(counts)):
  poly=list(v[idx[offset[j]:offset[j+1]]]);poly=clip(poly,x-.0125,1)
  if poly:poly=clip(poly,x+.0125,-1)
  pts.extend(poly)
 top=o[2]+min(t[1]for t in pts)-.0001;bottom=-.035;pos=o+rk@np.array([x,0,0]);t=np.eye(4);t[:3,:3]=np.column_stack([rk[:,0]*.025,rk[:,2]*.045,[0,0,top-bottom]]);t[:3,3]=[pos[0],pos[1],(top+bottom)/2];matrix(UsdGeom.Xformable(s.GetPrimAtPath('/PickupFixture/Post'+str(i))),t);report.append({'post':i,'top_z':top,'knife_gap_m':.0001})
s.GetRootLayer().Save();p['scene']=str(w/'pickup_scene_v02.usda');(w/'pickup_plan_v02.json').write_text(json.dumps(p,indent=2));(w/'fixture_seating.json').write_text(json.dumps(report,indent=2));print(report)
