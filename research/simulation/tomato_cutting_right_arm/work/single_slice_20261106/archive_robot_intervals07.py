"""Passively preserve published attempted robot intervals; acceptance is separate."""
from pathlib import Path
import json,time
p=Path(__file__).parent/'robot_cut07';out=p/'robot_intervals';out.mkdir(exist_ok=True)
while not (p/'worker_result.json').exists():
 try:
  blob=(p/'pending_robot_interval.json').read_bytes();row=json.loads(blob);dest=out/f"step_{row['step']:06d}.json"
  if not dest.exists():dest.write_bytes(blob)
 except (OSError,ValueError,KeyError):pass
 time.sleep(.1)
(out/'scope.json').write_text(json.dumps(dict(attempted_actual_robot_states=True,acceptance_requires_matching_cutting_trace=True,video_recorded=False),indent=2))
