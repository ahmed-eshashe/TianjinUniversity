"""Independent native signed-load and actual-q coasting interface readback."""
from pathlib import Path
import hashlib, json, time
import numpy as np
from scipy.spatial.transform import Rotation
from tomato_exported_robot import ExportedRobot
root=Path(__file__).resolve().parents[2];run=root/'runs/native/joint_recenter_v03_20261102_01';out=root/'runs/offline/recenter_interface_readback_20261102_01';out.mkdir(exist_ok=False);start=time.monotonic();pins={}
def pin(path):pins[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest();return path
def read(path):return json.loads(pin(path).read_text())
native=read(run/'supervisor_result.json');assert native['passed']and native['worker']['joint_recenter_v03_component_passed'];assert native['worker']['controlled_steps']==264
closure=read(run/'source_closure.json')['source_sha256']
for name,h in closure.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h,name
definition=read(run/'known_wrench_definition.json');cases=read(run/'known_wrench_cases.json')['cases'];assert len(cases)==17
snapshot_path=pin(run/'robot_kinematic_snapshot_recenter.json');snapshot=json.loads(snapshot_path.read_text());fk=ExportedRobot(snapshot_path);joint=next(j for j in snapshot['joints']if j['child'].endswith('/MountedKnife'));C=np.linalg.inv(joint['inverse_child_joint_matrix']);tool=definition['body_names'].index('MountedKnife');backend=definition['backend_body_names'].index('MountedKnife');dt=1/38400;assert definition['native_reported_dt_s']==dt
records=[];maxF=maxM=0.;raw_count=0
for case in cases:
    label=case['case'];Fmax=Mmax=0.;linear=np.zeros(3);angular=np.zeros(3);assert len(case['rows'])==8
    for i,row in enumerate(case['rows']):
        with np.load(pin(run/f'{label}_interval{i}.npz'))as z:
            R0=Rotation.from_quat(z['before_body_link_pose'][tool,3:]).as_matrix();R1=Rotation.from_quat(z['after_body_link_pose'][tool,3:]).as_matrix();v0=z['before_body_com_velocity'][tool];v1=z['after_body_com_velocity'][tool];mass=z['mass'][tool];I=z['body_inertia_com_link_axes'][tool];raw=z['incoming_joint_wrench_backend'][0,backend].astype(float);w=z['applied_wrench_COM'].astype(float);assert np.array_equal(w,np.array(row['actual_requested_wrench_COM'],dtype=np.float32).astype(float))
            assert all(np.isfinite(a).all()for a in [R0,R1,v0,v1,I,raw,w])
            Jrot=R1@C[:3,:3];Fjoint=Jrot@raw[:3];Mjoint=Jrot@raw[3:]+np.cross(R1@(C[:3,3]-z['local_tool_com']),Fjoint);dp=mass*(v1[:3]-v0[:3]);dL=R1@I@R1.T@v1[3:]-R0@I@R0.T@v0[3:];netF=Fjoint+mass*np.array([0.,0.,-9.81])+w[:3];netM=Mjoint+w[3:];ferr=float(np.linalg.norm(dp/dt-netF));merr=float(np.linalg.norm(dL/dt-netM));Fmax=max(Fmax,ferr);Mmax=max(Mmax,merr);linear+=dp-dt*netF;angular+=dL-dt*netM;raw_count+=1
    maxF=max(maxF,Fmax);maxM=max(maxM,Mmax);records.append(dict(case=label,maximum_force_balance_error_n=Fmax,maximum_moment_balance_error_nm=Mmax,linear_impulse_error_ns=float(np.linalg.norm(linear)),angular_impulse_error_nms=float(np.linalg.norm(angular))))
signed_pass=maxF<=1e-6 and maxM<=1e-7
coasts=[];right=[definition['joint_names'].index(name)for name in snapshot['right_joint_names']];reference={}
for direction in ['down','up']:
    for repeat in range(2):
        label=f'coast_{direction}_{repeat}';trace=read(run/(label+'_coast_trace.json'));assert len(trace)==32;dq=np.zeros(36);dc=np.zeros(3);q0=np.array(trace[0]['q_before']);com=None
        for i,row in enumerate(trace):
            with np.load(pin(run/f'{label}_interval{i}.npz'))as z:
                com=z['local_tool_com'];assert np.max(abs(np.array(row['actual_tool_velocity_before'])-z['before_body_com_velocity'][tool]))<1e-14
                assert np.max(abs(np.array(row['actual_tool_velocity_after'])-z['after_body_com_velocity'][tool]))<1e-14
            q=np.array(row['q_after']);K=fk.forward(dict(zip(definition['joint_names'],q)))[fk.tool];assert np.max(abs(K-np.array(row['kinematic_tool_matrix_after'])))<1e-14
            dq+=dt*.5*(np.array(row['qd_before'])+row['qd_after']);dc+=dt*.5*(np.array(row['actual_tool_velocity_before'])[:3]+np.array(row['actual_tool_velocity_after'])[:3]);raw_count+=1
        K0=fk.forward(dict(zip(definition['joint_names'],q0)))[fk.tool];dck=K[:3,3]+K[:3,:3]@com-K0[:3,3]-K0[:3,:3]@com;qerror=float(abs((q-q0-dq)[right]).max());error=float(abs(dck-dc).max());assert qerror<=1e-9 and error<=1e-9 and np.linalg.norm(dck)>=.5e-6
        final=np.r_[q,trace[-1]['qd_after'],K.ravel()]
        if repeat==0:reference[direction]=final
        else:assert np.max(abs(final-reference[direction]))<=1e-9
        coasts.append(dict(case=label,right_joint_position_velocity_error_rad=qerror,actual_q_kinematic_COM_velocity_error_m=error,actual_q_kinematic_COM_displacement_m=dck.tolist()))
assert raw_count==264
pin(Path(__file__).resolve());report=dict(passed=bool(signed_pass),signed_load_measurement_passed=bool(signed_pass),original_force_budget_n=1e-6,original_moment_budget_nm=1e-7,maximum_force_balance_error_n=maxF,maximum_moment_balance_error_nm=maxM,calibration_cases=records,coast_cases=coasts,all_raw_intervals_read_back=raw_count,source_sha256=pins,elapsed_wall_s=time.monotonic()-start,scope='All17 signed/off-centre/clear calibration cases retain original absolute force/moment limits. Four actual-q coasts independently reconstruct position/velocity and replay. Original raw native body-pose/velocity gate failures are retained in native coast_measurements; this new interface uses float64 FK of actual native joint states. No coupled target, moving contact work or cutting qualification inferred.')
(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='source_sha256'},indent=2))
