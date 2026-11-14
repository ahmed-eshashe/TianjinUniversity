"""RGB-D-only grasp targeting with frozen head/flat-board calibration.

The public predictor accepts images, not simulator poses, episode IDs or reset
parameters. The fixed nominal rest height is a disclosed flat-rest prior.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import torch
from scipy.spatial.transform import Rotation
from handle_vision import HandleVision, prepare_image, coordinates


class VisualGrasp:
    def __init__(self, checkpoint, calibration, device='cpu'):
        self.device = device
        self.calibration = json.loads(Path(calibration).read_text())
        saved = torch.load(checkpoint, map_location=device, weights_only=False)
        module = Path(__file__).with_name('handle_vision.py')
        assert saved['source_hash'] == hashlib.sha256(module.read_bytes()).hexdigest()
        self.model = HandleVision().to(device)
        self.model.load_state_dict(saved['state_dict'])
        self.model.eval()

    def predict(self, rgb, depth, blank=False):
        image = prepare_image(rgb[None], depth[None], self.device)
        if blank:
            image.zero_()
        with torch.no_grad():
            pixels, confidence = coordinates(self.model(image))
        pixels = pixels[0].cpu().numpy()
        confidence = confidence[0].cpu().numpy()
        c = self.calibration
        C = np.array(c['camera_world_matrix'])
        K = np.array(c['intrinsics'])
        nominal = np.array(c['nominal_landmarks_world'])
        rays = np.column_stack([pixels, np.ones(2)]) @ np.linalg.inv(K).T @ (C[:3,:3] @ np.diag([1.,-1.,-1.])).T
        reasons = []
        if not np.isfinite(pixels).all() or np.min(confidence) < .10:
            reasons.append('Handle landmarks insufficiently localized')
        if np.any(rays[:,2] >= -.05):
            reasons.append('Invalid board intersection')
        points = C[:3,3] + rays * ((nominal[:,2] - C[2,3]) / rays[:,2])[:,None]
        distance = float(np.linalg.norm(points[1]-points[0]))
        if not .075 <= distance <= .095:
            reasons.append('Estimated handle landmark spacing outside calibrated range')
        bounds = np.array(c['board_world_bounds'])
        if np.any(points[:,:2] < bounds[0,:2]+.005) or np.any(points[:,:2] > bounds[1,:2]-.005):
            reasons.append('Estimated handle outside supported board region')
        vector = points[1]-points[0]
        nominal_vector = nominal[1]-nominal[0]
        yaw = np.arctan2(vector[1],vector[0])-np.arctan2(nominal_vector[1],nominal_vector[0])
        D = np.eye(4)
        D[:3,:3] = Rotation.from_euler('z',yaw).as_matrix()
        D[:3,3] = (points - nominal @ D[:3,:3].T).mean(0)
        D[2,3] = 0.
        target = D @ np.array(c['nominal_hand_target_world'])
        return dict(accepted=not reasons, reasons=reasons, pixels=pixels.tolist(),
                    confidence=confidence.tolist(), landmarks_world=points.tolist(),
                    landmark_distance_m=distance, hand_target_world=target.tolist(),
                    inputs=['head RGB', 'head depth', 'fixed calibration'],
                    ground_truth_pose_input=False, flat_rest_height_prior=True)
