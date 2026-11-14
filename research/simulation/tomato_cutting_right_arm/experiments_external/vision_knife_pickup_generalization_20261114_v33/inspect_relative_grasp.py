from pathlib import Path
import sys,json,numpy as np
from scipy.spatial.transform import Rotation
from scipy.spatial import ConvexHull
from pxr import Usd,UsdGeom
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path[:0]=[str(R/'scripts'),str(R/'rl')]
from plan_contact_seating import HandGeometry
from reach_kinematics import PALM_OFFSET
c=json.loads((W/'scene_config.json').read_text());s=Usd.Stage.Open(str(W/'medium_original_handle_v01.usda'));m=HandGeometry(s)
a=json.loads((W/'reports/opposite_relative_grasp_candidate.json').read_text());H=np.array(a['target_world_example']);g=json.loads((W/'reports/pinch_geometry02.json').read_text());q=np.array(g['hand_joint_rad']);kin=m.kin;seed,pe,re=kin.solve(H[:3,3]+H[:3,:3]@PALM_OFFSET,H[:3,:3],g['q']);rows=[]
for phase in ['pre','reference','measured_pinch']:
 vals=q.copy()
 if phase=='pre':vals[1]-=.07;vals[2:]-=.1
 if phase=='measured_pinch':
  p=W/'datasets/v13_teacher01/opposite';b=json.loads((p/'balanced_before_lift.json').read_text());ns=json.loads((p/'joint_names.json').read_text())['all'];vals=np.array([b['q'][ns.index(n)] for n in ['right_rh_thumb_cmc_yaw','right_rh_thumb_cmc_pitch',*[f'right_rh_{f}_mcp_pitch' for f in ['index','middle','ring','pinky']]]])
 tr=m.transforms(vals);heights={}
 for name,(v,eq) in m.meshes.items():
  B=H@tr[name];heights[name]=float((v@B[:3,:3].T+B[:3,3])[:,2].min())
 rows.append(dict(phase=phase,minimum_board_gap_m=min(heights.values()),by_body=heights))
a.update(ik_position_error_m=pe,ik_orientation_error_rad=re,q=seed.tolist(),board_screen=rows)
(W/'reports/opposite_relative_grasp_screen.json').write_text(json.dumps(a,indent=2));print('IK',pe,re);print([(r['phase'],r['minimum_board_gap_m']) for r in rows])
