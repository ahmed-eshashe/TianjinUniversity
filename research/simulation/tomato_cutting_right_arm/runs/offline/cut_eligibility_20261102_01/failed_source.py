"""Transactional geometry-only eligibility candidate for a finite CAD blade.

A past accepted inward edge event is necessary, and current blade-solid overlap
is necessary on every update. A seed alone never keeps a patch eligible. One
existing damage scalar per patch remains a spatial-resolution limitation.
The mechanical caller must apply the last ACCEPTED mask (one interval lag),
then commit the next geometry only after both simulations accept the step.
This module never changes cohesive history or mechanical state.
"""
from dataclasses import dataclass
import numpy as np
from scipy.spatial.transform import Rotation
from tomato_cut_geometry import current_footprints
from tomato_exact_blade_coverage import coverage,verify_cells

@dataclass(frozen=True)
class EligibilityTrial:
 generation:int
 owner:object
 world:np.ndarray
 pose:np.ndarray
 seen:np.ndarray
 eligible:np.ndarray
 edge_candidates:tuple
 inward_patches:tuple
 overlapping_patches:tuple

def freeze(value):
 value=np.asarray(value).copy();value.setflags(write=False);return value

class CutEligibility:
 def __init__(self,blade,solid,registration,front_face_ids,detector,world,pose,*,maximum_rotation_rad=1e-3):
  verify_cells(blade,solid);self.local_vertices=np.asarray(blade['vertices'],dtype=float);self.solid_vertices=np.asarray(solid['vertices'],dtype=float);self.cells=np.asarray(solid['cells'],dtype=int);self.faces=np.asarray(blade['triangles'],dtype=int)[front_face_ids];self.registration=registration;self.detector=detector;self.patch_count=len(registration['patch_geometric_area_m2']);self.maximum_rotation_rad=maximum_rotation_rad;self.owner=object();self.generation=0;self.reset(world,pose)
 def _geometry(self,world,pose):
  world=np.asarray(world,dtype=float);pose=np.asarray(pose,dtype=float)
  if not np.isfinite(world).all() or pose.shape!=(7,) or not np.isfinite(pose).all() or abs(np.linalg.norm(pose[3:])-1)>1e-10:raise ValueError('Finite accepted state and unit xyzw pose required')
  rotation=Rotation.from_quat(pose[3:]).as_matrix();front=(self.local_vertices@rotation.T+pose[:3])[self.faces];material=current_footprints(world,self.registration);return front,material,rotation
 def _overlap(self,material,pose,rotation):
  positions=((material.reshape(-1,3)-pose[:3])@rotation);triangles=np.arange(len(positions)).reshape(-1,3);result=coverage(self.solid_vertices,self.cells,positions,triangles,capacity=131072);patches=set()
  for row in result['triangles']:
   if row['covered_area_m2']>1e-16:patches.add(int(self.registration['patch'][row['id']]))
  return patches
 def reset(self,world,pose):
  front,material,rotation=self._geometry(world,pose)
  if self._overlap(material,np.asarray(pose),rotation):raise ValueError('Eligibility reset requires blade-clear target geometry')
  self.world=freeze(world);self.pose=freeze(pose);self.seen=freeze(np.zeros(self.patch_count,dtype=bool));self.eligible=freeze(np.zeros(self.patch_count,dtype=bool));self.generation+=1
 def trial(self,world,pose):
  f0,m0,r0=self._geometry(self.world,self.pose);f1,m1,r1=self._geometry(world,pose);angle=float(Rotation.from_matrix(r1@r0.T).magnitude())
  if angle>self.maximum_rotation_rad:raise ValueError('Blade rotation exceeds the declared linear-trajectory interval bound; subdivide before eligibility')
  candidates=self.detector.detect(f0,f1,m0,m1,self.registration['patch'])['events'];inward=set()
  for row in candidates:
   i=row['front_face_index'];j=row['material_subtriangle_index'];forward=True
   for triangle in [f0[i],f1[i]]:
    normal=np.cross(triangle[1]-triangle[0],triangle[2]-triangle[0]);normal/=np.linalg.norm(normal)
    # Sufficient inward condition at both endpoint normals, for every possible
    # barycentric contact point in these two facets. General rotating-front
    # trajectory accuracy still requires dynamic subdivision/refinement tests.
    lower=float(np.min((f1[i]-f0[i])@normal)-np.max((m1[j]-m0[j])@normal))
    forward=forward and lower>1e-12
   if forward:inward.add(int(row['patch']))
  seen=self.seen.copy();seen[list(inward)]=True;overlap=self._overlap(m1,np.asarray(pose),r1);eligible=np.zeros(self.patch_count,dtype=bool);eligible[list(overlap)]=seen[list(overlap)]
  return EligibilityTrial(self.generation,self.owner,freeze(world),freeze(pose),freeze(seen),freeze(eligible),tuple(candidates),tuple(sorted(inward)),tuple(sorted(overlap)))
 def commit(self,trial,*,accepted):
  if trial.owner is not self.owner or trial.generation!=self.generation:raise ValueError('Stale or foreign eligibility trial')
  if not accepted:return
  self.world=trial.world;self.pose=trial.pose;self.seen=trial.seen;self.eligible=trial.eligible;self.generation+=1
