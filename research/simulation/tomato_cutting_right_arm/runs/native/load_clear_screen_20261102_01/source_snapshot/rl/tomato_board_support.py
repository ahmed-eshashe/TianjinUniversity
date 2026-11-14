"""Versioned frictionless nodal area-lumped plane contact; no calibrated friction."""
import numpy as np
import warp as wp
from tomato_native_full_model import FullTomatoVBD

@wp.kernel
def plane_blocks(color:int,colors:wp.array[int],x:wp.array[wp.vec3],stiffness:wp.array[float],height:float,forces:wp.array[wp.vec3],hessians:wp.array[wp.mat33]):
 i=wp.tid()
 if colors[i]==color and x[i][2]<height:
  f=forces[i];f[2]+=stiffness[i]*(height-x[i][2]);forces[i]=f
  h=hessians[i];h[2,2]+=stiffness[i];hessians[i]=h

def nodal_plane_stiffness(data,pressure=1.75e9):
 area=np.zeros(len(data['x']))
 for piece in data['design']['pieces']:
  for tri in piece['triangles']:
   a,b,c=data['x'][tri];area[tri]+=np.linalg.norm(np.cross(b-a,c-a))/6.
 return area*pressure

class BoardSupportVBD(FullTomatoVBD):
 def _gather_blocks(self,color,state,dt):
  super()._gather_blocks(color,state,dt)
  wp.launch(plane_blocks,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,state.particle_q,self.board_stiffness,self.board_height],outputs=[self.particle_forces,self.particle_hessians],device=self.device)

@wp.kernel
def minimum_ratio(x:wp.array[wp.vec3],cells:wp.array[wp.vec4i],volumes:wp.array[float],minimum:wp.array[float]):
 i=wp.tid();t=cells[i];j=wp.dot(x[t[1]]-x[t[0]],wp.cross(x[t[2]]-x[t[0]],x[t[3]]-x[t[0]]))/(6.*volumes[i]);wp.atomic_min(minimum,0,j)

class AuditedBoardSupportVBD(BoardSupportVBD):
 def _gather_blocks(self,color,state,dt):
  wp.launch(minimum_ratio,dim=self.cells.size,inputs=[state.particle_q,self.cells,self.volumes],outputs=[self.minimum_trial_ratio],device=self.device)
  super()._gather_blocks(color,state,dt)

@wp.kernel
def first_bad_cell(x:wp.array[wp.vec3],cells:wp.array[wp.vec4i],volumes:wp.array[float],phase:int,info:wp.array[int],snapshot:wp.array[wp.vec3]):
 i=wp.tid();t=cells[i];j=wp.dot(x[t[1]]-x[t[0]],wp.cross(x[t[2]]-x[t[0]],x[t[3]]-x[t[0]]))/(6.*volumes[i])
 if j<=.1:
  if wp.atomic_cas(info,0,0,1)==0:
   info[1]=phase;info[2]=i
   for a in range(4):snapshot[a]=x[t[a]]

class DiagnosedBoardSupportVBD(AuditedBoardSupportVBD):
 def check(self,x,phase):
  wp.launch(first_bad_cell,dim=self.cells.size,inputs=[x,self.cells,self.volumes,phase],outputs=[self.bad_info,self.bad_snapshot],device=self.device)
 def _penetration_free_truncation(self,particle_q_out=None):
  self.check(self.pos_prev_collision_detection,-2)
  super()._penetration_free_truncation(particle_q_out)
  self.check(particle_q_out,-1)
 def _volume_safe_update(self,color,positions):
  super()._volume_safe_update(color,positions)
  self.check(positions,color)

@wp.kernel
def copy_if_clean(source:wp.array[wp.vec3],info:wp.array[int],target:wp.array[wp.vec3]):
 i=wp.tid()
 if info[0]==0:target[i]=source[i]

class ReplayDiagnosedBoardSupportVBD(DiagnosedBoardSupportVBD):
 def _volume_safe_update(self,color,positions):
  wp.launch(copy_if_clean,dim=self.model.particle_count,inputs=[positions,self.bad_info],outputs=[self.before_color],device=self.device)
  wp.launch(copy_if_clean,dim=self.model.particle_count,inputs=[self.particle_displacements,self.bad_info],outputs=[self.before_displacements],device=self.device)
  super()._volume_safe_update(color,positions)

class CheckedBoardSupportVBD(BoardSupportVBD):
 def _penetration_free_truncation(self,particle_q_out=None):
  from tomato_native_volume_steps import predictor_fraction,apply_predictor
  from tomato_checked_volume_steps import check_predictor,finish_predictor,reject_unverified_predictor
  if self.particle_enable_self_contact:raise NotImplementedError('Combined full self-contact still unqualified')
  self.volume_step_fraction.fill_(1.);self.candidate_active.fill_(1)
  wp.launch(predictor_fraction,dim=self.cells.size,inputs=[self.pos_prev_collision_detection,self.particle_displacements,self.cells,self.volumes],outputs=[self.volume_step_fraction,self.volume_invalid],device=self.device)
  for _ in range(40):
   self.candidate_bad.zero_()
   wp.launch(check_predictor,dim=self.cells.size,inputs=[self.pos_prev_collision_detection,self.particle_displacements,self.cells,self.volumes,self.volumes64,self.volume_step_fraction,self.candidate_active],outputs=[self.candidate_bad],device=self.device)
   wp.launch(finish_predictor,dim=1,inputs=[self.volume_step_fraction,self.candidate_active,self.candidate_bad],device=self.device)
  wp.launch(reject_unverified_predictor,dim=1,inputs=[self.volume_step_fraction,self.candidate_active,self.volume_invalid],device=self.device)
  wp.launch(apply_predictor,dim=self.model.particle_count,inputs=[particle_q_out,self.pos_prev_collision_detection,self.particle_displacements,self.volume_step_fraction],device=self.device)
 def _volume_safe_update(self,color,positions):
  from tomato_checked_volume_steps import checked_colored_step
  wp.launch(checked_colored_step,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,positions,self.pos_prev_collision_detection,self.particle_displacements,self.cell_offsets,self.cell_ids,self.cells,self.volumes,self.volumes64],outputs=[self.volume_invalid,self.volume_clip_count],device=self.device)
