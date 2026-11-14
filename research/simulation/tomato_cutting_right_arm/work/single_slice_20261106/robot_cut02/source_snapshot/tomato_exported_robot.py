"""Pure host FK/IK using an explicitly native-checked joint-frame snapshot.

No simulator imports or physics stepping. Authored geometry boxes are coarse
clearance certificates when disjoint; overlapping boxes are not collisions.
A planned IK pose is not an actual tracking or mounted-contact qualification.
"""
import json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares

class ExportedRobot:
 def __init__(self,path):
  self.path=Path(path);self.data=json.loads(self.path.read_text());d=self.data
  if d.get('all_body_fk_matches')is not True:raise ValueError('Exported joint frames must first match actual initialized native link poses')
  self.joints={j['child']:j for j in d['joints']};self.root=np.array(d['root_world_matrix']);self.names=d['right_joint_names'];self.values=dict(d['joint_values_rad']);self.lower=np.array(d['right_lower_rad']);self.upper=np.array(d['right_upper_rad']);self.hand=d['hand_path'];self.mount=np.array(d['fixed_mount_hand_from_knife']);self.bodies=d['body_records'];self.tool=next(b['path']for b in self.bodies if b['name']=='MountedKnife')
 def forward(self,q):
  values=dict(self.values);values.update(q if isinstance(q,dict)else dict(zip(self.names,q)));poses={'/dual_ar5_o6':self.root};visiting=set()
  def visit(path):
   if path in poses:return poses[path]
   if path not in self.joints or path in visiting:raise ValueError('Unconnected/recursive exported body: '+path)
   visiting.add(path);j=self.joints[path];turn=np.eye(4)
   if j['axis']is not None:turn[:3,:3]=Rotation.from_rotvec(np.asarray(j['axis'])*values.get(j['name'],0.)).as_matrix()
   poses[path]=visit(j['parent'])@np.array(j['parent_joint_matrix'])@turn@np.array(j['inverse_child_joint_matrix']);visiting.remove(path);return poses[path]
  for b in self.bodies:visit(b['path'])
  return poses
 def knife_pose(self,q):return self.forward(q)[self.tool]
 def solve_knife(self,position,orientation,seed):
  position=np.asarray(position);orientation=np.asarray(orientation);seed=np.asarray(seed)
  def residual(q):
   pose=self.knife_pose(q);return np.r_[pose[:3,3]-position,.15*Rotation.from_matrix(orientation@pose[:3,:3].T).as_rotvec(),.0002*(q-seed)]
  solution=least_squares(residual,np.clip(seed,self.lower,self.upper),bounds=(self.lower,self.upper),max_nfev=400,ftol=1e-10,xtol=1e-10,gtol=1e-10);pose=self.knife_pose(solution.x)
  return solution.x,float(np.linalg.norm(pose[:3,3]-position)),float(Rotation.from_matrix(orientation@pose[:3,:3].T).magnitude())
 def body_boxes(self,q):
  poses=self.forward(q);records=[]
  for b in self.bodies:
   if 'geometry_body_local_min_m'not in b or b.get('unbounded_geometry_paths'):raise ValueError('Incomplete authored geometry bounds for '+b['name'])
   lo=np.array(b['geometry_body_local_min_m']);hi=np.array(b['geometry_body_local_max_m']);corners=np.array([[x,y,z]for x in [lo[0],hi[0]]for y in [lo[1],hi[1]]for z in [lo[2],hi[2]]]);t=poses[b['path']];world=corners@t[:3,:3].T+t[:3,3];records.append(dict(name=b['name'],path=b['path'],minimum_world=world.min(0),maximum_world=world.max(0)))
  return records
 def target_box_gaps(self,q,target,*,inflation_m=.002):
  target=np.asarray(target);lo=target.min(0);hi=target.max(0);records=[]
  for b in self.body_boxes(q):
   low=b['minimum_world']-inflation_m;high=b['maximum_world']+inflation_m;gap=float(np.maximum(lo-high,low-hi).max());records.append(dict(name=b['name'],path=b['path'],inflated_aabb_axis_separation_m=gap,coarse_disjoint=gap>0))
  return records
