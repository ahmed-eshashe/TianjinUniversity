from pathlib import Path
import json,sys,numpy as np
from scipy.spatial.transform import Rotation
r=Path(__file__).resolve().parents[2];w=Path(__file__).resolve().parent;sys.path.insert(0,str(r/'scripts'));import search_wrap_grasp as g
p=json.loads((w/'native01/actual_pose.json').read_text());tool=np.array(p['tool_pose']);rt=Rotation.from_quat(tool[3:]).as_matrix();poses=dict(zip(p['body_names'],p['poses']));report={}
for name,v in g.mesh:
 short=name.rsplit('/',1)[-1]
 if not any(f in short for f in ['thumb','index','middle','ring','pinky']):continue
 pose=np.array(poses[short]);world=v@Rotation.from_quat(pose[3:]).as_matrix().T+pose[:3];local=(world-tool[:3])@rt;report[short]=dict(minimum_knife_x_m=float(local[:,0].min()),maximum_knife_x_m=float(local[:,0].max()),clearance_behind_blade_boundary_m=float(local[:,0].min()+.17205831))
assert min(x['clearance_behind_blade_boundary_m'] for x in report.values())>.02
(w/'actual_grip_audit.json').write_text(json.dumps(report,indent=2));print('Smallest full-finger axial clearance behind blade:',min(x['clearance_behind_blade_boundary_m']for x in report.values()))
