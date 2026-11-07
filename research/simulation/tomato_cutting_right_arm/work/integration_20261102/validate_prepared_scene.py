"""Read actual compressed synchronized scene traces, clocks and numerical gates."""
from pathlib import Path
import argparse,gzip,json,hashlib
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.run.resolve();manifest=json.loads((run/'input_manifest.json').read_text());result=json.loads((run/'supervisor_result.json').read_text());measure=json.loads((run/'hold_measurements.json').read_text());provenance=json.loads((run/'prepared_state_provenance.json').read_text());parent=Path(provenance['parent']);parent_energy=json.loads((parent/'static_preparation_measurements.json').read_text())['prestressed_physical_energy']['total_j'];n=manifest['deformable_steps']//manifest['episodes'];dt=manifest['dt_s'];loaded='load_case'in manifest;robot_reference=np.empty((n,79));records=[];finals=[];pins={};max_q=max_qd=max_tool=0.;work_error=impulse_error=moment_error=0.
if not result['passed']or result['worker']['matched_physx_steps']!=manifest['deformable_steps']or result['worker']['controlled_steps']!=manifest['deformable_steps']+3 or result['worker']['setup_physx_steps']!=3:raise ValueError('Native result or actual clock counts not qualified')
if loaded:
 field=np.load(run/'synthetic_load_definition.npz');center=field['prepared_cap_center_world'];definition=json.loads((run/'load_definition.json').read_text())
for ep in range(manifest['episodes']):
 path=run/f'episode{ep}_audit.jsonl.gz';initial=measure['episodes'][ep]['initial_energy_j'];count=0;previous_projection=0.;independent_work=0.;previous_impulse=np.zeros(3);previous_angular=np.zeros(3);last_window_speed=0.;maximum_speed=0.;peak_force=0.;peak_moment=0.;maximum_energy=-float('inf')
 if abs(initial-parent_energy)>1e-12:raise ValueError('Prepared initial energy differs from qualified prestress')
 with gzip.open(path,'rt')as stream:
  for count,line in enumerate(stream,1):
   d=json.loads(line);robot=d['parked_robot'];t=count*dt
   if abs(d['time_s']-t)>1e-12 or abs(d['matched_robot_time_s']-t)>1e-12 or robot['episode_physx_steps']!=count or robot['total_matched_physx_steps']!=ep*n+count:raise ValueError('Robot/target timestamp or counter mismatch')
   values=[d[k]for k in ['minimum_volume_ratio','board_penetration_m','linear_impulse_residual_ns','angular_impulse_residual_nms','cumulative_absolute_nodal_impulse_residual_ns','maximum_displacement_m','maximum_speed_m_s']]+[d['energy']['total_j'],initial]
   if not np.isfinite(values).all()or d['minimum_volume_ratio']<=.1 or d['board_penetration_m']>.0001 or d['maximum_displacement_m']>.02 or d['linear_impulse_residual_ns']>1e-4 or d['angular_impulse_residual_nms']>1e-5 or d['cumulative_absolute_nodal_impulse_residual_ns']>1e-4:raise ValueError('Saved target audit exceeds original operating/numerical gate')
   energy_increase=d['energy']['total_j']-initial;maximum_speed=max(maximum_speed,d['maximum_speed_m_s'])
   if t>manifest['duration_s']-1.-dt/2:last_window_speed=max(last_window_speed,d['maximum_speed_m_s'])
   if abs(energy_increase-d['energy_increase_j'])>1e-12:raise ValueError('Recorded physical energy baseline mismatch')
   if loaded:
    alpha=float(np.sin(np.pi*t/.1))if t<.1 else 0.;F=alpha*field['field_n'].sum(0);actual=np.array(d['gravity_board_fixture_force_n'][3]);logged=np.array(d['applied_synthetic_force_n']);M=np.array(d['applied_moment_about_prepared_center_nm']);peak_force=max(peak_force,float(np.linalg.norm(logged)));peak_moment=max(peak_moment,float(np.linalg.norm(M)))
    if abs(alpha-d['held_load_amplitude'])>1e-14 or np.linalg.norm(F-actual)>1e-10 or np.linalg.norm(F-logged)>1e-10 or peak_force>.010000000001 or peak_moment>.0002 or maximum_speed>.1:raise ValueError('Synthetic force pulse/envelope mismatch')
    impulse=np.array(d['gravity_board_fixture_impulse_ns'][3]);angular=np.array(d['gravity_board_fixture_angular_impulse_nms'][3]);impulse_error=max(impulse_error,float(np.linalg.norm(impulse-previous_impulse-dt*F)));moment_error=max(moment_error,float(np.linalg.norm(angular-previous_angular-dt*(M+np.cross(center,F)))));previous_impulse=impulse;previous_angular=angular
    if 'unit_amplitude_load_projection_j'in d:
     projection=d['unit_amplitude_load_projection_j'];independent_work+=alpha*(projection-previous_projection);previous_projection=projection
    elif manifest['load_case']!='clear':raise ValueError('Missing sufficient coordinate statistic for independent held-work reconstruction')
    work_error=max(work_error,abs(independent_work-d['prescribed_load_work_j']));balanced=energy_increase-independent_work
    if not np.isfinite([balanced,independent_work,work_error,impulse_error,moment_error]).all()or work_error>1e-12 or impulse_error>1e-12 or moment_error>1e-12 or abs(balanced-d['energy_increase_after_load_work_j'])>1e-12:raise ValueError('Held-load impulse/moment/work reconstruction failed')
   else:balanced=energy_increase
   maximum_energy=max(maximum_energy,balanced)
   if balanced>1e-5:raise ValueError('Original energy-rise bound exceeded after accounting for actual external work')
   state=np.r_[robot['q'],robot['qd'],robot['tool_pose']]
   if state.shape!=(79,)or not np.isfinite(state).all()or robot['minimum_target_aabb_gap_m']<=.015 or robot['minimum_blade_board_height_m']<=.004 or robot['mount_position_error_m']>2e-5 or robot['mount_angle_error_rad']>2e-4 or robot['maximum_joint_speed_rad_s']>3. or robot['right_tracking_error_rad']>.03 or robot['maximum_rigid_contact_force_n']>.1:raise ValueError('Recorded robot state exceeds inherited clear-scene gates')
   if ep==0:robot_reference[count-1]=state
   else:
    delta=abs(state-robot_reference[count-1]);max_q=max(max_q,float(delta[:36].max()));max_qd=max(max_qd,float(delta[36:72].max()));max_tool=max(max_tool,float(delta[72:].max()))
   trace=d['nonlinear_trace'];last=trace[-1];declared=manifest['solver_declared_duration_s']
   if last.get('converged') is not True or last['absolute_nodal_impulse_residual_ns']>1e-4*dt/declared or last['maximum_euler_velocity_defect_m_s']>1e-6*dt/declared:raise ValueError('Accepted mechanical interval lacks required nonlinear convergence')
 if count!=n or measure['episodes'][ep]['steps']!=n:raise ValueError('Incomplete gzip records or episode steps')
 if not loaded and not manifest['screen']and not manifest['preview']and last_window_speed>.001:raise ValueError('Full unloaded hold settling-speed gate failed')
 if loaded and not manifest['screen']and manifest['load_case']!='clear'and peak_force<.009999:raise ValueError('Full challenge never reached nominal force')
 final=np.load(run/f'episode{ep}_final.npz');finals.append((final['x_sim'],final['v']));records.append(dict(episode=ep,complete_records=count,final_time_s=t,maximum_speed_m_s=maximum_speed,last_one_second_maximum_speed_m_s=last_window_speed,maximum_energy_increase_after_actual_load_work_j=maximum_energy,peak_synthetic_force_n=peak_force,peak_synthetic_moment_nm=peak_moment));pins[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
pe=float(abs(finals[0][0]-finals[1][0]).max());ve=float(abs(finals[0][1]-finals[1][1]).max())
if pe>1e-10 or ve>1e-8 or max_q>1e-5 or max_qd>2e-5 or max_tool>2e-6:raise ValueError('Independent per-step robot/final-target replay failed')
for q in [run/'supervisor_result.json',run/'input_manifest.json',run/'source_closure.json',parent/'static_preparation_measurements.json',Path(__file__)]:pins[str(q)]=hashlib.sha256(q.read_bytes()).hexdigest()
a.output.mkdir(exist_ok=False);report=dict(passed=True,episodes=records,actual_target_steps=n*manifest['episodes'],actual_matched_physx_steps=n*manifest['episodes'],separate_setup_physx_steps=3,target_replay_position_error_m=pe,target_replay_velocity_error_m_s=ve,robot_replay_joint_error_rad=max_q,robot_replay_velocity_error_rad_s=max_qd,robot_replay_tool_pose_component_error=max_tool,maximum_reconstructed_load_work_error_j=work_error,maximum_load_channel_impulse_error_ns=impulse_error,maximum_load_channel_angular_impulse_error_nms=moment_error,source_sha256=pins,scope='Independent gzip completeness, every accepted clock/nonlinear/numerical/geometry gate, original prestress energy baseline, full per-step robot replay and final target replay. For prescribed scalar-amplitude fields only, reconstruct held-load work from saved coordinate projection and audit actual load impulse/moment channels. No new cut, contact adapter, stability beyond tested envelope or training claim.');(a.output/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='source_sha256'},indent=2))
