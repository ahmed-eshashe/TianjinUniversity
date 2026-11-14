"""Supervised grasp labels from actual settled images; no test data permitted."""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parent
a=argparse.ArgumentParser();a.add_argument('--targets',type=Path,required=True);a.add_argument('--output',type=Path,required=True);args=a.parse_args()
assert not args.output.exists();args.output.mkdir(parents=True)
offsets=json.loads(args.targets.read_text());cal=json.loads((W/'grasp_calibration_v02.json').read_text());C=np.array(cal['camera_world_matrix']);K=np.array(cal['intrinsics']);R=C[:3,:3]@np.diag([1.,-1.,-1.]);nominal=np.array(cal['nominal_landmarks_world'])
samples=[];metadata=[]
for path in sorted(W.glob('head_images_v0[12]/*/*/metadata.json')):
    meta=json.loads(path.read_text());ep=meta['episode'];assert ep['split'] in ['train','validation'] and ep['family']!='novel'
    specification=offsets[ep['family']][str(ep['rest_roll_deg'])]
    shift=specification['along_m'];wrist_yaw=specification['yaw_deg']
    points=np.array([[-.13+shift,.0076461609,.001586524],[-.045+shift,.0076461609,.001586524]])
    pose=np.array(meta['knife_pose']);object_rotation=Rotation.from_quat(pose[3:]).as_matrix();world=points@object_rotation.T+pose[:3]
    v=world[1]-world[0];n=nominal[1]-nominal[0]
    D=np.eye(4);D[:3,:3]=Rotation.from_euler('z',np.arctan2(v[1],v[0])-np.arctan2(n[1],n[0])).as_matrix();D[:3,3]=(world-nominal@D[:3,:3].T).mean(0)
    if wrist_yaw:
        anchor=np.array([-.1441+shift,.0234 if ep['rest_roll_deg'] else -.0021,-.0024 if ep['rest_roll_deg'] else .00765])
        anchor=object_rotation@anchor+pose[:3]
        turn=np.eye(4);turn[:3,:3]=Rotation.from_euler('z',wrist_yaw,degrees=True).as_matrix();turn[:3,3]=anchor-turn[:3,:3]@anchor;D=turn@D
    # Virtual grasp-frame markers encode the chosen hand pose. They are not
    # claimed to be two physical points on the handle when yaw is adjusted.
    world=nominal@D[:3,:3].T+D[:3,3]
    view=(world-C[:3,3])@R;projected=view@K.T;xy=projected[:,:2]/projected[:,2,None]
    assert (np.array(meta['intrinsics']).squeeze()==K).all()
    if not ((xy[:,0]>100)&(xy[:,0]<540)&(xy[:,1]>100)&(xy[:,1]<412)).all():raise ValueError(('Training grasp outside fixed crop',ep['id'],xy))
    rgb=np.array(Image.open(path.parent/'rgb.png'));depth=np.load(path.parent/'depth.npy')
    ij=np.rint(xy).astype(int);observed=depth[ij[:,1],ij[:,0]]
    assert np.isfinite(observed).all() and (abs(observed-view[:,2])<.03).all(),ep['id']
    height=world[:,2]-nominal[:,2]
    assert ((height>=-.004)&(height<=.010)).all(),(ep['id'],height)
    samples.append((rgb,depth,xy.astype(np.float32),height,0 if ep['split']=='train' else 1))
    metadata.append(dict(id=ep['id'],split=ep['split'],family=ep['family'],face=ep['rest_roll_deg'],teacher_shift_m=shift,teacher_wrist_yaw_deg=wrist_yaw,world_points=world.tolist(),hand_target_world=(D@np.array(cal['nominal_hand_target_world'])).tolist(),height_correction_m=height.tolist(),source=str(path)))
assert len(samples)==252
np.savez_compressed(args.output/'labels.npz',rgb=np.stack([x[0] for x in samples]),depth=np.stack([x[1] for x in samples]),points=np.stack([x[2] for x in samples]),height=np.array([x[3] for x in samples],dtype=np.float32),split=np.array([x[4] for x in samples]))
(args.output/'metadata.json').write_text(json.dumps(dict(samples=metadata,actor_inputs=['head RGB','head depth'],label_type='Virtual grasp-frame markers and heights, encoding teacher hand pose',object_pose_used_for_labels_only=True,targets=str(args.targets.resolve()),test_images_consumed=0),indent=2))
print('Labelled',len(samples),'real head images; test/novel images excluded')
