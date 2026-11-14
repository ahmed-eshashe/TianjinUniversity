"""Independent saved-image causal check; not a physical robustness claim."""
from pathlib import Path
import json
import numpy as np
import torch
from PIL import Image
from scipy.spatial.transform import Rotation
from visual_grasp import VisualGrasp
W=Path(__file__).resolve().parent;torch.set_num_threads(2)
v=VisualGrasp(W/'policies/handle_vision_v01/best.pt',W/'hybrid_calibration_v01.json')
rows=[]
for case in ['validation_000','validation_001','validation_002']:
 p=W/'datasets/hybrid_v01_validation'/case
 rgb=np.array(Image.open(p/'vision_input_rgb.png'));depth=np.load(p/'vision_input_depth.npy')
 result=v.predict(rgb,depth)
 saved=json.loads((p/'visual_prediction.json').read_text())
 assert np.max(np.abs(np.array(saved['hand_target_world'])-result['hand_target_world']))<1e-6
 blank=v.predict(rgb,depth,blank=True)
 rows.append(dict(case=case,prediction=result,blank_rejected=not blank['accepted']))
A=np.array(rows[0]['prediction']['hand_target_world']);B=np.array(rows[1]['prediction']['hand_target_world'])
result=dict(inputs=['actual saved head RGB-D','fixed calibration'],no_episode_or_reset_input=True,
 recomputation_matches_live=True,blank_rejected_all=all(r['blank_rejected'] for r in rows),
 mismatched_image_target_shift_m=float(np.linalg.norm(A[:3,3]-B[:3,3])),
 mismatched_image_orientation_shift_deg=float(np.rad2deg(Rotation.from_matrix(A[:3,:3]@B[:3,:3].T).magnitude())),
 scope='Swapping the visual input changes the grasp target. This is an inference dependency check, not a live wrong-image pickup or real-world safety guarantee.',rows=rows)
(W/'reports/hybrid_visual_dependency.json').write_text(json.dumps(result,indent=2));print({k:x for k,x in result.items() if k!='rows'})
