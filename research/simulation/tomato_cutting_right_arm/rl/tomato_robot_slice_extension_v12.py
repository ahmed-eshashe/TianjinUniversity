"""Experimental mounted-robot research cut, retaining the original material.

Explicit one-step delayed reaction at the actual tool COM. This is not a
motor-work qualification. No prescribed material damage or mesh replacement.
"""
from pathlib import Path
import json,time,sys
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import lsq_linear
ROOT=Path(__file__).resolve().parents[1]

def run(sim,robot,tool,plan,advance,set_dt,target,closed,right,out,*,maximum_steps=20000,resume_checkpoint=None):
 import torch
 from pxr import UsdGeom,UsdShade,Sdf,Gf,Vt,Usd
 from tomato_master_remap_slice_engine import subcycled_engine as live_engine
 route=json.loads((ROOT/'work/single_slice_20261106/lateral_continuation_plan_v1.json').read_text());F=np.array(route['target_rotation']);placement=np.array(route['target_translation']);entry=[x for x in route['rows'] if x['phase']=='entry'];cut=[x for x in route['rows'] if x['phase']=='cut']
 for point in entry:
  before=target.clone();target=closed.clone();target[:,right]=torch.tensor(point['q'])
  for k in range(48):advance(before+(target-before)*((k+1)/48),'research_entry')
 for _ in range(240):advance(target,'research_entry_hold')
 sys.path.insert(0,str(ROOT/'scripts'))
 from reach_kinematics import ArmKinematics
 kinematics=ArmKinematics(Usd.Stage.Open(plan['scene']));mount=np.array(plan['mount_hand_from_knife'])
 def correction(position,rotation):
  measured=tool.data.root_pose_w.torch[0].cpu().numpy().astype(float);actual_rotation=Rotation.from_quat(measured[3:]).as_matrix();error=np.r_[np.asarray(position)-measured[:3],Rotation.from_matrix(np.asarray(rotation)@actual_rotation.T).as_rotvec()]
  q=robot.data.joint_pos.torch[0,right].cpu().numpy().astype(float);base=kinematics.transforms(q)[kinematics.hand_path]@mount;J=np.empty((6,7));eps=1e-6
  for j in range(7):
   shifted=q.copy();shifted[j]+=eps;T=kinematics.transforms(shifted)[kinematics.hand_path]@mount;J[:,j]=np.r_[(T[:3,3]-base[:3,3])/eps,Rotation.from_matrix(T[:3,:3]@base[:3,:3].T).as_rotvec()/eps]
  scale=np.array([1,1,1,.15,.15,.15]);command=target[0,right].cpu().numpy().astype(float);dq=lsq_linear(J*scale[:,None],error*scale,bounds=(kinematics.lower-command,kinematics.upper-command),tol=1e-12,max_iter=200).x
  return dq,float(np.linalg.norm(error[:3])),float(np.linalg.norm(error[3:]))
 desired_position=np.array(cut[0]['tool_origin']);desired_rotation=np.array(cut[0]['tool_rotation']);alignment=[]
 for attempt in range(120):
  dq,pe,re=correction(desired_position,desired_rotation);alignment.append(dict(attempt=attempt,position_error_m=pe,rotation_error_rad=re,actual_tool_pose=tool.data.root_pose_w.torch[0].tolist(),actual_root_pose=robot.data.root_pose_w.torch[0].tolist(),gravity=robot.data.gravity_compensation_forces.torch[0,right].tolist(),velocity=robot.data.joint_vel.torch[0,right].tolist(),projected=robot.root_view.get_dof_projected_joint_forces().numpy()[0,right].tolist(),actuation=robot.root_view.get_dof_actuation_forces().numpy()[0,right].tolist(),q=robot.data.joint_pos.torch[0,right].tolist(),command=target[0,right].tolist(),dq=dq.tolist()));(out/'alignment_progress.json').write_text(json.dumps(alignment,indent=2))
  if pe<2e-5 and re<2e-4:break
  corrected=target[0,right].cpu().numpy()+dq*min(.5,.002/max(float(np.max(abs(dq))),1e-15))
  if np.any(corrected<kinematics.lower)or np.any(corrected>kinematics.upper):raise ValueError('Alignment exceeds arm limits')
  target[:,right]=torch.tensor(corrected,dtype=target.dtype)
  for _ in range(60):advance(target,'research_alignment')
 else:raise ValueError(('Actual blade alignment failed',alignment[-1]))
 (out/'actual_alignment.json').write_text(json.dumps(alignment,indent=2));bias=target[0,right].cpu().numpy().astype(float)-np.array(cut[0]['q'])
 dt=1/2400;set_dt(dt)
 def canonical_pose():
  p=tool.data.root_pose_w.torch[0].cpu().numpy().astype(float);rotation=Rotation.from_quat(p[3:]).as_matrix();return np.r_[F.T@(p[:3]-placement),Rotation.from_matrix(F.T@rotation).as_quat()]
 com=tool.data.body_com_pose_b.torch[0,0,:3].cpu().numpy().astype(float)
 (out/'actual_entry.json').write_text(json.dumps(dict(canonical_pose=canonical_pose().tolist(),desired_world_origin=cut[0]['tool_origin'],desired_world_rotation=cut[0]['tool_rotation'],q=robot.data.joint_pos.torch[0].tolist(),target=target[0].tolist()),indent=2))
 resume=None
 if resume_checkpoint is not None:
  import hashlib
  resume_checkpoint=Path(resume_checkpoint);resume=json.loads(resume_checkpoint.with_suffix('.json').read_text());source_scope=json.loads((resume_checkpoint.parent.parent/'coupling_scope.json').read_text())
  if source_scope.get('interface_frame_extension')!='remainder_side_volume_backed_material_frame':raise ValueError('Checkpoint has a different material formulation')
  restored=resume['robot_state'];robot.write_joint_position_to_sim_index(position=torch.tensor([restored['q']],dtype=torch.float32));robot.write_joint_velocity_to_sim_index(velocity=torch.tensor([restored['qd']],dtype=torch.float32));tool.write_root_pose_to_sim_index(root_pose=torch.tensor([restored['tool_pose']],dtype=torch.float32));tool.write_root_velocity_to_sim_index(root_velocity=torch.tensor([restored['tool_com_velocity']],dtype=torch.float32));sim.forward();robot.update(0.);tool.update(0.)
  saved=np.load(resume_checkpoint);actual=canonical_pose();expected=np.r_[saved['blade_translation']+[-.0225,0,.0295],Rotation.from_matrix(saved['blade_rotation']).as_quat()]
  errors=dict(q=float(np.max(abs(robot.data.joint_pos.torch[0].cpu().numpy()-restored['q']))),qd=float(np.max(abs(robot.data.joint_vel.torch[0].cpu().numpy()-restored['qd']))),tool_position=float(np.linalg.norm(actual[:3]-expected[:3])),tool_rotation=float(Rotation.from_matrix(Rotation.from_quat(actual[3:]).as_matrix()@saved['blade_rotation'].T).magnitude()),tool_velocity=float(np.max(abs(tool.data.root_com_vel_w.torch[0].cpu().numpy()-restored['tool_com_velocity']))))
  if max(errors.values())>1e-6:raise ValueError(('Checkpoint restore discrepancy',errors))
  bias=np.asarray(resume['bias']);(out/'restore_audit.json').write_text(json.dumps(dict(passed=True,errors=errors,source_checkpoint=str(resume_checkpoint),sha256=hashlib.sha256(resume_checkpoint.read_bytes()).hexdigest(),native_constraint_warm_start_restored=False,material_history_preserved=True),indent=2))
 engine=live_engine(canonical_pose(),com,checkpoint=resume_checkpoint,padding_m=.001,diagnostic_directory=out);state=next(engine)
 if resume is not None:
  saved=np.load(resume_checkpoint);reaction_error=float(np.linalg.norm(state['wrench']-np.array(resume['reaction'])))
  if reaction_error>1e-8 or not np.array_equal(state['history'],saved['history']) or not np.array_equal(state['v'],saved['v']):raise ValueError(('Material checkpoint restoration mismatch',reaction_error))
  audit=json.loads((out/'restore_audit.json').read_text());audit.update(material_reaction_error=reaction_error,history_exactly_preserved=True,material_velocity_exactly_preserved=True);(out/'restore_audit.json').write_text(json.dumps(audit,indent=2));state['average_wrench_at_end_com']=np.array(resume['average_wrench'])
 design=json.loads((ROOT/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text());old=sim.stage.GetPrimAtPath('/CuttingTargetVisual');material=None
 if old.IsValid():
  material=UsdShade.MaterialBindingAPI(old).ComputeBoundMaterial()[0];UsdGeom.Imageable(old).MakeInvisible()
 meshes=[]
 for piece in design['pieces']:
  mesh=UsdGeom.Mesh.Define(sim.stage,'/ResearchCut/'+piece['side']);faces=np.asarray(piece['triangles'],np.int32);mesh.CreateFaceVertexCountsAttr([3]*len(faces));mesh.CreateFaceVertexIndicesAttr(faces.ravel().tolist());mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateDoubleSidedAttr(True)
  if material and material.GetPrim().IsValid():UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(material)
  else:mesh.CreateDisplayColorAttr([Gf.Vec3f(.7,.025,.01)])
  meshes.append(mesh)
 def display():
  points=Vt.Vec3fArray.FromNumpy(np.asarray(state['x']@F.T+placement,dtype=np.float32))
  for mesh in meshes:mesh.GetPointsAttr().Set(points)
 display();(out/'coupling_scope.json').write_text(json.dumps(dict(original_research_model=True,motion_route='lateral_continuation_plan_v1',native_contact_reporting_verified=True,board_footprint="board_footprint_v02.json",wrist_collision_refinement="original_CAD_shrink_wrapped_128_hulls",partition_scope="conservative_local_material_triangle_face_bound_full_CAD_queries",contact_sample_capacity=4194304,quadrature_rule="parent_when_original_error_budgets_pass_else_children",interface_frame_extension="remainder_side_volume_backed_material_frame",original_traction_quadrature_and_law=True,prescribed_material_damage=False,scripted_joint_targets=True,actual_measured_blade_pose=True,fixed_hand_attachment=True,friction_retention_validated=False,exchange='One-step delayed accepted reaction at actual tool COM',dt_s=dt,motor_work_qualified=False,experimental_validation='pending',initial_canonical_tool_pose=state['pose'].tolist(),tool_com_local=com.tolist()),indent=2))
 trajectory=np.array([p['q']for p in cut])
 # Vertical speed is 20 mm/s; derive duration directly from world Z travel.
 times=np.array([p['time_s'] for p in cut]);duration=float(times[-1])
 if np.any(np.diff(times)<=0):raise ValueError('Route times must increase')
 clock=0.;phase='cut';progress=0.;stable=0.;settled=0.;passed=False;records=[];start=time.monotonic()
 free=np.flatnonzero(np.array([n['side']for n in design['nodes']])=='slice')
 start_k=0
 if resume is not None:
  clock=resume['clock'];phase=resume['phase'];progress=resume['progress'];start_k=resume.get('outer_step',int(Path(resume_checkpoint).stem.split('_')[-1]))+1
  if abs(clock-state['elapsed'])>1e-12:raise ValueError('Checkpoint clocks disagree')
  source_run=Path(resume_checkpoint).parent.parent;trace_path=source_run/'cutting_trace.json'
  if trace_path.exists():parent_trace=json.loads(trace_path.read_text())
  else:parent_trace=[json.loads(p.read_text()) for p in sorted((source_run/'material_states').glob('step_*.json'))]
  records=[row for row in parent_trace if row['step']<start_k]
  if not records or records[-1]['step']!=start_k-1:raise ValueError('No archived accepted state matching checkpoint')
  (out/'prefix_provenance.json').write_text(json.dumps(dict(source_run=str(source_run),source_checkpoint=str(resume_checkpoint),source_trace_available=trace_path.exists(),archived_prefix_rows=len(records),complete_per_step_prefix=len(records)==start_k,missing_prefix_rows_not_synthesized=True,continuation_start_step=start_k),indent=2))
 if resume is not None and source_scope.get('motion_route')!='lateral_continuation_plan_v1':
  if Path(resume_checkpoint).resolve()!=Path(route['transition_checkpoint']).resolve():raise ValueError('Unexpected motion-transition checkpoint')
  previous_progress=progress;previous_phase=phase;progress=progress*route['parent_duration_s']/duration;phase='cut'
  (out/'motion_transition.json').write_text(json.dumps(dict(old_phase=previous_phase,old_progress=previous_progress,new_phase=phase,new_progress=progress,material_state_unchanged=True,physical_lateral_continuation=True),indent=2))
 for k in range(start_k,maximum_steps):
  if (out/'stop.request').exists():raise InterruptedError('Owned cutting stop request')
  if phase=='cut':progress=min(1.,progress+dt/duration)
  elif phase=='withdraw':progress=max(0.,progress-dt/duration)
  path_time=progress*duration;i=min(max(int(np.searchsorted(times,path_time,side='right'))-1,0),len(trajectory)-2);segment_dt=times[i+1]-times[i];u=(path_time-times[i])/segment_dt;target=closed.clone();desired_q=(1-u)*trajectory[i]+u*trajectory[i+1];desired_p=(1-u)*np.array(cut[i]['tool_origin'])+u*np.array(cut[i+1]['tool_origin']);
  target[:,right]=torch.tensor(desired_q+bias,dtype=target.dtype)
  if k%10==0:
   dq,pe,re=correction(desired_p,np.array(cut[i]['tool_rotation']));bias+=np.clip(4*10*dt*dq,-.0002,.0002)
   if pe>.001 or re>.005:raise ValueError(('Actual cutting route tracking failed',pe,re))
  target[:,right]=torch.tensor(desired_q+bias,dtype=target.dtype)
  canonical_wrench=state.get('average_wrench_at_end_com',state['wrench']);wrench=np.r_[F@canonical_wrench[:3],F@canonical_wrench[3:]]
  if not np.isfinite(wrench).all() or np.linalg.norm(wrench[:3])>100:raise ValueError('Nonfinite or excessive exploratory load')
  if tool.instantaneous_wrench_composer.active or tool.permanent_wrench_composer.active:raise ValueError('Ambiguous existing tool force queue')
  tool.instantaneous_wrench_composer.set_forces_and_torques_index(forces=torch.tensor(wrench[:3][None,None],dtype=torch.float32),torques=torch.tensor(wrench[3:][None,None],dtype=torch.float32),positions=None,is_global=True)
  velocity_target=torch.zeros_like(target)
  route_rate=(1. if phase=='cut' else -1. if phase=='withdraw' else 0.)
  velocity_target[:,right]=torch.tensor((trajectory[i+1]-trajectory[i])/segment_dt*route_rate,dtype=target.dtype)
  before=dict(q=robot.data.joint_pos.torch[0].tolist(),qd=robot.data.joint_vel.torch[0].tolist(),tool_pose=tool.data.root_pose_w.torch[0].tolist(),tool_com_velocity=tool.data.root_com_vel_w.torch[0].tolist())
  advance(target,'research_'+phase,velocity_target)
  current=dict(q=robot.data.joint_pos.torch[0].tolist(),qd=robot.data.joint_vel.torch[0].tolist(),tool_pose=tool.data.root_pose_w.torch[0].tolist(),tool_com_velocity=tool.data.root_com_vel_w.torch[0].tolist())
  (out/'pending_robot_interval.json').write_text(json.dumps(dict(step=k,phase=phase,progress=progress,clock=clock,bias=bias.tolist(),before=before,after=current,applied_wrench=wrench.tolist(),target=target[0].tolist(),velocity_target=velocity_target[0].tolist()),indent=2))
  if tool.instantaneous_wrench_composer.active:raise ValueError('Tool force queue was not consumed')
  try:state=engine.send(dict(pose=canonical_pose(),dt=dt))
  except BaseException:
   (out/'cutting_trace.json').write_text(json.dumps(records,indent=2));raise
  clock+=dt
  if k%25==0:
   checkpoint_path=out/'checkpoints'/f'step_{k:06d}.npz';state['checkpoint_writer'](checkpoint_path,outer_step=k,robot_state=current,phase=phase,progress=progress,clock=clock,bias=bias.tolist(),applied_wrench=wrench.tolist(),reaction=state['wrench'].tolist(),average_wrench=state.get('average_wrench_at_end_com',state['wrench']).tolist(),scope='Saved accepted material and robot coordinates; native constraint warm-start is not serialized')
  if abs(state['elapsed']-clock)>1e-12:raise ValueError('Target and robot clocks diverged')
  if phase=='cut' and (progress>=1 or state['separation']['topological_separation']):phase='withdraw'
  elif phase=='withdraw' and progress<=0:phase='settle'
  if phase=='settle':
   settled+=dt;supported=abs(float(state['x'][free,2].min()))<2e-4;quiet=float(np.linalg.norm(state['v'][free],axis=1).max())<.01;clear=np.linalg.norm(state['wrench'])<1e-5 and not state['eligible'].any();stable=stable+dt if state['separation']['topological_separation'] and supported and quiet and clear else 0.
   if stable>=.1:passed=True
  row=dict(step=k,time_s=clock,phase=phase,route_fraction=progress,failed_patches=state['separation']['failed_patches'],component_count=state['separation']['component_count'],applied_previous_wrench_world=wrench.tolist(),current_reaction_canonical=state['wrench'].tolist(),actual_tool_pose_canonical=state['pose'].tolist(),stable_supported_s=stable,wall_s=time.monotonic()-start)
  records.append(row)
  if k%25==0 and (out/'checkpoint_stop.request').exists():
   (out/'cutting_trace.json').write_text(json.dumps(records,indent=2));raise InterruptedError('Stopped at complete accepted checkpoint')
  if k%10==0:
   display();np.savez(out/'latest_material.npz',x=state['x'],v=state['v'],history=state['history'],actual_tool_pose=state['pose']);(out/'cutting_status.json').write_text(json.dumps(row,indent=2));print(row,flush=True)
  if passed or settled>=1:break
 display();result=dict(full_slice_success=passed,steps=len(records),final=state['separation'],stable_supported_duration_s=stable,motor_work_qualified=False,experimental_validation='pending',fixed_mount=True,scripted=True);(out/'cutting_result.json').write_text(json.dumps(result,indent=2));(out/'cutting_trace.json').write_text(json.dumps(records,indent=2))
 return result
