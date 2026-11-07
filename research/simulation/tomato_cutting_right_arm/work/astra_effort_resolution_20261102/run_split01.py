from pathlib import Path
from tomato_isaac_startup_guard import supervise
print(supervise(Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/runs/native/effort_split_20261102_01'),mode='effort_split',wall_s=180),flush=True)
