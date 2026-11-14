"""Image-only validation audit; held-out physical test episodes remain unseen."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from scipy.spatial.transform import Rotation
from visual_grasp_v03 import VisualGrasp
W=Path(__file__).resolve().parent
a=argparse.ArgumentParser();a.add_argument('--data',type=Path,required=True);a.add_argument('--checkpoint',type=Path,required=True);a.add_argument('--output',type=Path,required=True);args=a.parse_args()
assert not args.output.exists()
d=dict(np.load(args.data/'labels.npz'));metadata=json.loads((args.data/'metadata.json').read_text());est=VisualGrasp(args.checkpoint,W/'grasp_calibration_v02.json');rows=[]
for i,sample in enumerate(metadata['samples']):
 if sample['split']!='validation':continue
 prediction=est.predict(d['rgb'][i],d['depth'][i]);H=np.array(prediction['hand_target_world']);truth=np.array(sample['hand_target_world'])
 rows.append(dict(id=sample['id'],family=sample['family'],face=sample['face'],accepted=prediction['accepted'],reasons=prediction['reasons'],position_error_mm=float(np.linalg.norm(H[:3,3]-truth[:3,3])*1000),height_error_mm=float(abs(H[2,3]-truth[2,3])*1000),orientation_error_deg=float(np.rad2deg(Rotation.from_matrix(H[:3,:3]@truth[:3,:3].T).magnitude())),prediction=prediction))
blank=est.predict(d['rgb'][0],d['depth'][0],blank=True)
result=dict(scope='Offline validation images only; not pickup success',checkpoint=str(args.checkpoint.resolve()),checkpoint_sha256=hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(),test_images_consumed=0,blank_image_rejected=not blank['accepted'],rows=rows)
args.output.write_text(json.dumps(result,indent=2))
print(json.dumps(dict(validation_count=len(rows),accepted=sum(x['accepted'] for x in rows),maximum_position_error_mm=max(x['position_error_mm'] for x in rows),maximum_orientation_error_deg=max(x['orientation_error_deg'] for x in rows),blank_rejected=not blank['accepted'])))
