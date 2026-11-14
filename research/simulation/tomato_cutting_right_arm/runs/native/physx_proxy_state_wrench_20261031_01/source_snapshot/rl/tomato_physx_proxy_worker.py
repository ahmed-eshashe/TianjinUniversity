"""CPU PhysX pose/CUDA echo, one wrench pulse and one zero-input coast step."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import signal
import traceback
from tomato_isaac_startup_worker import write
from tomato_physx_bridge_reference import reference_packet
from tomato_physx_proxy_reference import check_pulse,check_coast

ROOT=Path(__file__).resolve().parents[1]
DT=1/1200


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output;app=sim=None;passed=False;steps=0;echoes=0
    def stop(signum,frame):raise InterruptedError('CPU PhysX proxy check stopped')
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    def result():
        return {'diagnostic_passed':passed,'shutdown_requested':app is not None,
            'shutdown_completion':'supervisor_must_observe_exit','physx_proxy_cases_completed':2 if passed else 0,
            'controlled_steps':steps,'cuda_state_echoes_completed':echoes,'physx_proxy_checks_passed':passed,
            'training':False,'newton_contact_feedback_validated':False,'robot_validated':False}
    try:
        pins={}
        for name in ('tomato_physx_proxy_worker.py','tomato_physx_proxy_reference.py','tomato_physx_bridge_reference.py',
                     'tomato_reaction_metadata.py','tomato_wrench_contract.py','tomato_isaac_startup_guard.py'):
            p=ROOT/'rl'/name;pins[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
        write(out,'input_manifest.json',{'source_sha256':pins,'body_count':2,'controlled_step_cap':2,'dt_s':DT,
            'scope':'Own CPU PhysX bodies, CUDA format echo only; no robot, blade or Newton contact solve.'})
        write(out,'worker_status.json',{'stage':'launching_cpu_physx'})
        from isaaclab.app import AppLauncher
        launcher=AppLauncher(headless=True,device='cpu',visualizer=['none']);app=launcher.app
        import torch
        import warp as wp
        import isaaclab.sim as sim_utils
        from isaaclab.assets import RigidObject,RigidObjectCfg
        from isaaclab_physx.physics import PhysxCfg
        from isaaclab_physx.sim.schemas import PhysxRigidBodyCfg
        sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(device='cpu',dt=DT,gravity=(0.,0.,0.),
            physics=PhysxCfg(),use_fabric=False,use_newton_actuators=False,log_dir=str(out)))
        bodies=[];descriptors=[]
        for index,offset in enumerate((0.,.01)):
            angle=0. if index==0 else math.pi/2
            pose=[float(index),0.,1.,0.,0.,math.sin(angle/2),math.cos(angle/2)]
            spawn=sim_utils.CuboidCfg(size=(.02,.02,.02),
                rigid_props=[sim_utils.UsdPhysicsRigidBodyCfg(kinematic_enabled=False),
                    PhysxRigidBodyCfg(linear_damping=0.,angular_damping=0.,disable_gravity=True,
                                     sleep_threshold=0.,stabilization_threshold=0.)],
                collision_props=sim_utils.UsdPhysicsCollisionCfg(collision_enabled=False),
                mass_props=sim_utils.MassCfg(mass=.02,density=0.))
            body=RigidObject(RigidObjectCfg(prim_path=f'/World/BridgeProxy{index}',spawn=spawn,
                init_state=RigidObjectCfg.InitialStateCfg(pos=tuple(pose[:3]),rot=tuple(pose[3:]))))
            bodies.append(body);descriptors.append({'id':f'proxy{index}','pose':pose,'com_local_m':[offset,0.,0.]})
        sim.reset()
        if 'isaaclab_physx' not in sim.physics_manager.__module__:raise ValueError('Expected PhysX backend')
        step_baseline=int(sim._physics_step_count)
        def state(body):
            return {'pose_xyzw':body.data.root_link_pose_w.torch.detach().cpu().tolist()[0],
                    'velocity_com_world':body.data.root_com_vel_w.torch.detach().cpu().tolist()[0],
                    'com_local_pose':body.data.body_com_pose_b.torch.detach().cpu().tolist()[0][0]}
        records=[]
        for body,description in zip(bodies,descriptors):
            if str(body.device)!='cpu':raise ValueError('Expected CPU PhysX asset')
            body.reset()
            body.set_coms_index(coms=torch.tensor([[description['com_local_m']+[0.,0.,0.,1.]]],dtype=torch.float32))
            body.set_inertias_index(inertias=torch.tensor([[[.001,0.,0.,0.,.001,0.,0.,0.,.001]]],dtype=torch.float32))
            body.write_root_pose_to_sim_index(root_pose=torch.tensor([description['pose']],dtype=torch.float32))
            echo_velocity=[.02,-.01,.03,.1,.2,-.1]
            body.write_root_com_velocity_to_sim_index(root_velocity=torch.tensor([echo_velocity],dtype=torch.float32))
            echo=state(body)
            if math.dist(echo['pose_xyzw'],description['pose'])>1e-6 or math.dist(echo['velocity_com_world'],echo_velocity)>1e-6:
                raise ValueError('CPU PhysX pose/COM velocity readback mismatch')
            if math.dist(echo['com_local_pose'][:3],description['com_local_m'])>1e-7:raise ValueError('COM offset readback mismatch')
            cuda_pose=wp.empty(1,dtype=wp.transform,device='cuda:0')
            cuda_velocity=wp.empty(1,dtype=wp.spatial_vector,device='cuda:0')
            wp.copy(cuda_pose,body.data.root_link_pose_w.warp);wp.copy(cuda_velocity,body.data.root_com_vel_w.warp);wp.synchronize()
            if cuda_pose.numpy().tolist()[0]!=echo['pose_xyzw'] or cuda_velocity.numpy().tolist()[0]!=echo['velocity_com_world']:
                raise ValueError('CPU to CUDA buffer echo mismatch')
            echoes+=1
            body.write_root_com_velocity_to_sim_index(root_velocity=torch.zeros((1,6),dtype=torch.float32))
            initial=state(body);mass=float(body.data.body_mass.torch[0,0]);matrix=body.data.body_inertia.torch[0,0].tolist()
            if any(abs(matrix[i]-(.001 if i in (0,4,8) else 0.))>1e-8 for i in range(9)):
                raise ValueError('Expected explicit isotropic diagnostic inertia')
            base_packet=reference_packet(initial['pose_xyzw'],initial['velocity_com_world'],initial['com_local_pose'][:3],
                [-3.,0.,0.],[0.,0.,0.])
            contact=[v+d for v,d in zip(base_packet['com_world_m'],[0.,.0004,0.])]
            packet=reference_packet(initial['pose_xyzw'],initial['velocity_com_world'],initial['com_local_pose'][:3],[-3.,0.,0.],contact)
            body.instantaneous_wrench_composer.set_forces_and_torques_index(
                forces=torch.tensor([[packet['physx_wrench']['force_n']]],dtype=torch.float32),
                torques=torch.tensor([[packet['physx_wrench']['torque_about_com_nm']]],dtype=torch.float32),
                positions=None,is_global=True)
            body.write_data_to_sim()
            if body.instantaneous_wrench_composer.active or body.permanent_wrench_composer.active:
                raise ValueError('One-shot composer did not clear or permanent wrench active')
            records.append({'id':description['id'],'readback_echo':echo,'cuda_echo_exact':True,
                'initial':initial,'mass_kg':mass,'isotropic_inertia_kg_m2':matrix[0],'packet':packet})
        write(out,'proxy_initial_and_echo.json',{'cases':records,'step_baseline_after_reset':step_baseline})
        if (out/'stop.request').exists():raise InterruptedError('Stopped before wrench pulse step')
        write(out,'worker_status.json',{'stage':'one_shot_wrench_step','controlled_steps':steps})
        sim.step(render=False);steps+=1
        for body,record in zip(bodies,records):
            body.update(DT);record['after_pulse']=state(body)
            record['pulse_check']=check_pulse(record['initial']['velocity_com_world'],record['after_pulse']['velocity_com_world'],
                record['packet']['physx_wrench']['force_n'],record['packet']['physx_wrench']['torque_about_com_nm'],
                record['mass_kg'],record['isotropic_inertia_kg_m2'],DT)
        write(out,'proxy_after_pulse.json',{'cases':records,'controlled_steps':steps})
        if (out/'stop.request').exists():raise InterruptedError('Stopped before zero-input coast step')
        for body in bodies:
            if body.instantaneous_wrench_composer.active or body.permanent_wrench_composer.active:raise ValueError('Unexpected queued wrench')
            body.write_data_to_sim()  # No new input, deliberately testing backend clearing.
        sim.step(render=False);steps+=1
        for body,record in zip(bodies,records):
            body.update(DT);record['after_coast']=state(body)
            record['coast_check']=check_coast(record['after_pulse']['velocity_com_world'],record['after_coast']['velocity_com_world'])
        if steps!=2 or int(sim._physics_step_count)!=step_baseline+2:raise ValueError('Unexpected controlled step count')
        write(out,'physx_proxy_measurements.json',{'cases':records,'controlled_steps':steps,'dt_s':DT,
            'physics_manager':sim.physics_manager.__module__,'physics_steps_before_pulse':step_baseline,
            'physics_steps_after_coast':int(sim._physics_step_count),'cuda_state_echoes_completed':echoes,
            'comparison_scope':'CPU PhysX synthetic bodies: pose/velocity echo 1e-6, COM echo 1e-7 m; pulse linear error 2e-5 m/s, angular 2e-6 rad/s; coast drift 2e-6.',
            'newton_state_or_contact_solve_connected':False,'robot_or_blade_loaded':False})
        passed=True
    except BaseException:
        write(out,'worker_failure.json',{'traceback':traceback.format_exc()});traceback.print_exc()
    finally:
        try:
            if sim is not None:
                sim.stop()
                sim_utils.SimulationContext.clear_instance()
            write(out,'worker_result.json',result())
            if app is not None:app.close(exit_code=0 if passed else 1)
        except BaseException:
            passed=False;write(out,'close_failure.json',{'traceback':traceback.format_exc()})
        write(out,'worker_result.json',result())
    return 0 if passed else 1


if __name__=='__main__':raise SystemExit(main())
