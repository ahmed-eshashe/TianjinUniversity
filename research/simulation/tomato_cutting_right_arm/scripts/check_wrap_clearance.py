"""Sample the experimental wrapped-grasp arm path against the parked arm and torso."""
import argparse,json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd
from reach_kinematics import ArmKinematics,PALM_OFFSET
from check_reach_clearance import check
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--seed',required=True);args=parser.parse_args()
seed=json.loads((ROOT/args.seed).read_text());kin=ArmKinematics(Usd.Stage.Open(str(ROOT/'work/kitchen_reach.usda')))
kin.root[:2,3]+=seed['root_offset_xy'];kin.root[:3,:3]=Rotation.from_euler('z',seed['root_yaw_deg'],degrees=True).as_matrix();r=np.array(seed['orientation'])
h=np.array([-2.2627178722644663,-1.7618141868696735,.871988845153742]);grasp=h-r@(np.array(seed['center_xyz'])-PALM_OFFSET);outside=grasp+r[:,1]*seed['approach_distance_m'];q=np.array(seed['ready_rad']);start=kin.pose(q)[0];samples=[]
for target in [outside+[0,0,seed['approach_clearance_m']],outside,grasp,grasp+[0,0,.03]]:
 for a in np.linspace(0,1,11)[1:]:
  q,e,ang=kin.solve(start+(target-start)*a,r,q);overlaps=check(q,True,kin.root)
  samples.append({'position_error_m':e,'rotation_error_rad':ang,'overlaps':overlaps})
 start=target
out={'passed':all(v['position_error_m']<.005 and v['rotation_error_rad']<.04 and not v['overlaps'] for v in samples),'seed':args.seed,'sample_count':len(samples),'samples':samples,'limitations':'Arm versus parked left arm/torso only, open-finger geometry, 2 mm overlap tolerance; separate kitchen approach and runtime contact guards required; not full self-collision validation.'}
(ROOT/'logs/wrap_arm_clearance.json').write_text(json.dumps(out,indent=2));print('PASS',out['passed'],flush=True)
raise SystemExit(0 if out['passed'] else 1)
