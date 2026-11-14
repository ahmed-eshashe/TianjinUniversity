"""Necessary static point-contact equilibrium screen, not a retention certificate."""
from pathlib import Path
import sys,json,numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import linprog
from pxr import Usd
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path[:0]=[str(R/'scripts'),str(R/'rl')];from plan_contact_seating import HandGeometry
m=HandGeometry(Usd.Stage.Open(str(W/'head_vision_pickup_v02.usda')));results=[]
for run in ['pickup01','pickup02','pickup03','pickup05']:
 x=json.loads((W/'runs'/run/'before_lift.json').read_text());cs=x['contacts'];hp=np.array(x['hand_pose']);hr=Rotation.from_quat(hp[3:]).as_matrix();kp=np.array(x['knife_pose']);kr=Rotation.from_quat(kp[3:]).as_matrix();com=kp[:3]+kr@np.array([-.1909371633,.005026592,.0013825955]);q=np.array(x['q'])[[19,29,20,21,22,23]];trans=m.transforms(q);wrenches=[];efforts=[];groups=[]
 for ci,c in enumerate(cs):
  name='right_rh_'+c['part']+'_distal';T=trans[name];br=hr@T[:3,:3];bp=hp[:3]+hr@T[:3,3];point=np.array(c['point']);local=br.T@(point-bp);J=[]
  for j in range(6):
   qq=q.copy();qq[j]+=1e-5;t=m.transforms(qq)[name];new=hp[:3]+hr@(t[:3,3]+t[:3,:3]@local);J.append((new-point)/1e-5)
  J=np.array(J).T;n=-np.array(c['normal']);t=np.cross(n,[0,0,1]);t/=np.linalg.norm(t);b=np.cross(n,t)
  for angle in np.linspace(0,2*np.pi,16,endpoint=False):
   tangent=t*np.cos(angle)+b*np.sin(angle)
   f=n+.6*tangent;wrenches.append(np.r_[f,np.cross(point-com,f)]);efforts.append(-J.T@f);groups.append(ci)
 if not cs:continue
 A=np.array(wrenches).T;E=np.array(efforts).T;caps=np.array([1,1,.3,.3,.3,.3]);res=linprog(np.ones(len(groups)),A_ub=np.r_[E,-E],b_ub=np.r_[caps,caps],A_eq=A,b_eq=[0,0,.25*9.81,0,0,0],bounds=(0,None),method='highs');out=dict(run=run,feasible=bool(res.success),message=res.message,scope='Static point-contact friction pyramid mu=.6; no soft-contact torsion. Necessary, not sufficient. Joint effort bounds only; no learned policy.')
 unbounded=linprog(np.ones(len(groups)),A_eq=A,b_eq=[0,0,.25*9.81,0,0,0],bounds=(0,None),method='highs');out['without_motor_caps_feasible']=bool(unbounded.success)
 if unbounded.success:out['unbounded_required_effort_Nm']=(E@unbounded.x).tolist();out['unbounded_normals_N']=[float(sum(unbounded.x[j] for j,g in enumerate(groups) if g==i)) for i in range(len(cs))]
 if res.success:out.update(normal_by_contact_N=[float(sum(res.x[j] for j,g in enumerate(groups) if g==i)) for i in range(len(cs))],hand_effort_Nm=(E@res.x).tolist())
 angles=[]
 for angle in [-90,-75,-60,-45,-30,0,30,45,60,75,90]:
  rot=kr@Rotation.from_euler('y',angle,degrees=True).as_matrix()@kr.T;rhs=np.r_[rot.T@np.array([0,0,.25*9.81]),[0,0,0]];fit=linprog(np.ones(len(groups)),A_ub=np.r_[E,-E],b_ub=np.r_[caps,caps],A_eq=A,b_eq=rhs,bounds=(0,None),method='highs');angles.append(dict(pitch_degrees=angle,feasible=bool(fit.success)))
 out['orientation_screen']=angles;results.append(out)
(W/'reports/grasp_wrench_screen.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
