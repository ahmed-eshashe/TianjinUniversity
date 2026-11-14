"""Image-only selection of grasp position, planar orientation and height."""
from pathlib import Path
import hashlib,json
import numpy as np
import torch
from scipy.spatial.transform import Rotation
from grasp_vision_v03 import GraspVision,prepare_image,coordinates

class VisualGrasp:
    def __init__(self,checkpoint,calibration,device='cpu'):
        self.device=device;self.calibration=json.loads(Path(calibration).read_text())
        saved=torch.load(checkpoint,map_location=device,weights_only=False)
        source=Path(__file__).with_name('grasp_vision_v03.py')
        assert saved['source_hash']==hashlib.sha256(source.read_bytes()).hexdigest()
        self.model=GraspVision().to(device);self.model.load_state_dict(saved['state_dict']);self.model.eval()

    def predict(self,rgb,depth,blank=False):
        image=prepare_image(rgb[None],depth[None],self.device)
        if blank:image.zero_()
        with torch.no_grad():
            logits,height,along=self.model(image);pixels,confidence=coordinates(logits)
        pixels=pixels[0].cpu().numpy();confidence=confidence[0].cpu().numpy();height=height[0].cpu().numpy()
        c=self.calibration;C=np.array(c['camera_world_matrix']);K=np.array(c['intrinsics']);nominal=np.array(c['nominal_landmarks_world'])
        rays=np.c_[pixels,np.ones(2)]@np.linalg.inv(K).T@(C[:3,:3]@np.diag([1.,-1.,-1.])).T
        reasons=[]
        if not np.isfinite(pixels).all() or confidence.min()<.10:reasons.append('Grasp landmarks insufficiently localized')
        if not np.isfinite(height).all() or not ((height>=-.004)&(height<=.010)).all():reasons.append('Resting-height estimate outside validated range')
        if np.any(rays[:,2]>=-.05):reasons.append('Invalid downward camera rays')
        xy=np.rint(pixels).astype(int)
        valid_pixel=(xy[:,0]>=0)&(xy[:,0]<640)&(xy[:,1]>=0)&(xy[:,1]<480)
        if blank or not valid_pixel.all():reasons.append('Missing or invalid depth at grasp landmarks')
        else:
            observed=depth[xy[:,1],xy[:,0]]
            if not (np.isfinite(observed)&(observed>.05)&(observed<3.)).all():reasons.append('Missing or invalid depth at grasp landmarks')
        points=C[:3,3]+rays*((nominal[:,2]+height-C[2,3])/rays[:,2])[:,None]
        distance=float(np.linalg.norm(points[1]-points[0]))
        if not .075<=distance<=.095:reasons.append('Estimated landmark spacing outside calibrated range')
        bounds=np.array(c['board_world_bounds'])
        if np.any(points[:,:2]<bounds[0,:2]+.005) or np.any(points[:,:2]>bounds[1,:2]-.005):reasons.append('Grasp estimate outside supported board')
        v=points[1]-points[0];n=nominal[1]-nominal[0]
        yaw=np.arctan2(v[1],v[0])-np.arctan2(n[1],n[0])
        D=np.eye(4);D[:3,:3]=Rotation.from_euler('z',yaw).as_matrix();D[:3,3]=(points-nominal@D[:3,:3].T).mean(0)
        target=D@np.array(c['nominal_hand_target_world']);axis=v/np.linalg.norm(v);target[:3,3]+=float(along[0])*axis
        return dict(accepted=not reasons,reasons=reasons,pixels=pixels.tolist(),confidence=confidence.tolist(),
                    learned_along_offset_m=float(along[0]),landmarks_world=points.tolist(),landmark_distance_m=distance,height_correction_m=height.tolist(),
                    hand_target_world=target.tolist(),inputs=['head RGB','head depth','fixed camera calibration'],
                    ground_truth_pose_input=False,family_or_rest_pose_input=False,flat_rest_height_prior=False,
                    scope='Learned grasp landmarks/height for planar knife yaw and two stable resting faces; not arbitrary 3D grasps.')
