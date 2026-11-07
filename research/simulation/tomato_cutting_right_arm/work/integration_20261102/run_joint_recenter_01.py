from pathlib import Path
import json
from tomato_isaac_startup_guard import supervise
r=Path(__file__).resolve().parents[2];d=supervise(r/'runs/native/joint_recenter_20261102_01',mode='joint_recenter',wall_s=900);print(json.dumps(d,indent=2),flush=True)
