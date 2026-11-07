"""Independent CAD, fine-step work, block impulse and reset readback.

No SDK imports. CAD is independently queried at the first interval and all
fixed contact-clock endpoints, plus before/after each actual robot pose jump.
All saved fine-step node force/work/reaction/domain/clock channels are checked.
"""
from pathlib import Path
import argparse, gzip, hashlib, json, time
import numpy as np
from scipy.spatial.transform import Rotation
from tomato_host_fixed_pressure import evaluate_fixed

p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[2];run=a.run.resolve();out=a.output.resolve();out.mkdir(exist_ok=False);started=time.monotonic();pins={}
def pin(path):
    pins[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
    return path
def read(path): return json.loads(pin(path).read_text())
native=read(run/'supervisor_result.json');m=read(run/'input_manifest.json');closure=read(run/'source_closure.json')['source_sha256'];extra=read(run/'moving_protocol_pins.json')
assert native['passed'] and native['worker']['moving_contact_component_passed'] and native['worker']['moving_contact_work_qualified'] is False
for name,h in (closure|extra).items(): assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h, name
blade=read(root/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json');vertices=np.array(blade['vertices']);n=m['target_intervals_per_case'];dt=m['target_dt_s'];T=m['robot_dt_s'];sub=m['subcycles'];nrobot=m['robot_intervals_per_case'];assert dt*sub==T and n==1024
maxima=dict(force_n=0.,energy_j=0.,wrench_n_or_nm=0.,particle_work_j=0.,block_wrench_impulse_ns_nms=0.,ledger_force_impulse_ns=0.,ledger_moment_impulse_nms=0.,target_domain_motion_m=0.,rigid_domain_motion_m=0.)
records=[];saved={};cad_count=0;steps=0;body_steps=0
for label in m['cases']:
    robots=read(run/(label+'_robot_audit.json'));assert len(robots)==nrobot
    with gzip.open(pin(run/(label+'_target_audit.jsonl.gz')),'rt') as f: rows=[json.loads(line)for line in f]
    assert len(rows)==n
    cumulative=np.zeros(3);angular=np.zeros(3);block_impulse=np.zeros(6);block_work=0.;particle_sum=0.;quad=0.;qabs=0.;previous=None;last_raw=None;max_jump=0.
    for i,row in enumerate(rows):
        block=i//sub;robot=robots[block]
        raw=pin(run/f'{label}_target_interval{i}.npz')
        with np.load(raw) as z:
            x0=z['x_before'];x1=z['x_after'];v=z['v'];F=z['accepted_particle_force'];w=z['body_wrench'];origin=z['origin'];rotation=z['knife_rotation_held'];translation=z['knife_translation_held_sim'];com=z['local_tool_com'];packet={key:z['pressure_'+key]for key in ['indices','barycentric','areas']}
            if previous is not None: assert np.array_equal(x0,previous),'Target state discontinuity'
            previous=x1.copy()
            assert all(np.isfinite(q).all()for q in [x0,x1,v,F,w])
            assert row['interval']==i and row['coupling_block']==block
            assert abs(row['time_s']-(i+1)*dt)<1e-15 and abs(row['held_robot_time_s']-block*T)<1e-15
            held_pose=np.array(robot['actual_tool_pose_before']);assert np.max(abs(held_pose[:3]-origin-translation))<1e-14
            assert np.max(abs(Rotation.from_quat(held_pose[3:]).as_matrix()-rotation))<1e-14
            assert np.all(packet['areas']>0) and np.all(packet['barycentric']>=0)
            assert np.max(abs(packet['barycentric'].sum(1)-1),initial=0)<1e-12
            center=z['body_com_world'];expected_center=translation+origin+rotation@com;assert np.max(abs(center-expected_center))<1e-14
            wr=np.r_[-F.sum(0),-np.cross(x1+origin-center,F).sum(0)]
            ferror=eerror=0.;werror=float(abs(wr-w).max())
            if len(packet['areas']) and (i==0 or (i+1)%32==0):
                cad_count+=1;ref=evaluate_fixed(blade,x1,packet,rotation,translation,com);ref0=evaluate_fixed(blade,x0,packet,rotation,translation,com)
                ferror=float(abs(ref['force_n']-F).max());werror=max(werror,float(abs(ref['body_wrench']-w).max()));eerror=max(abs(ref['energy_j']-row['pressure_energy_after_target_j']),abs(ref0['energy_j']-row['pressure_energy_before_j']))
            work=float(np.sum(F*(x1-x0)));particle_sum+=work;block_work+=work;block_impulse+=dt*w;cumulative+=dt*F.sum(0);angular+=dt*np.cross(x1+origin,F).sum(0)
            motion=float(np.linalg.norm(x1-z['domain_reference_x_sim'],axis=1).max());rigid=float(np.linalg.norm(vertices@rotation.T+translation-z['domain_reference_blade_vertices_sim'],axis=1).max());audit=row['target_audit']
            errors=dict(force_n=ferror,energy_j=eerror,wrench_n_or_nm=werror,particle_work_j=abs(work-row['particle_pressure_work_j']),ledger_force_impulse_ns=float(np.linalg.norm(cumulative-np.array(audit['gravity_board_fixture_impulse_ns'][3]))),ledger_moment_impulse_nms=float(np.linalg.norm(angular-np.array(audit['gravity_board_fixture_angular_impulse_nms'][3]))),target_domain_motion_m=motion,rigid_domain_motion_m=rigid)
            for k,value in errors.items():maxima[k]=max(maxima[k],value)
            assert ferror<=1e-9 and eerror<=1e-12 and werror<=1e-10
            assert errors['particle_work_j']<=1e-15 and errors['ledger_force_impulse_ns']<=1e-12 and errors['ledger_moment_impulse_nms']<=1e-12
            assert abs(particle_sum-audit['prescribed_load_work_j'])<=1e-15
            assert max(motion,rigid)<=5e-6 and abs(motion-row['target_domain_motion_m'])<1e-14 and abs(rigid-row['rigid_domain_motion_m'])<1e-14
            refresh=row['packet_refresh']
            if refresh:
                q=refresh['quadrature'][-1]
                assert abs(refresh['native_energy_jump_j']-refresh['energy_jump_j'])<1e-12
                assert q['force_difference_from_old_n']<=q['force_budget_n'] and abs(q['energy_jump_from_old_j'])<=q['energy_budget_j']
                assert q['successive_force_difference_n']<=q['force_budget_n'] and q['successive_energy_difference_j']<=q['energy_budget_j']
                quad+=refresh['native_energy_jump_j'];qabs+=abs(refresh['native_energy_jump_j'])
            assert abs(quad-row['cumulative_quadrature_rebuild_energy_jump_j'])<1e-15 and abs(qabs-row['cumulative_absolute_quadrature_jump_j'])<1e-15
            assert row['minimum_volume_ratio']>.1 and row['board_penetration_m']<=1e-4 and row['maximum_penetration_m']<=1e-4 and row['maximum_source_displacement_m']<=.02 and row['maximum_speed_m_s']<=.1
            assert row['minimum_forbidden_body_target_inflated_gap_m']>.01 and row['minimum_blade_board_height_m']>.004
            assert np.linalg.norm(w[:3])<=.01 and np.linalg.norm(w[3:])<=.0002
            assert max(audit[k]for k in ['linear_impulse_residual_ns','angular_impulse_residual_nms','cumulative_absolute_nodal_impulse_residual_ns'])<=1e-9
            if i==0:
                initial_x=x0.copy();initial_velocity=np.array(robot['qd_before']);initial_pose=np.array(robot['actual_tool_pose_before'])
            if (i+1)%sub==0:
                assert robot['block']==block and abs(robot['time_s']-(i+1)*dt)<1e-15 and abs(robot['matched_target_time_s']-robot['time_s'])<1e-15
                assert robot['target_steps']==steps+1 and robot['robot_steps']==body_steps+1
                impulse_error=float(abs(block_impulse-np.array(robot['integrated_accepted_wrench_ns_nms'])).max());maxima['block_wrench_impulse_ns_nms']=max(maxima['block_wrench_impulse_ns_nms'],impulse_error)
                assert impulse_error<1e-15 and np.max(abs(block_impulse/T-np.array(robot['applied_average_wrench_n_nm'])))<1e-12
                assert abs(block_work-robot['block_target_pressure_work_j'])<1e-15
                newpose=np.array(robot['actual_tool_pose_after']);newR=Rotation.from_quat(newpose[3:]).as_matrix();newt=newpose[:3]-origin
                ref=evaluate_fixed(blade,x1,packet,newR,newt,com)if len(packet['areas'])else dict(energy_j=0.)
                assert abs(ref['energy_j']-robot['contact_potential_after_robot_j'])<1e-12
                assert abs(robot['pose_jump_contact_potential_change_j']-(ref['energy_j']-row['pressure_energy_after_target_j']))<1e-12
                endmotion=float(np.linalg.norm(vertices@newR.T+newt-z['domain_reference_blade_vertices_sim'],axis=1).max());assert endmotion<=5e-6
                max_jump=max(max_jump,float(np.linalg.norm(newpose[:3]-held_pose[:3])))
                bodyraw=pin(run/f'{label}_robot_interval{block}.npz')
                with np.load(bodyraw)as bz: assert np.max(abs(bz['body_wrench']-block_impulse/T))<1e-12
                if label=='clear':assert not np.any(F) and not np.any(w) and work==0 and robot['cumulative_actual_robot_contact_work_j']==0 and ref['energy_j']==0
                block_impulse[:]=0.;block_work=0.;body_steps+=1
            steps+=1
            last_raw=(x1.copy(),v.copy())
    assert not np.any(block_impulse) and block_work==0
    final=robots[-1];tool_move=float(np.linalg.norm(np.array(final['actual_tool_pose_after'])[:3]-initial_pose[:3]));assert tool_move>=.5e-6
    if label in ['feedback','replay']:assert abs(final['cumulative_actual_robot_contact_work_j'])>=1e-10
    saved[label]=dict(initial_x=initial_x,initial_qd=initial_velocity,initial_pose=initial_pose,final=last_raw+(np.array(final['q_after']),np.array(final['qd_after'])),first=robots[0])
    records.append(dict(case=label,target_intervals=n,actual_robot_intervals=nrobot,actual_tool_displacement_m=tool_move,maximum_coupling_pose_origin_jump_m=max_jump,cumulative_target_pressure_work_j=particle_sum,cumulative_actual_robot_contact_work_j=final['cumulative_actual_robot_contact_work_j'],cumulative_absolute_quadrature_jump_j=qabs))
    (out/'partial.json').write_text(json.dumps(dict(cases=records,maximum_independent_errors=maxima),indent=2)+'\n')
for label in m['cases']:
    for key in ['initial_x','initial_qd','initial_pose']:assert np.array_equal(saved[label][key],saved['feedback'][key]),('Actual reset initial state differs',label,key)
replay=[float(abs(x-y).max())for x,y in zip(saved['feedback']['final'],saved['replay']['final'])];assert replay[0]<=1e-10 and replay[1]<=1e-8 and max(replay[2:])<=1e-6
delta=np.array(saved['feedback']['first']['qd_after'])-saved['no_feedback']['first']['qd_after'];power=float(np.array(saved['feedback']['first']['generalized_pressure_torque_nm'])@delta);assert np.linalg.norm(delta)>1e-9 and power>0
assert steps==4096 and body_steps==32*m['coupling_refinement'] and native['worker']['deformable_steps']==steps and native['worker']['matched_physx_steps']==body_steps
pin(Path(__file__).resolve())
report=dict(component_readback_passed=True,actual_target_intervals=steps,actual_robot_intervals=body_steps,independent_CAD_check_count=cad_count,cases=records,maximum_independent_errors=maxima,replay_errors_x_v_q_qd=replay,paired_joint_velocity_response_rad_s=float(np.linalg.norm(delta)),paired_virtual_power_increment_w=power,source_sha256=pins,elapsed_wall_s=time.monotonic()-started,work_qualified=False,scope='All fine-step node force/work/reaction/domain/clock channels, accumulated six-axis block impulse, actual end-pose contact potential, geometry/physical stops, observed motion, paired causal feedback, loaded replay and no-contact clear. Independent CAD at first/contact-clock endpoints and actual coupling endpoints. Full robot-body/measured-knife work audit and coupling refinement are separate; no cut or training qualification.')
(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='source_sha256'},indent=2))
