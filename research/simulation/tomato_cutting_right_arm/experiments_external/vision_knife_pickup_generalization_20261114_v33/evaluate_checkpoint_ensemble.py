"""Development validation only; compare same-target checkpoint averages."""
from pathlib import Path
import json,numpy as np,torch
from torch import nn
from scipy.spatial.transform import Rotation
from visual_grasp_v02 import VisualGrasp
W=Path(__file__).resolve().parent;torch.set_num_threads(2)
d=dict(np.load(W/'grasp_data_v10/labels.npz'));meta=json.loads((W/'grasp_data_v10/metadata.json').read_text())['samples'];rows=[]
class Ensemble(nn.Module):
 def __init__(self,models):super().__init__();self.models=nn.ModuleList(models)
 def forward(self,im):
  predictions=[m(im) for m in self.models]
  p=torch.stack([l.float().flatten(2).softmax(-1).reshape_as(l) for l,h in predictions]).mean(0)
  return p.clamp_min(1e-30).log(),torch.stack([h for l,h in predictions]).mean(0)
for names in [['flank_margin','flank_pose','flank_float'],['flank_float','flank_final'],['flank_margin','flank_pose','flank_float','flank_final']]:
 estimators=[VisualGrasp(W/'policies'/('grasp_vision_v02_'+n)/'best.pt',W/'grasp_calibration_v02.json') for n in names]
 est=estimators[0];est.model=Ensemble([e.model for e in estimators]);scores=[]
 for i,s in enumerate(meta):
  if s['split']!='validation':continue
  a=est.predict(d['rgb'][i],d['depth'][i]);P=np.array(a['hand_target_world']);T=np.array(s['hand_target_world']);scores.append(dict(id=s['id'],accepted=a['accepted'],position_error_mm=float(np.linalg.norm(P[:3,3]-T[:3,3])*1000),orientation_error_deg=float(np.rad2deg(Rotation.from_matrix(P[:3,:3]@T[:3,:3].T).magnitude()))))
 row=dict(checkpoints=names,maximum_position_mm=max(x['position_error_mm'] for x in scores),maximum_angle_deg=max(x['orientation_error_deg'] for x in scores),rows=scores,blank_image_rejected=not est.predict(d['rgb'][0],d['depth'][0],blank=True)['accepted']);rows.append(row);print(names,row['maximum_position_mm'],row['maximum_angle_deg'],flush=True)
p=W/'reports/checkpoint_ensemble_validation.json';assert not p.exists();p.write_text(json.dumps(rows,indent=2))
