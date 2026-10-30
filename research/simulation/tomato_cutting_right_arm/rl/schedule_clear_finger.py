"""Plan a collision-clear little-finger schedule without changing pinch contact anchors."""
import json,argparse,numpy as np
from pathlib import Path
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom
from plan_contact_seating import HandGeometry
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--finger',choices=['middle','ring','pinky'],default='pinky');parser.add_argument('--min-deg',type=int,default=60);parser.add_argument('--input',type=Path,default=ROOT/'docs/rl/contact_seating_plan_initial.json');parser.add_argument('--output',type=Path,default=ROOT/'docs/rl/contact_seating_plan_pinky_schedule.json');args=parser.parse_args()
p=json.loads(args.input.read_text());p['sequencing_input']=str(args.input.resolve());s=Usd.Stage.Open(str(ROOT/'rl/scene/phase3_grasp.usda'));model=HandGeometry(s)
meta=json.loads((ROOT/'rl/scene/manifest.json').read_text());pose=np.array(p['reference_sample']['knife_pose_xyzw']);kr=Rotation.from_quat(pose[3:]).as_matrix();top=np.array(meta['board_world_bounds'])[1,2];shapes={}
for part in ['Handle','Blade']:
 v=np.array(UsdGeom.Mesh(s.GetPrimAtPath(meta['knife_path']+'/Collision'+part)).GetPointsAttr().Get());h=ConvexHull(v);shapes[part]=(v[h.vertices],h.equations)
rows=[]
for w in p['waypoints']:
 r=np.array(w['hand_rotation_in_knife']);t=np.array(w['hand_root_in_knife_m']);row={}
 for degrees in range(args.min_deg,86):
  q=np.array(w['joint_rad']);q[['thumb_yaw','thumb_pitch','index','middle','ring','pinky'].index(args.finger)]=np.deg2rad(degrees);links=model.transforms(q);gaps={};bg=[];bo=[]
  for name in ['right_rh_'+args.finger+'_proximal','right_rh_'+args.finger+'_distal']:
   v,eq=model.meshes[name];link=links[name];br=r@link[:3,:3];bp=t+r@link[:3,3];vk=v@br.T+bp
   def sat(part):
    ov,oeq=shapes[part];local=(ov-bp)@br
    return max(float((local@eq[:,:3].T+eq[:,3]).min(0).max()),float((vk@oeq[:,:3].T+oeq[:,3]).min(0).max()))
   gaps[name]=sat('Handle');bg.append(sat('Blade'));bo.append(float((vk@kr.T+pose[:3])[:,2].min()-top))
  if min(gaps.values())>=.0015 and min(bg)>=.002 and min(bo)>=.002:row[degrees]=(gaps,min(bg),min(bo))
 if not row:break
 rows.append(row)
# Choose a continuous path backwards so folding starts before a collision would occur.
while rows:
 selected=[min(rows[-1])];ok=True
 for row in reversed(rows[:-1]):
  choices=[d for d in row if abs(d-selected[-1])<=3]
  if not choices:ok=False;break
  selected.append(min(choices))
 if ok:break
 rows.pop()
if not rows:raise RuntimeError('No clear little-finger schedule')
selected=selected[::-1];valid=[]
for w,row,d in zip(p['waypoints'],rows,selected):
 w['joint_rad'][['thumb_yaw','thumb_pitch','index','middle','ring','pinky'].index(args.finger)]=float(np.deg2rad(d));g,bg,bo=row[d];w['handle_gaps_m'].update(g);w['min_blade_gap_m']=min(w['min_blade_gap_m'],bg);w['min_board_gap_m']=min(w['min_board_gap_m'],bo);valid.append(w)
p['preshape_parts']=sorted(set(p.get('preshape_parts',['pinky'])+[args.finger]))
p.update(waypoints=valid,preshape_joint_rad=valid[0]['joint_rad'],sequencing_note='Selected fingers follow rescreened clearance schedules; no physical constraints are created.')
args.output.write_text(json.dumps(p,indent=2));print('Schedule',len(valid),'waypoints',args.finger+' degrees',selected,'end fraction',valid[-1]['fraction'])
