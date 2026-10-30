"""Keep the little finger clear during contact handoff; re-screen the entire offline path."""
import json,sys,argparse
from pathlib import Path
import numpy as np
from pxr import Usd,UsdGeom
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from plan_contact_seating import HandGeometry
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--finger',choices=['middle','ring','pinky'],default='pinky');parser.add_argument('--degrees',type=float,default=60);parser.add_argument('--minimum-gap',type=float,default=.001);parser.add_argument('--input',type=Path,default=ROOT/'docs/rl/contact_seating_plan_initial.json');parser.add_argument('--output',type=Path,default=ROOT/'docs/rl/contact_seating_plan.json');args=parser.parse_args()
p=json.loads(args.input.read_text());p['sequencing_input']=str(args.input.resolve());s=Usd.Stage.Open(str(ROOT/'rl/scene/phase3_grasp.usda'));model=HandGeometry(s)
meta=json.loads((ROOT/'rl/scene/manifest.json').read_text());kp=meta['knife_path'];pose=np.array(p['reference_sample']['knife_pose_xyzw']);kr=Rotation.from_quat(pose[3:]).as_matrix();board_hi=np.array(meta['board_world_bounds'])[1]
shapes={}
for part in ['Handle','Blade']:
 v=np.array(UsdGeom.Mesh(s.GetPrimAtPath(kp+'/Collision'+part)).GetPointsAttr().Get());h=ConvexHull(v);shapes[part]=(v[h.vertices],h.equations)
valid=[]
for w in p['waypoints']:
 q=np.array(w['joint_rad']);q[['thumb_yaw','thumb_pitch','index','middle','ring','pinky'].index(args.finger)]=np.deg2rad(args.degrees);r=np.array(w['hand_rotation_in_knife']);t=np.array(w['hand_root_in_knife_m']);links=model.transforms(q);gaps={};bg=[];board=[]
 for name,(v,eq) in model.meshes.items():
  link=links[name];br=r@link[:3,:3];bp=t+r@link[:3,3];vknife=v@br.T+bp
  def sat(part):
   ov,oeq=shapes[part];local=(ov-bp)@br
   return max(float((local@eq[:,:3].T+eq[:,3]).min(0).max()),float((vknife@oeq[:,:3].T+oeq[:,3]).min(0).max()))
  gaps[name]=sat('Handle');bg.append(sat('Blade'));board.append(float((vknife@kr.T+pose[:3])[:,2].min()-board_hi[2]))
 if min(gaps['right_rh_'+args.finger+'_distal'],gaps['right_rh_'+args.finger+'_proximal'])<args.minimum_gap:
  p['status']='Selected digit surface-gap bound; valid prefix only';break
 w.update(joint_rad=q.tolist(),handle_gaps_m=gaps,min_blade_gap_m=min(bg),min_board_gap_m=min(board));valid.append(w)
p['waypoints']=valid;p['preshape_joint_rad']=valid[0]['joint_rad'];p['sequencing_note']=args.finger+' follows a fixed '+str(args.degrees)+' degree acquisition posture; all edited poses rescreened. No physical constraints are created.'
args.output.write_text(json.dumps(p,indent=2));print('Rescreened',len(valid),'waypoints, end fraction',valid[-1]['fraction'],'palm gap',valid[-1]['handle_gaps_m']['right_rh_hand_base_link'])
