from pathlib import Path
from tomato_isaac_startup_guard import supervise
print(supervise(Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/runs/native/corrected_exchange_operator_20261102_01'),mode='corrected_exchange_operator',wall_s=300),flush=True)
