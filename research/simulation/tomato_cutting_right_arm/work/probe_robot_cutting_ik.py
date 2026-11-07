import sys,json,numpy as np
from pxr import Usd
from pathlib import Path
sys.path.insert(0,'scripts');from reach_kinematics import ArmKinematics
s=Usd.Stage.Open('rl/scene/phase3.usda');k=ArmKinematics(s);p=json.load(open('docs/rl/phase3_physics.json'));m=json.load(open('rl/scene/manifest.json'));q=np.array([p['home_rad'][n] for n in k.names]);_,rh=k.pose(q);lo,hi=np.array(m['board_world_bounds']);centre=(lo+hi)/2;centre[2]=hi[2]
v=np.array(json.load(open('runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json'))['vertices']);h=np.array(p['handle_centre_local_m'])
for sign in [1,-1]:
 r=np.array([[0,0,sign],[sign,0,0],[0,1,0]])
 for cy in [0.,-.06,.06]:
  # Blade middle lies over target, lower edge starts 4 cm above tomato.
  origin=centre+[-.0225,cy,.055+.04-v[:,1].min()]-r@np.array([v[:,0].mean(),0.,0.])
  palm=origin+r@h
  a,e,ang=k.solve(palm,rh,q)
  print(sign,cy,palm.tolist(),e,ang,a.tolist())
