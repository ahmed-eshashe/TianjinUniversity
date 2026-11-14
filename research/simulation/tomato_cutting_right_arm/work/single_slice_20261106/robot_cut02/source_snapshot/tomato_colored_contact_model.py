"""Color-gated assembly, unchanged exact forces and positive blocks."""
from tomato_objective_gn_compact_model import ContactObjectiveGNTomatoVBD
class ColoredContactObjectiveGNVBD(ContactObjectiveGNTomatoVBD):
 def _gather_blocks(self,color,state,dt):
  self.surface_contact.current_color=color
  try:super()._gather_blocks(color,state,dt)
  finally:self.surface_contact.current_color=-1
