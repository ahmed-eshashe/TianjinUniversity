"""Supervision for visible handle landmarks in actual head RGB-D recordings.

Object poses are labels only, never deployed network inputs. Initial frames of
failed pickup attempts can still provide correct perception labels; they are
not motor demonstrations and do not turn a failed pickup into a success.
"""
from pathlib import Path
import json
import numpy as np
from scipy.spatial.transform import Rotation

W = Path(__file__).resolve().parent
c = json.loads((W/'scene_config.json').read_text())
camera = np.array(c['camera_world_matrix'])
ros_rotation = camera[:3,:3] @ np.diag([1.,-1.,-1.])
intrinsic = np.array(json.loads((W/'runs/camera01/result.json').read_text())['intrinsics'])
landmarks = np.array([[-.13, .0076461609, .001586524],[-.045,.0076461609,.001586524]])
samples = []
metadata = []
for folder in sorted((W/'datasets/teacher_v02').iterdir()):
    if not folder.is_dir() or not (folder/'demonstration_metadata.json').exists():
        continue
    d = np.load(folder/'demonstration.npz')
    trace = json.loads((folder/'trajectory.json').read_text())
    reset = json.loads((folder/'reset_audit.json').read_text())['actual']
    selected = [np.argmin(abs(d['sim_s']-t)) for t in [0.,.2,.4,.8,1.2,1.6,2.,2.4]]
    for index in sorted(set(selected)):
        t = float(d['sim_s'][index])
        pose = np.array(reset if t==0 else min(trace,key=lambda x:abs(x['sim_s']-t))['knife_pose'])
        points = landmarks @ Rotation.from_quat(pose[3:]).as_matrix().T + pose[:3]
        view = (points-camera[:3,3]) @ ros_rotation
        projected = view @ intrinsic.T
        pixels = projected[:,:2]/projected[:,2,None]
        xy = np.rint(pixels).astype(int)
        if not ((xy[:,0]>=48)&(xy[:,0]<272)&(xy[:,1]>=48)&(xy[:,1]<208)).all():
            continue
        depth = d['depth'][index].astype(np.float32)
        observed = depth[xy[:,1],xy[:,0]]
        # Centreline lies inside the handle, a few millimetres behind the visible
        # surface. Larger front occluders are excluded from visible-landmark training.
        if not np.isfinite(observed).all() or (abs(observed-view[:,2])>.025).any():
            continue
        samples.append((d['rgb'][index],d['depth'][index],pixels.astype(np.float32),
                        1 if folder.name.startswith('validation_') else 0))
        metadata.append(dict(episode=folder.name,sim_s=t,landmark_pixels=pixels.tolist(),
                             visible_depth_residual_m=(observed-view[:,2]).tolist()))
out = W/'perception_data_v01'
assert not out.exists(), 'Preserve label versions'
out.mkdir()
np.savez_compressed(out/'labels.npz',rgb=np.stack([x[0] for x in samples]),depth=np.stack([x[1] for x in samples]),
                    points=np.stack([x[2] for x in samples]),split=np.array([x[3] for x in samples]))
(out/'metadata.json').write_text(json.dumps(dict(samples=metadata,source='Actual rendered head camera; simulator geometry only supplies supervised labels.',
                                               actor_inputs=['RGB-D'],landmarks_local=landmarks.tolist(),camera_world=camera.tolist(),intrinsics=intrinsic.tolist(),
                                               split='Whole episodes held out. No test placements or held-out knife geometries used.'),indent=2))
print(dict(total=len(samples),train=sum(x[3]==0 for x in samples),validation=sum(x[3]==1 for x in samples)))
