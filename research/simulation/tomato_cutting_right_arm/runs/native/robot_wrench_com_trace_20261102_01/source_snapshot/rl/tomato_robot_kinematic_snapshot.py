"""Read-only joint/geometry export for future CPU route planning.

Call after AppLauncher and robot initialization. This exports measurements;
it does not execute a route or qualify reach/collision/contact by itself.
"""
import sys
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from pxr import UsdGeom,UsdPhysics
ROOT=Path(__file__).resolve().parents[1]

def snapshot(parked):
 sys.path.insert(0,str(ROOT/'scripts'))
 from reach_kinematics import ArmKinematics,PALM_OFFSET
 r=parked.robot;stage=parked.sim.stage;k=ArmKinematics(stage);q=r.data.joint_pos.torch[0].cpu().numpy();values=dict(zip(r.joint_names,map(float,q)));graph=list(k.by_child.values());children={j[1]:j for j in graph};cache={'/dual_ar5_o6':k.root};visiting=set()
 def transform(path):
  if path in cache:return cache[path]
  if path not in children or path in visiting:raise ValueError('Rigid body not connected to exported robot joint graph: '+path)
  visiting.add(path);parent,child,A,B,axis,name=children[path];turn=np.eye(4)
  if axis is not None:turn[:3,:3]=Rotation.from_rotvec(axis*values.get(name,0.)).as_matrix()
  result=transform(parent)@A@turn@B;cache[path]=result;visiting.remove(path);return result
 xc=UsdGeom.XformCache();body_records=[];sdk_poses=r.data.body_link_pose_w.torch[0].cpu().numpy();all_fk=True;missing=[]
 for index,name in enumerate(r.body_names):
  paths=[p for p in parked.bodies if p.rsplit('/',1)[-1]==name and p.startswith('/dual_ar5_o6/')];record=dict(body_index=index,name=name,candidate_paths=paths,actual_link_pose_world=sdk_poses[index].tolist());bounds=[];uncovered=[]
  if len(paths)==1:
   path=paths[0];record['path']=path
   try:
    fk=transform(path);pose=sdk_poses[index];error=float(np.linalg.norm(fk[:3,3]-pose[:3]));angle=float(Rotation.from_matrix(fk[:3,:3]@Rotation.from_quat(pose[3:]).as_matrix().T).magnitude());record.update(fk_position_error_m=error,fk_angle_error_rad=angle,fk_matches=bool(error<=2e-5 and angle<=2e-4));all_fk=all_fk and record['fk_matches']
   except ValueError as e:record.update(fk_matches=False,fk_reason=str(e));all_fk=False
   root=stage.GetPrimAtPath(path);inverse=xc.GetLocalToWorldTransform(root).GetInverse()
   for prim in stage.Traverse():
    if not str(prim.GetPath()).startswith(path+'/')or not prim.IsA(UsdGeom.Boundable):continue
    ancestor=prim
    while ancestor and not ancestor.HasAPI(UsdPhysics.RigidBodyAPI):ancestor=ancestor.GetParent()
    if not ancestor or str(ancestor.GetPath())!=path:continue
    extent=UsdGeom.Boundable(prim).GetExtentAttr().Get()
    if extent is None or len(extent)!=2:
     if prim.IsA(UsdGeom.Mesh):
      points=UsdGeom.Mesh(prim).GetPointsAttr().Get()
      if points is not None and len(points):extent=np.array([np.asarray(points).min(0),np.asarray(points).max(0)])
     if extent is None or len(extent)!=2:uncovered.append(str(prim.GetPath()));continue
    e=np.asarray(extent,dtype=float);corners=np.array([[a,b,c,1.]for a in e[:,0]for b in e[:,1]for c in e[:,2]]);mapping=np.array(xc.GetLocalToWorldTransform(prim)*inverse);local=(corners@mapping)[:,:3];bounds.extend(local);record.setdefault('geometry_paths',[]).append(str(prim.GetPath()))
   record['unbounded_geometry_paths']=uncovered
   if bounds:
    points=np.array(bounds);record['geometry_body_local_min_m']=points.min(0).tolist();record['geometry_body_local_max_m']=points.max(0).tolist()
   else:missing.append(path)
  else:all_fk=False;missing.append(name)
  body_records.append(record)
 return dict(scope='Static initialized robot kinematic/geometry snapshot only. Future route reach, actual tracking, all-body clearance, mesh-distance checks and force exchange need separate qualification. Bounds cover owned authored Boundable geometry, with unbounded/missing cases explicit; collision cooking/contact offsets are not certified here.',right_joint_names=k.names,right_lower_rad=k.lower.tolist(),right_upper_rad=k.upper.tolist(),hand_path=k.hand_path,palm_offset_m=PALM_OFFSET.tolist(),root_world_matrix=k.root.tolist(),joint_values_rad=values,joints=[dict(parent=j[0],child=j[1],parent_joint_matrix=j[2].tolist(),inverse_child_joint_matrix=j[3].tolist(),axis=None if j[4] is None else j[4].tolist(),name=j[5])for j in graph],body_records=body_records,all_body_fk_matches=all_fk,bodies_without_geometry_bounds=missing,fixed_mount_hand_from_knife=parked.mount.tolist())
