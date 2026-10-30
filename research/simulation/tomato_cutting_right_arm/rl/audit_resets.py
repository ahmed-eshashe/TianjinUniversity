"""Quantify geometrically valid flat resets and kinematic pre-approach coverage, without simulation."""
import json
from pathlib import Path
import sys
import numpy as np
from pxr import Usd,UsdGeom
from scipy.spatial.transform import Rotation
from reset_sampler import FlatResetSampler

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from reach_kinematics import ArmKinematics

def main():
    stage=Usd.Stage.Open(str(ROOT/'rl/scene/phase3.usda'))
    physics=json.loads((ROOT/'docs/rl/phase3_physics.json').read_text())
    meta=json.loads((ROOT/'rl/scene/manifest.json').read_text())
    points=np.array(UsdGeom.Mesh(stage.GetPrimAtPath(meta['knife_path'])).GetPointsAttr().Get())
    sampler=FlatResetSampler(points,meta['board_world_bounds'])
    cases=sampler.sample(1000)
    k=ArmKinematics(stage);home=physics['home_rad'];seed=np.array([home[n] for n in k.names])
    orientation=np.array(json.loads((ROOT/'work/grasp_stance_cooking_clear.json').read_text())['orientation'])
    handle=np.array(physics['handle_centre_local_m'])
    approaches=[]
    for case in cases[::50]:
        pose=np.array(case['pose_xyzw']);position=Rotation.from_quat(pose[3:]).apply(handle)+pose[:3]
        target=position+np.array([0,0,.14])
        q,error,angle=k.solve(target,orientation,seed)
        approaches.append({'reset':case,'target_palm_world_m':target.tolist(),'q_rad':q.tolist(),
                           'position_error_m':error,'orientation_error_rad':angle,
                           'kinematically_solved':bool(error<.005 and angle<.04),
                           'collision_checked':False})
    xs=np.array([x['centre_xy'] for x in cases]);lo,hi=np.array(meta['board_world_bounds'])
    report={'passed_geometry':all(c['valid'] and c['minimum_edge_margin_m']>=.02-1e-6 for c in cases),
        'sample_count':len(cases),'rejected_proposals':sampler.rejected,'centre_xy_min_m':xs.min(0).tolist(),
        'centre_xy_max_m':xs.max(0).tolist(),'board_dimensions_xy_m':(hi-lo)[:2].tolist(),
        'knife_dimensions_local_m':np.ptp(points,axis=0).tolist(),'yaw_range_rad':[min(c['yaw_rad'] for c in cases),max(c['yaw_rad'] for c in cases)],
        'preapproach_ik_solved':sum(x['kinematically_solved'] for x in approaches),'preapproach_ik_tested':len(approaches),
        'preapproaches':approaches,'physical_grasp_reachability_established':False,
        'limitations':['Full-footprint geometry limits positions/yaws: knife is almost as long as board',
                       'IK only establishes pre-approach geometry, not a collision-free route or flat pickup',
                       'Do not treat sampling rejection as a learned-policy failure or claim arbitrary full-board reachability']}
    (ROOT/'docs/rl/phase3_reset_coverage.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='preapproaches'},indent=2))

if __name__=='__main__':main()
