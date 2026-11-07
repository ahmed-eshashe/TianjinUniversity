from pathlib import Path
import json,numpy as np
w=Path(__file__).parent
screen=json.loads((w/'bodyward_withdrawal_screen.json').read_text());cp=Path(screen['checkpoint']);m=json.loads(cp.read_text());route=json.loads((w/'fitted_continuation_plan_v2.json').read_text());parent=m['progress']*route['duration_s'];prefix=[x for x in route['rows'] if x['phase']=='entry' or x['time_s']<parent];extra=[]
for row in screen['rows']:
 if row['distance_m']>.06000001:break
 extra.append(dict(row,phase='cut',motion_stage='bodyward_withdrawal',time_s=parent+row['distance_m']/.02))
if len(extra)<121:raise ValueError('Full 60 mm constant-height IK screen required')
route.update(rows=prefix+extra,parent_duration_s=parent,duration_s=extra[-1]['time_s'],cut_end_time_s=parent,transition_checkpoint=str(cp.with_suffix('.npz')),purpose='User-requested constant-height retreat toward robot body, 60 mm at 20 mm/s',motion_route='bodyward_withdrawal_plan_v1',direction_world=screen['direction_world'],height_change_m=0,kinematic_only=True,robot_dynamics_checked=False,full_slice=False)
(w/'bodyward_withdrawal_plan_v1.json').write_text(json.dumps(route,indent=2));print('Built',route['transition_checkpoint'],route['duration_s']-parent,'seconds')
