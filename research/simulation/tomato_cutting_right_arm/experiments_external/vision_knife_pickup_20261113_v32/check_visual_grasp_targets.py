"""Offline check of learned landmarks -> grasp targets for the flat-rest curriculum.

This prepares a reviewable hybrid-controller proposal; it does not execute a
robot pickup or claim that a motor policy has learned the complete motion.
"""
from pathlib import Path
import json
import numpy as np
import torch
from scipy.spatial.transform import Rotation
from handle_vision import HandleVision,prepare_image,coordinates

W=Path(__file__).resolve().parent
torch.set_num_threads(2)
model=HandleVision()
checkpoint=torch.load(W/'policies/handle_vision_v01/best.pt',map_location='cpu',weights_only=False)
model.load_state_dict(checkpoint['state_dict']);model.eval()
c=json.loads((W/'scene_config.json').read_text());C=np.array(c['camera_world_matrix']);R=C[:3,:3]@np.diag([1.,-1.,-1.])
intrinsic=np.array(json.loads((W/'runs/camera01/result.json').read_text())['intrinsics'])
old=np.array(json.loads((W/'runs/camera01/result.json').read_text())['knife_pose'])
def matrix(p):
    T=np.eye(4);T[:3,:3]=Rotation.from_quat(p[3:]).as_matrix();T[:3,3]=p[:3];return T
legacy=matrix(old);g=json.loads((W/'reports/pinch_geometry02.json').read_text());H0=legacy@np.array(g['hand_from_knife'])
trace=json.loads((W/'runs/pickup18_control20/trajectory.json').read_text());nominal=matrix(min(trace,key=lambda x:abs(x['sim_s']-.5))['knife_pose'])
landmarks=np.array([[-.13,.0076461609,.001586524],[-.045,.0076461609,.001586524]])
nominal_points=landmarks@nominal[:3,:3].T+nominal[:3,3]
nominal_yaw=np.arctan2(*(nominal_points[1]-nominal_points[0])[[1,0]])
meta=json.loads((W/'perception_data_v02_settled/metadata.json').read_text());d=np.load(W/'perception_data_v02_settled/labels.npz');rows=[]
for index in np.flatnonzero(d['split']==1):
    with torch.no_grad():pixels,confidence=coordinates(model(prepare_image(d['rgb'][index:index+1],d['depth'][index:index+1],'cpu')))
    pixels=pixels[0].numpy();rays=np.column_stack([pixels,np.ones(2)])@np.linalg.inv(intrinsic).T@R.T
    points=C[:3,3]+rays*((nominal_points[:,2]-C[2,3])/rays[:,2])[:,None]
    yaw=np.arctan2(*(points[1]-points[0])[[1,0]])-nominal_yaw
    D=np.eye(4);D[:3,:3]=Rotation.from_euler('z',yaw).as_matrix();D[:3,3]=(points-nominal_points@D[:3,:3].T).mean(0);D[2,3]=0.
    predicted=D@H0
    record=meta['samples'][index];config=json.loads((W/'datasets/teacher_v02'/record['episode']/'configuration.json').read_text())['args']
    expected=np.eye(4);expected[:3,:3]=Rotation.from_euler('z',config['yaw_deg'],degrees=True).as_matrix();centre=legacy[:3,3]+legacy[:3,:3]@np.array([-.0860033812,.0076461609,.001586524]);expected[:3,3]=centre-expected[:3,:3]@centre+[config['dx'],config['dy'],0.];expected=expected@H0
    rows.append(dict(episode=record['episode'],sim_s=record['sim_s'],pixels=pixels.tolist(),confidence=confidence[0].tolist(),
                     handle_position_error_m=float(np.linalg.norm(predicted[:3,3]-expected[:3,3])),
                     orientation_error_deg=float(np.rad2deg(Rotation.from_matrix(predicted[:3,:3]@expected[:3,:3].T).magnitude())),
                     estimated_landmark_distance_m=float(np.linalg.norm(points[1]-points[0]))))
result=dict(scope='Offline learned-vision grasp targeting only. Known fixed head calibration, board plane and nominal flat resting height. No actual vision-driven pickup or arbitrary-rest/knife-generalization claim.',
            independent_placements=len(set(x['episode'] for x in rows)),frames=len(rows),
            mean_grasp_position_error_m=float(np.mean([x['handle_position_error_m'] for x in rows])),
            max_grasp_position_error_m=max(x['handle_position_error_m'] for x in rows),
            mean_orientation_error_deg=float(np.mean([x['orientation_error_deg'] for x in rows])),
            max_orientation_error_deg=max(x['orientation_error_deg'] for x in rows),rows=rows)
(W/'reports/learned_visual_grasp_targets.json').write_text(json.dumps(result,indent=2))
print({k:v for k,v in result.items() if k!='rows'})
