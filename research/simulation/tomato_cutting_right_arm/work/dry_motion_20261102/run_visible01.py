from pathlib import Path
from tomato_isaac_startup_guard import supervise
print(supervise(Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/runs/native/visible_dry_motion_20261102_01'),mode='visible_dry_motion',wall_s=600),flush=True)
