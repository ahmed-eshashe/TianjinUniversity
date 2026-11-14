"""Image-only locator plus learned known-family/rest-face grasp selection."""
from pathlib import Path
import hashlib,json
import numpy as np,torch
from grasp_vision_v02 import prepare_image
from grasp_selector_v01 import GraspSelector
from visual_grasp_v02 import VisualGrasp as BaseGrasp
class VisualGrasp:
 def __init__(self,checkpoint,calibration,device='cpu'):
  self.device=device;self.saved=torch.load(checkpoint,map_location=device,weights_only=False)
  assert self.saved['selector_source_hash']==hashlib.sha256(Path(__file__).with_name('grasp_selector_v01.py').read_bytes()).hexdigest()
  base=Path(self.saved['base_checkpoint']);assert hashlib.sha256(base.read_bytes()).hexdigest()==self.saved['base_sha256']
  self.base=BaseGrasp(base,calibration,device);self.selector=GraspSelector().to(device);self.selector.load_state_dict(self.saved['selector_state_dict']);self.selector.eval()
 def predict(self,rgb,depth,blank=False):
  p=self.base.predict(rgb,depth,blank);im=prepare_image(rgb[None],depth[None],self.device)
  if blank:im.zero_()
  with torch.no_grad():prob=self.selector(im).softmax(-1)[0].cpu().numpy()
  choice=int(prob.argmax());confidence=float(prob[choice]);H=np.array(p['hand_target_world']);offset=np.array(self.saved['hand_frame_offsets'][choice]);H[:3,3]+=H[:3,:3]@offset
  if confidence<.95:p['reasons'].append('Visual grasp style uncertain')
  p.update(accepted=not p['reasons'],hand_target_world=H.tolist(),grasp_style=dict(predicted=self.saved['classes'][choice],confidence=confidence,probabilities=prob.tolist(),offset_in_hand_m=offset.tolist(),labels_from_image_classifier_only=True),scope='Learned visual locator and known-family/two-face grasp selector; engineered motion, not arbitrary3D grasps',family_or_rest_pose_input=False,ground_truth_pose_input=False)
  return p
