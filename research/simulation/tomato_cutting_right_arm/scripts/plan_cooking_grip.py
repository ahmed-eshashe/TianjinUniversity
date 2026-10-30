"""Screen wrist orientations for a blade-outward grip without starting Isaac Sim."""
import json
import numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd
from reach_kinematics import ArmKinematics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
k=ArmKinematics(Usd.Stage.Open(str(ROOT/'work/kitchen_reach.usda')))
s=json.load(open(ROOT/'work/grasp_stance_top_deep.json'));k.root[:2,3]+=s['root_offset_xy'];k.root[:3,:3]=Rotation.from_euler('z',s['root_yaw_deg'],degrees=True).as_matrix()
h=np.array([-2.262692645,-1.761800740,.871952299]);results=[]
for yaw in [120,150,90,60,180]:
 r=Rotation.from_euler('z',yaw-180,degrees=True).as_matrix()@np.array(s['orientation'])
 grasp=h-r@np.array([.035,-.015,.020]);q=np.array(s['ready_rad']);solutions=[]
 for pos in [grasp+[0,0,.15],grasp+[0,0,.08],grasp,grasp+[0,0,.03]]:
  q,e,a=k.solve(pos,r,q);solutions.append({'q':q.tolist(),'e':e,'a':a})
 good=all(x['e']<.003 and x['a']<.03 for x in solutions)
 print('YAW',yaw,'reachable',good,'errors',[(round(x['e'],4),round(x['a'],4)) for x in solutions],flush=True)
 candidate={**s,'orientation':r.tolist(),'ready_rad':solutions[0]['q'],'ready_position':(grasp+[0,0,.15]).tolist(),'knife_setup_yaw_deg':yaw,'center_xyz':[.035,-.015,.085],'approach_distance_m':0.,'approach_clearance_m':.08}
 (ROOT/f'work/grasp_stance_cooking_{yaw}_seed.json').write_text(json.dumps(candidate,indent=2))
 results.append({'yaw':yaw,'reachable':good,'solutions':solutions})
(ROOT/'work/cooking_orientation_screen.json').write_text(json.dumps(results,indent=2))
