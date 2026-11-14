from pathlib import Path
import json,sys,time,numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path.insert(0,str(R/'scripts'))
from reach_kinematics import ArmKinematics,PALM_OFFSET
s=Usd.Stage.Open(str(W/'medium_original_handle_v01.usda'));kin=ArmKinematics(s);g=json.loads((W/'reports/pinch_geometry02.json').read_text());H0=np.array(json.loads((W/'reports/opposite_relative_grasp_candidate.json').read_text())['target_world_example']);p=W/'datasets/v13_teacher_matrix/train_medium_face180_00';traj=json.loads((p/'trajectory.json').read_text());pose=[x for x in traj if x['phase']=='settle'][-1]['knife_pose'];axis=Rotation.from_quat(pose[3:]).as_matrix()[:,0];rng=np.random.default_rng(2026111409);base=np.array(g['q']);start=time.monotonic();rows=[]
for shift in [0.,.01,.02,.03]:
 H=H0.copy();H[:3,3]+=axis*(shift+.011);best=None
 for seed in [base,*[np.clip(base+rng.normal(0,.9,7),kin.lower,kin.upper) for _ in range(6)]]:
  q,pe,re=kin.solve(H[:3,3]+H[:3,:3]@PALM_OFFSET,H[:3,:3],seed)
  if best is None or pe+.15*re<best['pe']+.15*best['re']:best=dict(q=q.tolist(),pe=pe,re=re)
  if pe<.0002 and re<.002:break
  if time.monotonic()-start>90:break
 best.update(along_m=shift,hand_target_world=H.tolist());rows.append(best);print(shift,best['pe'],best['re'],flush=True)
 if time.monotonic()-start>90:break
(W/'reports/full_tilt_reach.json').write_text(json.dumps(rows,indent=2))
