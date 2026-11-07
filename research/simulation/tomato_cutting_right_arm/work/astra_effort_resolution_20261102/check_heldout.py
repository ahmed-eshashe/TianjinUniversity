from pathlib import Path
import numpy as np,json
from tomato_tgs_feedforward_readback import FeedforwardReadback
R=Path(__file__).resolve().parents[2];run=R/'runs/native/moving_contact_c1_down_20261102_01';bind=np.load(run/'robot_energy_binding_inputs.npz');scope=json.loads((run/'robot_energy_binding_scope.json').read_text());order=json.loads((R/'runs/native/motor_effort_capture_20261102_01/ordering.json').read_text());snap=json.loads((R/'runs/native/robot_wrench_com_trace_20261102_01/robot_kinematic_snapshot_com_frame.json').read_text());f=FeedforwardReadback(scope['body_names'],order['joint_names'],snap,bind['mass'],bind['inertia_com_link_axes'],bind['armature']);arms=[i for i,n in enumerate(order['joint_names'])if '_AR5_'in n];errors=[];rawerrors=[];records=[]
for label in ['no_feedback','feedback','replay','clear']:
 p=run/(label+'_robot_audit.json')
 if not p.exists():continue
 rows=json.loads(p.read_text())
 for i,row in enumerate(rows):
  z=np.load(run/f'{label}_robot_interval{i}.npz');tau=np.array(row['robot_audit']['commanded_effort_nm']);dt=float(z['dt']);res=f.calculate(z['robot_body_link_pose_before'],z['robot_body_com_pose_before'],z['robot_body_link_pose_after'],z['robot_body_com_pose_after'],tau,z['robot_incoming_joint_wrench_child_frame_backend_order']);rotor=bind['armature']*(np.array(row['qd_after'])-np.array(row['qd_before']))/dt;pred=res['projected_corrected']+rotor;err=pred-tau;errors.append(err);raw=np.zeros(36)
  for bi,qi in f.qi.items():raw[qi]=z['robot_incoming_joint_wrench_child_frame_backend_order'][bi,3:]@f.axes[bi]
  rawerrors.append(raw+rotor-tau);records.append(dict(case=label,step=i,error=err.tolist()))
a=np.array(errors);b=np.array(rawerrors);print('intervals',len(a),'max arm raw',abs(b[:,arms]).max(),'corrected',abs(a[:,arms]).max(),'all',abs(a).max());print('arm errors',abs(a[:,arms]).max(axis=0));(R/'work/astra_effort_resolution_20261102/heldout_initial.json').write_text(json.dumps(dict(intervals=len(a),max_raw_arm=float(abs(b[:,arms]).max()),max_corrected_arm=float(abs(a[:,arms]).max()),records=records),indent=2)+'\n')
for label in sorted(set(r['case']for r in records)):
 rows=json.loads((run/(label+'_robot_audit.json')).read_text());c=rawc=known=0.;maxerr=0.
 for row,record in zip(rows,[x for x in records if x['case']==label]):
  i=record['step'];z=np.load(run/f'{label}_robot_interval{i}.npz');dt=float(z['dt'].item());v=.5*(np.array(row['qd_after'])+np.array(row['qd_before']));tau=np.array(row['robot_audit']['commanded_effort_nm']);known+=dt*tau@v;c+=dt*np.array(record['error'])@v;maxerr=max(maxerr,abs(c))
 print(label,'known motor estimator J',known,'cumulative corrected-estimator error J',c,'maximum accumulated error',maxerr)
