from pathlib import Path
from tomato_isaac_startup_guard import supervise
print(supervise(Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/runs/native/dry_tracking_corrected_20261102_01'),mode='dry_tracking_v02',wall_s=600),flush=True)
