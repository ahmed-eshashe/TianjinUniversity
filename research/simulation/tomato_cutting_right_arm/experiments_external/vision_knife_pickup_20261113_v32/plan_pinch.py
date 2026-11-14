"""Fit handle-side thumb and finger contacts geometrically; no physics success claim."""
from pathlib import Path
import sys,json,numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
from pxr import Usd,UsdGeom
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path[:0]=[str(R/'scripts'),str(R/'rl')]
from plan_contact_seating import HandGeometry
s=Usd.Stage.Open(str(W/'head_vision_pickup_v02.usda'));m=HandGeometry(s);report=json.loads((W/'reports/initial_grasp_reach.json').read_text());ref=np.array(report[-1]['hand_from_knife']);r0=ref[:3,:3];t0=ref[:3,3];pose=np.array(json.loads((W/'runs/camera01/result.json').read_text())['knife_pose']);kr=Rotation.from_quat(pose[3:]).as_matrix();handle=np.array(UsdGeom.Mesh(s.GetPrimAtPath('/dual_ar5_o6/MountedKnife/CollisionHandle')).GetPointsAttr().Get());blade=np.array(UsdGeom.Mesh(s.GetPrimAtPath('/dual_ar5_o6/MountedKnife/CollisionBlade')).GetPointsAttr().Get());hh=ConvexHull(handle);bh=ConvexHull(blade);handle=handle[hh.vertices];blade=blade[bh.vertices];names=list(m.meshes)
prior=json.loads((W/'reports/pinch_geometry01.json').read_text());P=np.array(prior['hand_from_knife']);initial=np.r_[P[:3,3],Rotation.from_matrix(P[:3,:3]@r0.T).as_rotvec(),prior['hand_joint_rad']]
# Each fingertip contacts an opposing handle side. Thumb supports on the near side;
# multiple fingertips provide a longitudinal support span and resist knife pitching.
def state(x):
 r=Rotation.from_rotvec(x[3:6]).as_matrix()@r0;t=x[:3];tr=m.transforms(x[6:]);gaps={};bg=[];board=[];centers={}
 for name,(v,eq) in m.meshes.items():
  T=tr[name];br=r@T[:3,:3];bp=t+r@T[:3,3];vk=v@br.T+bp;centers[name]=vk.mean(0)
  def gap(other,othereq):
   ov=(other-bp)@br
   return max(float((ov@eq[:,:3].T+eq[:,3]).min(0).max()),float((vk@othereq[:,:3].T+othereq[:,3]).min(0).max()))
  gaps[name]=gap(handle,hh.equations);bg.append(gap(blade,bh.equations));board.append((vk@kr.T+pose[:3])[:,2].min())
 return r,gaps,np.array(bg),np.array(board),centers
low=np.r_[t0-.04,[-.6,-.6,-.6],[.5,.02,.4,.4,.4,.4]];high=np.r_[t0+.04,[.6,.6,.6],[1.2,.31,1.2,1.2,1.2,1.2]]
parts=['thumb','index','middle','ring']
def fun(x):
 r,g,bg,board,c=state(x);distal=[g['right_rh_'+p+'_distal'] for p in parts]
 return np.r_[(np.array(distal)-.0007)*1500,np.minimum(np.array(list(g.values()))-.0003,0)*4000,np.minimum(bg-.004,0)*5000,np.minimum(board-.001,0)*3000,(x[:3]-t0)*6,x[3:6]*.1,(x[6:]-initial[6:])*.02,np.array([c['right_rh_'+p+'_distal'][2]-.007 for p in parts])*200]
sol=least_squares(fun,initial,bounds=(low,high),max_nfev=120,ftol=1e-9,xtol=1e-9,gtol=1e-8);x=sol.x;r,g,bg,board,c=state(x);rel=np.eye(4);rel[:3,:3]=r;rel[:3,3]=x[:3];K=np.eye(4);K[:3,:3]=kr;K[:3,3]=pose[:3];T=K@rel;kin=m.kin;cc=json.loads((W/'scene_config.json').read_text());q,pe,re=kin.solve(T[:3,3]+r@np.array([0,0,.065]) if False else T[:3,3]+T[:3,:3]@np.array([0,0,.065]),T[:3,:3],report[-1]['q'])
out=dict(scope='Unvalidated geometric pinch candidate only',hand_from_knife=rel.tolist(),hand_joint_rad=x[6:].tolist(),q=q.tolist(),position_error_m=pe,orientation_error_rad=re,handle_gaps_m=g,blade_gaps_m=bg.tolist(),board_gaps_m=board.tolist(),cost=float(sol.cost),nfev=sol.nfev)
(W/'reports/pinch_geometry02.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
