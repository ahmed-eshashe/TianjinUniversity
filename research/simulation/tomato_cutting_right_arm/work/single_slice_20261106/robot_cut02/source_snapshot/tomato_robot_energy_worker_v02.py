"""Version 2: body-only native mass query and explicitly retained rotor energy."""
import argparse,signal,traceback,json
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=parked=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Robot energy references stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  plan_path=ROOT/'runs/offline/fixed_mount_scene_20261101_01/fixed_mount_plan.json';plan=json.loads(plan_path.read_text());waypoint_path=ROOT/'runs/offline/prepared_contact_candidate_20261102_03/ik_waypoints.json';waypoints=json.loads(waypoint_path.read_text());inputs=[plan_path,waypoint_path,Path(plan['scene'])]+[Path(name)for name in plan['source_sha256']]
  pins=capture_sources(out,[Path(__file__)],inputs=inputs)
  write(out,'input_manifest.json',dict(cases=2,mass_matrix_absolute_budget_kg_m2=1e-5,mass_matrix_relative_budget=2e-5,gravity_torque_absolute_budget_nm=1e-4,gravity_torque_relative_budget=2e-5,kinetic_energy_relative_budget=2e-5,kinetic_energy_absolute_budget_j=1e-10,physical_time_advanced_s=0.,controlled_steps=0,deformable_steps=0,newton_steps=0,native_mass_query_scope='Body inertia only; rotor inertia remains physically included by adding the unchanged native armature diagonal to both energy references. Test this relationship rather than assuming the query includes rotors.',prior_failed_run='robot_energy_operator_20261102_01',external_report='https://github.com/NVIDIA-Omniverse/PhysX/issues/575',scope='Static robot home and candidate contact configuration. Read-only actual native COM/Jacobian/mass/gravity data against independent body-sum mechanics. Placement is initial state assignment, NOT an executed route. Manufactured velocities, no actual dynamic work/feedback or target step.',references=[dict(url='https://docs.omniverse.nvidia.com/kit/docs/omni_physics/107.0/extensions/runtime/source/omni.physics.tensors/docs/api/python.html',claim='Articulation inertia tensors are in center-of-mass local frames.'),dict(path='/home/omen/IsaacLab/source/isaaclab/isaaclab/assets/articulation/base_articulation_data.py',claim='COM Jacobian row convention, generalized M(q), gravity-loading g(q).')]))
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch
  from scipy.spatial.transform import Rotation
  from tomato_parked_robot import ParkedRobot
  from tomato_robot_energy_reference import body_sum_reference,kinetic_energy
  torch.set_num_threads(1);parked=ParkedRobot(out,plan,1/2400);r=parked.robot;initial_count=int(parked.sim._physics_step_count);rng=np.random.default_rng(7791)
  for kind in ['home','candidate_contact']:
   q=parked.home.clone()
   if kind=='candidate_contact':q[:,parked.ids]=torch.tensor([waypoints[-1]['q_right_rad']],dtype=torch.float32)
   r.reset();r.write_joint_state_to_sim_index(position=q,velocity=torch.zeros_like(q));r.set_joint_position_target_index(target=q);r.write_data_to_sim();r.update(1/2400)
   def read(name):return getattr(r.data,name).torch[0].cpu().numpy().astype(float).copy()
   mass=read('body_mass');inertia=read('body_inertia').reshape(-1,3,3);pose=read('body_com_pose_w');R=Rotation.from_quat(pose[:,3:]).as_matrix();jac=read('body_com_jacobian_w');J=np.zeros((len(mass),6,r.num_joints));J[1:]=jac;armature=read('joint_armature');native_M=read('mass_matrix');native_g=read('gravity_compensation_forces');ref=body_sum_reference(mass,inertia,R,J,armature);M=ref['body_mass_matrix'];effective_M=M+np.diag(armature);native_effective_M=native_M+np.diag(armature);g=ref['gravity_compensation'];mass_error=float(abs(native_M-M).max());gravity_error=float(abs(native_g-g).max());energy_errors=[]
   np.savez(out/(kind+'_raw_before_assertion.npz'),mass=mass,inertia_com_local=inertia,rotation_com_world=R,jacobian_com_world=J,armature=armature,native_mass_matrix=native_M,native_gravity=native_g,reference_body_mass_matrix=M,reference_effective_mass_matrix=effective_M,reference_gravity=g)
   for _ in range(5):
    qd=rng.normal(size=r.num_joints)*.01;body_v=np.einsum('bki,i->bk',J,qd);body_energy=kinetic_energy(mass,ref['inertia_world'],body_v,armature,qd);joint_energy=float(.5*qd@native_effective_M@qd);error=abs(body_energy-joint_energy);energy_errors.append(dict(body_sum_j=body_energy,native_mass_matrix_j=joint_energy,error_j=error))
    if error>1e-10+2e-5*max(abs(body_energy),abs(joint_energy)):raise ValueError(('Manufactured energy reference failed',kind,energy_errors[-1]))
   np.savez(out/(kind+'_robot_mechanics.npz'),mass=mass,inertia_com_local=inertia,rotation_com_world=R,body_com_pose_world=pose,jacobian_com_world=J,armature=armature,native_mass_matrix=native_M,native_gravity=native_g,reference_mass_matrix=M,reference_effective_mass_matrix=effective_M,native_effective_mass_matrix=native_effective_M,reference_gravity=g,q=q.numpy()[0]);row=dict(case=kind,mass_matrix_error_kg_m2=mass_error,gravity_torque_error_nm=gravity_error,mass_matrix_scale=float(abs(native_M).max()),gravity_torque_scale=float(abs(native_g).max()),minimum_native_mass_eigenvalue=float(np.linalg.eigvalsh((native_M+native_M.T)/2).min()),manufactured_energy=energy_errors,body_names=r.body_names,joint_names=r.joint_names,actual_tool_pose=read('body_link_pose_w')[parked.tool].tolist(),local_tool_com=read('body_com_pose_b')[parked.tool,:3].tolist());write(out,'robot_energy_partial.json',dict(cases=cases+[row]))
   if mass_error>1e-5+2e-5*row['mass_matrix_scale']or gravity_error>1e-4+2e-5*row['gravity_torque_scale']or row['minimum_native_mass_eigenvalue']<=0:raise ValueError(row)
   cases.append(row)
  if int(parked.sim._physics_step_count)!=initial_count or parked.steps or parked.setup_steps:raise ValueError('Static reference unexpectedly advanced PhysX')
  if not sources_unchanged(pins):raise ValueError('Static robot mechanics inputs changed')
  write(out,'robot_energy_measurements.json',dict(passed=True,cases=cases,scope='Two static actual-robot body-sum mass/gravity/COM reference controls, manufactured velocities only. No actual route, contact, physical step, dynamic base reaction or actuator work qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  if parked is not None:parked.close()
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,robot_energy_operator_v02_passed=passed,cases_completed=len(cases),physical_time_advanced_s=0.,controlled_steps=0,deformable_steps=0,newton_steps=0))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
