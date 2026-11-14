"""Candidate coupled zero-gap-surface contact and checked mechanical stepping.

Collision model has complete enabled self-contact. Mechanical model uses that
separate embedded collision model rather than Newton's direct zero-gap path.
No combined solver qualification is implied by importing this class.
"""
from tomato_objective_full_model import ObjectiveTomatoVBD
from tomato_board_support import CheckedBoardSupportVBD

class EmbeddedContactMixin:
 def _initialize_particles(self,state_in,state_out,dt):
  self.surface_contact.detect(state_in.particle_q)
  super()._initialize_particles(state_in,state_out,dt)
 def _penetration_free_truncation(self,particle_q_out=None):
  self.surface_contact.cap(-1,self.model.particle_colors,self.pos_prev_collision_detection,self.particle_displacements)
  super()._penetration_free_truncation(particle_q_out)
 def _volume_safe_update(self,color,positions):
  self.surface_contact.cap(color,self.model.particle_colors,self.pos_prev_collision_detection,self.particle_displacements)
  super()._volume_safe_update(color,positions)
 def _gather_blocks(self,color,state,dt):
  super()._gather_blocks(color,state,dt)
  self.surface_contact.evaluate(state.particle_q,dt)
  self.surface_contact.scatter(color,self.model.particle_colors,self.particle_forces,self.particle_hessians)
 def commit_cohesion(self,state):
  if int(self.surface_contact.invalid.numpy()[0]):raise ValueError('Contact geometry/capacity failed; history not committed')
  super().commit_cohesion(state)

class ContactObjectiveTomatoVBD(EmbeddedContactMixin,ObjectiveTomatoVBD):pass
class ContactFixedFrameTomatoVBD(EmbeddedContactMixin,CheckedBoardSupportVBD):pass
