"""Original-mesh screening at a recorded, physically attained supported knife pose."""
import itertools,json,sys,argparse
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from reach_kinematics import ArmKinematics
from search_wrap_grasp import geometry
parser=argparse.ArgumentParser();parser.add_argument('--run',default='runs/rl/phase3/in_place_tilt_07');parser.add_argument('--sample',default='after_tilt.json');parser.add_argument('--output',default='supported_wrap_candidates.json');parser.add_argument('--high-clearance',action='store_true');args=parser.parse_args()
run=ROOT/args.run
sample=json.loads((run/args.sample).read_text())
s=Usd.Stage.Open(str(ROOT/'rl/scene/phase3_grasp.usda'));kin=ArmKinematics(s)
meta=json.loads((ROOT/'rl/scene/manifest.json').read_text());lo,hi=np.array(meta['board_world_bounds'])
hv=np.array(UsdGeom.Mesh(s.GetPrimAtPath(meta['knife_path']+'/CollisionHandle')).GetPointsAttr().Get());hc=(hv.min(0)+hv.max(0))/2
hv=hv[ConvexHull(hv).vertices]-hc
pose=np.array(sample['knife_pose_xyzw']);kr=Rotation.from_quat(pose[3:]).as_matrix();handle=kr@hc+pose[:3]
_,initial_r=kin.pose(sample['q_rad'][:7])
grid=np.array(list(itertools.product(np.arange(.005,.056,.005),np.arange(-.04,.041,.01),np.arange(.065,.151,.005))))
results=[];cache={}
for roll in ([-20,-10,0,10,20,30] if args.high_clearance else [0,10,20]):
 r=Rotation.from_rotvec(kr[:,0]*np.deg2rad(roll)).as_matrix()@initial_r
 kv=hv@kr.T@r
 for finger,pitch,yaw in (itertools.product([65,75,85],[5,10,15,18],[40,50]) if args.high_clearance else itertools.product([75,85],[20,30],[50])):
  gaps=[];heights=[];names=[]
  for name,v in geometry(finger,yaw,pitch):
   key=(roll,name,pitch,yaw) if 'thumb' in name else (roll,name,finger if 'hand_base' not in name else 0)
   if key not in cache:
    eq=ConvexHull((v[:,None,:]-kv[None,:,:]).reshape(-1,3)).equations
    cache[key]=((grid@eq[:,:3].T+eq[:,3]).max(1),(v@r[2]).min()-grid@r[2]+handle[2]-hi[2])
   gap,height=cache[key];gaps.append(gap);heights.append(height);names.append(name)
  gaps=np.array(gaps);heights=np.array(heights);ix=lambda n:names.index('right_rh_'+n)
  fg=np.array([np.minimum(abs(gaps[ix(f+'_proximal')]),abs(gaps[ix(f+'_distal')])) for f in ['index','middle','ring','pinky']])
  palm=gaps[ix('hand_base_link')];thumb=gaps[ix('thumb_distal')]
  cost=(np.sort(fg,axis=0)[:3]**2).sum(0)*1e5+(palm**2+thumb**2)*1e5
  cost+=np.maximum(-.001-gaps,0).sum(0)*1e5
  cost+=np.maximum(.002-heights.min(0),0)*1e5
  j=cost.argmin()
  results.append({'score':float(cost[j]),'roll_delta_deg':roll,'finger_deg':finger,'thumb_pitch_deg':pitch,'thumb_yaw_deg':yaw,
   'handle_in_hand_m':grid[j].tolist(),'hand_rotation_world':r.tolist(),'minimum_board_gap_m':float(heights[:,j].min()),
   'gaps_m':dict(zip(names,gaps[:,j].tolist()))})
for c in results:
 g=c['gaps_m'];finger_gaps=[min(abs(g['right_rh_'+f+'_proximal']),abs(g['right_rh_'+f+'_distal'])) for f in ['index','middle','ring','pinky']]
 c['predicted_simultaneous_contacts']=bool(c['minimum_board_gap_m']>=.002 and min(g.values())>=-.001 and abs(g['right_rh_hand_base_link'])<=.003 and abs(g['right_rh_thumb_distal'])<=.003 and sum(d<=.003 for d in finger_gaps)>=3)
results.sort(key=lambda c:c['score'])
output={'scope':'Offline mesh proposals only; not physical grasp validation','source_run':str(run.relative_to(ROOT)),
 'predicted_wrap_found':any(c['predicted_simultaneous_contacts'] for c in results),
 'supported_handle_world_m':handle.tolist(),'supported_sample':sample,'candidates':results[:20]}
(ROOT/'docs/rl'/args.output).write_text(json.dumps(output,indent=2))
print(json.dumps(results[:3],indent=2))
