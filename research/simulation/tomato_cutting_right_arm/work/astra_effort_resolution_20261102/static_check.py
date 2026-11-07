from pathlib import Path
import numpy as np,json
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parents[2];run=R/'runs/native/motor_effort_capture_20261102_01';o=json.loads((run/'ordering.json').read_text());s=json.loads((R/'runs/native/load_down_20261102_01/robot_kinematic_snapshot.json').read_text());z=np.load(run/'interval_000.npz');b=np.load(R/'runs/native/mounted_target_v06_r4_20261102_01/robot_energy_binding_inputs.npz');scope=json.loads((R/'runs/native/mounted_target_v06_r4_20261102_01/robot_energy_binding_scope.json').read_text());mass={n:m for n,m in zip(scope['body_names'],b['mass'])};bychild={j['child'].split('/')[-1]:j for j in s['joints']};js={j['name']:j for j in s['joints']if j.get('name')}
for n in ['left_AR5_5_07L_W4C4A2_joint_2','right_AR5_5_07R_W4C4A2_joint_1','right_AR5_5_07R_W4C4A2_joint_2']:
 j=js[n];ch=j['child'].split('/')[-1];idx=o['body_names'].index(ch);pose=z['after_body_pose'][idx];rot=Rotation.from_quat(pose[3:]).as_matrix();child=np.linalg.inv(j['inverse_child_joint_matrix']);anchor=pose[:3]+rot@child[:3,3];axis=rot@child[:3,:3]@j['axis'];desc=[]
 for bn in o['body_names']:
  cur=bn
  while cur in bychild:
   if cur==ch:desc.append(bn);break
   cur=bychild[cur]['parent'].split('/')[-1]
 gravity=np.array([0,0,-9.81]);F=np.zeros(3);M=np.zeros(3)
 for bn in desc:
  c=z['after_body_com_pose'][o['body_names'].index(bn),:3];f=mass[bn]*gravity;F-=f;M-=np.cross(c-anchor,f)
 i=o['joint_names'].index(n);raw=z['incoming_joint_wrench_backend'][o['backend_body_names'].index(ch)];worldF=rot@child[:3,:3]@raw[:3];worldM=rot@child[:3,:3]@raw[3:]
 print(n,'subtree',len(desc),'expectedF',F,'reportedF',worldF,'expectedTau',M@axis,'reportedTau',worldM@axis,'ff',z['gravity_feedforward'][i])
