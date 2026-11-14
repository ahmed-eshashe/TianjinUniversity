from pathlib import Path
import json,numpy as np,torch
from torch import nn
from scipy.spatial.transform import Rotation
from visual_grasp_v02 import VisualGrasp
from grasp_vision_v02 import prepare_image,coordinates
W=Path(__file__).resolve().parent;torch.set_num_threads(2);d=dict(np.load(W/'grasp_data_v10/labels.npz'));meta=json.loads((W/'grasp_data_v10/metadata.json').read_text())['samples'];rows=[]
class Ensemble(nn.Module):
 def __init__(self,model,factors):super().__init__();self.model=model;self.factors=factors
 def forward(self,im):
  ims=[]
  for f in self.factors:
   x=im.clone();x[:,:3]=(x[:,:3]*f).clamp(0,1);ims.append(x)
  logits,height=self.model(torch.cat(ims));size=len(im);p=logits.float().flatten(2).softmax(-1).reshape(len(ims),size,2,*logits.shape[2:]).mean(0);h=height.reshape(len(ims),size,2).mean(0)
  return p.clamp_min(1e-30).log(),h
for checkpoint in ['grasp_vision_v02_flank_margin','grasp_vision_v02_flank_pose']:
 for factors in [[1.],[.9,1.,1.1],[.85,.925,1.,1.075,1.15]]:
  est=VisualGrasp(W/'policies'/checkpoint/'best.pt',W/'grasp_calibration_v02.json');est.model=Ensemble(est.model,factors);scores=[]
  for i,s in enumerate(meta):
   if s['split']!='validation':continue
   a=est.predict(d['rgb'][i],d['depth'][i]);P=np.array(a['hand_target_world']);T=np.array(s['hand_target_world']);scores.append(dict(id=s['id'],accepted=a['accepted'],position_mm=float(np.linalg.norm(P[:3,3]-T[:3,3])*1000),angle_deg=float(np.rad2deg(Rotation.from_matrix(P[:3,:3]@T[:3,:3].T).magnitude()))))
  row=dict(checkpoint=checkpoint,factors=factors,maximum_position_mm=max(x['position_mm'] for x in scores),maximum_angle_deg=max(x['angle_deg'] for x in scores),rows=scores);rows.append(row);print(checkpoint,factors,row['maximum_position_mm'],row['maximum_angle_deg'],flush=True)
(W/'reports/brightness_ensemble_validation.json').write_text(json.dumps(rows,indent=2))
