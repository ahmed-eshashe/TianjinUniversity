exec(open('inspect_index_reach_flank_sweep.py').read().split('rows=[]')[0])
p=W/'datasets/v22_cross_probe/train_medium_face180_00';a=json.loads((p/'trajectory.json').read_text());pose=[x for x in a if x['phase']=='settle'][-1]['knife_pose'];K=np.eye(4);K[:3,:3]=Rotation.from_quat(pose[3:]).as_matrix();K[:3,3]=pose[:3];H=np.array(json.loads((p/'teacher_target_override.json').read_text())['hand_target_world']);H[:3,3]+=K[:3,0]*.011+K[:3,1]*.0025;A=np.linalg.inv(K)@H;rows=[]
for rear in [None,.5,1.15,1.25]:
 q=np.array(g['hand_joint_rad']);q[1]-=.07;q[2:]-=.1
 if rear is not None:q[3:]=rear
 values={}
 for name,T in m.transforms(q).items():
  if not any(f in name for f in ['middle','ring','pinky']):continue
  B=A@T;v,eq=m.meshes[name];vk=v@B[:3,:3].T+B[:3,3];ov=(handle-B[:3,3])@B[:3,:3];gap=max(float((ov@eq[:,:3].T+eq[:,3]).min(0).max()),float((vk@hh.equations[:,:3].T+hh.equations[:,3]).min(0).max()));values[name]=dict(handle_gap_mm=gap*1000,board_gap_mm=float((vk@K[:3,:3].T+K[:3,3])[:,2].min())*1000)
 row=dict(rear=rear,values=values);rows.append(row);print(row,flush=True)
(W/'reports/unused_finger_clearance.json').write_text(json.dumps(rows,indent=2))
