import time,json
from pathlib import Path
from tomato_isaac_startup_guard import supervise
previous=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/runs/native/dry_scene_inspection_20261102_01/supervisor_result.json')
end=time.monotonic()+15
while not previous.exists()and time.monotonic()<end:time.sleep(.2)
assert previous.exists()and not json.loads(previous.read_text())['remaining_live_group_members']
print(supervise(Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/runs/native/dry_scene_inspection_20261102_02'),mode='dry_scene_inspection_v02',wall_s=300),flush=True)
