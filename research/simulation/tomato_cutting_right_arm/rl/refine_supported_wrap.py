"""Refine the near-contact posture with independent finger angles; offline proposal only."""
import itertools,json,sys
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from search_wrap_grasp import geometry
p=json.loads((ROOT/'docs/rl/supported_wrap_high_clearance.json').read_text());base=p['candidates'][0];r=np.array(base['hand_rotation_world']);sample=p['supported_sample'];pose=np.array(sample['knife_pose_xyzw']);kr=Rotation.from_quat(pose[3:]).as_matrix()
s=Usd.Stage.Open(str(ROOT/'rl/scene/phase3_grasp.usda'));m=json.loads((ROOT/'rl/scene/manifest.json').read_text());hv=np.array(UsdGeom.Mesh(s.GetPrimAtPath(m['knife_path']+'/CollisionHandle')).GetPointsAttr().Get());hc=(hv.min(0)+hv.max(0))/2;kv=(hv[ConvexHull(hv).vertices]-hc)@kr.T@r
handle=kr@hc+pose[:3];board_hi=np.array(m['board_world_bounds'])[1]
centre=np.array(base['handle_in_hand_m']);grid=np.array(list(itertools.product(*[np.arange(c-.004,c+.0041,.001) for c in centre])))
fingers=['index','middle','ring','pinky'];cache={};results=[]
for angles,pitch,yaw in itertools.product(itertools.product([60,65,70],repeat=4),[15,17,18],[40,45,50]):
 fd=dict(zip(fingers,angles));gaps=[];heights=[];names=[]
 for name,v in geometry(fd,yaw,pitch):
  part=name.removeprefix('right_rh_').split('_')[0];key=(name,pitch,yaw) if part=='thumb' else (name,fd.get(part,0))
  if key not in cache:
   eq=ConvexHull((v[:,None,:]-kv[None,:,:]).reshape(-1,3)).equations
   cache[key]=((grid@eq[:,:3].T+eq[:,3]).max(1),(v@r[2]).min()-grid@r[2]+handle[2]-board_hi[2])
  gap,height=cache[key];gaps.append(gap);heights.append(height);names.append(name)
 gaps=np.array(gaps);heights=np.array(heights);ix=lambda n:names.index('right_rh_'+n)
 fg=np.array([np.minimum(abs(gaps[ix(f+'_proximal')]),abs(gaps[ix(f+'_distal')])) for f in fingers]);palm=gaps[ix('hand_base_link')];thumb=gaps[ix('thumb_distal')]
 cost=(np.sort(fg,axis=0)[:3]**2).sum(0)*1e5+(palm**2+thumb**2)*1e5
 cost+=np.maximum(-.001-gaps,0).sum(0)*1e5+np.maximum(.002-heights.min(0),0)*1e5
 j=cost.argmin();results.append({'score':float(cost[j]),'finger_degrees':fd,'thumb_pitch_deg':pitch,'thumb_yaw_deg':yaw,
  'handle_in_hand_m':grid[j].tolist(),'hand_rotation_world':r.tolist(),'minimum_board_gap_m':float(heights[:,j].min()),'gaps_m':dict(zip(names,gaps[:,j].tolist()))})
for c in results:
 g=c['gaps_m'];fg=[min(abs(g['right_rh_'+f+'_proximal']),abs(g['right_rh_'+f+'_distal'])) for f in fingers]
 c['predicted_simultaneous_contacts']=bool(c['minimum_board_gap_m']>=.002 and min(g.values())>=-.001 and abs(g['right_rh_hand_base_link'])<=.003 and abs(g['right_rh_thumb_distal'])<=.003 and sum(d<=.003 for d in fg)>=3)
results.sort(key=lambda c:(not c['predicted_simultaneous_contacts'],c['score']))
out={'scope':'Independent original-mesh near-contact proposals; no physical validation','source_run':p['source_run'],'supported_sample':sample,'predicted_wrap_found':any(c['predicted_simultaneous_contacts'] for c in results),'candidates':results[:20]}
(ROOT/'docs/rl/refined_supported_wrap.json').write_text(json.dumps(out,indent=2));print(json.dumps(results[:2],indent=2))
