"""Build a prospective robot path from a read-only blade-edge geometry screen."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'scripts'))
from reach_kinematics import ArmKinematics,PALM_OFFSET
screen=json.loads((w/'heel_rocking_edge_coverage.json').read_text())
if not screen['all_reached']:raise ValueError('Geometric edge coverage is incomplete; no robot plan generated')
source=w/'clear_entry_robot_plan_v8.json';route=json.loads(source.read_text());plan=json.loads((r/'work/backward_elbow_20261105/plan.json').read_text())
k=ArmKinematics(Usd.Stage.Open(plan['scene']));k.upper[5]=.85;k.lower[6]=-.85
mount=np.asarray(plan['mount_hand_from_knife']);F=np.asarray(route['target_rotation']);placement=np.asarray(route['target_translation'])
cut=[p for p in route['rows'] if p['phase']=='cut'];parent_duration=abs(cut[-1]['tool_origin'][2]-cut[0]['tool_origin'][2])/.02
for i,p in enumerate(cut):p['time_s']=parent_duration*i/(len(cut)-1);p['motion_stage']='original_cut'
q=np.array(cut[-1]['q']);position=np.array(cut[-1]['tool_origin']);rotation=np.array(cut[-1]['tool_rotation']);t=parent_duration;extra=[]
poses=np.asarray(screen['poses']);end_cut_count=len(poses)
# Withdraw vertically instead of retracing the blade along the board.
last=poses[-1].copy();poses=np.r_[poses,np.array([last+np.r_[0,0,h,0,0,0,0] for h in np.linspace(0,.04,81)[1:]])]
for i,p in enumerate(poses):
 desired=F@p[:3]+placement;R=F@Rotation.from_quat(p[3:]).as_matrix();hand_R=R@mount[:3,:3].T
 previous=q.copy();q,pe,re=k.solve(desired-hand_R@mount[:3,3]+hand_R@PALM_OFFSET,hand_R,q)
 if pe>2e-5 or re>2e-4 or np.max(abs(q-previous))>.05:
  (w/'fitted_plan_ik_failure.json').write_text(json.dumps(dict(index=i,position_error=pe,rotation_error=re,q=q.tolist(),previous_q=previous.tolist(),lower=k.lower.tolist(),upper=k.upper.tolist(),desired=desired.tolist(),hand_rotation=hand_R.tolist()),indent=2))
  raise ValueError(('Continuation IK failed',i,pe,re,np.max(abs(q-previous))))
 distance=np.linalg.norm(desired-position);angle=Rotation.from_matrix(R@rotation.T).magnitude()
 # Keep conservative 20 mm/s contact motion and <=0.2 rad/s rotation.
 t+=max(distance/.02,angle/.2,.002)
 extra.append(dict(phase='cut',motion_stage='withdraw' if i>=end_cut_count else 'fitted_continuation',q=q.tolist(),tool_origin=desired.tolist(),tool_rotation=R.tolist(),time_s=t,position_error=pe,angle_error=re))
 position=desired;rotation=R
 if i==end_cut_count-1:cut_end_time=t
route.update(rows=[p for p in route['rows'] if p['phase']=='entry']+cut+extra,parent_duration_s=parent_duration,duration_s=t,cut_end_time_s=cut_end_time,parent_route=str(source),parent_route_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),transition_checkpoint=str(w/'robot_cut13/checkpoints/step_005375.npz'),purpose='Follow the deformed interface with the actual blade heel, then withdraw upward',material_law_unchanged=True,kinematic_only=True,robot_dynamics_checked=False,full_slice=False,geometry_screen=str(w/'heel_rocking_edge_coverage.json'))
(w/'fitted_continuation_plan_v1.json').write_text(json.dumps(route,indent=2));print({key:value for key,value in route.items() if key!='rows'})
