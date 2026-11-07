from pathlib import Path
from tomato_isaac_startup_guard import supervise
print(supervise(Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/runs/native/dry_scene_inspection_20261102_01'),mode='dry_scene_inspection',wall_s=300),flush=True)
