from pathlib import Path
import time,json
p=Path(__file__).parent/'robot_cut13'
while not (p/'supervisor_result.json').exists():
 try:
  s=json.loads((p/'cutting_status.json').read_text())
  if s['route_fraction']>=.999 and s['failed_patches']<47:
   (p/'end_stroke_assessment_requested.json').write_text(json.dumps(s,indent=2))
   (p/'checkpoint_stop.request').write_text('Preserve complete accepted end-of-stroke state for assessment of incomplete separation. Do not repeat cut or claim success.\n')
   break
 except (OSError,ValueError,KeyError):pass
 time.sleep(1)
