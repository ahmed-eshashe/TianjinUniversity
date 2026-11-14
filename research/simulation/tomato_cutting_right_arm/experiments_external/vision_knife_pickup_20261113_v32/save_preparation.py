from pathlib import Path
import json,numpy as np,hashlib,datetime
from zoneinfo import ZoneInfo
from scipy.spatial.transform import Rotation
from scipy.spatial import Delaunay
W=Path(__file__).resolve().parent;r=W/'runs/camera01';d=json.loads((r/'result.json').read_text());depth=np.load(r/'head_depth_m.npy');K=np.array(d['intrinsics']);R=Rotation.from_quat(d['camera_quaternion_xyzw_ros']).as_matrix();pos=np.array(d['camera_position_world_m']);vv,uu=np.indices(depth.shape);pixels=np.stack([uu,vv],axis=-1);roi=Delaunay(np.array(d['board_corner_pixels'])).find_simplex(pixels.reshape(-1,2)).reshape(depth.shape)>=0;rays=np.stack([uu,vv,np.ones_like(uu)],axis=-1)@np.linalg.inv(K).T@R.T
with np.errstate(invalid='ignore'):world=pos+rays*depth[:,:,None]
finite=roi&np.isfinite(depth);check={'board_roi_pixels':int(roi.sum()),'board_roi_finite_depth_fraction':float(finite.sum()/roi.sum()),'maximum_height_above_board_in_roi_m':float(np.max(world[finite,2])),'median_world_height_m':float(np.median(world[finite,2])),'scope':'Camera depth consistency check; includes the raised knife and board rim.'};(r/'depth_consistency.json').write_text(json.dumps(check,indent=2));print(check)
assert check['board_roi_finite_depth_fraction']>.99
pres=json.loads((W/'preserved_sources.json').read_text());assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pres.items())
if not (W/'STATUS.json').exists(): (W/'STATUS.json').write_text(json.dumps(dict(updated_local=datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),status='scene_camera_ready',board_centered=True,board_footprint_supported=True,head_rgbd_checked=True,free_knife_settling_checked=True,real_grasp_verified=False,policy_trained=False,end_grasp_choice='secure_pickup_then_separate_cutting_grip_adjustment',original_sources_unchanged=True),indent=2))
O=Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs');p=O/'learning-roadmap.json';data=json.loads(p.read_text());backup=W/'reports/learning-roadmap-before.json'
if not backup.exists():backup.write_text(p.read_text())
stage={'id':10,'title':'Head-vision knife pickup','phase':'Scene and camera checked; grasp learning pending','description':'Separate right-hand task: true contact/friction, no fixed attachment, head-mounted RGB-D, varied knife geometry and resting poses. Simulation first; physical transfer later.','items':[
{'id':'10.1','text':'Center the board in front of the abdomen on supported countertop.','status':'complete','evidence':'Board aligned to torso forward midline; 315 interior footprint samples lie on countertop top faces. Original scene unchanged.'},
{'id':'10.2','text':'Verify color and depth sensing from the robot head.','status':'complete','evidence':'Native 320×240 head RGB-D capture; all board corners inside the frame, board-region depth checked. Unattached knife settled under gravity.'},
{'id':'10.3','text':'Verify a real finger-contact pickup and unsupported hold.','status':'pending','evidence':'No new pickup pass. Existing fixed-mount cutting demos are not grasp qualification. Secure pickup first; cutting-grip adjustment afterward.'},
{'id':'10.4','text':'Build knife variants and feasible randomized resting poses.','status':'pending','evidence':'Planned; geometry families and evaluation cases will be separated before training.'},
{'id':'10.5','text':'Validate task observations, outcomes, resets and training throughput.','status':'pending','evidence':'Deployment actor will use head images/depth and joint feedback, without hidden object pose.'},
{'id':'10.6','text':'Train and evaluate a vision-based pickup policy.','status':'pending','evidence':'No pickup policy has been trained.'},
{'id':'10.7','text':'Improve robustness across positions, angles and knife shapes.','status':'pending','evidence':'Held-out geometry and placement evaluation required; no any-pose claim.'},
{'id':'10.8','text':'Show a learned contact-based pickup in the original kitchen.','status':'pending','evidence':'Pending successful independent evaluation.'}]}
if not any(x['id']==10 for x in data['stages']):
 data['stages'].append(stage);p.write_text(json.dumps(data,indent=2))
if not (W/'README.txt').exists(): (W/'README.txt').write_text('Head-vision knife pickup: isolated preparation\n\nConfirmed: real contact/friction, no fixed attachment; head RGB-D camera;\nvaried knife models and settled placements; simulation first, transfer later.\n\nChecked so far: centered and supported board, a real head RGB-D image,\nvalid board-region depth and gravity settlement of an unattached original knife.\nNo learned policy or new physical pickup has been demonstrated.\n\nThe remaining scope question is whether each episode must finish with a full\nwrapped cutting grip, or whether secure pickup is followed by a later grip adjustment.\n\nSee PLAN.txt, scene_config.json, runs/camera01/result.json,\nruns/camera01/head_rgb.png and STATUS.json. Original source files are unchanged.\n')
print('Preparation and checklist saved; no learner started')
