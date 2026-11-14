from pathlib import Path
import json,sys,numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path[:0]=[str(R/'scripts'),str(R/'rl')]
from plan_contact_seating import HandGeometry
s=Usd.Stage.Open(str(W/'medium_original_handle_v01.usda'));m=HandGeometry(s);names=['right_rh_thumb_cmc_yaw','right_rh_thumb_cmc_pitch','right_rh_index_mcp_pitch','right_rh_middle_mcp_pitch','right_rh_ring_mcp_pitch','right_rh_pinky_mcp_pitch'];rows=[]
for case in ['v27_flank_margin_teacher/train_medium_face180_00','v27_filtered_touch_teacher/train_medium_face180_00','v13_teacher01/medium','v13_teacher01/opposite']:
 p=W/'datasets'/case;jn=json.loads((p/'joint_names.json').read_text())['all'];traj=json.loads((p/'trajectory.json').read_text());d=traj[-1] if 'flank_margin' in case else json.loads((p/'balanced_before_lift.json').read_text());q=np.array([d['q'][jn.index(n)] for n in names]);pose=d['hand_pose'];H=np.eye(4);H[:3,:3]=Rotation.from_quat(pose[3:]).as_matrix();H[:3,3]=pose[:3];T=m.transforms(q);cs=[]
 for c in d['contacts']:
  if c['part'] not in ['thumb','index']:continue
  name='right_rh_'+c['part']+'_distal';which=1 if c['part']=='thumb' else 2;B=H@T[name];point=np.array(c['point']);local=B[:3,:3].T@(point-B[:3,3]);qp=q.copy();qm=q.copy();qp[which]+=.00001;qm[which]-=.00001;Bp=H@m.transforms(qp)[name];Bm=H@m.transforms(qm)[name];deriv=(Bp[:3,:3]@local+Bp[:3,3]-Bm[:3,:3]@local-Bm[:3,3])/.00002;normal=np.array(c['normal']);cs.append(dict(part=c['part'],normal_force_N=c['force_N'],normal_lever_mm=float(deriv@normal)*1000,full_lever_mm=float(np.linalg.norm(deriv))*1000,force_derivative_alignment=float(deriv@normal/np.linalg.norm(deriv))))
 row=dict(case=case,sim_s=d['sim_s'],contacts=cs);rows.append(row);print(row,flush=True)
(W/'reports/contact_leverage.json').write_text(json.dumps(rows,indent=2))
