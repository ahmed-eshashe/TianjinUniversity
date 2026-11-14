from pathlib import Path
import sys,json,numpy as np
from pxr import Usd,UsdGeom
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path.insert(0,str(R/'scripts'))
from reach_kinematics import ArmKinematics,PALM_OFFSET
c=json.loads((W/'scene_plan.json').read_text());p=json.loads(Path(c['source_plan']).read_text());stage=Usd.Stage.Open(c['scene']);kin=ArmKinematics(stage);Q=np.array(c['material_to_world_rotation']);rk=np.array(c['knife_rotation_world']);C=np.array(c['proxy_origin_in_knife_m']);mount=np.array(p['mount_hand_from_knife']);result=[]
for anchor in [np.array([.04,.04,0]),np.array([.04,.07,0]),np.array([.0,.05,0])]:
 q=np.array(c['entry'][0]['q']);worst=0;fail=None
 route=c['entry'][::15]+c['cut'][::80]+c['cut'][-1:]+c['withdraw'][::10]+c['withdraw'][-1:]
 for i,row in enumerate(route):
  proxy=np.array(row['proxy']);origin=anchor+Q@proxy-rk@C;T=np.eye(4);T[:3,:3]=rk;T[:3,3]=origin;hand=T@np.linalg.inv(mount);q,pe,re=kin.solve(hand[:3,3]+hand[:3,:3]@PALM_OFFSET,hand[:3,:3],q);worst=max(worst,pe)
  if pe>1e-4 or re>1e-3:fail=[i,pe,re];break
 result.append(dict(anchor=anchor.tolist(),pass_ik=fail is None,fail=fail,max_error=worst))
print(json.dumps(result,indent=2));(W/'reports/cradle_avoidance_screen.json').write_text(json.dumps(result,indent=2))
cache=UsdGeom.BBoxCache(0,['default','render']);print('post bounds')
for path in p['fixture_paths']:print(path,cache.ComputeWorldBound(stage.GetPrimAtPath(path)).ComputeAlignedRange())
