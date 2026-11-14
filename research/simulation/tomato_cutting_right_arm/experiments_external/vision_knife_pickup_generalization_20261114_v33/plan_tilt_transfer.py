from pathlib import Path
import json,sys,numpy as np
from scipy.spatial.transform import Rotation,Slerp
from pxr import Usd
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path.insert(0,str(R/'scripts'))
from reach_kinematics import ArmKinematics,PALM_OFFSET
s=Usd.Stage.Open(str(W/'medium_original_handle_v01.usda'));kin=ArmKinematics(s)
p=W/'datasets/v13_teacher_matrix/train_medium_face180_00';old=np.array(json.loads((p/'teacher_target_override.json').read_text())['hand_target_world']);goal=np.array(json.loads((W/'reports/opposite_relative_grasp_candidate.json').read_text())['target_world_example']);base=np.array(json.loads((W/'reports/pinch_geometry02.json').read_text())['q']);names=json.loads((p/'joint_names.json').read_text())['all'];actual=json.loads((p/'before_lift.json').read_text())['q'];actual=np.array([actual[names.index(n)] for n in kin.names]);rng=np.random.default_rng(17);rows=[]
for fraction in [1.,.75,.5]:
 H=old.copy();H[:3,:3]=Slerp([0,1],Rotation.from_matrix([old[:3,:3],goal[:3,:3]]))(fraction).as_matrix();H[:3,3]=old[:3,3]*(1-fraction)+goal[:3,3]*fraction
 best=None
 for seed in [actual,base,*[np.clip(actual+rng.normal(0,.35,7),kin.lower,kin.upper) for _ in range(6)]]:
  q,pe,re=kin.solve(H[:3,3]+H[:3,:3]@PALM_OFFSET,H[:3,:3],seed)
  if best is None or pe+.15*re<best['position_error_m']+.15*best['orientation_error_rad']:best=dict(q=q.tolist(),position_error_m=pe,orientation_error_rad=re)
  if pe<.0002 and re<.002:break
 best.update(fraction=fraction,hand_target=H.tolist(),q_difference_rad=float(np.linalg.norm(np.array(best['q'])-actual)))
 rows.append(best);print(fraction,best['position_error_m'],best['orientation_error_rad'],best['q_difference_rad'],flush=True)
(W/'reports/tilt_transfer_ik.json').write_text(json.dumps(rows,indent=2))
