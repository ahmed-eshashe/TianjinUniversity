from pathlib import Path
from tomato_isaac_startup_guard import supervise
print(supervise(Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/runs/native/motor_effort_capture_20261102_01'),mode='motor_effort_capture',wall_s=180),flush=True)
