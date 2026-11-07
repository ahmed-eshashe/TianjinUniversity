from pathlib import Path
import sys,json,numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;sys.path.insert(0,str(r/'scripts'))
from reach_kinematics import ArmKinematics,PALM_OFFSET
p=json.loads((r/'work/backward_elbow_20261105/plan.json').read_text());k=ArmKinematics(Usd.Stage.Open(p['scene']));m=np.array(p['mount_hand_from_knife']);seed=np.array(p['approach_routes'][-1][-1]);hand=k.transforms(seed)[k.hand_path];tool=hand@m;R=tool[:3,:3];rotation=Rotation.from_euler('z',-70,degrees=True).as_matrix();shift=rotation@np.array([-.0225,0,0]);start=tool[:3,3]+shift
blade=np.array(json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())['vertices']);bottom=min((blade@R.T)[:,2]);end=start.copy();end[2]=.001-bottom
rows=[]
for z in np.linspace(start[2],end[2],241):
 origin=start.copy();origin[2]=z;hr=R@m[:3,:3].T;seed,e,a=k.solve(origin-hr@m[:3,3]+hr@PALM_OFFSET,hr,seed)
 rows.append(dict(q=seed.tolist(),position_error=e,angle_error=a,tool_origin=origin.tolist()))
 if e>2e-5 or a>2e-4:break
result=dict(kinematic_only=True,passed=len(rows)==241 and rows[-1]['position_error']<2e-5 and rows[-1]['angle_error']<2e-4,target_world_from_material_rotation=rotation.tolist(),target_rotation_note='Rigid scene rotation only; canonical research mechanics frame retained. Not yet integrated or validated.',stroke_m=float(start[2]-end[2]),rows=rows,collisions_checked=False,contact_tested=False,cutting=False);(w/'research_stroke_plan.json').write_text(json.dumps(result,indent=2));print({k:v for k,v in result.items()if k!='rows'})
