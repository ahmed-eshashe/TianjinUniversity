"""Continuous robot reconfiguration above target, followed by screened edge path."""
exec(open(str(__import__('pathlib').Path(__file__).with_name('plan_fitted_continuation.py'))).read().split('poses=np.asarray')[0])
from scipy.spatial.transform import Rotation
source_q=q.copy();source_position=position.copy();source_R=rotation.copy();maximum_free_speed=.04
blade=np.array(json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())['vertices'])
z=np.load(w/'robot_cut13/checkpoints/step_005375.npz');target_top=z['x'][:,2].max()+.0295
minimum_reconfiguration_clearance=1.
def add_q(new_q,stage,pe=0.,re=0.):
 global q,position,rotation,t,minimum_reconfiguration_clearance
 T=k.transforms(new_q)[k.hand_path]@mount;P=T[:3,3];R=T[:3,:3]
 distance=np.linalg.norm(P-position);angle=Rotation.from_matrix(R@rotation.T).magnitude();dt=max(distance/(.04 if stage=='clear_reconfiguration' else .02),angle/.2,np.max(abs(new_q-q))/.4,.002)
 if stage=='clear_reconfiguration':
  cv=(blade@R.T+P-placement)@F;clearance=float(cv[:,2].min()-target_top);minimum_reconfiguration_clearance=min(minimum_reconfiguration_clearance,clearance)
  if clearance<.02:raise ValueError(('Reconfiguration is not clear of target',clearance))
 t+=dt;extra.append(dict(phase='cut',motion_stage=stage,q=new_q.tolist(),tool_origin=P.tolist(),tool_rotation=R.tolist(),time_s=t,position_error=pe,angle_error=re));q=new_q.copy();position=P;rotation=R

def solve_pose(P,R,stage):
 H=R@mount[:3,:3].T;new_q,pe,re=k.solve(P-H@mount[:3,3]+H@PALM_OFFSET,H,q)
 if pe>2e-5 or re>2e-4 or np.max(abs(new_q-q))>.05:raise ValueError(('IK failed',stage,len(extra),pe,re,np.max(abs(new_q-q))))
 add_q(new_q,stage,pe,re)
# First lift along the already reachable direction, retaining the current branch.
for lift in np.linspace(0,.08,161)[1:]:solve_pose(source_position+F@np.array([0,0,lift]),source_R,'lift_clear')
alt=np.array(json.loads((w/'alternate_ik_assessment.json').read_text())['results'][0]['q']);H=rotation@mount[:3,:3].T
alt,pe,re=k.solve(position-H@mount[:3,3]+H@PALM_OFFSET,H,alt)
if pe>2e-5 or re>2e-4:raise ValueError(('Alternate clear posture unavailable',pe,re))
old=q.copy()
for u in np.linspace(0,1,801)[1:]:add_q(old*(1-u)+alt*u,'clear_reconfiguration')
# Return to the same geometric screen's lifted pose, with the arm unwound.
poses=np.asarray(screen['poses']);first=poses[79];endP=F@first[:3]+placement;endR=F@Rotation.from_quat(first[3:]).as_matrix();startP=position.copy();startR=Rotation.from_matrix(rotation);rv=(Rotation.from_matrix(endR)*startR.inv()).as_rotvec()
for u in np.linspace(0,1,101)[1:]:solve_pose(startP*(1-u)+endP*u,(Rotation.from_rotvec(rv*u)*startR).as_matrix(),'return_to_screen')
for p in poses[80:]:solve_pose(F@p[:3]+placement,F@Rotation.from_quat(p[3:]).as_matrix(),'fitted_continuation')
cut_end_time=t;lastP=position.copy();lastR=rotation.copy()
for lift in np.linspace(0,.04,81)[1:]:solve_pose(lastP+F@np.array([0,0,lift]),lastR,'withdraw')
route.update(rows=[p for p in route['rows'] if p['phase']=='entry']+cut+extra,parent_duration_s=parent_duration,duration_s=t,cut_end_time_s=cut_end_time,parent_route=str(source),parent_route_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),transition_checkpoint=str(w/'robot_cut13/checkpoints/step_005375.npz'),purpose='Lift clear, continuously unwind arm within limits, follow deformed interface, withdraw upward',material_law_unchanged=True,kinematic_only=True,robot_dynamics_checked=False,full_slice=False,minimum_reconfiguration_target_clearance_m=minimum_reconfiguration_clearance,geometry_screen=str(w/'heel_rocking_edge_coverage.json'))
(w/'fitted_continuation_plan_v2.json').write_text(json.dumps(route,indent=2));print({key:value for key,value in route.items() if key!='rows'})
