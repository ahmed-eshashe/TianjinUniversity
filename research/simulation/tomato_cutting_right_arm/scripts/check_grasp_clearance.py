"""Sample the validated arm route against the parked left arm and torso."""
import argparse,json
from pathlib import Path
import numpy as np
from pxr import Usd
from scipy.spatial.transform import Rotation
from reach_kinematics import ArmKinematics
from check_reach_clearance import check
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--report',default='logs/kitchen_grasp_validation_report.json')
args=parser.parse_args()
evidence=json.loads((ROOT/args.report).read_text())
cfg=evidence.get('configuration') or json.loads((ROOT/'work/validated_grasp_configuration.json').read_text())
seed=json.loads((ROOT/cfg['stance_seed']).read_text());kin=ArmKinematics(Usd.Stage.Open(str(ROOT/'work/kitchen_reach.usda')))
kin.root[:2,3]+=seed['root_offset_xy'];kin.root[:3,:3]=Rotation.from_euler('z',seed['root_yaw_deg'],degrees=True).as_matrix()
rot=np.array(seed['orientation']);q=np.array(seed['ready_rad']);start=kin.pose(q)[0]
if 'initial_handle_world_m' in evidence:h=np.array(evidence['initial_handle_world_m'])
else:
 log=(ROOT/'logs/grasp_trial53.log').read_text().splitlines();plan=json.loads(next(x.removeprefix('REACH_PLAN_READY ') for x in log if x.startswith('REACH_PLAN_READY ')));h=np.array(plan['handle'])
grasp=h-rot@np.array([cfg['palm_height'],0,cfg['finger_offset']])+rot[:,1]*cfg['handle_offset']
approach=grasp-rot[:,'xyz'.index(cfg['approach_axis'])]*cfg['insert_distance'] if cfg['insert_distance'] else grasp+np.array([0,0,cfg['approach_clearance']])
targets=([approach+[0,0,cfg['approach_clearance']]] if cfg['approach_axis']=='y' else [])+[approach,grasp,grasp+[0,0,cfg['lift_height']]];samples=[]
for target in targets:
 count=20
 for alpha in np.linspace(0,1,count+1)[1:]:
  q,e,a=kin.solve(start+(target-start)*alpha,rot,q)
  overlaps=check(q,True,kin.root)
  samples.append({'q_rad':q.tolist(),'position_error_m':e,'rotation_error_rad':a,'overlaps':overlaps})
 start=target
report={'passed':all(not x['overlaps'] and x['position_error_m']<.005 and x['rotation_error_rad']<.04 for x in samples),'source_report':args.report,'sample_count':len(samples),'samples':samples,'limitations':'Right versus parked left and torso only; shoulder attachment excluded; 2 mm overlap tolerance; hand open in screen. Runtime monitors kitchen contact; robot self-collision remains disabled.'}
(ROOT/'logs/kitchen_grasp_stance_clearance.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'passed':report['passed'],'samples':len(samples),'overlaps':[x['overlaps'] for x in samples if x['overlaps']]}))
raise SystemExit(0 if report['passed'] else 1)
