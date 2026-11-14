from pathlib import Path
import json,sys,numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path[:0]=[str(R/'scripts'),str(R/'rl')]
from plan_contact_seating import HandGeometry
model=HandGeometry(Usd.Stage.Open(str(W/'knife_short_blade_v02.usda')));report=[]
for folder in ['hybrid_v03_validation/validation_001','hybrid_v03_test/test_002','hybrid_v03_test/test_003']:
 p=W/'datasets'/folder;rows=json.loads((p/'trajectory.json').read_text());names=json.loads((p/'joint_names.json').read_text())['all'];hn=['right_rh_thumb_cmc_yaw','right_rh_thumb_cmc_pitch']+['right_rh_'+f+'_mcp_pitch' for f in ['index','middle','ring','pinky']];ids=[names.index(n) for n in hn]
 selected=[]
 for t in [6.5,7.,7.4,7.5]:
  r=min(rows,key=lambda r:abs(r['sim_s']-t));q=np.array(r['q'])[ids];H=np.array(r['hand_pose']);hr=Rotation.from_quat(H[3:]).as_matrix();transforms=model.transforms(q);clearance={}
  for name,(vertices,eq) in model.meshes.items():
   T=transforms[name];v=(vertices@T[:3,:3].T+T[:3,3])@hr.T+H[:3];clearance[name]=float(v[:,2].min())
  selected.append(dict(sim_s=r['sim_s'],min_board_clearance_m=min(clearance.values()),distal_clearances_m={n:v for n,v in clearance.items() if 'distal' in n},knife_min_height_m=r['minimum_tool_height_m']))
 report.append(dict(episode=folder,rows=selected))
(W/'reports/hybrid_closure_geometry_audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
